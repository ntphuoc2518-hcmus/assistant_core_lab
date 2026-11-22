# Lab 7 — Kiểm tra trạng thái giao diện

**Ngày kiểm tra:** 2026-11-19  
**Nguồn:** [Quan sát hallway test](../../worksheets/user_test_observations.md) và [usability checklist](../../worksheets/usability_checklist.md).

> Cột kết quả dựa trên ghi chú kiểm thử hiện có. Tên ảnh dưới đây là tên đề xuất để lưu ảnh minh chứng; hiện chưa có ảnh kiểm thử trong workspace.

| Trạng thái | Mong đợi | Kết quả (Đạt/Không) + tên ảnh |
|---|---|---|
| Màn hình ban đầu | Hiện tên trợ lý, ô nhập câu hỏi, câu hỏi gợi ý và thông báo đây là trợ lý AI. | Đạt — `state_01_initial_screen.png` |
| Đang chờ phản hồi | Hiện chỉ báo “Thinking…” để người dùng biết câu hỏi đang được xử lý. | Đạt — `state_02_thinking.png` |
| Trả lời có nguồn | Hiện câu trả lời cùng nguồn tham khảo có tiêu đề và mã tài liệu. | Đạt — `state_03_answer_with_source.png` |
| Gửi phản hồi 👍 | Gửi phản hồi thành công và hiện thông báo cảm ơn. | Đạt — `state_04_positive_feedback.png` |
| Gửi phản hồi 👎 | Gửi phản hồi thành công và hiện thông báo xác nhận. | Đạt — `state_05_negative_feedback.png` |
| Không tìm được câu trả lời | Thông báo chuyển đến Training Office khi thiếu thông tin hoặc không thể trả lời. | Đạt — `state_06_escalation.png` |
| Nhập tiếng Việt, emoji hoặc dấu ngoặc kép thông minh | Chấp nhận nội dung Unicode, không lỗi hoặc làm hỏng văn bản. | Đạt — `state_07_unicode_input.png` |
| Dùng trên điện thoại | Bố cục sử dụng được và lịch sử hội thoại cuộn bình thường. | Đạt — `state_08_mobile_layout.png` |
| Mở nguồn trích dẫn | Chạm hoặc nhấn giữ mã nguồn sẽ mở được nội dung quy định tương ứng. | Không — nguồn hiện là văn bản thường; `state_09_source_link.png` |

