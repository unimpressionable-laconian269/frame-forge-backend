from __future__ import annotations

import re

from app.agents.base import ValidationResult

_DEFAULT_EXPORT = re.compile(r"export\s+default\s+", re.MULTILINE)
_FUNCTION_COMPONENT = re.compile(
    r"(?:function\s+[A-Z]\w*|const\s+[A-Z]\w*\s*=\s*(?:\([^)]*\)\s*=>|\(\s*\)\s*=>))",
    re.MULTILINE,
)
_JSX_RETURN = re.compile(r"return\s*\(?\s*<", re.MULTILINE)
_CODE_FENCE = re.compile(r"```(?:tsx|jsx|js|ts)?\n([\s\S]*?)```", re.MULTILINE)


class ValidatorAgent:
    def validate(self, raw_llm_output: str) -> ValidationResult:
        """Extract the code and run heuristic checks."""
        code = self._extract_code(raw_llm_output)
        if not code:
            return ValidationResult(valid=False, issues=["No valid code block found in LLM output."])

        issues: list[str] = []

        if not _DEFAULT_EXPORT.search(code):
            issues.append("Component is missing `export default`.")

        if not _FUNCTION_COMPONENT.search(code):
            issues.append("No named React component (PascalCase function or const) detected.")

        if not _JSX_RETURN.search(code):
            issues.append("Component does not appear to return JSX.")

        return ValidationResult(valid=len(issues) == 0, issues=issues)

    @staticmethod
    def _extract_code(raw: str) -> str:
        match = _CODE_FENCE.search(raw)
        return match.group(1).strip() if match else ""
