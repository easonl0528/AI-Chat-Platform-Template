"""Simple compliance and privacy filters."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


SENSITIVE_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("phone", re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")),
    (
        "id_card",
        re.compile(r"(?<!\d)(\d{6})(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)"),
    ),
    ("email", re.compile(r"[\w.-]+@[\w.-]+\.[A-Za-z]{2,6}")),
]

PROHIBITED_KEYWORDS = ["暴力", "恐怖", "赌博", "政治"]


@dataclass
class ComplianceResult:
    filtered_text: str
    hits: Dict[str, List[str]]
    rejected: bool


def mask_sensitive(text: str) -> ComplianceResult:
    hits: Dict[str, List[str]] = {key: [] for key, _ in SENSITIVE_PATTERNS}
    filtered = text
    for key, pattern in SENSITIVE_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            hits[key] = [m.group(0) for m in matches]
            for match in matches:
                span = match.span()
                replacement = f"<{key}_redacted>"
                filtered = filtered[: span[0]] + replacement + filtered[span[1] :]
    rejected = any(keyword in text for keyword in PROHIBITED_KEYWORDS)
    return ComplianceResult(filtered_text=filtered, hits=hits, rejected=rejected)


def rewrite_prompt(text: str) -> str:
    """Basic rewrite to improve safety and clarity for mainland Chinese LLMs."""

    text = text.strip()
    if not text:
        return text

    if any(keyword in text for keyword in PROHIBITED_KEYWORDS):
        return "该问题可能涉及不合规内容，请提供其他话题。"

    if not text.endswith("？") and not text.endswith("?"):
        text += "？"

    return f"请用简体中文、客观中立地回答：{text}"


def run_compliance_pipeline(text: str, enable_rewrite: bool = True) -> ComplianceResult:
    masked = mask_sensitive(text)
    if enable_rewrite and not masked.rejected:
        rewritten = rewrite_prompt(masked.filtered_text)
        return ComplianceResult(filtered_text=rewritten, hits=masked.hits, rejected=False)
    return masked
