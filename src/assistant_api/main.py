import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assistant_api.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackIn,
    FeedbackOut,
    Weather,
)
from assistant_api.weather import ExternalServiceError, WeatherClient
from assistant_core.config import Settings
from assistant_core.service import AssistantService, Message


def create_app(
    settings: Settings | None = None,
    service: AssistantService | None = None,
    weather_client: WeatherClient | None = None,
) -> FastAPI:
    if settings is None:
        settings = Settings()

    if service is None:
        try:
            service = AssistantService(settings)
        except Exception:
            service = None

    if weather_client is None:
        try:
            weather = WeatherClient(settings)
        except Exception:
            weather = None
    else:
        weather = weather_client

    app = FastAPI(title="Study Assistant API")
    feedback_store: list[FeedbackOut] = []

    # Format lỗi Validation (422) theo chuẩn {"error": {"code": "invalid_request", ...}}
    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "invalid_request", "message": "Validation error"}},
        )

    # Format lỗi HTTP (401, 503, ...)
    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "error", "message": str(exc.detail)}},
        )

    # Kiểm tra Header API Key (cho phép Optional để chủ động trả 401 thay vì 422)
    def require_admin(x_api_key: str | None = Header(None, alias="X-API-Key")):
        admin_key = getattr(settings, "api_admin_key", "secret-admin-key") if settings else "secret-admin-key"
        if not x_api_key or x_api_key != admin_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "unauthorized", "message": "Invalid or missing API key"},
            )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    # T1: POST /v1/chat
    @app.post("/v1/chat")
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        resp = service.handle(Message(text=req.message, session_id=req.session_id))
        return ChatResponse(**resp.model_dump(), request_id=uuid.uuid4().hex[:12])

    # T2: POST /v1/feedback
    @app.post("/v1/feedback", status_code=201)
    def add_feedback(fb: FeedbackIn) -> FeedbackOut:
        item = FeedbackOut(
            **fb.model_dump(),
            id=len(feedback_store) + 1,
            created_at=datetime.now(timezone.utc),
        )
        feedback_store.append(item)
        return item

    # T3: GET /v1/feedback
    @app.get("/v1/feedback", dependencies=[Depends(require_admin)])
    def list_feedback() -> list[FeedbackOut]:
        return feedback_store

    # T4: GET /v1/weather
    @app.get("/v1/weather")
    def campus_weather() -> Weather:
        try:
            return weather.current()
        except ExternalServiceError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "weather_service_unavailable", "message": "Weather service unavailable"},
            ) from None


    # H1: GET /v1/offices
    @app.get("/v1/offices")
    def list_offices():
        if hasattr(service, "offices") and hasattr(service.offices, "all"):
            offices = service.offices.all()
        elif hasattr(service, "knowledge") and hasattr(service.knowledge, "all"):
            offices = service.knowledge.all()
        else:
            offices = []
        return [o.__dict__ if hasattr(o, "__dict__") else o for o in offices]

    return app