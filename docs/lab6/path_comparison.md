# Lab 6 - Path Comparison & Analysis

## 1. Initial Comparison Table (20 Cases)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :---: | :---: | :---: | :---: | :--- |
| deterministic | 7/20 | 5/5 | 0.0 | 0.5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| retrieval | 16/20 | 4/5 | 0.0 | 0.1 | E13 E14 E15 E19 |
| llm (stub) | 16/20 | 4/5 | 0.1 | 0.4 | E13 E14 E15 E19 |

## 2. Updated Comparison Table after H1 & H3 (25 Cases)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :---: | :---: | :---: | :---: | :--- |
| deterministic | 9/25 | 7/7 | 0.0 | 1.1 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| retrieval | 20/25 | 5/7 | 0.0 | 0.2 | E13 E14 E15 E19 E20 |
| llm (stub) | 20/25 | 5/7 | 0.2 | 1.0 | E13 E14 E15 E19 E20 |

## 3. Analysis (3 Sentences)

1. **Which path to use**: Tôi chọn đường đi **llm (RAG)** cho các câu hỏi tra cứu sổ tay và quy chế sinh viên.
2. **Why**: Đường đi RAG đạt độ chính xác vượt trội (20/25 so với 9/25 của deterministic), diễn đạt tự nhiên và luôn đính kèm mã nguồn trích dẫn để kiểm chứng.
3. **First failure to fix**: Lỗi **E13** ("when is tuition due") hoặc **E14** ("can I take 32 credits") cần ưu tiên cải thiện bằng tìm kiếm ngữ nghĩa (embeddings) hoặc mở rộng từ đồng nghĩa vì khớp từ khóa BM25 đơn thuần bị hạn chế bởi khác biệt từ vựng và trọng số IDF thấp của từ phổ biến.

## 4. Observation on H1 & H3 Failures (1 Sentence)

Toàn bộ 5 câu hỏi mới E21–E25 đều đạt kết quả chính xác, trong khi các câu còn fail (E13, E14, E15, E19, E20) xuất phát từ việc thiếu từ đồng nghĩa (E13), quy tắc định tuyến cứng bắt nhầm từ khóa (E15), điểm IDF của từ "credit" chưa vượt ngưỡng 2.0 dù đã bỏ hậu tố "s" ở H3 (E14), và các câu hỏi ngoài phạm vi có từ khóa trùng lặp khiến mô hình giả (stub) không tự từ chối được (E19, E20).

## 5. Responder Comparison: StubLLM vs Template (`eval/compare_paths.py`)

Cases come from `eval/compare_cases.jsonl` (IDs C01–C04, formerly E13/E14/E15/E19 before the Lab 6 eval set took those IDs).

| ID  | Question                              | Expected contains | Pass A (StubLLM) | Pass B (Template) | Answer A (StubLLM)                                      | Answer B (Template)                            |
|-----|---------------------------------------|-------------------|:----------------:|:-----------------:|--------------------------------------------------------|------------------------------------------------|
| C01 | hello                                 | Hello             | PASS             | PASS              | Hello! I can help with offices, fees and rules.        | Hello! I can help with offices, fees and rules. |
| C02 | tuition for 18 credits and 2 retake   | VND               | PASS             | PASS              | Your tuition is 9,450,000 VND                          | Your tuition is 9,450,000 VND                   |
| C03 | where is Training Office?             | I.101             | PASS             | PASS              | Training Office: room I.101, open Mon-Fri 07:30-16:30  | Training Office: room I.101, open Mon-Fri 07:30-16:30 |
| C04 | thesis regulations                    | Thesis            | PASS             | PASS              | Based on 'Thesis registration': Students may register… | Thesis registration: Students may register a t… |

Both paths produce correct answers for greeting (C01), fee calculation (C02), and office lookup (C03) because those intents bypass the responder entirely. For rule intent (C04), **StubLLM** returns a richer prefix (`Based on '…'`) while **Template** formats as `Title: text` — both satisfy the eval criterion. The two paths diverge only on handbook responses, making the responder the natural seam for future LLM integration without touching routing or fee logic.

> **Re-run note:** C04 used to fail on both paths because `Handbook.search` matched title words as *substrings*: the word "a" in *Retaking a course* is found inside almost any question, so every rule question returned H26-4.2. `Handbook.search` now matches whole words (ignoring stop words) and picks the title with the most matching words, returning nothing when no word matches. `python eval/compare_paths.py` now gives **C01–C04 PASS on both paths** ("All cases passed."). Both paths now answer C04 as `Thesis registration: …`, because the StubLLM responder uses the same template since Lab 6.
