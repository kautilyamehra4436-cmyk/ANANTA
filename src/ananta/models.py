"""Typed data contracts shared by ANANTA modules."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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


@dataclass(frozen=True)
class Claim:
    text: str
    evidence: tuple[Evidence, ...] = ()
    confidence: float | None = None  # internal score only; not calibrated probability


@dataclass(frozen=True)
class TaskRequest:
    text: str
    task_id: str = "task-001"
    language: str = "auto"


@dataclass(frozen=True)
class ToolAction:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    high_impact: bool = False
    human_approved: bool = False


@dataclass
class AuditEvent:
    event: str
    details: dict[str, Any] = field(default_factory=dict)
