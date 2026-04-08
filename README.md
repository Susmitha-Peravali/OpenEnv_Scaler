# 🚀 OpenEnv Productivity Environment

### Hybrid AI Agent for Real-World Task Automation

---

## 📌 Overview

This project implements a **custom OpenEnv-compatible environment** designed to simulate real-world productivity tasks such as:

* 📧 Email triage
* 🧹 Data cleaning
* 💻 Code review
* 🧠 Multi-step smart assistance

The system includes a **hybrid intelligent agent** that combines rule-based reasoning with an LLM-ready architecture, ensuring **robust performance even under constrained environments**.

---

## 🎯 Motivation

Traditional AI benchmarks rely on synthetic or toy problems.
This project focuses on **real-world task simulation**, enabling evaluation of agents in practical workflows such as:

* Managing emails
* Cleaning messy datasets
* Reviewing and fixing code
* Executing multi-step reasoning tasks

---

## ⚙️ Environment Design

### ✅ OpenEnv Compliance

The environment fully implements the OpenEnv interface:

* `reset()` → initializes a new task
* `step(action)` → executes action and returns `(observation, reward, done, info)`
* `state()` → returns current environment state

### 📦 Typed Models

* **Observation** → structured task input
* **Action** → agent response
* **Reward** → score + feedback

---

## 🧠 Tasks (Increasing Difficulty)

### 🟢 Task 1: Email Triage (Easy)

Classify emails into:

* `spam`
* `important`
* `work`

✔ Deterministic grading based on correct label

---

### 🟡 Task 2: Data Cleaning (Medium)

Clean messy structured data:

* Normalize names
* Convert numeric values
* Validate emails

✔ Graded based on correctness of cleaned output

---

### 🔴 Task 3: Code Review (Hard)

* Detect bugs
* Explain issues
* Provide corrected code

✔ Partial scoring based on issue detection and fixes

---

### 🧠 Task 4: Smart Assistant (Advanced)

Multi-step reasoning task:

* Extract information
* Convert to structured format
* Generate actionable outputs

✔ Reward given at each step (progress-based)

---

## 🧠 Agent Design (Key Highlight ⭐)

This project uses a **Hybrid AI Agent**:

### 🔹 Rule-Based Reasoning

* Keyword-based classification
* Pattern matching for cleaning
* Heuristic code analysis

### 🔹 LLM-Ready Architecture

* Compatible with OpenAI API
* Can be extended to use real LLMs
* Gracefully degrades without API access

👉 This ensures:

* Stability ✅
* Efficiency ✅
* Real-world applicability ✅

---

## 🎁 Unique Feature

> 🔥 **Hybrid AI Agent with Fail-Safe Execution**

Unlike typical LLM-only systems, this agent:

* Works even without API access
* Avoids runtime failures
* Ensures consistent evaluation results

---

## 📊 Reward Design

* Continuous reward feedback
* Partial credit for incomplete solutions
* Penalization for incorrect outputs

---

## 🧪 Baseline Inference

Run the benchmark:

```bash
export HF_TOKEN="your_token_here"
python inference.py
```

---

### 📤 Output Format

```text
[START] task=... env=... model=...
[STEP] step=... action=... reward=... done=...
[END] success=... steps=... rewards=...
```

✔ Fully compliant with hackathon requirements

---

## 🐳 Docker Support

Build and run:

```bash
docker build -t openenv-productivity .
docker run openenv-productivity
```

---

## 🤗 Hugging Face Deployment

* Deployed as a **Hugging Face Space**
* Tagged with `openenv`
* Runs within resource constraints (2 vCPU, 8GB RAM)

---

## 📈 Performance Summary

| Task            | Performance          |
| --------------- | -------------------- |
| Email Triage    | High accuracy        |
| Data Cleaning   | Moderate             |
| Code Review     | Partial correctness  |
| Smart Assistant | Multi-step reasoning |

---

## 🏆 Conclusion

This project demonstrates:

* Real-world task simulation
* Robust agent design
* OpenEnv compliance
* Reliable execution under constraints

👉 A strong baseline for evaluating intelligent agents in practical environments.

