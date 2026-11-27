"""Deterministic first implementations of ANANTA's eight modules."""
from .models import Claim, EvidenceGrade, TaskRequest, ToolAction


class RITA:
    name = "RITA"

    @staticmethod
    def check_dependencies(dependencies: dict[str, list[str]]) -> list[str]:
        errors = []
        for task, prerequisites in dependencies.items():
            if task in prerequisites:
                errors.append(f"self-dependency:{task}")
            for prerequisite in prerequisites:
                if prerequisite not in dependencies:
                    errors.append(f"unknown-dependency:{task}->{prerequisite}")
        visiting, visited = set(), set()

        def visit(node):
            if node in visiting:
                errors.append(f"cycle:{node}")
                return
            if node in visited:
                return
            visiting.add(node)
            for nxt in dependencies.get(node, []):
                if nxt in dependencies:
                    visit(nxt)
            visiting.remove(node)
            visited.add(node)

        for node in dependencies:
            visit(node)
        return sorted(set(errors))


class VAK:
    name = "VAK"

    @staticmethod
    def parse(request: TaskRequest) -> dict:
        text = request.text.strip()
        if not text:
            raise ValueError("input must not be empty")
        return {"task_id": request.task_id, "text": text, "language": request.language}


class MANAS:
    name = "MANAS"

    @staticmethod
    def focus(parsed: dict) -> dict:
        return {**parsed, "objective": parsed["text"], "state": "READY"}


class BUDDHI:
    name = "BUDDHI"

    @staticmethod
    def plan(focused: dict) -> dict:
        return {
            "task_id": focused["task_id"],
            "steps": ["understand", "check evidence", "review", "respond"],
            "status": "PLANNED",
        }


class AHAMKARA:
    name = "AHAMKARA"
    identity = {"system": "ANANTA", "version": "0.2.0", "consciousness_claim": False}

    @staticmethod
    def boundaries() -> dict:
        return {"can_execute_external_actions": False, "requires_yantra_gate": True}


class PRAMANA:
    name = "PRAMANA"

    @staticmethod
    def assess(claim: Claim) -> dict:
        if not claim.evidence:
            return {"claim": claim.text, "status": "UNVERIFIED", "grade": "E",
                    "reason": "No evidence attached", "confidence_is_calibrated": False}
        best = min(claim.evidence, key=lambda e: list(EvidenceGrade).index(e.grade))
        return {"claim": claim.text, "status": "SUPPORTED_SOURCE_ATTACHED",
                "grade": best.grade.value, "source": best.source,
                "source_date": best.source_date,
                "confidence": claim.confidence,
                "confidence_is_calibrated": False}

    @staticmethod
    def has_unsupported_claims(claims: list[Claim]) -> bool:
        return any(not claim.evidence for claim in claims)


class SAKSHI:
    name = "SAKSHI"

    @staticmethod
    def review(claims: list[Claim]) -> dict:
        unsupported = [claim.text for claim in claims if not claim.evidence]
        return {"passed": not unsupported, "unsupported_claims": unsupported,
                "review_rule": "claims without attached evidence remain unverified"}


class YANTRA:
    name = "YANTRA"
    ALLOWED_ACTIONS = {"read_file", "safe_calculation", "local_report"}

    @classmethod
    def authorize(cls, action: ToolAction) -> dict:
        if action.name not in cls.ALLOWED_ACTIONS:
            return {"authorized": False, "reason": "action_not_allowlisted"}
        if action.high_impact and not action.human_approved:
            return {"authorized": False, "reason": "human_approval_required"}
        if action.name == "read_file" and not action.human_approved:
            return {"authorized": False, "reason": "explicit_approval_required"}
        return {"authorized": True, "reason": "allowlisted_and_approved_or_low_risk"}
