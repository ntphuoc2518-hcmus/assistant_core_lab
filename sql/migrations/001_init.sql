-- 001_init.sql — Lab 5 schema (equivalent to the SQLModel classes in src/assistant_api/db.py).
-- Privacy: no raw messages, no raw session ids, no names, only metadata, a hashed session id and feedback.
-- Every statement uses IF NOT EXISTS so the file is safe even if the app already created the tables.

CREATE TABLE IF NOT EXISTS chat_session (
    id          VARCHAR(16) NOT NULL PRIMARY KEY,      -- salted SHA-256 of the session id (truncated)
    channel     VARCHAR(16) NOT NULL DEFAULT 'web',
    created_at  DATETIME    NOT NULL
);

CREATE TABLE IF NOT EXISTS interaction (
    id          INTEGER     NOT NULL PRIMARY KEY,
    request_id  VARCHAR(32) NOT NULL,
    session_id  VARCHAR(16) NOT NULL REFERENCES chat_session (id),
    intent      VARCHAR(16) NOT NULL,
    topic       VARCHAR(32),
    resolved    BOOLEAN     NOT NULL DEFAULT 1,
    degraded    BOOLEAN     NOT NULL DEFAULT 0,
    latency_ms  FLOAT       NOT NULL DEFAULT 0,
    created_at  DATETIME    NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_interaction_request_id ON interaction (request_id);
CREATE INDEX IF NOT EXISTS ix_interaction_session_id ON interaction (session_id);
CREATE INDEX IF NOT EXISTS ix_interaction_intent ON interaction (intent);
CREATE INDEX IF NOT EXISTS ix_interaction_created_at ON interaction (created_at);

CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER      NOT NULL PRIMARY KEY,
    request_id  VARCHAR(32)  NOT NULL REFERENCES interaction (request_id),
    rating      INTEGER      NOT NULL,
    comment     VARCHAR(500),
    created_at  DATETIME     NOT NULL,
    CONSTRAINT ck_feedback_rating CHECK (rating IN (-1, 0, 1))
);
CREATE INDEX IF NOT EXISTS ix_feedback_request_id ON feedback (request_id);
CREATE INDEX IF NOT EXISTS ix_feedback_created_at ON feedback (created_at);
