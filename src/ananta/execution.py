"""Sandboxed execution for a deliberately small set of low-risk ANANTA actions."""
from __future__ import annotations

import ast
import math
import operator
import re
from pathlib import Path

from .models import ToolAction
from .modules import YANTRA


class SafeCalculationError(ValueError):
    pass


class SandboxedExecutor:
    """Execute allowlisted actions; never invokes a shell or arbitrary Python."""

    _BINARY = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def __init__(self, workspace_dir: str | Path | None = None):
        self.workspace = Path(workspace_dir).resolve() if workspace_dir is not None else None

    @classmethod
    def _calculate_node(cls, node: ast.AST, depth: int = 0):
        if depth > 24:
            raise SafeCalculationError("expression_too_complex")
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SafeCalculationError("only_numeric_constants_allowed")
            return value
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls._UNARY:
            return cls._UNARY[type(node.op)](cls._calculate_node(node.operand, depth + 1))
        if isinstance(node, ast.BinOp) and type(node.op) in cls._BINARY:
            left = cls._calculate_node(node.left, depth + 1)
            right = cls._calculate_node(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and (abs(right) > 12 or abs(left) > 1_000_000):
                raise SafeCalculationError("exponent_or_base_limit_exceeded")
            result = cls._BINARY[type(node.op)](left, right)
            if isinstance(result, (int, float)):
                if isinstance(result, int) and result.bit_length() > 256:
                    raise SafeCalculationError("integer_result_too_large")
                if isinstance(result, float) and (not math.isfinite(result) or abs(result) > 1e100):
                    raise SafeCalculationError("numeric_result_out_of_range")
            return result
        raise SafeCalculationError("unsupported_expression_syntax")

    @classmethod
    def calculate(cls, expression: str):
        if not isinstance(expression, str) or not expression.strip() or len(expression) > 512:
            raise SafeCalculationError("valid_expression_required")
        try:
            tree = ast.parse(expression, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > 64:
                raise SafeCalculationError("expression_too_complex")
            return cls._calculate_node(tree.body)
        except SafeCalculationError:
            raise
        except (SyntaxError, ArithmeticError, OverflowError, TypeError, ValueError) as exc:
            raise SafeCalculationError("calculation_failed") from exc

    def _write_report(self, title: str, content: str) -> dict:
        if self.workspace is None:
            raise RuntimeError("workspace_dir_required_for_local_report")
        if len(title) > 160 or len(content) > 20_000:
            raise ValueError("report_title_or_content_too_long")
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "report"
        report_dir = (self.workspace / "reports").resolve()
        if self.workspace not in report_dir.parents:
            raise ValueError("report_path_outside_workspace")
        report_dir.mkdir(parents=True, exist_ok=True)
        destination = (report_dir / f"{slug}.md").resolve()
        if report_dir not in destination.parents:
            raise ValueError("report_path_outside_workspace")
        temporary = destination.with_suffix(".md.tmp")
        temporary.write_text(f"# {title.strip()}\n\n{content}", encoding="utf-8")
        temporary.replace(destination)
        return {"executed": True, "action": "local_report", "path": str(destination.relative_to(self.workspace))}

    def execute(self, action: ToolAction, *, emergency_stop: bool = False) -> dict:
        decision = YANTRA.authorize(action, emergency_stop=emergency_stop)
        if not decision["authorized"]:
            return {"executed": False, "decision": decision}
        if action.name == "safe_calculation":
            try:
                result = self.calculate(action.payload["expression"])
                return {"executed": True, "action": action.name, "result": result}
            except SafeCalculationError as exc:
                return {"executed": False, "action": action.name, "error": str(exc)}
        if action.name == "local_report":
            try:
                return self._write_report(action.payload.get("title", ""), action.payload.get("content", ""))
            except (OSError, RuntimeError, ValueError) as exc:
                return {"executed": False, "action": action.name, "error": str(exc)}
        return {"executed": False, "decision": {"authorized": False, "reason": "execution_adapter_not_implemented"}}
