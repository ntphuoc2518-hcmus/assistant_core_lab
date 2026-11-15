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
