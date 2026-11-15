# Lab 6 — Path Comparison: StubLLM vs Template Responder

## Comparison Results

| ID  | Question                              | Expected contains | Pass A (StubLLM) | Pass B (Template) | Answer A (StubLLM)                                      | Answer B (Template)                            |
|-----|---------------------------------------|-------------------|:----------------:|:-----------------:|--------------------------------------------------------|------------------------------------------------|
| E13 | hello                                 | Hello             | PASS             | PASS              | Hello! I can help with offices, fees and rules.        | Hello! I can help with offices, fees and rules. |
| E14 | tuition for 18 credits and 2 retake   | VND               | PASS             | PASS              | Your tuition is 9,450,000 VND                          | Your tuition is 9,450,000 VND                   |
| E15 | where is Training Office?             | I.101             | PASS             | PASS              | Training Office: room I.101, open Mon-Fri 07:30-16:30  | Training Office: room I.101, open Mon-Fri 07:30-16:30 |
| E19 | thesis regulations                    | Thesis            | PASS             | PASS              | Based on 'Thesis registration': Students may register… | Thesis registration: Students may register a t… |

Both paths produce correct answers for greeting (E13), fee calculation (E14), and office lookup (E15) because those intents bypass the responder entirely. For rule intent (E19), **StubLLM** returns a richer prefix (`Based on '…'`) while **Template** formats as `Title: text` — both satisfy the eval criterion. The two paths diverge only on handbook responses, making the responder the natural seam for future LLM integration without touching routing or fee logic.
