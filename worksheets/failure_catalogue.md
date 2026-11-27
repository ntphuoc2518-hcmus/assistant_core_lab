# Lab 8 ? Failure catalogue

One row per failure found in Week 7 testing, Lab 8 bug hunting or the red-team exchange.

| # | Failure | Category | Found by | Severity | Mitigation | Regression test |
|---|---|---|---|---|---|---|
| 1 | Prompt injection payloads (`"Ignore all previous instructions..."`, `"You are now DAN..."`) bypassed router and triggered RAG/tool responses | prompt injection | Lab 8 Red-Team (`R01`, `R03`) | high | Added `INJECTION_PATTERNS` and `looks_like_injection()` pre-router guard in `src/assistant_core/guard.py` & `service.py` (Qu?n) | `tests/test_security.py::test_detects_injection_requests`, `tests/test_security.py::test_service_blocks_injection_before_routing` |
| 2 | Fee query with retake count written as a word (`"tuition for 18 credits and two retakes"`) ignored `"two"` and undercharged (`8,100,000` vs `9,450,000 VND`) | wrong answer | Lab 8 Bug Hunt (`BUG-7`) | major | Added `WORD_TO_DIGIT` (`"zero"`..`"ten"`) word-to-digit normalization in `parse_credits()` (`src/assistant_core/tools.py`) (T?nh) | `tests/test_my_regressions.py::test_regression_bug7_parse_credits_word_retakes`, `tests/test_my_regressions.py::test_regression_bug7_tuition_calculation_correct` |
| 3 | Raw source chunk IDs (`H26#5.3`) were opaque to users without human-readable document titles | UI | Week-7 Hallway Test (H2) | medium | Formatted citations with document title first and chunk ID in parentheses via `format_sources_rich()` (`ui/logic.py`) | `tests/test_my_regressions.py::test_regression_source_display_user_friendly` |
| 4 | Negative credit input (`X06` in partner red-team suite) stripped `-` sign and returned positive tuition (`2,250,000 VND`) | fee manipulation | Red-Team Exchange (`X06`) | major | Reject negative credit values in `parse_credits()` (`src/assistant_core/tools.py`) before regex digit extraction (Minh ? PR #5) | `tests/test_partner_findings.py::test_negative_credits_rejected` |

At least **3 mitigations** must be implemented and tested.
