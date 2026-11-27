"""Deterministic implementations of ANANTA's eight control modules."""
import heapq

from .models import Claim, EvidenceGrade, TaskRequest, ToolAction


class RITA:
    name = "RITA"

    @staticmethod
    def check_dependencies(dependencies: dict[str, list[str]]) -> list[str]:
        if not isinstance(dependencies, dict):
            raise TypeError("dependencies must be a dictionary")
        errors = []
        normalized = {}
        for task, prerequisites in dependencies.items():
            if not isinstance(task, str) or not task:
                errors.append("invalid-task-name")
                continue
            if not isinstance(prerequisites, list):
                errors.append(f"invalid-prerequisites:{task}")
                continue
            valid_prerequisites = []
            for prerequisite in prerequisites:
                if not isinstance(prerequisite, str) or not prerequisite:
                    errors.append(f"invalid-prerequisite:{task}")
                    continue
                valid_prerequisites.append(prerequisite)
                if prerequisite == task:
                    errors.append(f"self-dependency:{task}")
                if prerequisite not in dependencies:
                    errors.append(f"unknown-dependency:{task}->{prerequisite}")
            normalized[task] = valid_prerequisites

        # Iterative color DFS avoids recursion-depth failures on long graphs.
        color = {node: 0 for node in normalized}
        for root in normalized:
            if color[root]:
                continue
            stack = [(root, 0)]
            color[root] = 1
            while stack:
                node, index = stack[-1]
                neighbors = normalized.get(node, [])
                if index >= len(neighbors):
                    color[node] = 2
                    stack.pop()
                    continue
                nxt = neighbors[index]
                stack[-1] = (node, index + 1)
                if nxt not in normalized:
                    continue
                if color[nxt] == 1:
                    errors.append(f"cycle:{nxt}")
                elif color[nxt] == 0:
                    color[nxt] = 1
                    stack.append((nxt, 0))
        return sorted(set(errors))

    @staticmethod
    def topological_order(dependencies: dict[str, list[str]]) -> list[str]:
        errors = RITA.check_dependencies(dependencies)
        if errors:
            raise ValueError("invalid dependency graph: " + ", ".join(errors))

        # Kahn's algorithm with a min-heap: deterministic O((V + E) log V)
        # ordering, without repeatedly scanning and sorting every remaining node.
        prerequisites = {node: set(reqs) for node, reqs in dependencies.items()}
        dependents = {node: [] for node in dependencies}
        indegree = {node: len(reqs) for node, reqs in prerequisites.items()}
        for node, reqs in prerequisites.items():
            for prerequisite in reqs:
                dependents[prerequisite].append(node)
        for children in dependents.values():
            children.sort()

        ready = [node for node, degree in indegree.items() if degree == 0]
        heapq.heapify(ready)
        ordered = []
        while ready:
            node = heapq.heappop(ready)
            ordered.append(node)
            for child in dependents[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    heapq.heappush(ready, child)
        if len(ordered) != len(dependencies):
            raise ValueError("dependency graph contains a cycle")
        return ordered


class VAK:
    name = "VAK"

    @staticmethod
    def parse(request: TaskRequest) -> dict:
        if not isinstance(request, TaskRequest):
            raise TypeError("request must be a TaskRequest")
        text = request.text.strip()
        if not text:
            raise ValueError("input must not be empty")
        return {"task_id": request.task_id, "text": text, "language": request.language}


class MANAS:
    name = "MANAS"

    @staticmethod
    def focus(parsed: dict) -> dict:
        if not isinstance(parsed, dict) or not {"task_id", "text", "language"} <= parsed.keys():
            raise ValueError("parsed task is missing required fields")
        return {**parsed, "objective": parsed["text"], "state": "READY"}


class BUDDHI:
    name = "BUDDHI"

    @staticmethod
    def plan(focused: dict) -> dict:
        if not isinstance(focused, dict) or not focused.get("task_id"):
            raise ValueError("focused task must contain a task_id")
        return {
            "task_id": focused["task_id"],
            "steps": ["understand", "check evidence", "review", "respond"],
            "status": "PLANNED",
        }


class AHAMKARA:
    name = "AHAMKARA"
    identity = {"system": "ANANTA", "version": "0.4.0", "consciousness_claim": False}

    @staticmethod
    def boundaries() -> dict:
        return {"can_execute_local_actions": True, "local_actions": ["safe_calculation", "local_report"], "can_execute_external_actions": False, "requires_yantra_gate": True}


class PRAMANA:
    name = "PRAMANA"

    @staticmethod
    def assess(claim: Claim) -> dict:
        if not isinstance(claim, Claim):
            raise TypeError("claim must be a Claim")
        if not claim.evidence:
            return {"claim": claim.text, "status": "UNVERIFIED", "grade": "E",
                    "reason": "No evidence attached", "confidence_is_calibrated": False}
        best = min(claim.evidence, key=lambda e: list(EvidenceGrade).index(e.grade))
        return {"claim": claim.text, "status": "SUPPORTED_SOURCE_ATTACHED",
                "grade": best.grade.value, "source": best.source,
                "source_date": best.source_date, "confidence": claim.confidence,
                "confidence_is_calibrated": False,
                "verification_note": "Source attachment is not proof of claim entailment or source authenticity."}

    @staticmethod
    def has_unsupported_claims(claims: list[Claim]) -> bool:
        return any(not claim.evidence for claim in claims)


class SAKSHI:
    name = "SAKSHI"

    @staticmethod
    def review(claims: list[Claim]) -> dict:
        if not isinstance(claims, list) or any(not isinstance(c, Claim) for c in claims):
            raise TypeError("claims must be a list of Claim objects")
        unsupported = [claim.text for claim in claims if not claim.evidence]
        return {"passed": not unsupported, "unsupported_claims": unsupported,
                "review_rule": "claims without attached evidence remain unverified"}


class YANTRA:
    name = "YANTRA"
    ALLOWED_ACTIONS = {"read_file", "safe_calculation", "local_report"}
    PAYLOAD_KEYS = {
        "read_file": {"path"},
        "safe_calculation": {"expression"},
        "local_report": {"title", "content"},
    }

    @classmethod
    def authorize(cls, action: ToolAction, emergency_stop: bool = False) -> dict:
        if not isinstance(action, ToolAction):
            raise TypeError("action must be a ToolAction")
        if emergency_stop:
            return {"authorized": False, "reason": "emergency_stop_active"}
        if action.name not in cls.ALLOWED_ACTIONS:
            return {"authorized": False, "reason": "action_not_allowlisted"}
        if action.high_impact and not action.human_approved:
            return {"authorized": False, "reason": "human_approval_required"}
        if action.name == "read_file" and not action.human_approved:
            return {"authorized": False, "reason": "explicit_approval_required"}
        allowed_keys = cls.PAYLOAD_KEYS[action.name]
        if set(action.payload) - allowed_keys:
            return {"authorized": False, "reason": "payload_has_unknown_fields"}
        if action.name == "read_file":
            path = action.payload.get("path")
            if not isinstance(path, str) or not path.strip():
                return {"authorized": False, "reason": "valid_path_required"}
            if path.startswith(("/", "\\")) or ".." in path.replace("\\", "/").split("/"):
                return {"authorized": False, "reason": "path_outside_workspace"}
        if action.name == "safe_calculation":
            expression = action.payload.get("expression")
            if not isinstance(expression, str) or not expression.strip() or len(expression) > 512:
                return {"authorized": False, "reason": "valid_expression_required"}
        if action.name == "local_report":
            if not isinstance(action.payload.get("title", ""), str) or not isinstance(action.payload.get("content", ""), str):
                return {"authorized": False, "reason": "report_fields_must_be_strings"}
        return {"authorized": True, "reason": "allowlisted_and_approved_or_low_risk"}
