"""Flask backend + static frontend for the GEO 优化工具."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, request, send_from_directory

from geo_optimizer.config import (
    DEFAULT_CONFIG,
    OptimizerConfig,
    ProviderConfig,
    RoutePolicy,
    load_optimizer_config,
)
from geo_optimizer.optimizer import GeoOptimizer
from geo_optimizer.prompt_library import PromptLibrary
from geo_optimizer.publishing import PublishingBoard

STATIC_DIR = Path(__file__).resolve().parent / "geo_optimizer" / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

prompt_library = PromptLibrary()
publishing_board = PublishingBoard()


def create_app() -> Flask:
    """Factory mainly for packaging/entrypoint use."""

    return app


def _build_config(payload: Dict[str, object]) -> OptimizerConfig:
    """Construct an optimizer config from request payload or defaults."""

    config_raw = payload.get("config")
    if config_raw is None:
        return load_optimizer_config(None)

    providers = [ProviderConfig.from_dict(entry) for entry in config_raw.get("providers", [])]
    policy_raw = config_raw.get("policy", DEFAULT_CONFIG["policy"])
    policy = RoutePolicy(**policy_raw)

    return OptimizerConfig(
        providers=providers or [ProviderConfig.from_dict(entry) for entry in DEFAULT_CONFIG["providers"]],
        policy=policy,
        enable_cache=config_raw.get("enable_cache", True),
        cache_ttl_seconds=config_raw.get("cache_ttl_seconds", 120),
        enable_compliance_checks=config_raw.get("enable_compliance_checks", True),
        enable_rewrites=config_raw.get("enable_rewrites", True),
    )


@app.post("/api/optimize")
def optimize_prompt():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt 字段不能为空"}), 400

    config = _build_config(data)
    optimizer = GeoOptimizer(config)

    try:
        result = optimizer.run(prompt)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "routed_provider": result.decision.provider.name,
            "routing_reason": result.decision.reason,
            "rewritten_prompt": result.prompt,
            "compliance_hits": result.compliance.hits,
            "from_cache": result.cached,
            "cached_response": result.cached_response,
        }
    )


@app.get("/api/prompts")
def list_prompts():
    category = request.args.get("category")
    prompts = [prompt.to_dict() for prompt in prompt_library.list_prompts(category=category)]
    return jsonify(prompts)


@app.post("/api/prompts")
def add_prompt():
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title")
    category = data.get("category")
    content = data.get("content")
    if not title or not category or not content:
        return jsonify({"error": "title/category/content 为必填项"}), 400

    record = prompt_library.add_prompt(
        title=title,
        category=category,
        content=content,
        tone=data.get("tone", "专业/友好"),
        tags=data.get("tags", []),
    )
    return jsonify(record.to_dict()), 201


@app.get("/api/prompts/<prompt_id>")
def get_prompt(prompt_id: str):
    record = prompt_library.get(prompt_id)
    if record is None:
        return jsonify({"error": "未找到对应 Prompt"}), 404
    return jsonify(record.to_dict())


@app.patch("/api/prompts/<prompt_id>")
def update_prompt(prompt_id: str):
    data = request.get_json(force=True, silent=True) or {}
    content = data.get("content")
    if not content:
        return jsonify({"error": "content 字段不能为空"}), 400

    record = prompt_library.update_prompt(prompt_id, content)
    if record is None:
        return jsonify({"error": "未找到对应 Prompt"}), 404
    return jsonify(record.to_dict())


@app.get("/api/publish")
def list_publish_tasks():
    status = request.args.get("status")
    tasks = [task.to_dict() for task in publishing_board.list_tasks(status=status)]
    return jsonify(tasks)


@app.post("/api/publish")
def queue_publish_task():
    data = request.get_json(force=True, silent=True) or {}
    prompt_id = data.get("prompt_id")
    channel = data.get("channel")
    if not prompt_id or not channel:
        return jsonify({"error": "prompt_id 与 channel 为必填项"}), 400

    task = publishing_board.queue_task(prompt_id=prompt_id, channel=channel, notes=data.get("notes", ""))
    return jsonify(task.to_dict()), 201


@app.patch("/api/publish/<task_id>")
def update_publish_task(task_id: str):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get("status")
    if status not in {"queued", "sent", "failed"}:
        return jsonify({"error": "status 需为 queued/sent/failed"}), 400

    task = publishing_board.update_status(task_id=task_id, status=status)
    if task is None:
        return jsonify({"error": "未找到对应任务"}), 404
    return jsonify(task.to_dict())


@app.get("/api/publish/stats")
def publish_stats():
    return jsonify(publishing_board.stats())


@app.get("/")
def index():
    static_dir = Path(app.static_folder)
    return send_from_directory(static_dir, "index.html")


def main() -> None:
    """Start the built-in web server."""

    app.run(host="0.0.0.0", port=8000, debug=False)


if __name__ == "__main__":
    main()
