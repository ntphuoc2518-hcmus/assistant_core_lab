from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from assistant_core.config import Settings
from assistant_core.errors import ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

if TYPE_CHECKING:
    from assistant_core.rag.answerer import RagAnswerer

log = logging.getLogger("assistant_core")


class AssistantService:
    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: TemplateResponder | StubLLMResponder,
        rag: RagAnswerer | None = None,
    ):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()
        self.rag = rag

    def handle(self, msg: Message) -> Response:
                # Guardrail runs before router
        try:
            from assistant_core.guard import (
                INJECTION_REPLY,
                PRIVATE_REPLY,
                is_injection_request,
                is_private_request,
            )

            # Block prompt injection attempts
            if is_injection_request(msg.text):
                return Response(
                    answer=INJECTION_REPLY,
                    intent=Intent.UNKNOWN,
                    path="abstain",
                    escalate=False,
                )

            # Block requests for private information
            if is_private_request(msg.text):
                return Response(
                    answer=PRIVATE_REPLY,
                    intent=Intent.UNKNOWN,
                    path="abstain",
                    escalate=False,
                )

        except ImportError:
            pass

        intent = route(msg.text, self.offices.names)

        if intent is Intent.GREETING:
            return Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=intent,
            )

        if intent is Intent.FEE:
            try:
                credits_val, retake_val = parse_credits(msg.text)
                total = tuition(
                    credits=credits_val,
                    retake=retake_val,
                    rate=self.settings.credit_rate_vnd,
                    retake_multiplier=self.settings.retake_multiplier,
                    max_credits=self.settings.max_credits,
                )
                return Response(
                    answer=f"Your tuition is {total:,} VND",
                    intent=intent,
                )
            except Exception as e:  # noqa: BLE001
                return Response(
                    answer=str(e),
                    intent=intent,
                    degraded=True,
                )

        if intent is Intent.OFFICE:
            o = self.offices.find(msg.text)
            if not o:
                return Response(
                    answer="Sorry, I couldn't find that office.",
                    intent=intent,
                )
            return Response(
                answer=f"{o.name}: room {o.room}, open {o.hours}",
                intent=intent,
            )

        # RAG for rule questions
        return self._rule(msg.text)

    def _rule(self, text: str) -> Response:
        if self.rag is not None:
            try:
                from assistant_core.guard import PRIVATE_REPLY, is_private_request

                if is_private_request(text):
                    return Response(
                        answer=PRIVATE_REPLY,
                        intent=Intent.UNKNOWN,
                        path="abstain",
                        escalate=False,
                    )
            except ImportError:
                pass
            return self.rag.answer(text)

        rule = self.handbook.search(text)
        if rule is None:
            return Response(
                answer="Sorry, I don't know that yet.",
                intent=Intent.UNKNOWN,
            )

        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
            )
        except ProviderError:
            log.warning(
                "provider failed; using template fallback",
                extra={"degraded": True, "intent": "rule"},
            )
            answer = self.fallback.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=True,
            )


def build_service(settings: Settings) -> AssistantService:
    """Build the assistant service using configured resources and RAG if available."""
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = TemplateResponder()
    rag = None
    kb_dir = getattr(settings, "kb_dir", Path("data/kb"))
    if kb_dir.exists():
        try:
            from assistant_core.llm import make_llm
            from assistant_core.rag.answerer import RagAnswerer
            from assistant_core.rag.chunker import load_folder
            from assistant_core.rag.index import make_index
            from assistant_core.tools import run_tool_call

            retrieval_kind = getattr(settings, "retrieval_kind", "bm25")
            index = make_index(retrieval_kind, load_folder(kb_dir))
            llm_provider = getattr(settings, "llm_provider", "stub")
            llm = (
                None
                if llm_provider == "template"
                else make_llm(
                    llm_provider,
                    getattr(settings, "llm_model", "llama3.2"),
                    getattr(settings, "llm_base_url", None),
                    getattr(settings, "llm_api_key", None),
                    getattr(settings, "llm_timeout_s", 5.0),
                )
            )

            def tool_runner(raw: str) -> str | None:
                return run_tool_call(
                    raw, settings.credit_rate_vnd, settings.retake_multiplier, settings.max_credits
                )

            min_score = getattr(settings, "retrieval_min_score", 2.0)
            prompt_version = getattr(settings, "prompt_version", "answer_v1")
            rag = RagAnswerer(
                index, llm, min_score, prompt_version=prompt_version, tool_runner=tool_runner
            )
        except ImportError:
            pass

    return AssistantService(settings, offices, handbook, responder, rag)
