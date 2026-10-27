"""Public interface for assistant_core."""

from .models import Message
from .service import AssistantService, build_service

__all__ = ["AssistantService", "Message", "build_service"]