"""
Deterministic grader functions for each task type.
Each grader returns a Reward with a score in [0.0, 1.0].
Graders are reproducible and deterministic given the same inputs.
"""

import json
import re
import math
from typing import Any, Dict, List, Optional
from env.models import Reward


# ─────────────────────────────────────────────
# TASK 1: Email Triage Grader
# ─────────────────────────────────────────────

def grade_email_triage(action_payload: Dict[str, Any], expected_label: str) -> Reward:
    """
    Exact-match grader for email triage.
    Score: 1.0 for correct label, 0.0 for incorrect, -0.1 penalty for missing/invalid.
    """
    predicted = str(action_payload.get("label", "")).strip().lower()
    expected = expected_label.strip().lower()

    if not predicted:
        return Reward(
            score=0.0,
            feedback="No label provided. Expected one of: spam, important, work.",
        )

    valid_labels = {"spam", "important", "work"}
    if predicted not in valid_labels:
        return Reward(
            score=0.0,
            feedback=f"Invalid label '{predicted}'. Must be one of: spam, important, work.",
        )

    if predicted == expected:
        return Reward(
            score=1.0,
            feedback=f"Correct! Email classified as '{predicted}'.",
        )
    else:
        return Reward(
            score=0.0,
            feedback=f"Incorrect. Predicted '{predicted}', expected '{expected}'.",
        )


# ─────────────────────────────────────────────
# TASK 2: Data Cleaning Grader
# ─────────────────────────────────────────────

def _normalize_value(v: Any) -> Any:
    """Normalize a value for comparison (strip strings, lowercase where needed)."""
    if isinstance(v, str):
        return v.strip()
    return v


def _compare_record(predicted: Dict, expected: Dict, fields: List[str]) -> Dict[str, float]:
    """Compare a single record field-by-field, returning per-field scores."""
    field_scores = {}
    for field in fields:
        pred_val = _normalize_value(predicted.get(field))
        exp_val = _normalize_value(expected.get(field))

        if exp_val is None and pred_val is None:
            field_scores[field] = 1.0
        elif exp_val is None or pred_val is None:
            field_scores[field] = 0.0
        elif isinstance(exp_val, float) and isinstance(pred_val, (int, float)):
            # Allow small floating point tolerance
            field_scores[field] = 1.0 if math.isclose(float(pred_val), exp_val, rel_tol=0.01) else 0.0
        elif isinstance(exp_val, str) and isinstance(pred_val, str):
            field_scores[field] = 1.0 if pred_val.lower() == exp_val.lower() else 0.0
        else:
            field_scores[field] = 1.0 if pred_val == exp_val else 0.0

    return field_scores


def grade_data_cleaning(action_payload: Dict[str, Any], expected_output: Dict, task_metadata: Dict) -> Reward:
    """
    Partial scoring grader for data cleaning.
    Score = fraction of (record × field) pairs that are correct.
    """
    cleaned = action_payload.get("cleaned_data")
    if not cleaned:
        return Reward(score=0.0, feedback="No cleaned_data provided in action payload.")

    # Try to parse if it's a string
    if isinstance(cleaned, str):
        try:
            cleaned = json.loads(cleaned)
        except json.JSONDecodeError:
            return Reward(score=0.0, feedback="cleaned_data is not valid JSON.")

    # Determine the top-level key (employees, orders, etc.)
    exp_key = list(expected_output.keys())[0]
    pred_records = cleaned.get(exp_key, cleaned) if isinstance(cleaned, dict) else cleaned
    exp_records = expected_output[exp_key]

    if not isinstance(pred_records, list):
        return Reward(score=0.0, feedback=f"Expected a list under key '{exp_key}'.")

    fields = task_metadata.get("fields", [])
    total_checks = len(exp_records) * len(fields)
    correct_checks = 0
    partial_credit = {}

    for i, (pred, exp) in enumerate(zip(pred_records, exp_records)):
        field_scores = _compare_record(pred, exp, fields)
        for field, score in field_scores.items():
            key = f"record_{i+1}_{field}"
            partial_credit[key] = score
            correct_checks += score

    # Penalize if fewer records than expected
    missing_records = max(0, len(exp_records) - len(pred_records))
    total_checks += missing_records * len(fields)  # these remain 0

    final_score = round(correct_checks / total_checks, 3) if total_checks > 0 else 0.0
    pct = round(final_score * 100, 1)

    return Reward(
        score=final_score,
        feedback=f"Data cleaning score: {pct}% of fields correct ({int(correct_checks)}/{total_checks} checks passed).",
        partial_credit=partial_credit,
    )


# ─────────────────────────────────────────────
# TASK 3: Code Review Grader
# ─────────────────────────────────────────────

def _keyword_score(text: str, keywords: List[str]) -> float:
    """Score based on presence of expected keywords (case-insensitive)."""
    text_lower = text.lower()
    matched = sum(1 for kw in keywords if kw.lower() in text_lower)
    return matched / len(keywords) if keywords else 0.0


def grade_code_review(action_payload: Dict[str, Any], task_def: Dict) -> Reward:
    """
    Keyword + logic-based grader for code review.
    Evaluates:
      - Bug identification (40%): Does the explanation mention the bugs?
      - Fix quality (40%): Does the fix contain expected code pattern?
      - Clarity (20%): Does the explanation have minimum length/structure?
    """
    explanation = str(action_payload.get("explanation", "")).strip()
    fixed_code = str(action_payload.get("fixed_code", "")).strip()

    if not explanation and not fixed_code:
        return Reward(score=0.0, feedback="No explanation or fixed_code provided.")

    expected_keywords: List[str] = task_def.get("expected_keywords", [])
    expected_fix_snippet: str = task_def.get("expected_fix_snippet", "")
    bugs: List[str] = task_def.get("bugs", [])

    # 1. Bug identification score (40%)
    combined_text = explanation + " " + fixed_code
    keyword_match = _keyword_score(combined_text, expected_keywords)
    bug_id_score = min(1.0, keyword_match * 1.5)  # allow some leniency

    # 2. Fix quality score (40%)
    fix_score = 0.0
    if fixed_code:
        if expected_fix_snippet and expected_fix_snippet.lower() in fixed_code.lower():
            fix_score = 1.0
        elif len(fixed_code) > 30:  # has some meaningful code
            fix_score = 0.4
    elif explanation and expected_fix_snippet.lower() in explanation.lower():
        fix_score = 0.5  # described fix but didn't write code

    # 3. Clarity score (20%)
    clarity_score = 0.0
    if len(explanation) >= 50:
        clarity_score = 0.5
    if len(explanation) >= 150:
        clarity_score = 1.0
    # Bonus for mentioning each bug
    for bug in bugs:
        bug_keywords = bug.lower().split()[:4]
        if any(kw in explanation.lower() for kw in bug_keywords if len(kw) > 3):
            clarity_score = min(1.0, clarity_score + 0.25)

    final_score = round(0.4 * bug_id_score + 0.4 * fix_score + 0.2 * clarity_score, 3)

    partial = {
        "bug_identification": round(bug_id_score, 3),
        "fix_quality": round(fix_score, 3),
        "clarity": round(clarity_score, 3),
    }

    feedback_parts = [f"Code review score: {round(final_score*100,1)}%."]
    if bug_id_score < 0.5:
        feedback_parts.append("Hint: Not all bugs were identified.")
    if fix_score < 0.5:
        feedback_parts.append("Hint: The fix is missing or incorrect.")
    if clarity_score < 0.5:
        feedback_parts.append("Hint: Explanation is too brief.")

    return Reward(
        score=final_score,
        feedback=" ".join(feedback_parts),
        partial_credit=partial,
    )


# ─────────────────────────────────────────────
# TASK 4: Smart Assistant Step Grader
# ─────────────────────────────────────────────

def _extract_json_from_text(text: str) -> Optional[Dict]:
    """Try to extract a JSON object from mixed text."""
    # Look for JSON block
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def grade_smart_assistant_step(
    action_payload: Dict[str, Any],
    step_def: Dict,
    memory: List[Dict],
) -> Reward:
    """
    Incremental grader for multi-step Smart Assistant task.
    Evaluates each step independently with partial credit.
    Memory is checked for context awareness.
    """
    response = str(action_payload.get("response", "")).strip()
    step_num = step_def["step"]
    expected_keys = step_def.get("expected_keys", [])
    action_type = step_def.get("action_type", "respond")

    if not response:
        return Reward(
            score=0.0,
            feedback=f"Step {step_num}: Empty response. No points awarded.",
        )

    # --- Step 1: Summary grader ---
    if step_num == 1:
        keywords = ["phoenix", "november", "15", "alex", "maya", "jordan", "deadline"]
        matched = sum(1 for kw in keywords if kw.lower() in response.lower())
        score = round(min(1.0, matched / 5), 3)  # need at least 5/7 for full score
        feedback = (
            f"Step 1 - Summary: {matched}/{len(keywords)} key elements mentioned. "
            f"Score: {round(score*100)}%."
        )
        return Reward(score=score, feedback=feedback)

    # --- Step 2: Structured extraction grader ---
    if step_num == 2:
        parsed = _extract_json_from_text(response)
        if not parsed:
            return Reward(
                score=0.1,
                feedback="Step 2 - Extraction: Could not parse JSON. Provide a valid JSON object.",
            )

        field_scores = {}
        # project_name
        pn = str(parsed.get("project_name", "")).lower()
        field_scores["project_name"] = 1.0 if "phoenix" in pn else 0.0

        # deadline
        dl = str(parsed.get("deadline", ""))
        field_scores["deadline"] = 1.0 if ("2024-11-15" in dl or "november 15" in dl.lower() or "nov 15" in dl.lower()) else 0.0

        # owners
        owners = parsed.get("owners", [])
        owner_text = json.dumps(owners).lower() if owners else ""
        has_alex = "alex" in owner_text
        has_maya = "maya" in owner_text
        has_jordan = "jordan" in owner_text
        field_scores["owners"] = round((has_alex + has_maya + has_jordan) / 3, 2)

        # urgency
        urg = str(parsed.get("urgency", "")).lower()
        field_scores["urgency"] = 1.0 if urg in {"high", "critical"} else (0.5 if urg == "medium" else 0.0)

        score = round(sum(field_scores.values()) / len(field_scores), 3)
        return Reward(
            score=score,
            feedback=f"Step 2 - Extraction: {round(score*100)}% correct. Fields: {field_scores}",
            partial_credit=field_scores,
        )

    # --- Step 3: Task scheduling grader ---
    if step_num == 3:
        parsed = _extract_json_from_text(response)
        if not parsed:
            return Reward(
                score=0.1,
                feedback="Step 3 - Scheduling: Could not parse JSON. Provide tasks as JSON.",
            )

        tasks = parsed.get("tasks", [])
        if not tasks or not isinstance(tasks, list):
            return Reward(score=0.1, feedback="Step 3: 'tasks' key missing or not a list.")

        # Check memory awareness: did agent reference data from step 2?
        memory_bonus = 0.0
        for mem in memory:
            extracted = mem.get("extracted", {})
            if extracted.get("project_name") or extracted.get("deadline"):
                memory_bonus = 0.1  # bonus for using memory
                break

        score_components = []
        for i, task in enumerate(tasks[:3]):
            t_score = 0.0
            if task.get("task_name"):
                t_score += 0.25
            if task.get("assigned_to"):
                t_score += 0.25
            # Due date must be before 2024-11-15
            due = str(task.get("due_date", ""))
            if re.match(r'\d{4}-\d{2}-\d{2}', due) and due <= "2024-11-15":
                t_score += 0.25
            if task.get("priority") in {"high", "medium", "low"}:
                t_score += 0.25
            score_components.append(t_score)

        base_score = sum(score_components) / 3 if score_components else 0.0
        final_score = round(min(1.0, base_score + memory_bonus), 3)

        return Reward(
            score=final_score,
            feedback=(
                f"Step 3 - Scheduling: {len(tasks)} tasks created. "
                f"Base score: {round(base_score*100)}%. "
                f"Memory bonus: +{int(memory_bonus*100)}%. "
                f"Final: {round(final_score*100)}%."
            ),
        )

    return Reward(score=0.0, feedback=f"Unknown step {step_num}.")
