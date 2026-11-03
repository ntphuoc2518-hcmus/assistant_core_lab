-- F3: Topic nhận nhiều thumbs-down nhất (rating = -1)
SELECT i.topic, COUNT(*) AS thumbs_down_count
FROM feedback f
JOIN interaction i ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC;

-- H2: Câu hỏi tùy chọn - Giờ nào trong ngày có nhiều câu hỏi (interaction) nhất?
SELECT strftime('%H', created_at) AS hour_of_day, COUNT(*) AS request_count
FROM interaction
GROUP BY hour_of_day
ORDER BY request_count DESC;