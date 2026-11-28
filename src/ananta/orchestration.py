"""Additive, deterministic orchestration for ANANTA's existing control modules.

This layer coordinates existing modules; it does not replace their implementations
or claim autonomous reasoning or consciousness.
"""
from .modules import BUDDHI, MANAS, PRAMANA, RITA, SAKSHI, VAK
from .models import Claim, TaskRequest


class ANANTAOrchestrator:
    """Run the existing control stages in a validated dependency order."""

    DEPENDENCIES = {
        "parse_input": [],
        "focus": ["parse_input"],
        "plan": ["focus"],
        "assess_evidence": ["plan"],
        "review_claims": ["assess_evidence"],
        "validate_flow": ["review_claims"],
        "assemble": ["validate_flow"],
    }

    @classmethod
    def execution_order(cls) -> list[str]:
        return RITA.topological_order(cls.DEPENDENCIES)

    @classmethod
    def run(cls, request: TaskRequest, claims: list[Claim] | None = None) -> dict:
        if claims is None:
            claims = []
        if not isinstance(claims, list) or any(not isinstance(item, Claim) for item in claims):
            raise TypeError("claims must be a list of Claim objects")

        artifacts = {}
        steps = {
            "parse_input": lambda: VAK.parse(request),
            "focus": lambda: MANAS.focus(artifacts["parsed"]),
            "plan": lambda: BUDDHI.plan(artifacts["focused"]),
            "assess_evidence": lambda: [PRAMANA.assess(claim) for claim in claims],
            "review_claims": lambda: SAKSHI.review(claims),
            "validate_flow": lambda: RITA.check_dependencies(cls.DEPENDENCIES),
            "assemble": lambda: None,
        }
        for name in cls.execution_order():
            artifacts[name] = steps[name]()

        return {
            "parsed": artifacts["parse_input"],
            "focused": artifacts["focus"],
            "plan": artifacts["plan"],
            "evidence": artifacts["assess_evidence"],
            "review": artifacts["review_claims"],
            "consistency_errors": artifacts["validate_flow"],
            "execution_order": cls.execution_order(),
        }
