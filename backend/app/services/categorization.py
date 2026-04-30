"""Rule-based project → program categorization.

When a project row has an explicit `program` value, use it.
Otherwise, match the project name + description against keyword rules
to infer the right program. Falls back to "Uncategorized".

Rules are loaded from `app/config/categorization_rules.json`. Edit that
file to retune categorization without touching code.
"""
import json
import re
from pathlib import Path

_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "categorization_rules.json"


def _load_rules() -> list[dict]:
    if not _RULES_PATH.exists():
        return []
    with _RULES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


_RULES = _load_rules()


def reload_rules() -> int:
    """Re-read the rules file. Useful after editing the JSON at runtime."""
    global _RULES
    _RULES = _load_rules()
    return len(_RULES)


def categorize(project_name: str, description: str = "", portfolio: str = "") -> tuple[str, str]:
    """Return (program_name, reason).

    `reason` is one of:
      - 'keyword:<pattern>'   — matched a keyword rule
      - 'portfolio:<name>'    — matched on portfolio
      - 'fallback'            — no rule matched
    """
    haystack = " ".join([project_name or "", description or "", portfolio or ""]).lower()

    for rule in _RULES:
        for kw in rule.get("keywords", []):
            if kw.lower() in haystack:
                return rule["program"], f"keyword:{kw}"

        if portfolio and rule.get("portfolio", "").lower() == portfolio.lower():
            return rule["program"], f"portfolio:{portfolio}"

    return "Uncategorized", "fallback"
