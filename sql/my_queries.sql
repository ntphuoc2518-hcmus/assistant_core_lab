-- Lab 5 Part F: Truy vấn dữ liệu trợ lý (assistant.db)
-- Thành viên thực hiện: Hà Xuân Tình (Dữ liệu + F1, F2) & Minh (F3, H2)
-- Dữ liệu được khởi tạo từ scripts/migrate.py và scripts/seed.py assistant.db 300

-- ====================================================================
-- Phần của Tình: F1, F2
-- ====================================================================

-- F1: Số câu hỏi theo intent
SELECT intent, COUNT(*) AS request_count
FROM interaction
GROUP BY intent
ORDER BY request_count DESC;

/*
Kết quả F1 (300 interactions sau khi seed):
intent      request_count
----------  -------------
rule        140
fee         61
office      47
greeting    26
unknown     26
*/

-- F2: Latency trung bình theo intent (ROUND 1)
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC;

/*
Kết quả F2 (300 interactions sau khi seed):
intent      avg_latency_ms
----------  --------------
rule        76.2
unknown     8.1
fee         5.1
office      3.4
greeting    2.4
*/

-- ====================================================================
-- Phần của Minh: F3, H2 (chạy trên dữ liệu seed của Tình)
-- ====================================================================

-- F3: Topic nhận nhiều thumbs-down nhất (rating = -1)
SELECT i.topic, COUNT(*) AS thumbs_down_count
FROM feedback f
JOIN interaction i ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC;

/*
Kết quả F3:
topic       thumbs_down_count
----------  -----------------
H26-5.3     8
H26-4.2     8
H26-7.2     2
*/

-- H2: Câu hỏi tùy chọn - Giờ nào trong ngày có nhiều câu hỏi (interaction) nhất?
SELECT strftime('%H', created_at) AS hour_of_day, COUNT(*) AS request_count
FROM interaction
GROUP BY hour_of_day
ORDER BY request_count DESC;

/*
Kết quả H2:
hour_of_day  request_count
-----------  -------------
15           300
*/
