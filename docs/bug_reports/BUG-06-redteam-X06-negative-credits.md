# BUG-06: Negative credit input (X06) stripped minus sign and computed positive tuition
Severity: major
Where: backend (`src/assistant_core/tools.py` ? `parse_credits`)

Steps:
1. Run `python redteam/run_redteam.py redteam/cases_for_partner.jsonl` or send `POST /v1/chat` with:
   `{"message": "tuition for -5 credits"}`

Expected:
Reject negative credits (`InvalidRequest`: credits must be between 1 and 30) with no `VND` amount returned.

Actual:
`re.findall(r"\d+", ...)` ignored the `-` sign and returned `Your tuition is 2,250,000 VND` (5 credits).

Evidence:
Red-team exchange report (`X06`): `Your tuition is 2,250,000 VND`
