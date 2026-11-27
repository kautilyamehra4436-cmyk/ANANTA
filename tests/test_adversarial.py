import math
import random

import pytest

from ananta import ToolAction
from ananta.execution import SafeCalculationError, SandboxedExecutor
from ananta.modules import RITA


@pytest.mark.parametrize("expression", [
    "9" * 512,
    "-" + "9" * 512,
    "1e999",
    "1e999 + 0",
    "1e99 * 100",
    "2 ** 13",
    "1000001 ** 1",
    "True + 1",
    "False",
])
def test_calculator_rejects_out_of_policy_numbers(expression):
    with pytest.raises(SafeCalculationError):
        SandboxedExecutor.calculate(expression)


@pytest.mark.parametrize(("expression", "expected"), [
    ("0", 0),
    ("-0", 0),
    ("2 ** 12", 4096),
    ("1e100", 1e100),
    ("(12 + 8) * 3", 60),
    ("7 // 2", 3),
    ("7 % 2", 1),
    ("-(-5)", 5),
])
def test_calculator_accepts_bounded_numeric_cases(expression, expected):
    assert SandboxedExecutor.calculate(expression) == expected


def test_calculator_rejects_non_finite_constant():
    with pytest.raises(SafeCalculationError, match="numeric_result_out_of_range"):
        SandboxedExecutor.calculate("1e999")


def test_calculator_rejects_non_finite_intermediate():
    with pytest.raises(SafeCalculationError):
        SandboxedExecutor.calculate("1e99 * 100")


def test_calculator_rejects_excessive_ast_depth_or_size():
    expression = "+".join(["1"] * 40)
    with pytest.raises(SafeCalculationError):
        SandboxedExecutor.calculate(expression)


def test_calculator_division_by_zero_is_a_controlled_failure():
    result = SandboxedExecutor().execute(ToolAction("safe_calculation", {"expression": "1 / 0"}))
    assert result["executed"] is False
    assert result["error"] == "calculation_failed"


def test_report_temp_symlink_cannot_write_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    reports = workspace / "reports"
    reports.mkdir(parents=True)
    outside = tmp_path / "outside.txt"
    outside.write_text("unchanged", encoding="utf-8")
    (reports / "daily-status.md.tmp").symlink_to(outside)

    result = SandboxedExecutor(workspace).execute(
        ToolAction("local_report", {"title": "Daily Status", "content": "safe"})
    )
    assert result["executed"] is True
    assert outside.read_text(encoding="utf-8") == "unchanged"
    assert (reports / "daily-status.md.tmp").is_symlink()


def test_report_destination_symlink_is_replaced_not_followed(tmp_path):
    workspace = tmp_path / "workspace"
    reports = workspace / "reports"
    reports.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("unchanged", encoding="utf-8")
    (reports / "daily-status.md").symlink_to(outside)

    result = SandboxedExecutor(workspace).execute(
        ToolAction("local_report", {"title": "Daily Status", "content": "safe"})
    )
    assert result["executed"] is True
    assert outside.read_text(encoding="utf-8") == "unchanged"
    assert not (reports / "daily-status.md").is_symlink()


@pytest.mark.parametrize("graph", [
    {"a": [[]]},
    {"a": [None]},
    {"a": [1]},
    {"a": [""]},
])
def test_dependency_graph_rejects_malformed_prerequisite_entries(graph):
    errors = RITA.check_dependencies(graph)
    assert any(error.startswith("invalid-prerequisite:") for error in errors)
    with pytest.raises(ValueError, match="invalid dependency graph"):
        RITA.topological_order(graph)


def test_dependency_graph_handles_large_linear_chain():
    size = 5000
    graph = {f"n{i}": ([f"n{i-1}"] if i else []) for i in range(size)}
    order = RITA.topological_order(graph)
    assert len(order) == size
    assert order[0] == "n0"
    assert order[-1] == f"n{size-1}"


def test_dependency_graph_handles_diamond_and_deterministic_order():
    graph = {"d": ["b", "c"], "c": ["a"], "b": ["a"], "a": []}
    first = RITA.topological_order(graph)
    second = RITA.topological_order(graph)
    assert first == second
    assert first.index("a") < first.index("b")
    assert first.index("a") < first.index("c")
    assert first.index("b") < first.index("d")
    assert first.index("c") < first.index("d")


def test_dependency_graph_random_dags_respect_every_edge():
    rng = random.Random(7319)
    for _ in range(50):
        size = rng.randint(2, 35)
        graph = {f"n{i:02d}": [] for i in range(size)}
        for i in range(size):
            graph[f"n{i:02d}"] = [
                f"n{j:02d}" for j in range(i) if rng.random() < 0.12
            ]
        order = RITA.topological_order(graph)
        positions = {node: index for index, node in enumerate(order)}
        for node, prerequisites in graph.items():
            for prerequisite in prerequisites:
                assert positions[prerequisite] < positions[node]


def test_dependency_graph_detects_long_cycle_without_recursion():
    size = 3000
    graph = {f"n{i}": [f"n{(i - 1) % size}"] for i in range(size)}
    errors = RITA.check_dependencies(graph)
    assert any(error.startswith("cycle:") for error in errors)


def test_report_content_is_written_exactly_and_overwrites_atomically(tmp_path):
    executor = SandboxedExecutor(tmp_path)
    action = ToolAction("local_report", {"title": "Status", "content": "first"})
    assert executor.execute(action)["executed"] is True
    second = executor.execute(ToolAction("local_report", {"title": "Status", "content": "second"}))
    assert second["executed"] is True
    assert (tmp_path / "reports" / "status.md").read_text(encoding="utf-8") == "# Status\n\nsecond"


def test_calculator_random_bounded_integer_arithmetic_matches_python():
    rng = random.Random(2048)
    for _ in range(200):
        left = rng.randint(-1_000_000, 1_000_000)
        right = rng.randint(-1_000_000, 1_000_000)
        expression = f"({left}) * ({right}) + ({left})"
        assert SandboxedExecutor.calculate(expression) == left * right + left
