from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"


@dataclass
class Office:
    name: str
    room: str
    hours: str


@dataclass
class Rule:
    id: str
    title: str
    text: str


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"


class Source(BaseModel):
    id: str
    title: str


class Response(BaseModel):
    answer: str
    intent: Intent | str = Intent.UNKNOWN
    sources: list[Source] = []
    degraded: bool = False
