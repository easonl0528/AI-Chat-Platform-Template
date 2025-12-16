"""Command-line toolkit for GEO prompt优化、路由和发布管理。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from geo_optimizer.config import OptimizerConfig, load_optimizer_config
from geo_optimizer.optimizer import GeoOptimizer
from geo_optimizer.prompt_library import PromptLibrary
from geo_optimizer.publishing import PublishingBoard


def load_config(path: Optional[str]) -> OptimizerConfig:
    config_path = Path(path) if path else None
    return load_optimizer_config(config_path)


def run_optimize(prompt: str, config_path: Optional[str] = None) -> None:
    config = load_config(config_path)
    optimizer = GeoOptimizer(config)
    result = optimizer.run(prompt)

    payload = {
        "routed_provider": result.decision.provider.name,
        "routing_reason": result.decision.reason,
        "rewritten_prompt": result.prompt,
        "compliance_hits": result.compliance.hits,
        "from_cache": result.cached,
        "cached_response": result.cached_response,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_prompt_actions(args) -> None:
    library = PromptLibrary()
    if args.prompt_command == "add":
        record = library.add_prompt(
            title=args.title,
            category=args.category,
            content=args.content,
            tone=args.tone,
            tags=args.tags,
        )
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    elif args.prompt_command == "list":
        prompts = [prompt.to_dict() for prompt in library.list_prompts(category=args.category)]
        print(json.dumps(prompts, ensure_ascii=False, indent=2))
    elif args.prompt_command == "show":
        record = library.get(args.id)
        if record is None:
            raise SystemExit(f"未找到Prompt：{args.id}")
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    elif args.prompt_command == "update":
        record = library.update_prompt(args.id, args.content)
        if record is None:
            raise SystemExit(f"未找到Prompt：{args.id}")
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))


def run_publish_actions(args) -> None:
    board = PublishingBoard()
    if args.publish_command == "queue":
        task = board.queue_task(prompt_id=args.prompt_id, channel=args.channel, notes=args.notes)
        print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
    elif args.publish_command == "list":
        tasks = [task.to_dict() for task in board.list_tasks(status=args.status)]
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
    elif args.publish_command == "update":
        task = board.update_status(task_id=args.id, status=args.status)
        if task is None:
            raise SystemExit(f"未找到任务：{args.id}")
        print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
    elif args.publish_command == "stats":
        print(json.dumps(board.stats(), ensure_ascii=False, indent=2))


def build_parser():
    import argparse

    parser = argparse.ArgumentParser(description="GEO优化工具：路由、Prompt库、发布看板")

    subparsers = parser.add_subparsers(dest="command")

    preview_parser = subparsers.add_parser("preview", help="快速预览优化输出")
    preview_parser.add_argument(
        "--prompt",
        default="请写一段关于北京周末亲子活动的推荐",
        help="预览用的示例提示词，可自定义",
    )
    preview_parser.add_argument("--config", type=str, help="Path to JSON config file", default=None)

    optimize_parser = subparsers.add_parser("optimize", help="执行路由+合规优化")
    optimize_parser.add_argument("prompt_text", type=str, help="User prompt to optimize")
    optimize_parser.add_argument("--config", type=str, help="Path to JSON config file", default=None)

    prompt_parser = subparsers.add_parser("prompt", help="管理Prompt库")
    prompt_sub = prompt_parser.add_subparsers(dest="prompt_command", required=True)

    prompt_add = prompt_sub.add_parser("add", help="新增Prompt")
    prompt_add.add_argument("title")
    prompt_add.add_argument("category")
    prompt_add.add_argument("content")
    prompt_add.add_argument("--tone", default="专业/友好")
    prompt_add.add_argument("--tags", nargs="*", default=[])

    prompt_list = prompt_sub.add_parser("list", help="列出Prompt")
    prompt_list.add_argument("--category", default=None)

    prompt_show = prompt_sub.add_parser("show", help="查看单个Prompt")
    prompt_show.add_argument("id")

    prompt_update = prompt_sub.add_parser("update", help="更新Prompt内容")
    prompt_update.add_argument("id")
    prompt_update.add_argument("content")

    publish_parser = subparsers.add_parser("publish", help="模拟手动发布看板")
    publish_sub = publish_parser.add_subparsers(dest="publish_command", required=True)

    publish_queue = publish_sub.add_parser("queue", help="创建发布任务")
    publish_queue.add_argument("prompt_id")
    publish_queue.add_argument("channel", help="投放渠道，如公众号/自定义平台")
    publish_queue.add_argument("--notes", default="")

    publish_list = publish_sub.add_parser("list", help="查看任务")
    publish_list.add_argument("--status", choices=["queued", "sent", "failed"], default=None)

    publish_update = publish_sub.add_parser("update", help="更新任务状态")
    publish_update.add_argument("id")
    publish_update.add_argument("status", choices=["queued", "sent", "failed"])

    publish_stats = publish_sub.add_parser("stats", help="查看统计")

    return parser


def main() -> None:
    import sys

    parser = build_parser()
    argv = sys.argv[1:]

    if not any(arg in {"preview", "optimize", "prompt", "publish"} for arg in argv if not arg.startswith("-")):
        argv = ["optimize", *argv]

    args = parser.parse_args(argv)

    if args.command == "preview":
        run_optimize(args.prompt, config_path=getattr(args, "config", None))
    elif args.command == "optimize":
        run_optimize(args.prompt_text, config_path=getattr(args, "config", None))
    elif args.command == "prompt":
        run_prompt_actions(args)
    elif args.command == "publish":
        run_publish_actions(args)


if __name__ == "__main__":
    main()
