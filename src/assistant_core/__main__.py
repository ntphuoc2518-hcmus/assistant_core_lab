"""Entry point for the assistant_core package.

CLI demos (run from repo root with the package installed in editable mode):

    $ python -m assistant_core "hello"
    Hello! I can help with offices, fees and rules.

    $ python -m assistant_core "tuition for 18 credits and 2 retake"
    Your tuition is 9,450,000 VND

    $ python -m assistant_core "thesis regulations"
    Based on 'Thesis registration': Students may register a thesis when they have at least 120 accumulated credits and a GPA of at least 2.0.
      [H26-5.3] Thesis registration
"""
import logging
import sys
import time

from assistant_core.config import load_settings
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.service import build_service

logger = logging.getLogger("assistant_core")


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m assistant_core "<question>"', file=sys.stderr)
        sys.exit(1)

    # Merge all trailing args so the user can omit quotes
    user_text = " ".join(sys.argv[1:])

    settings = load_settings()
    setup_logging(settings.log_level)

    service = build_service(settings)

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
    if res.sources:
        for src in res.sources:
            print(f"  [{src.id}] {src.title}")


if __name__ == "__main__":
    main()
