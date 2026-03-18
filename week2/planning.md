### 第 2 周：架构深度游，吃透 RAG + Agent Workflow

这周决定你是不是“工程师”，不是“提示词玩家”。

**主线一：RAG**

- 文档切块策略
- metadata 设计
- dense + sparse hybrid retrieval
- rerank
- 引用回溯
- 评测集构造

Qdrant 和 Milvus 现在都在强调 hybrid retrieval；这意味着你做作品集时，别再只做“纯向量召回”了，要把 BM25/稀疏检索也放进去。([Milvus][10])

**主线二：Agent 框架**

- 主学 LangGraph
- 对比 CrewAI
- 用 LlamaIndex 接检索与 workflow
- 明确 state、node、edge、memory、tool、checkpoint 的边界

**本周输出物**

1. `rag-eval-lab`
   展示不同 chunk、retrieval、rerank 方案对 groundedness / recall 的影响。

2. `langgraph-agent-playground`
   展示：
   - 单 Agent
   - 多工具
   - 条件分支
   - 循环重试
   - 人工确认节点

**简历加分话术**

> 具备从检索增强到工作流编排的完整落地经验，能够基于状态图设计可追踪、可回放、可扩展的 Agent 执行链路。

More Advanced version:

> 独立完成 RAG 实验平台与 Agent Workflow Playground 搭建，系统比较 chunking、dense/sparse hybrid retrieval、rerank 与 citation 追溯策略对 recall 与 groundedness 的影响；基于 LangGraph 设计具备条件分支、循环重试、人工确认与 checkpoint 能力的状态图执行链路，并对比 CrewAI 在多智能体协作与流程编排场景下的适用边界。

---
