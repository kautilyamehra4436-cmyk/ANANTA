from ananta import AnantaController, Claim, Evidence, TaskRequest, ToolAction
from ananta.models import EvidenceGrade
from ananta.modules import PRAMANA, RITA, YANTRA


def test_basic_task_pipeline_and_audit():
    engine = AnantaController()
    result = engine.process(TaskRequest("test input", "t-1"))
    assert result["answer_status"] == "READY_FOR_RESPONSE"
    assert result["review"]["passed"] is True
    assert len(engine.audit()) == 2


def test_unsupported_claim_requires_review():
    engine = AnantaController()
    result = engine.process(
        TaskRequest("check an unsupported claim", "t-2"),
        [Claim("unsupported statement")],
    )
    assert result["answer_status"] == "REVIEW_REQUIRED"
    assert result["review"]["passed"] is False
    assert result["evidence"][0]["status"] == "UNVERIFIED"


def test_empty_input_rejected():
    try:
        AnantaController().process(TaskRequest("   "))
        assert False, "empty input should fail"
    except ValueError as exc:
        assert "empty" in str(exc)


def test_claim_without_evidence_is_unverified():
    result = PRAMANA.assess(Claim("unsupported statement"))
    assert result["status"] == "UNVERIFIED"
    assert result["grade"] == "E"


def test_claim_with_evidence_is_not_misrepresented_as_proof():
    claim = Claim("A source is attached", (Evidence("primary source", EvidenceGrade.A),))
    result = PRAMANA.assess(claim)
    assert result["status"] == "SUPPORTED_SOURCE_ATTACHED"
    assert result["confidence_is_calibrated"] is False


def test_dependency_cycle_detected():
    errors = RITA.check_dependencies({"a": ["b"], "b": ["a"]})
    assert any(error.startswith("cycle:") for error in errors)


def test_unknown_dependency_detected():
    assert "unknown-dependency:a->missing" in RITA.check_dependencies({"a": ["missing"]})


def test_tool_denied_by_default():
    assert YANTRA.authorize(ToolAction("delete_account"))["authorized"] is False


def test_high_impact_requires_human_approval():
    action = ToolAction("local_report", high_impact=True)
    assert YANTRA.authorize(action)["reason"] == "human_approval_required"
    approved = ToolAction("local_report", high_impact=True, human_approved=True)
    assert YANTRA.authorize(approved)["authorized"] is True


def test_unapproved_read_file_denied():
    assert YANTRA.authorize(ToolAction("read_file"))["reason"] == "explicit_approval_required"


def test_safe_calculation_allowlisted():
    assert YANTRA.authorize(ToolAction("safe_calculation"))["authorized"] is True
