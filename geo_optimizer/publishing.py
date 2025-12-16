"""Manual publish board and KPI stats similar to GEO dashboards."""

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
class PublishTask:
    id: str
    prompt_id: str
    channel: str
    status: str = "queued"  # queued | sent | failed
    scheduled_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "channel": self.channel,
            "status": self.status,
            "scheduled_at": self.scheduled_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
        }


class PublishingBoard:
    """Queue publish tasks and provide quick KPI-style aggregates."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path("geo_data/publish_tasks.json")
        raw = load_json(self.path, {"tasks": []})
        self.tasks: Dict[str, PublishTask] = {
            entry["id"]: PublishTask(**entry) for entry in raw.get("tasks", [])
        }
        self._save()

    def _save(self) -> None:
        dump_json(self.path, {"tasks": [task.to_dict() for task in self.tasks.values()]})

    def queue_task(self, prompt_id: str, channel: str, notes: str = "") -> PublishTask:
        task = PublishTask(id=str(uuid4()), prompt_id=prompt_id, channel=channel, notes=notes)
        self.tasks[task.id] = task
        self._save()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[PublishTask]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [task for task in tasks if task.status == status]
        return sorted(tasks, key=lambda task: task.scheduled_at, reverse=True)

    def update_status(self, task_id: str, status: str) -> Optional[PublishTask]:
        if status not in {"queued", "sent", "failed"}:
            raise ValueError("Invalid status; use queued, sent, or failed")
        task = self.tasks.get(task_id)
        if not task:
            return None
        task.status = status
        task.updated_at = _now_iso()
        self._save()
        return task

    def stats(self) -> Dict[str, object]:
        total = len(self.tasks)
        by_status: Dict[str, int] = {"queued": 0, "sent": 0, "failed": 0}
        by_channel: Dict[str, int] = {}
        for task in self.tasks.values():
            by_status[task.status] = by_status.get(task.status, 0) + 1
            by_channel[task.channel] = by_channel.get(task.channel, 0) + 1
        return {"total_tasks": total, "by_status": by_status, "by_channel": by_channel}
