from ananta.models import Claim, TaskRequest
from ananta.orchestration import ANANTAOrchestrator


def test_orchestration_uses_dependency_order():
    order = ANANTAOrchestrator.execution_order()
    assert order.index("parse_input") < order.index("focus")
    assert order.index("focus") < order.index("plan")
    assert order.index("plan") < order.index("assess_evidence")
    assert order.index("assess_evidence") < order.index("review_claims")
    assert order.index("review_claims") < order.index("validate_flow")


def test_orchestrator_runs_existing_modules():
    result = ANANTAOrchestrator.run(TaskRequest("test task", "orch-1"), [Claim("claim")])
    assert result["parsed"]["text"] == "test task"
    assert result["focused"]["objective"] == "test task"
    assert result["plan"]["status"] == "PLANNED"
    assert result["evidence"][0]["status"] == "UNVERIFIED"
    assert result["review"]["passed"] is False
    assert result["consistency_errors"] == []


def test_orchestrator_rejects_invalid_claim_collection():
    try:
        ANANTAOrchestrator.run(TaskRequest("test"), ["not-a-claim"])
        assert False, "invalid claims must be rejected"
    except TypeError:
        pass
