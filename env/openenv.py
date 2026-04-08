"""
OpenEnv Productivity Environment
=================================
Implements the OpenEnv interface for productivity task simulation.
Supports 4 task types with a Memory-Based Multi-Step system.

Interface:
  env.reset()        → Observation
  env.step(action)   → (Observation, Reward, done, info)
  env.state()        → Dict (current state snapshot)
"""

import random
import copy
from typing import Any, Dict, List, Optional, Tuple

from env.models import Observation, Action, Reward, StepResult, MemoryEntry
from env.tasks import (
    EMAIL_TASKS,
    DATA_CLEANING_TASKS,
    CODE_REVIEW_TASKS,
    SMART_ASSISTANT_TASKS,
)
from grader.graders import (
    grade_email_triage,
    grade_data_cleaning,
    grade_code_review,
    grade_smart_assistant_step,
)


class OpenEnv:
    """
    OpenEnv-compatible environment for productivity AI tasks.

    Manages a queue of tasks across four categories:
      1. email_triage      — classify emails (easy)
      2. data_cleaning     — clean messy JSON data (medium)
      3. code_review       — identify & fix bugs (hard)
      4. smart_assistant   — multi-step email→extract→schedule pipeline (advanced)

    Episode structure:
      - An episode is one task instance.
      - Call reset() to start a new episode.
      - Call step(action) to submit a response.
      - Multi-step tasks (smart_assistant) require multiple step() calls.
      - done=True signals the episode is finished.
    """

    # All supported task types in order of difficulty
    TASK_TYPES = ["email_triage", "data_cleaning", "code_review", "smart_assistant"]

    def __init__(self, seed: Optional[int] = 42, task_order: str = "sequential"):
        """
        Args:
            seed:        Random seed for reproducibility.
            task_order:  'sequential' (go through tasks in order) or 'random'.
        """
        self.seed = seed
        self.task_order = task_order
        self._rng = random.Random(seed)

        # Build a flat task queue: each entry is (task_type, task_def)
        self._task_queue: List[Tuple[str, Dict]] = []
        self._build_task_queue()

        # Current episode state
        self._current_task_type: Optional[str] = None
        self._current_task_def: Optional[Dict] = None
        self._current_step: int = 0
        self._episode_rewards: List[float] = []
        self._memory: List[Dict] = []          # Memory across steps (Task 4)
        self._queue_index: int = 0
        self._done: bool = False
        self._total_episodes_run: int = 0
        self._cumulative_scores: List[float] = []

    # ─────────────────────────────────────────
    # Task Queue Construction
    # ─────────────────────────────────────────

    def _build_task_queue(self) -> None:
        """Populate the internal task queue from all task pools."""
        queue = []
        for task in EMAIL_TASKS:
            queue.append(("email_triage", task))
        for task in DATA_CLEANING_TASKS:
            queue.append(("data_cleaning", task))
        for task in CODE_REVIEW_TASKS:
            queue.append(("code_review", task))
        for task in SMART_ASSISTANT_TASKS:
            queue.append(("smart_assistant", task))

        if self.task_order == "random":
            self._rng.shuffle(queue)

        self._task_queue = queue

    # ─────────────────────────────────────────
    # OpenEnv Interface
    # ─────────────────────────────────────────

    def reset(self) -> Observation:
        """
        Start a new episode.
        Advances to the next task in the queue.
        Returns the initial Observation for the new episode.
        """
        if self._queue_index >= len(self._task_queue):
            # Wrap around (allow multiple passes over the task set)
            self._queue_index = 0
            if self.task_order == "random":
                self._rng.shuffle(self._task_queue)

        self._current_task_type, self._current_task_def = self._task_queue[self._queue_index]
        self._queue_index += 1
        self._current_step = 0
        self._episode_rewards = []
        self._memory = []
        self._done = False
        self._total_episodes_run += 1

        return self._build_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Process an agent action and advance the environment.

        Args:
            action: An Action object with action_type and payload.

        Returns:
            (observation, reward, done, info)
            - observation: Updated observation (next step or terminal)
            - reward:      Reward for this step
            - done:        True if the episode is complete
            - info:        Diagnostic dictionary
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        if self._current_task_def is None:
            raise RuntimeError("No active task. Call reset() first.")

        # Penalize invalid or empty actions
        if not action.action_type or not action.payload:
            reward = Reward(
                score=0.0,
                feedback="Invalid action: action_type or payload is missing.",
            )
            self._episode_rewards.append(0.0)
            obs = self._build_observation()
            return obs, reward, self._done, self._build_info()

        # Dispatch to the correct grader
        reward = self._grade_action(action)
        self._episode_rewards.append(reward.score)

        # Advance step for multi-step tasks
        if self._current_task_type == "smart_assistant":
            total_steps = len(self._current_task_def["steps"])
            # Store memory entry
            self._memory.append({
                "step": self._current_step + 1,
                "action_type": action.action_type,
                "content": str(action.payload.get("response", ""))[:500],
                "extracted": self._try_extract_memory(action.payload),
            })
            self._current_step += 1
            if self._current_step >= total_steps:
                self._done = True
        else:
            # Single-step tasks always terminate after one step
            self._done = True

        if self._done:
            ep_score = round(sum(self._episode_rewards) / len(self._episode_rewards), 4)
            self._cumulative_scores.append(ep_score)

        obs = self._build_observation()
        info = self._build_info()

        return obs, reward, self._done, info

    def state(self) -> Dict[str, Any]:
        """
        Returns a full snapshot of the current environment state.
        Useful for debugging, logging, and reproducibility checks.
        """
        return {
            "task_type": self._current_task_type,
            "task_id": self._current_task_def.get("task_id") if self._current_task_def else None,
            "current_step": self._current_step,
            "done": self._done,
            "episode_rewards": copy.deepcopy(self._episode_rewards),
            "memory": copy.deepcopy(self._memory),
            "total_episodes_run": self._total_episodes_run,
            "cumulative_scores": copy.deepcopy(self._cumulative_scores),
            "queue_index": self._queue_index,
            "total_tasks_in_queue": len(self._task_queue),
            "average_score_so_far": (
                round(sum(self._cumulative_scores) / len(self._cumulative_scores), 4)
                if self._cumulative_scores else None
            ),
        }

    # ─────────────────────────────────────────
    # Internal Helpers
    # ─────────────────────────────────────────

    def _build_observation(self) -> Observation:
        """Construct an Observation from current environment state."""
        td = self._current_task_def
        tt = self._current_task_type

        if tt == "email_triage":
            return Observation(
                task_id=td["task_id"],
                task_type=tt,
                content=td["content"],
                metadata={
                    **td.get("metadata", {}),
                    "valid_labels": ["spam", "important", "work"],
                    "instruction": "Classify this email as: spam, important, or work.",
                },
                step=0,
                done=self._done,
            )

        elif tt == "data_cleaning":
            return Observation(
                task_id=td["task_id"],
                task_type=tt,
                content=td["content"],
                metadata={
                    **td.get("metadata", {}),
                    "cleaning_rules": td.get("cleaning_rules", []),
                    "instruction": (
                        "Clean the provided JSON data according to the cleaning_rules. "
                        "Return a JSON object with the same top-level key containing cleaned records."
                    ),
                },
                step=0,
                done=self._done,
            )

        elif tt == "code_review":
            return Observation(
                task_id=td["task_id"],
                task_type=tt,
                content=td["content"],
                metadata={
                    **td.get("metadata", {}),
                    "instruction": (
                        "Review this code. Identify any bugs, explain each issue, "
                        "and provide corrected code. "
                        "Return: {explanation: '...', fixed_code: '...'}"
                    ),
                },
                step=0,
                done=self._done,
            )

        elif tt == "smart_assistant":
            steps = td["steps"]
            if self._current_step < len(steps):
                step_def = steps[self._current_step]
                return Observation(
                    task_id=td["task_id"],
                    task_type=tt,
                    content=step_def["instruction"],
                    metadata={
                        **td.get("metadata", {}),
                        "step_number": self._current_step + 1,
                        "hint": step_def.get("hint", ""),
                        "memory": copy.deepcopy(self._memory),
                        "instruction": f"Step {self._current_step + 1} of {len(steps)}: {step_def['instruction']}",
                    },
                    step=self._current_step,
                    total_steps=len(steps),
                    done=self._done,
                )
            else:
                # All steps done — terminal observation
                return Observation(
                    task_id=td["task_id"],
                    task_type=tt,
                    content="All steps completed.",
                    metadata={"memory": copy.deepcopy(self._memory)},
                    step=self._current_step,
                    total_steps=len(steps),
                    done=True,
                )

        raise ValueError(f"Unknown task type: {tt}")

    def _grade_action(self, action: Action) -> Reward:
        """Route the action to the appropriate grader."""
        td = self._current_task_def
        tt = self._current_task_type

        if tt == "email_triage":
            return grade_email_triage(action.payload, td["expected_label"])

        elif tt == "data_cleaning":
            return grade_data_cleaning(
                action.payload,
                td["expected_output"],
                td["metadata"],
            )

        elif tt == "code_review":
            return grade_code_review(action.payload, td)

        elif tt == "smart_assistant":
            steps = td["steps"]
            if self._current_step < len(steps):
                return grade_smart_assistant_step(
                    action.payload,
                    steps[self._current_step],
                    self._memory,
                )
            else:
                return Reward(score=0.0, feedback="No more steps remaining.")

        return Reward(score=0.0, feedback="Unknown task type.")

    def _try_extract_memory(self, payload: Dict) -> Dict:
        """
        Attempt to extract structured data from the payload for memory storage.
        This enables context awareness across multi-step tasks.
        """
        import json, re
        response = str(payload.get("response", ""))
        # Try to parse any JSON in the response for memory
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        return {}

    def _build_info(self) -> Dict[str, Any]:
        """Construct the info dictionary for the current step."""
        return {
            "task_type": self._current_task_type,
            "task_id": self._current_task_def.get("task_id") if self._current_task_def else None,
            "step": self._current_step,
            "episode_rewards_so_far": copy.deepcopy(self._episode_rewards),
            "memory_size": len(self._memory),
        }

    # ─────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────

    def run_full_benchmark(self, agent_fn) -> Dict[str, Any]:
        """
        Run the agent through all tasks in the queue.

        Args:
            agent_fn: Callable(observation) → Action

        Returns:
            Summary dict with per-task and overall scores.
        """
        results = []
        self._queue_index = 0  # Reset queue

        for task_type, task_def in self._task_queue:
            obs = self.reset()
            episode_rewards = []
            done = False

            while not done:
                action = agent_fn(obs)
                obs, reward, done, info = self.step(action)
                episode_rewards.append(reward.score)

            episode_score = round(sum(episode_rewards) / len(episode_rewards), 4)
            results.append({
                "task_id": task_def["task_id"],
                "task_type": task_type,
                "score": episode_score,
                "num_steps": len(episode_rewards),
            })

        overall = round(sum(r["score"] for r in results) / len(results), 4) if results else 0.0
        by_type: Dict[str, List[float]] = {}
        for r in results:
            by_type.setdefault(r["task_type"], []).append(r["score"])
        avg_by_type = {k: round(sum(v) / len(v), 4) for k, v in by_type.items()}

        return {
            "overall_average": overall,
            "by_task_type": avg_by_type,
            "all_results": results,
        }
