# GEO 优化工具（面向中国大陆大模型）

本项目提供一个可直接运行的 GEO 优化工具，用于在中国大陆环境下对接本土大模型（如豆包、文心一言、通义千问等）。它实现了路由、合规、提示词重写、缓存、Prompt 管理与手动发布看板等核心能力，帮助你快速落地低延迟、高可靠的多模型调用方案；同时提供可运行的 Web 前端/后端示例（`server.py` + `static/`），并给出了打包为 Windows EXE 的指令。

## 功能概览
- **多模型路由**：基于延迟、成功率与成本的评分机制，自动选择最优可用的模型端点。
- **合规与脱敏**：内置手机号、身份证号、邮箱等敏感信息掩码；包含高风险关键词拦截与提示词重写。
- **缓存与复用**：可选的 TTL 缓存，加速热门问题的响应；命中缓存时直接返回结果。
- **可配置**：支持通过 JSON 配置文件自定义提供商、路由权重以及缓存和合规策略。
- **命令行演示**：`app.py` 提供快速演示入口，可输出路由决策、重写后的提示词及合规命中信息。
- **Prompt 库与发布看板**：内置类似「文播 GEO」的分类 Prompt、快速新增/更新，并提供发布任务队列与统计。

## 快速开始
1. 安装 Python 3.9+。
2. 克隆仓库后，直接运行演示脚本：
   ```bash
   python app.py "请帮我介绍北京的周末亲子活动"
   ```
3. 如需自定义配置，提供 JSON 文件并通过 `--config` 参数传入：
   ```bash
   python app.py "手机号13812345678需要掩码" --config custom_config.json
   ```

### 安装为可执行工具（pip）
1. 在项目根目录安装：
   ```bash
   pip install .
   ```
2. 之后即可在任意目录使用命令行：
   ```bash
   geo-optimizer "写一段周末亲子活动"      # 默认执行 optimize
   geo-optimizer preview --prompt "写一段上海美食探店脚本"
   geo-optimizer prompt list
   geo-optimizer publish stats
   ```

### 运行 Web 前端 + 后端
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：
   ```bash
   python server.py           # 或 geo-optimizer-web
   ```
   默认监听 `http://0.0.0.0:8000`。
3. 打开浏览器访问 `http://localhost:8000/`，即可在前端界面体验路由、合规、Prompt 库与发布队列。

**可用 API**（均返回 JSON）：
- `POST /api/optimize`：请求体 `{ "prompt": "..." }`
- `GET /api/prompts`、`POST /api/prompts`、`PATCH /api/prompts/<id>`
- `GET /api/publish`、`POST /api/publish`、`PATCH /api/publish/<id>`、`GET /api/publish/stats`

### 打包为 Windows EXE（可安装分发）
1. Windows 环境安装 Python 3.9+，再执行：
   ```powershell
   pip install -r requirements-dev.txt
   ```
2. 一键打包（自动携带前端静态文件与 geo_data 目录）：
   ```powershell
   python -m installer.build_exe
   ```
   - 生成文件位于 `dist/geo-optimizer/geo-optimizer.exe`，可直接运行。
   - 如需自定义输出目录：`python -m installer.build_exe --dist-path release`
3. 打包后的 EXE 仍然会在 8000 端口暴露 Web UI，双击启动即可访问 `http://localhost:8000/`。

### 预览示例输出
不带其他参数直接运行快速预览，或替换自定义提示词：
```bash
python app.py preview
python app.py preview --prompt "写一段上海美食探店脚本"
```

## 配置格式示例（路由）
```json
{
  "providers": [
    {
      "name": "doubao",
      "endpoint": "https://api.doubao.com/chat",
      "latency_ms": 220,
      "success_rate": 0.97,
      "cost_per_1k_tokens": 0.8,
      "supports_streaming": true
    },
    {
      "name": "wenxinyiyan",
      "endpoint": "https://wenxin.baidu.com/chat",
      "latency_ms": 280,
      "success_rate": 0.95,
      "cost_per_1k_tokens": 0.6,
      "supports_streaming": true
    }
  ],
  "policy": {
    "latency_weight": 0.45,
    "success_weight": 0.35,
    "cost_weight": 0.2
  },
  "enable_cache": true,
  "cache_ttl_seconds": 90,
  "enable_compliance_checks": true,
  "enable_rewrites": true
}
```

## Prompt 库与发布看板用法

### 列出现有 Prompt（已内置短篇/通稿/热点/自定义）
```bash
python app.py prompt list
```

### 按分类筛选 Prompt
```bash
python app.py prompt list --category "短篇Prompt"
```

### 新增或查看单个 Prompt
```bash
python app.py prompt add "节日祝福" "节日Prompt" "为春节写一条祝福语" --tags 春节 喜庆
python app.py prompt show <prompt_id>
```

### 更新 Prompt 内容
```bash
python app.py prompt update <prompt_id> "改成更适合抖音的口语化风格"
```

### 发布任务看板：创建、查看、统计
```bash
# 创建任务（手动发布）
python app.py publish queue <prompt_id> "公众号" --notes "周更栏目"

# 查看队列或按状态过滤
python app.py publish list
python app.py publish list --status sent

# 更新状态并查看 KPI 统计
python app.py publish update <task_id> sent
python app.py publish stats
```

## 目录结构
- `geo_optimizer/config.py`：配置模型提供商与路由策略，并包含默认配置。
- `geo_optimizer/router.py`：根据延迟、成功率、成本计算得分并挑选最佳提供商。
- `geo_optimizer/compliance.py`：敏感信息脱敏、关键词阻断与提示词重写。
- `geo_optimizer/cache.py`：简单的内存 TTL 缓存实现。
- `geo_optimizer/optimizer.py`：编排合规、路由、缓存等逻辑，给出优化结果。
- `geo_optimizer/prompt_library.py`：本地 Prompt 库，内置多分类模板，可新增/更新/筛选。
- `geo_optimizer/publishing.py`：发布任务看板与统计，支持队列、状态更新与渠道维度聚合。
- `geo_optimizer/storage.py`：简单的 JSON 持久化工具。
- `app.py`：命令行入口，覆盖路由演示、Prompt 管理与发布看板操作。

## 开发提示
- 默认配置内置常见大陆模型，可根据实际测得的延迟、成功率和成本调整参数。
- 如需扩展审计、RAG 等高级能力，可在 `optimizer.py` 中串联新组件或暴露钩子。

## 许可证
本项目基于 MIT 许可证发布，可自由使用与二次开发。
