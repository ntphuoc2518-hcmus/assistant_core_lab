# Lab 7 — Kiểm tra trạng thái giao diện (D.4 State Check)

**Người thực hiện:** Hà Xuân Tình (`tinhha777qz-dev`)  
**Ngày kiểm tra:** 2026-11-22  
**Môi trường:** Python 3.12, Streamlit 1.67.0, FastAPI / Uvicorn  
**Tài liệu liên quan:** [Usability checklist](../../worksheets/usability_checklist.md), [Hallway test observations](../../worksheets/user_test_observations.md)

---

## 1. Kết quả kiểm thử 6 trạng thái D.4 theo phân công

| STT | Trạng thái D.4 | Kịch bản kiểm thử | Kết quả mong đợi | Kết quả thực tế | Minh chứng (Ảnh) |
|---|---|---|---|---|---|
| 1 | **Câu mẫu ở sidebar** | Khởi động UI khi backend đang chạy | Hiển thị tiêu đề, lời chào AI, danh sách câu hỏi mẫu trong sidebar ("Try an example") | **Đạt** — Các câu mẫu hiển thị đầy đủ, click được; kèm ghi chú đây là trợ lý AI. | [`state_01_sidebar_examples.png`](states/state_01_sidebar_examples.png) |
| 2 | **Câu luận văn có nguồn `H26#5.3`** | Hỏi câu: `"Can I register my thesis with 118 credits?"` | Trả lời quy định đăng ký luận văn và trích dẫn mã nguồn `H26#5.3` | **Đạt** — Trả lời rõ ràng, kèm `Sources: 📄 5.3 Thesis registration (H26#5.3)`. | [`state_02_thesis_source.png`](states/state_02_thesis_source.png) |
| 3 | **'capital of France' hiện ghi chú Training Office** | Hỏi câu ngoài phạm vi: `"what is the capital of France"` | Kích hoạt cờ `escalate=True`, hiện ghi chú hướng dẫn liên hệ Training Office (phòng I.101) | **Đạt** — Hiển thị ghi chú: `"I could not find this in the official documents. A staff member can help: Training Office, room I.101."` | [`state_03_capital_of_france_escalate.png`](states/state_03_capital_of_france_escalate.png) |
| 4 | **Enter ô trống không gửi** | Nhập khoảng trắng / ô trống và nhấn Enter | Không crash, không gửi request rỗng tới backend, hiển thị cảnh báo thân thiện | **Đạt** — Hiển thị cảnh báo màu vàng: `"Please type a question."`, không gửi tin nhắn rỗng. | [`state_04_empty_input_warning.png`](states/state_04_empty_input_warning.png) |
| 5 | **👍 hiện toast và ẩn nút** | Nhấn nút 👍 dưới tin nhắn trả lời | Gửi phản hồi thành công lên API, hiện thông báo toast `"Thanks for your feedback!"` và ẩn các nút vote để tránh vote trùng | **Đạt** — Toast thông báo cảm ơn xuất hiện góc phải, 2 nút 👍/👎 của tin nhắn được ẩn ngay lập tức. | [`state_05_feedback_toast_hidden.png`](states/state_05_feedback_toast_hidden.png) |
| 6 | **Tắt API hiện lỗi backend** | Dừng dịch vụ FastAPI (cổng 8000) và tải lại UI | Giao diện cảnh báo rõ ràng backend không khả dụng kèm lệnh hướng dẫn khởi động | **Đạt** — Hiển thị banner lỗi đỏ: `"The assistant backend is not reachable. Start it with: uvicorn assistant_api.main:create_app --factory"`. | [`state_06_backend_unreachable.png`](states/state_06_backend_unreachable.png) |

---

## 2. Thư mục ảnh minh chứng
Toàn bộ ảnh chụp thực tế cho 6 trạng thái D.4 đã được lưu trữ tại thư mục [`docs/lab7/states/`](states/):
- `states/state_01_sidebar_examples.png`
- `states/state_02_thesis_source.png`
- `states/state_03_capital_of_france_escalate.png`
- `states/state_04_empty_input_warning.png`
- `states/state_05_feedback_toast_hidden.png`
- `states/state_06_backend_unreachable.png`

---

## 3. Đánh giá Usability Checklist
- Tất cả 10 tiêu chí trong [`worksheets/usability_checklist.md`](../../worksheets/usability_checklist.md) đều đạt (`[x]`).
- Giao diện đáp ứng tốt các yêu cầu MVP của Lab 07 (v0.7-MVP).
