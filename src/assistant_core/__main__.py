import logging
import sys
import time

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

logger = logging.getLogger("assistant_core")


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m assistant_core "<question>"', file=sys.stderr)
        sys.exit(1)

    # Cải tiến: gộp toàn bộ tham số phía sau để tránh lỗi quên ngoặc kép
    user_text = " ".join(sys.argv[1:])

    settings = load_settings()
    setup_logging(settings.log_level)

    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()

    service = AssistantService(settings, offices, handbook, responder)

    start_time = time.perf_counter()
    msg = Message(text=user_text)
    res = service.handle(msg)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "handled",
        extra={
            "intent": (
                res.intent.value
                if hasattr(res.intent, "value")
                else str(res.intent)
            ),
            "latency_ms": latency_ms,
            "session": msg.session_id,
            "degraded": res.degraded,
        },
    )

    print(res.answer)


if __name__ == "__main__":
    main()