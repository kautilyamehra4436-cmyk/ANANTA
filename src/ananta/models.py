"""Validated data contracts shared by ANANTA modules."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import json


MAX_REQUEST_LENGTH = 10_000
MAX_IDENTIFIER_LENGTH = 128
MAX_EVIDENCE_ITEMS = 100
MAX_PAYLOAD_BYTES = 16_384


class EvidenceGrade(str, Enum):
    A = "A"  # primary source / direct measurement
    B = "B"  # strong peer-reviewed research / systematic review
    C = "C"  # reliable secondary source
    D = "D"  # weak or unverified source
    E = "E"  # inference, imagination, or unsupported traditional claim


@dataclass(frozen=True)
class Evidence:
    source: str
    grade: EvidenceGrade
    excerpt: str = ""
    source_date: str | None = None

    def __post_init__(self):
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("evidence source must be a non-empty string")
        if not isinstance(self.grade, EvidenceGrade):
            raise TypeError("grade must be an EvidenceGrade")
        if not isinstance(self.excerpt, str) or len(self.excerpt) > 20_000:
            raise ValueError("evidence excerpt must be a string of at most 20000 characters")
        if self.source_date is not None and not isinstance(self.source_date, str):
            raise TypeError("source_date must be a string or None")


@dataclass(frozen=True)
class Claim:
    text: str
    evidence: tuple[Evidence, ...] = ()
    confidence: float | None = None  # internal score only; not calibrated probability

    def __post_init__(self):
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("claim text must be a non-empty string")
        if not isinstance(self.evidence, tuple) or len(self.evidence) > MAX_EVIDENCE_ITEMS:
            raise ValueError("claim evidence must be a tuple of at most 100 items")
        if any(not isinstance(item, Evidence) for item in self.evidence):
            raise TypeError("claim evidence entries must be Evidence objects")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class TaskRequest:
    text: str
    task_id: str = "task-001"
    language: str = "auto"

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise TypeError("request text must be a string")
        if len(self.text) > MAX_REQUEST_LENGTH:
            raise ValueError(f"request text exceeds {MAX_REQUEST_LENGTH} characters")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if len(self.task_id) > MAX_IDENTIFIER_LENGTH:
            raise ValueError("task_id is too long")
        if not isinstance(self.language, str) or not self.language.strip() or len(self.language) > 64:
            raise ValueError("language must be a non-empty string of at most 64 characters")


@dataclass(frozen=True)
class ToolAction:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    high_impact: bool = False
    human_approved: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("action name must be a non-empty string")
        if type(self.high_impact) is not bool or type(self.human_approved) is not bool:
            raise TypeError("approval and impact flags must be booleans")
        if not isinstance(self.payload, dict):
            raise TypeError("action payload must be a dictionary")
        try:
            encoded = json.dumps(self.payload, allow_nan=False, sort_keys=True).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("action payload must contain only finite JSON data") from exc
        if len(encoded) > MAX_PAYLOAD_BYTES:
            raise ValueError(f"action payload exceeds {MAX_PAYLOAD_BYTES} bytes")


@dataclass(frozen=True)
class AuditEvent:
    event: str
    details: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""
    timestamp: str = ""
    previous_hash: str = ""
    event_hash: str = ""
