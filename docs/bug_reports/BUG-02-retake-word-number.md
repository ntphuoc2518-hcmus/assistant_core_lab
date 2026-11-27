# BUG-02: Fee query with retake count written as a word ignores the retake credits
Severity: major
Where: backend (`src/assistant_core/tools.py` ? `parse_credits`)

Steps:
1. Send `POST /v1/chat` with `{"message": "tuition for 18 credits and two retakes"}`.

Expected:
`9,450,000 VND` (18 regular credits + 2 retake credits).

Actual:
`8,100,000 VND` (`parse_credits` only extracts `\d+`, so `"two"` is ignored).

Evidence:
Reproduced via `parse_credits("tuition for 18 credits and two retakes") -> (18, 0)`. Fixed by T?nh in `feat/lab8-tinh-regressions` using `WORD_TO_DIGIT`; verified by `tests/test_my_regressions.py::test_regression_bug7_parse_credits_word_retakes` and `tests/test_my_regressions.py::test_regression_bug7_tuition_calculation_correct`.
