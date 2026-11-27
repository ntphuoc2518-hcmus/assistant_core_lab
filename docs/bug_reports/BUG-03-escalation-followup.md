# BUG-03: Escalation banner provides no follow-up query suggestions
Severity: low
Where: frontend (`ui/logic.py` ? `status_note`)

Steps:
1. Ask an out-of-scope or underspecified question (e.g., `"Can I register thesis?"` without credit count) so the API returns `escalate=True`.

Expected:
Escalation note directs the user to the Training Office and suggests example topics they can ask next.

Actual:
The note only states `"I could not find this in the official documents. A staff member can help: Training Office, room I.101."`, leaving users unsure what to try next.

Evidence:
Observed during Week-7 hallway usability testing (`worksheets/user_test_observations.md`, Participant H3).
