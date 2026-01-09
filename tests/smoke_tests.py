"""Lightweight self-test script for GEO 优化工具.

Runs in-memory checks for routing/compliance, prompt library operations,
and publishing board stats without external API dependencies.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from geo_optimizer.compliance import run_compliance_pipeline
from geo_optimizer.config import load_optimizer_config
from geo_optimizer.optimizer import GeoOptimizer
from geo_optimizer.prompt_library import PromptLibrary
from geo_optimizer.publishing import PublishingBoard


def run_optimizer_checks() -> dict:
    config = load_optimizer_config(None)
    optimizer = GeoOptimizer(config)
    prompt = "测试手机号13812345678"

    output = optimizer.run(prompt)
    assert "<phone_redacted>" in output.prompt, "手机号应被脱敏"

    optimizer.record_response(output.prompt, "OK")
    cached = optimizer.run(prompt)
    assert cached.cached, "缓存应在第二次命中"
    assert cached.cached_response == "OK", "缓存内容应与写入一致"

    return {
        "routed_provider": output.decision.provider.name,
        "score": round(output.decision.score, 3),
        "masked_prompt": output.prompt,
        "cached": cached.cached,
    }


def run_prompt_library_checks() -> dict:
    with TemporaryDirectory() as tmp:
        store = Path(tmp) / "prompts.json"
        library = PromptLibrary(store)
        created = library.add_prompt(
            "测试模板",
            "自定义Prompt",
            "请生成一条关于杭州美食的短文案",
            tags=["测试", "美食"],
        )
        fetched = library.get(created.id)
        library.update_prompt(created.id, "请生成两条关于杭州美食的短文案")
        filtered = library.list_prompts("自定义Prompt")

        assert fetched is not None, "新增的 Prompt 应可读取"
        assert any(prompt.id == created.id for prompt in filtered), "筛选应包含新增项"

        return {
            "created_id": created.id,
            "category_count": len(filtered),
            "updated_content": library.get(created.id).content,
        }


def run_publishing_checks() -> dict:
    with TemporaryDirectory() as tmp:
        store = Path(tmp) / "publish.json"
        board = PublishingBoard(store)
        task = board.queue_task("prompt-1", "公众号", notes="测试任务")
        board.update_status(task.id, "sent")
        stats = board.stats()

        assert stats["by_status"]["sent"] == 1, "状态统计应记录已发送任务"

        return {
            "task_id": task.id,
            "status": board.tasks[task.id].status,
            "by_channel": stats["by_channel"],
        }


def run_compliance_checks() -> dict:
    masked = run_compliance_pipeline("请联系我，手机号13812345678")
    risky = run_compliance_pipeline("请讨论暴力相关的话题", enable_rewrite=False)

    assert masked.rejected is False, "脱敏后的请求应通过"
    assert masked.filtered_text != "请联系我，手机号13812345678", "应替换敏感信息"
    assert risky.rejected is True, "高风险关键词应被拒绝"

    return {
        "masked": masked.filtered_text,
        "risky_rejected": risky.rejected,
    }


def main() -> None:
    results = {
        "optimizer": run_optimizer_checks(),
        "prompt_library": run_prompt_library_checks(),
        "publishing": run_publishing_checks(),
        "compliance": run_compliance_checks(),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
