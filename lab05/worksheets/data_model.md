# Lab 5 — Data model worksheet

## 1. Critique the bad schema (sql/bad_schema.sql)
| # | Problem | Why it hurts | Fix |
|---|---|---|---|
| 1 | Storing raw PII (`student_name`, `phone_number`, full question text) | Violates user privacy principles; high risk of data leak under regulatory standards (e.g., GDPR). | Remove PII columns. Store only anonymized session IDs and extracted metadata (`intent`, `topic`). |
| 2 | Missing Primary Key / Foreign Key constraints | Allows duplicate records and orphan feedback entries, breaking referential integrity. | Set `request_id` as Primary Key in `requests` table and add `FOREIGN KEY (request_id) REFERENCES requests(id)` in `feedback`. |
| 3 | Unconstrained `rating` column | Permits invalid or corrupt rating values (e.g., -99, 100, NULL), distorting evaluation metrics. | Add constraint `CHECK (rating IN (1, -1))` or `CHECK (rating BETWEEN 1 AND 5)`. |
| 4 | Storing raw `session_id` in plain text | Enables cross-session tracking and potential re-identification of individual users. | Hash `session_id` with SHA-256 and a secret salt before persisting (`hash(session_id + salt)`). |
| 5 | Missing timestamps and indexes | Prevents time-series queries and slows down analytical reporting as data scales. | Add `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` and create indexes on `intent` and `created_at`. |
| 6 | Unnormalized schema / storing raw latency as string | Impairs SQL aggregate functions (`AVG`, `SUM`) and increases storage overhead. | Store numerical latency as `REAL` or `INTEGER` (in milliseconds) instead of text. |

## 2. Store or not? (privacy-aware storage)
| Data | Store? | Form (raw / hashed / aggregated / none) | Retention | Reason |
|---|---|---|---|---|
| raw user message | No | none | 0 days | Contains sensitive personal details; discard immediately after intent classification. |
| session id | Yes | hashed | 90 days | Enables session correlation without revealing user identity (SHA-256 + salt). |
| intent, latency, topic | Yes | raw | Permanent | Essential operational telemetry and system quality monitoring without containing PII. |
| feedback rating | Yes | raw | Permanent | Quantitative metric required to track assistant accuracy and user satisfaction over time. |
| feedback comment | Yes | raw / sanitized | 90 days | Provides qualitative debugging insights for negative ratings; purged periodically. |
| student name / phone | No | none | Never | Unnecessary PII that creates severe security and privacy liabilities. |

## 3. Product questions → fields
| Product question | Fields needed | Table(s) | Query sketch |
|---|---|---|---|
| Most failed intent? | `intent`, `resolved` | `requests` | `SELECT intent, COUNT(*) AS fails FROM requests WHERE resolved = FALSE GROUP BY intent ORDER BY fails DESC LIMIT 1;` |
| Average response time by intent? | `intent`, `latency` | `requests` | `SELECT intent, ROUND(AVG(latency), 1) AS avg_latency FROM requests GROUP BY intent;` |
| Top unresolved topics? | `topic`, `rating` | `requests` JOIN `feedback` | `SELECT r.topic, COUNT(*) AS negative_count FROM requests r JOIN feedback f ON r.request_id = f.request_id WHERE f.rating = -1 GROUP BY r.topic ORDER BY negative_count DESC LIMIT 1;` |

## 4. ER diagram

```mermaid
erDiagram
    REQUESTS {
        string request_id PK
        string hashed_session_id
        string intent
        string topic
        float latency
        boolean resolved
        datetime created_at
    }

    FEEDBACK {
        int id PK
        string request_id FK
        int rating
        string comment
        datetime created_at
    }

    REQUESTS ||--o| FEEDBACK : "receives"