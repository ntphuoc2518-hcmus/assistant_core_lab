
"""FastAPI application — Lab 4 API with Lab 5 persistence (SQLite via the Repository).

Run:
    uvicorn assistant_api.main:create_app --factory --reload

Endpoints (v1):
    GET  /health
    POST /v1/chat
    POST /v1/feedback
    GET  /v1/feedback (admin)
    GET  /v1/weather
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    FeedbackIn,
    FeedbackOut,
    Weather,
)
from assistant_api.weather import ExternalServiceError, WeatherClient
from assistant_core import AssistantService, Message, build_service
from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError
from assistant_core.models import Intent

log = logging.getLogger("assistant_api")


def build_repository(settings: Settings) -> Repository:
    """Open the configured database (a persistent SQLite file by default) and create missing tables."""
    if not settings.session_salt:
        raise ConfigError("SESSION_SALT is required to hash session ids (set it in .env; see .env.example)")
    engine = make_engine(settings.database_url)
    init_db(engine)
    return Repository(engine, settings.session_salt)


def create_app(
    settings: Settings | None = None,
    service: AssistantService | None = None,
    weather: WeatherClient | None = None,
    repo: Repository | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    service = service or build_service(settings)
    weather = weather or WeatherClient(
        settings.weather_url,
        settings.campus_lat,
        settings.campus_lon,
        timeout_s=settings.weather_timeout_s,
    )

    repo = repo or build_repository(settings)

    app = FastAPI(
        title="Study Assistant API",
        version="1.0.0",
        description="Backend of the CSC10014 Smart Virtual Assistant.",
    )

    def error(code: int, key: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={"error": {"code": key, "message": message}},
        )

    @app.exception_handler(RequestValidationError)
    async def on_validation(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"][1:]) or "body"
        return error(422, "invalid_request", f"{field}: {first['msg']}")

    @app.exception_handler(HTTPException)
    async def on_http(
        _: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        code = str(exc.detail).lower().replace(" ", "_")
        return error(exc.status_code, code, str(exc.detail))

    def require_admin(
        x_api_key: str | None = Header(default=None),
    ) -> None:
        if not settings.api_admin_key or x_api_key != settings.api_admin_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid API key",
            )

    @app.get("/health", tags=["ops"])
    def health() -> dict:
        return {"status": "ok", "version": app.version}

    # T1: POST /v1/chat
    @app.post(
        "/v1/chat",
        response_model=ChatResponse,
        tags=["chat"],
        responses={
            422: {"model": ErrorResponse},
            429: {"model": ErrorResponse},
        },
    )
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        # Bonus rate limiting will be added later.
        started = time.perf_counter()
        resp = service.handle(
            Message(
                text=req.message,
                session_id=req.session_id,
            )
        )
        latency_ms = (time.perf_counter() - started) * 1000
        request_id = uuid.uuid4().hex[:12]

        # Store metadata only — never the message text or the raw session id.
        try:
            repo.record_interaction(
                raw_session=req.session_id,
                request_id=request_id,
                intent=Intent(resp.intent).value,
                topic=resp.sources[0].id if resp.sources else None,
                resolved=resp.intent != Intent.UNKNOWN,
                degraded=resp.degraded,
                latency_ms=round(latency_ms, 2),
            )
        except SQLAlchemyError:
            # The answer is still useful; feedback for this request_id will return 404.
            log.exception("could not record interaction")

        return ChatResponse(
            **resp.model_dump(),
            request_id=request_id,
        )

    # T2: POST /v1/feedback
    @app.post(
        "/v1/feedback",
        response_model=FeedbackOut,
        status_code=status.HTTP_201_CREATED,
        tags=["feedback"],
        responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def add_feedback(fb: FeedbackIn) -> FeedbackOut:
        saved = repo.add_feedback(fb.request_id, fb.rating, fb.comment)
        if saved is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )
        return FeedbackOut.model_validate(saved.model_dump())

    # T3: GET /v1/feedback (admin only)
    @app.get(
        "/v1/feedback",
        response_model=list[FeedbackOut],
        tags=["feedback"],
        dependencies=[Depends(require_admin)],
        responses={401: {"model": ErrorResponse}},
    )
    def list_feedback(limit: int = Query(default=100, ge=1, le=100)) -> list[FeedbackOut]:
        return [FeedbackOut.model_validate(fb.model_dump()) for fb in repo.list_feedback(limit)]

    # T4: GET /v1/weather
    @app.get(
        "/v1/weather",
        response_model=Weather,
        tags=["external"],
        responses={503: {"model": ErrorResponse}},
    )
    def campus_weather() -> Weather:
        try:
            return weather.current()
        except ExternalServiceError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weather service unavailable",
            ) from None

    return app
