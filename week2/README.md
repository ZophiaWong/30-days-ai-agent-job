## Goals

拿出一套面试时能现场解释的工程证据链：

1. 能解释为什么纯向量召回不够，还要加 sparse/BM25 和 rerank
2. 能解释 chunk、metadata、citation、eval 之间的关系
3. 能把 Agent 讲成一个**状态机/工作流系统**。
4. 能区分清楚 `state / node / edge / tool / memory / checkpoint`。
   1. LangGraph 官方堆土的核心抽象就是 state、node、edge
   2. 而 thread 级短期记忆依赖 checkpointer，并通过 `thread_id` 做恢复和隔离

## Artifacts(Planning)

- 一个仓库：rag-eval-lab
- 一个仓库：langgraph-agent-playground
- 一份实验报告：week2_report.md
- 一张图：architecture_overview.png

## Daily Notes

### Day 1 - “AI agent / RAG engineering docs” 小语料库

1. 语料来源
   | source_id | topic | 类型 | 数量 |
   | --------------- | -------------- | ---- | --- |
   | langgraph_docs | agent_workflow | 官方文档 | ~15 |
   | llamaindex_docs | rag_ingestion | 官方文档 | ~15 |
   | qdrant_docs | retrieval | 官方文档 | ~15 |

2. 抓取方式
   1. 自定义 crawler `python scripts/crawl_docs.py`
   2. 策略：
      1. 从 `seed_urls` 开始
      2. 仅抓取指定前缀（防止跑出站点）
      3. 每个 source 限制最大文档数（防止数据爆炸）
      4. 保存两份数据：原始 HTML（用于回溯）、清洗后的 Markdown（用于后续处理）
3. 清洗规则
   1. 优先提取：`<main>、<article>、[role="main"]`
   2. fallback：`<body>`
   3. 使用 markdownify 转换为 Markdown
   4. 保留：标题结构（`# / ## / ###`）、列表、代码块
   5. 不保证完全去除：导航栏、页脚
      > 当前目标是：可读、可检索、可切块，而不是完美还原页面
4. metadata 字段
   1. 文档存储在 `metadata/documents.jsonl`
5. 当前限制
   1. PDF 未处理
   2. `created_at` 不完整
   3. section 仍为粗粒
   4. 页面噪音仍然存在：部分导航/页脚仍存在

### Day2 -
