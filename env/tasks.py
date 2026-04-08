"""
Task definitions for the OpenEnv Productivity environment.
Each task includes sample input data, expected outputs, and metadata.
"""

from typing import Any, Dict, List


# ─────────────────────────────────────────────
# TASK 1: Email Triage (Easy)
# ─────────────────────────────────────────────
EMAIL_TASKS: List[Dict[str, Any]] = [
    {
        "task_id": "email_001",
        "content": (
            "Subject: CONGRATULATIONS! You've won $1,000,000!\n"
            "From: prizes@lotterywin.biz\n\n"
            "Dear Lucky Winner, You have been selected in our international lottery. "
            "Click here to claim your prize. Provide your bank details immediately."
        ),
        "expected_label": "spam",
        "metadata": {"sender_domain": "lotterywin.biz", "has_links": True},
    },
    {
        "task_id": "email_002",
        "content": (
            "Subject: Q3 Budget Review - Action Required\n"
            "From: cfo@company.com\n\n"
            "Hi team, please review the attached Q3 budget spreadsheet before Friday's "
            "leadership meeting. We need your department forecasts updated by EOD Thursday."
        ),
        "expected_label": "work",
        "metadata": {"sender_domain": "company.com", "has_attachment": True},
    },
    {
        "task_id": "email_003",
        "content": (
            "Subject: Mom's surgery scheduled for next Tuesday\n"
            "From: sarah.johnson@gmail.com\n\n"
            "Hey, just wanted to let you know that Mom's knee surgery is confirmed for "
            "next Tuesday at 9am. Can you arrange to be there? She's nervous and would "
            "really appreciate having family around."
        ),
        "expected_label": "important",
        "metadata": {"sender_domain": "gmail.com", "personal": True},
    },
    {
        "task_id": "email_004",
        "content": (
            "Subject: Flash Sale! 70% OFF Everything Today Only!!!\n"
            "From: noreply@dealstoday.shop\n\n"
            "Don't miss our BIGGEST sale of the year! Use code SAVE70 at checkout. "
            "Limited time offer. Unsubscribe | Privacy Policy"
        ),
        "expected_label": "spam",
        "metadata": {"sender_domain": "dealstoday.shop", "promotional": True},
    },
    {
        "task_id": "email_005",
        "content": (
            "Subject: Your AWS bill for October: $2,847.23\n"
            "From: billing@amazon.com\n\n"
            "Your monthly AWS statement is ready. Total charges: $2,847.23. "
            "Services used: EC2 ($1,200), RDS ($900), S3 ($400), Data Transfer ($347). "
            "Payment due: November 15th."
        ),
        "expected_label": "work",
        "metadata": {"sender_domain": "amazon.com", "financial": True},
    },
]

VALID_EMAIL_LABELS = {"spam", "important", "work"}


# ─────────────────────────────────────────────
# TASK 2: Data Cleaning (Medium)
# ─────────────────────────────────────────────
DATA_CLEANING_TASKS: List[Dict[str, Any]] = [
    {
        "task_id": "data_001",
        "content": """{
  "employees": [
    {"name": "  John doe  ", "age": "thirty two", "email": "john.doe@company", "salary": "$75,000", "department": "eng"},
    {"name": "Jane Smith", "age": 28, "email": "jane.smith@company.com", "salary": "80000", "department": "Engineering"},
    {"name": "BOB JONES", "age": null, "email": "", "salary": "$90,000.00", "department": "MARKETING"},
    {"name": "alice wu", "age": "25", "email": "alice.wu@company.com", "salary": "70,000", "department": "marketing"}
  ]
}""",
        "expected_output": {
            "employees": [
                {"name": "John Doe", "age": None, "email": None, "salary": 75000.0, "department": "Engineering"},
                {"name": "Jane Smith", "age": 28, "email": "jane.smith@company.com", "salary": 80000.0, "department": "Engineering"},
                {"name": "Bob Jones", "age": None, "email": None, "salary": 90000.0, "department": "Marketing"},
                {"name": "Alice Wu", "age": 25, "email": "alice.wu@company.com", "salary": 70000.0, "department": "Marketing"},
            ]
        },
        "cleaning_rules": [
            "Trim whitespace from names and title-case them",
            "Convert text ages to integers; mark non-numeric ages as null",
            "Validate email format (must contain @ and domain with dot); invalid → null",
            "Strip currency symbols and commas from salary; convert to float",
            "Normalize department names to title-case; expand abbreviations (eng → Engineering)",
        ],
        "metadata": {"num_records": 4, "fields": ["name", "age", "email", "salary", "department"]},
    },
    {
        "task_id": "data_002",
        "content": """{
  "orders": [
    {"order_id": "ORD-001", "date": "13/07/2024", "amount": "$1,250.99", "status": "COMPLETED", "customer": "acme corp"},
    {"order_id": "ORD-002", "date": "2024-07-14", "amount": "500", "status": "pending", "customer": "  TechStart Inc.  "},
    {"order_id": "ORD-003", "date": "July 15, 2024", "amount": "$-200", "status": "refunded", "customer": "GLOBAL TRADE LLC"},
    {"order_id": "ORD-004", "date": "16-07-2024", "amount": "2,000.00", "status": "Shipped", "customer": "bright futures"}
  ]
}""",
        "expected_output": {
            "orders": [
                {"order_id": "ORD-001", "date": "2024-07-13", "amount": 1250.99, "status": "completed", "customer": "Acme Corp"},
                {"order_id": "ORD-002", "date": "2024-07-14", "amount": 500.0, "status": "pending", "customer": "TechStart Inc."},
                {"order_id": "ORD-003", "date": "2024-07-15", "amount": -200.0, "status": "refunded", "customer": "Global Trade Llc"},
                {"order_id": "ORD-004", "date": "2024-07-16", "amount": 2000.0, "status": "shipped", "customer": "Bright Futures"},
            ]
        },
        "cleaning_rules": [
            "Normalize all dates to ISO 8601 format (YYYY-MM-DD)",
            "Strip currency symbols and commas from amounts; convert to float",
            "Lowercase status field",
            "Title-case and strip customer names",
        ],
        "metadata": {"num_records": 4, "fields": ["order_id", "date", "amount", "status", "customer"]},
    },
]


# ─────────────────────────────────────────────
# TASK 3: Code Review (Hard)
# ─────────────────────────────────────────────
CODE_REVIEW_TASKS: List[Dict[str, Any]] = [
    {
        "task_id": "code_001",
        "content": '''def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

# Usage
scores = [85, 92, 78, 90, 88]
print(f"Average: {calculate_average(scores)}")
print(f"Empty list average: {calculate_average([])}")
''',
        "bugs": [
            "ZeroDivisionError when numbers list is empty — no guard for len(numbers) == 0",
        ],
        "expected_keywords": [
            "ZeroDivisionError", "empty", "len", "check", "guard", "return 0", "return None",
            "if not numbers", "if len(numbers) == 0",
        ],
        "expected_fix_snippet": "if not numbers",
        "difficulty": "easy_bug",
        "metadata": {"language": "python", "bug_count": 1},
    },
    {
        "task_id": "code_002",
        "content": '''import sqlite3

def get_user_data(username):
    """Fetch user data from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = \'{username}\'"
    cursor.execute(query)
    result = cursor.fetchone()
    
    return result

# Usage
user_input = input("Enter username: ")
print(get_user_data(user_input))
''',
        "bugs": [
            "SQL injection vulnerability — user input directly interpolated into query",
            "Database connection never closed — resource leak",
        ],
        "expected_keywords": [
            "sql injection", "parameterized", "prepared statement", "placeholder",
            "conn.close", "context manager", "with sqlite3", "?", "security",
        ],
        "expected_fix_snippet": "?",
        "difficulty": "security_bug",
        "metadata": {"language": "python", "bug_count": 2},
    },
    {
        "task_id": "code_003",
        "content": '''def merge_sorted_lists(list1, list2):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = 0
    j = 0
    
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    
    # BUG: remaining elements are never added
    return result

print(merge_sorted_lists([1, 3, 5, 7], [2, 4, 6, 8, 9, 10]))
# Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Actual:   [1, 2, 3, 4, 5, 6, 7]
''',
        "bugs": [
            "Missing tail-append: remaining elements of either list are discarded after the while loop exits",
        ],
        "expected_keywords": [
            "extend", "remaining", "tail", "list1[i:]", "list2[j:]",
            "while i", "while j", "append remaining",
        ],
        "expected_fix_snippet": "extend",
        "difficulty": "logic_bug",
        "metadata": {"language": "python", "bug_count": 1},
    },
]


# ─────────────────────────────────────────────
# TASK 4: Smart Task Assistant (Multi-Step)
# ─────────────────────────────────────────────
SMART_ASSISTANT_TASKS: List[Dict[str, Any]] = [
    {
        "task_id": "smart_001",
        "steps": [
            {
                "step": 1,
                "instruction": (
                    "Read the following email and summarize its key information:\n\n"
                    "Subject: Project Phoenix — Deadline Moved Up\n"
                    "From: director@company.com\n\n"
                    "Hi team,\n\n"
                    "Due to client pressure, the Project Phoenix final deliverable has been "
                    "moved from November 30th to November 15th at 5:00 PM EST. "
                    "This affects the backend API (owned by Alex), the frontend dashboard "
                    "(owned by Maya), and the QA sign-off (owned by Jordan). "
                    "Please confirm receipt and update your task trackers accordingly.\n\n"
                    "Best,\nDirector Chen"
                ),
                "expected_keys": ["project", "deadline", "owners", "date"],
                "action_type": "respond",
                "hint": "Extract: project name, new deadline, date, and team member names/roles.",
            },
            {
                "step": 2,
                "instruction": (
                    "Based on the email you just read, extract the following structured data:\n"
                    "- Project name\n"
                    "- New deadline (date only, ISO format)\n"
                    "- List of people responsible and their areas\n"
                    "- Urgency level (low/medium/high/critical)\n\n"
                    "Return a JSON object with keys: project_name, deadline, owners, urgency"
                ),
                "expected_keys": ["project_name", "deadline", "owners", "urgency"],
                "action_type": "respond",
                "hint": "Deadline is November 15th. Owners: Alex (backend API), Maya (frontend), Jordan (QA).",
            },
            {
                "step": 3,
                "instruction": (
                    "Using the extracted data, create a task schedule. "
                    "Assuming today is November 1st, create a list of 3 tasks with:\n"
                    "- task_name\n"
                    "- assigned_to\n"
                    "- due_date (ISO format, before the Nov 15 deadline)\n"
                    "- priority (high/medium/low)\n\n"
                    "Return a JSON object with key 'tasks' containing a list of task objects."
                ),
                "expected_keys": ["tasks"],
                "action_type": "respond",
                "hint": "Create one task per owner, all due before 2024-11-15.",
            },
        ],
        "metadata": {
            "description": "Email → Extract → Schedule pipeline",
            "total_steps": 3,
        },
    },
]
