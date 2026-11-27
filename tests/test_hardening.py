import sqlite3
import pytest

from ananta import AnantaController, Claim, Evidence, TaskRequest, ToolAction
from ananta.audit import AuditLedger
from ananta.models import EvidenceGrade
from ananta.modules import PRAMANA, RITA, SAKSHI, VAK, YANTRA


@pytest.mark.parametrize("value", [None, 1, [], {}])
def test_request_text_requires_string(value):
    with pytest.raises(TypeError):
        TaskRequest(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_task_id_rejects_blank(value):
    with pytest.raises(ValueError):
        TaskRequest("hello", task_id=value)


def test_request_length_limit():
    with pytest.raises(ValueError, match="exceeds"):
        TaskRequest("x" * 10001)


def test_language_must_be_nonempty():
    with pytest.raises(ValueError):
        TaskRequest("hello", language=" ")


def test_vak_rejects_wrong_object():
    with pytest.raises(TypeError):
        VAK.parse("hello")


def test_vak_trims_text():
    assert VAK.parse(TaskRequest("  hello  "))["text"] == "hello"


@pytest.mark.parametrize("text", ["", "  "])
def test_claim_rejects_blank_text(text):
    with pytest.raises(ValueError):
        Claim(text)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_claim_confidence_bounds(confidence):
    with pytest.raises(ValueError):
        Claim("claim", confidence=confidence)


@pytest.mark.parametrize("confidence", [True, "0.5"])
def test_claim_confidence_type(confidence):
    with pytest.raises(TypeError):
        Claim("claim", confidence=confidence)


def test_claim_rejects_non_tuple_evidence():
    with pytest.raises(ValueError):
        Claim("claim", evidence=[])


def test_claim_rejects_wrong_evidence_member():
    with pytest.raises(TypeError):
        Claim("claim", evidence=("source",))


def test_evidence_requires_source():
    with pytest.raises(ValueError):
        Evidence(" ", EvidenceGrade.A)


def test_evidence_requires_enum_grade():
    with pytest.raises(TypeError):
        Evidence("source", "A")


def test_tool_payload_requires_dict():
    with pytest.raises(TypeError):
        ToolAction("local_report", payload=[])


def test_tool_payload_rejects_non_json_values():
    with pytest.raises(ValueError):
        ToolAction("local_report", payload={"bad": object()})


def test_tool_payload_rejects_nan():
    with pytest.raises(ValueError):
        ToolAction("local_report", payload={"bad": float("nan")})


def test_tool_payload_size_limit():
    with pytest.raises(ValueError, match="exceeds"):
        ToolAction("local_report", payload={"content": "x" * 17000})


def test_action_flags_must_be_boolean():
    with pytest.raises(TypeError):
        ToolAction("local_report", high_impact=1)


def test_unknown_action_denied():
    assert YANTRA.authorize(ToolAction("shell"))["reason"] == "action_not_allowlisted"


def test_emergency_stop_denies_allowlisted_action():
    result = YANTRA.authorize(ToolAction("local_report"), emergency_stop=True)
    assert result == {"authorized": False, "reason": "emergency_stop_active"}


def test_read_file_requires_approval():
    assert YANTRA.authorize(ToolAction("read_file", {"path": "notes.txt"}))["authorized"] is False


def test_read_file_requires_path():
    result = YANTRA.authorize(ToolAction("read_file", human_approved=True))
    assert result["reason"] == "valid_path_required"


@pytest.mark.parametrize("path", ["../secret", "a/../../secret", "/etc/passwd", "\\server\\share"])
def test_read_file_blocks_paths_outside_workspace(path):
    result = YANTRA.authorize(ToolAction("read_file", {"path": path}, human_approved=True))
    assert result["reason"] == "path_outside_workspace"


def test_read_file_accepts_relative_path_with_approval():
    result = YANTRA.authorize(ToolAction("read_file", {"path": "docs/notes.txt"}, human_approved=True))
    assert result["authorized"] is True


def test_action_rejects_unknown_payload_keys():
    result = YANTRA.authorize(ToolAction("local_report", {"command": "rm -rf"}))
    assert result["reason"] == "payload_has_unknown_fields"


def test_calculation_requires_expression():
    assert YANTRA.authorize(ToolAction("safe_calculation"))["reason"] == "valid_expression_required"


def test_calculation_expression_length_limited():
    result = YANTRA.authorize(ToolAction("safe_calculation", {"expression": "x" * 513}))
    assert result["reason"] == "valid_expression_required"


def test_local_report_rejects_non_string_fields():
    result = YANTRA.authorize(ToolAction("local_report", {"title": 3}))
    assert result["reason"] == "report_fields_must_be_strings"


def test_high_impact_requires_approval():
    assert YANTRA.authorize(ToolAction("local_report", high_impact=True))["authorized"] is False


def test_dependency_planner_returns_topological_order():
    order = RITA.topological_order({"c": ["b"], "b": ["a"], "a": []})
    assert order.index("a") < order.index("b") < order.index("c")


def test_dependency_planner_rejects_cycle():
    with pytest.raises(ValueError, match="cycle"):
        RITA.topological_order({"a": ["b"], "b": ["a"]})


def test_dependency_planner_rejects_unknown_dependency():
    with pytest.raises(ValueError, match="unknown-dependency"):
        RITA.topological_order({"a": ["missing"]})


def test_dependency_cycle_detection_handles_long_chain_without_recursion():
    graph = {f"n{i}": ([f"n{i-1}"] if i else []) for i in range(1600)}
    assert RITA.check_dependencies(graph) == []


def test_dependency_graph_rejects_non_dict():
    with pytest.raises(TypeError):
        RITA.check_dependencies([])


def test_dependency_graph_reports_invalid_prerequisites():
    assert "invalid-prerequisites:a" in RITA.check_dependencies({"a": "b"})


def test_pramana_source_attachment_is_not_proof():
    item = Evidence("unverified webpage", EvidenceGrade.A)
    result = PRAMANA.assess(Claim("claim", (item,)))
    assert result["status"] == "SUPPORTED_SOURCE_ATTACHED"
    assert "not proof" in result["verification_note"]


def test_pramana_confidence_never_claimed_calibrated():
    result = PRAMANA.assess(Claim("claim", confidence=0.9))
    assert result["confidence_is_calibrated"] is False


def test_sakshi_rejects_invalid_claim_collection():
    with pytest.raises(TypeError):
        SAKSHI.review(["not a claim"])


def test_controller_rejects_invalid_claim_collection():
    with pytest.raises(TypeError):
        AnantaController().process(TaskRequest("x"), ["bad"])


def test_audit_returns_defensive_copy():
    engine = AnantaController()
    engine.process(TaskRequest("hello"))
    audit = engine.audit()
    audit[0]["details"]["task_id"] = "tampered"
    assert engine.audit()[0]["details"]["task_id"] == "task-001"


def test_audit_events_have_unique_ids_and_timestamps():
    engine = AnantaController()
    engine.process(TaskRequest("hello"))
    events = engine.audit()
    assert events[0]["event_id"] != events[1]["event_id"]
    assert events[0]["timestamp"]


def test_emergency_stop_requires_owner_confirmation():
    engine = AnantaController()
    result = engine.set_emergency_stop(True)
    assert result["changed"] is False
    assert engine.emergency_stop is False


def test_emergency_stop_can_be_enabled_with_confirmation():
    engine = AnantaController()
    assert engine.set_emergency_stop(True, owner_confirmed=True)["changed"] is True
    assert engine.authorize_action(ToolAction("local_report"))["authorized"] is False


def test_emergency_stop_can_be_released_with_confirmation():
    engine = AnantaController()
    engine.set_emergency_stop(True, owner_confirmed=True)
    engine.set_emergency_stop(False, owner_confirmed=True)
    assert engine.authorize_action(ToolAction("local_report"))["authorized"] is True


def test_ephemeral_audit_discloses_non_durable_mode():
    result = AnantaController().verify_audit()
    assert result["mode"] == "ephemeral"
    assert "not durable" in result["note"]


def test_sqlite_audit_persists_after_reopen(tmp_path):
    path = str(tmp_path / "audit.db")
    first = AnantaController(audit_db_path=path)
    first.process(TaskRequest("persistent"))
    expected = first.audit()
    first.close()
    second = AnantaController(audit_db_path=path)
    assert second.audit() == expected
    second.close()


def test_sqlite_audit_hash_chain_verifies(tmp_path):
    ledger = AuditLedger(str(tmp_path / "ledger.db"))
    ledger.append("event", {"value": 1})
    ledger.append("event", {"value": 2})
    assert ledger.verify()["verified"] is True
    ledger.close()


def test_sqlite_audit_detects_tampering(tmp_path):
    path = str(tmp_path / "tamper.db")
    ledger = AuditLedger(path)
    ledger.append("event", {"value": 1})
    ledger.connection.execute("UPDATE audit_events SET details_json='{}'")
    ledger.connection.commit()
    assert ledger.verify()["verified"] is False
    ledger.close()


def test_sqlite_audit_has_monotonic_hash_links(tmp_path):
    ledger = AuditLedger(str(tmp_path / "chain.db"))
    ledger.append("one", {})
    ledger.append("two", {})
    rows = ledger.read_all()
    assert rows[0]["previous_hash"] == "GENESIS"
    assert rows[1]["previous_hash"] == rows[0]["event_hash"]
    ledger.close()


def test_controller_audits_denied_action():
    engine = AnantaController()
    engine.authorize_action(ToolAction("unknown"))
    assert engine.audit()[-1]["event"] == "tool_action_decision"


def test_result_identity_is_defensively_copied():
    engine = AnantaController()
    result = engine.process(TaskRequest("hello"))
    result["system"]["system"] = "tampered"
    assert engine.process(TaskRequest("again"))["system"]["system"] == "ANANTA"
