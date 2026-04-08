"""
Typed Pydantic models for the OpenEnv Productivity environment.
Defines the data structures for Observations, Actions, and Rewards.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Observation(BaseModel):
    """
    Observation returned to the agent after each step.
    Contains the current task context and any memory/history.
    """
    task_id: str = Field(..., description="Unique identifier for the current task")
    task_type: str = Field(..., description="Type of task: email_triage | data_cleaning | code_review | smart_assistant")
    content: str = Field(..., description="The main content the agent needs to process")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context (step number, memory, etc.)")
    step: int = Field(default=0, description="Current step within a multi-step task")
    total_steps: Optional[int] = Field(default=None, description="Total steps expected (for multi-step tasks)")
    done: bool = Field(default=False, description="Whether the current task episode is complete")


class Action(BaseModel):
    """
    Action submitted by the agent.
    Carries the action type and its payload.
    """
    action_type: str = Field(..., description="Type of action: classify | clean | review | respond")
    payload: Dict[str, Any] = Field(..., description="Action data, varies by action_type")


class Reward(BaseModel):
    """
    Reward signal returned after each action.
    Contains a numeric score and human-readable feedback.
    """
    score: float = Field(..., ge=0.0, le=1.0, description="Reward score, clamped between 0.0 and 1.0")
    feedback: str = Field(..., description="Explanation of the reward or what was correct/incorrect")
    partial_credit: Optional[Dict[str, float]] = Field(
        default=None, description="Breakdown of partial scores per field (for complex tasks)"
    )


class StepResult(BaseModel):
    """Bundled return value from env.step()"""
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class MemoryEntry(BaseModel):
    """A single memory entry stored between steps in multi-step tasks."""
    step: int
    action_type: str
    content: str
    extracted: Dict[str, Any] = Field(default_factory=dict)
