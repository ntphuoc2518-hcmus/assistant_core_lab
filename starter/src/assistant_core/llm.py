"""LLM client wrapper and response parsing for RAG."""

from __future__ import annotations

import json
import logging

from pydantic import BaseModel, Field

from assistant_core.errors import ProviderError

log = logging.getLogger("assistant_core.llm")


class AnswerDraft(BaseModel):
    answer: str
    source_ids: list[str] = Field(default_factory=list)
    abstain: bool = False
    confidence: float = 1.0


def clean_json_str(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


class LLM:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


def build_prompt(question: str, hits: list, prompt_version: str) -> str:
    context = "\n\n".join(
        f"[{h.chunk.id}] {h.chunk.title}\n{h.chunk.text}" for h in hits
    )
    return f"Question: {question}\n\nContext:\n{context}"


def parse_draft(raw: str, allowed_source_ids: set[str]) -> AnswerDraft:
    try:
        cleaned = clean_json_str(raw)
        data = json.loads(cleaned)
        draft = AnswerDraft(**data)
    except Exception as exc:
        raise ProviderError(f"Failed to parse LLM JSON: {exc}") from exc

    if not draft.abstain:
        for sid in draft.source_ids:
            if sid not in allowed_source_ids:
                raise ProviderError(
                    f"Grounding check failed: cited source '{sid}' was not in retrieved chunks."
                )

    return draft