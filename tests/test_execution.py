import pytest

from ananta import ToolAction
from ananta.execution import SafeCalculationError, SandboxedExecutor


def test_safe_calculation_arithmetic():
    assert SandboxedExecutor.calculate("(12 + 8) * 3") == 60


@pytest.mark.parametrize("expression", [
    "__import__('os').system('echo unsafe')",
    "open('/etc/passwd').read()",
    "x + 1",
    "[1, 2, 3]",
    "2 ** 1000",
])
def test_safe_calculation_rejects_unsafe_or_unbounded_syntax(expression):
    with pytest.raises(SafeCalculationError):
        SandboxedExecutor.calculate(expression)


def test_safe_calculation_division_by_zero_is_reported():
    result = SandboxedExecutor().execute(ToolAction("safe_calculation", {"expression": "1 / 0"}))
    assert result["executed"] is False


def test_executor_denies_unknown_action():
    result = SandboxedExecutor().execute(ToolAction("shell"))
    assert result["executed"] is False
    assert result["decision"]["reason"] == "action_not_allowlisted"


def test_executor_honors_emergency_stop():
    result = SandboxedExecutor().execute(
        ToolAction("safe_calculation", {"expression": "2 + 2"}), emergency_stop=True
    )
    assert result["executed"] is False
    assert result["decision"]["reason"] == "emergency_stop_active"


def test_local_report_writes_only_inside_workspace(tmp_path):
    result = SandboxedExecutor(tmp_path).execute(
        ToolAction("local_report", {"title": "Daily Status", "content": "All checks recorded."})
    )
    assert result["executed"] is True
    report = tmp_path / "reports" / "daily-status.md"
    assert report.exists()
    assert report.read_text(encoding="utf-8") == "# Daily Status\n\nAll checks recorded."


def test_local_report_requires_workspace():
    result = SandboxedExecutor().execute(
        ToolAction("local_report", {"title": "Status", "content": "Text"})
    )
    assert result["executed"] is False
    assert "workspace_dir_required" in result["error"]


def test_read_file_is_not_yet_executable_even_if_authorized():
    result = SandboxedExecutor().execute(
        ToolAction("read_file", {"path": "notes.txt"}, human_approved=True)
    )
    assert result["executed"] is False
    assert result["decision"]["reason"] == "execution_adapter_not_implemented"
