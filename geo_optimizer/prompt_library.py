"""Prompt management inspired by multi-lane GEO tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from .storage import dump_json, load_json


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass
class PromptRecord:
    id: str
    title: str
    category: str
    content: str
    tone: str = "专业/友好"
    tags: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "content": self.content,
            "tone": self.tone,
            "tags": self.tags,
            "updated_at": self.updated_at,
        }


DEFAULT_PROMPTS: List[PromptRecord] = [
    PromptRecord(
        id="short-news",
        title="短资讯编写",
        category="短篇Prompt",
        content="请用150字以内的简体中文撰写新闻快讯，突出事实和时间。",
        tags=["快讯", "新闻"],
    ),
    PromptRecord(
        id="long-brief",
        title="通稿生成",
        category="通稿Prompt",
        content="根据要点撰写800字新闻通稿，包含背景、要点、引用与总结。",
        tags=["通稿", "长文"],
    ),
    PromptRecord(
        id="hotspot",
        title="热点联想",
        category="热点Prompt",
        content="结合最新热门话题生成3条社交媒体文案，每条不超过100字。",
        tags=["热点", "社交媒体"],
    ),
    PromptRecord(
        id="automation",
        title="自定义模板",
        category="自定义Prompt",
        content="根据提供的上下文生成可复用的模板，确保槽位使用{{slot}}形式。",
        tags=["模板", "自动化"],
    ),
]


class PromptLibrary:
    """Local prompt bank supporting categories, tags, and quick retrieval."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path("geo_data/prompts.json")
        raw = load_json(self.path, {"prompts": [p.to_dict() for p in DEFAULT_PROMPTS]})
        self.prompts: Dict[str, PromptRecord] = {
            entry["id"]: PromptRecord(**entry) for entry in raw.get("prompts", [])
        }
        self._save()

    def _save(self) -> None:
        dump_json(self.path, {"prompts": [prompt.to_dict() for prompt in self.prompts.values()]})

    def add_prompt(
        self,
        title: str,
        category: str,
        content: str,
        tone: str = "专业/友好",
        tags: Optional[List[str]] = None,
    ) -> PromptRecord:
        record = PromptRecord(
            id=str(uuid4()),
            title=title,
            category=category,
            content=content,
            tone=tone,
            tags=tags or [],
            updated_at=_now_iso(),
        )
        self.prompts[record.id] = record
        self._save()
        return record

    def list_prompts(self, category: Optional[str] = None) -> List[PromptRecord]:
        prompts = list(self.prompts.values())
        if category:
            prompts = [prompt for prompt in prompts if prompt.category == category]
        return sorted(prompts, key=lambda prompt: prompt.updated_at, reverse=True)

    def get(self, prompt_id: str) -> Optional[PromptRecord]:
        return self.prompts.get(prompt_id)

    def update_prompt(self, prompt_id: str, content: str) -> Optional[PromptRecord]:
        record = self.prompts.get(prompt_id)
        if not record:
            return None
        record.content = content
        record.updated_at = _now_iso()
        self._save()
        return record
