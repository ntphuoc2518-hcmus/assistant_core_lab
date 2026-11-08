#!/usr/bin/env bash
# Manual API test script. Start the server first:
#   uvicorn assistant_api.main:create_app --factory --reload
set -u
BASE="${BASE:-http://127.0.0.1:8000}"
ADMIN="${API_ADMIN_KEY:-change-me}"
hr() { echo; echo "== $1"; }
hr "health (expect 200)";              curl -s -w "  [%{http_code}]\n" "$BASE/health"
hr "chat fee (expect 200)";            curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/chat" -H "Content-Type: application/json" -d '{"message":"tuition for 18 credits and 2 retake","session_id":"demo"}'
hr "chat rule with source (200)";      curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/chat" -H "Content-Type: application/json" -d '{"message":"can I register my thesis with 118 credits"}'
hr "chat empty (expect 422)";          curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/chat" -H "Content-Type: application/json" -d '{"message":""}'
hr "chat wrong type (expect 422)";     curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/chat" -H "Content-Type: application/json" -d '{"message":123}'
# Lab 5: feedback must refer to a real answer, so reuse the request_id of a chat answer.
RID=$(curl -s -X POST "$BASE/v1/chat" -H "Content-Type: application/json" -d '{"message":"hello","session_id":"demo"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['request_id'])")
hr "feedback (expect 201)";            curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/feedback" -H "Content-Type: application/json" -d "{\"request_id\":\"$RID\",\"rating\":1,\"comment\":\"clear answer\"}"
hr "feedback unknown id (404)";        curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/feedback" -H "Content-Type: application/json" -d '{"request_id":"nope","rating":1}'
hr "feedback bad rating (422)";        curl -s -w "  [%{http_code}]\n" -X POST "$BASE/v1/feedback" -H "Content-Type: application/json" -d "{\"request_id\":\"$RID\",\"rating\":7}"
hr "list feedback no key (401)";       curl -s -w "  [%{http_code}]\n" "$BASE/v1/feedback"
hr "list feedback with key (200)";     curl -s -w "  [%{http_code}]\n" -H "X-API-Key: $ADMIN" "$BASE/v1/feedback"
hr "weather (200, or 503 if down)";    curl -s -w "  [%{http_code}]\n" -m 10 "$BASE/v1/weather"
hr "unknown route (404)";              curl -s -w "  [%{http_code}]\n" "$BASE/v1/nope"
