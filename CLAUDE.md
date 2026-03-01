# Solo Leveling System - Project Memory

> AI 面试辅导与职业成长平台，LangGraph 多 Agent 协作模拟面试系统。
> 详细信息见项目根目录 README.md，本文件仅记录快速上下文和开发经验。

## 项目概览

- **定位**: 上传简历 + 目标岗位 JD → 多 Agent 模拟面试 → 实时评估能力 Gap → 生成学习任务
- **当前版本**: v1.0（初版代码已提交）
- **v2 设计文档**: `design-doc/v2/` — 引入 Workspace 概念、Prompt 插件化、Plan-Execute-Observe 循环（尚未实现）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + Uvicorn, Python 3.12+ |
| Agent | LangGraph 0.2.60 + LangChain 0.3.14 |
| LLM | 可插拔: OpenAI (gpt-4o) / DeepSeek |
| Embedding | 可插拔: OpenAI / DeepSeek / Ollama |
| 关系 DB | PostgreSQL 16 + SQLAlchemy async + Alembic |
| 向量 DB | Qdrant |
| 缓存 | Redis 7 |
| 异步任务 | Celery + Redis |
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia |
| 部署 | Docker Compose |

## 架构分层

```
Frontend (Vue3) → REST + SSE → FastAPI Gateway (JWT/CORS)
                                    ↓
                        LangGraph Agent 编排层
                   Strategist → Interviewer → Evaluator (循环)
                   异步: PsychoAnalyst, QuestMaster (Celery)
                                    ↓
                        Domain Layer (DDD 四个域)
                   Interview / Capability / Knowledge / Growth
                                    ↓
                        Infrastructure Layer
                   PostgreSQL(温层) / Redis(热层) / Qdrant(冷层)
```

## 目录结构要点

- `app/main.py` — FastAPI 入口
- `app/config.py` — Pydantic Settings，`.env` 驱动
- `app/dependencies.py` — JWT 认证依赖注入
- `app/api/v1/` — 路由: auth, resumes, jobs, interviews, skills, quests, knowledge, growth
- `app/api/schemas/` — Pydantic 请求/响应模型
- `app/domain/` — DDD 领域层（models, service, repository）
- `app/agents/` — LangGraph: graph.py(主图), state.py, nodes/(5个节点), prompts/
- `app/infrastructure/` — database, cache, vector_store, llm_provider, embedding, file_parser
- `app/tasks/` — Celery: post_interview, knowledge_indexing
- `alembic/versions/` — 3 个迁移文件 (001_initial, 002_parsing_status, 003_skill_advice)
- `frontend/src/` — Vue 页面: Login, Layout, Dashboard, Interview, Resumes, Jobs, Skills, Quests, Knowledge
- `scripts/db_manage.py` — 数据库初始化/迁移管理

## 数据库 (9 张表 + 2 个向量集合)

- **users** — 用户账号与设置
- **resumes** — 简历 (parsed_data JSONB)
- **target_jobs** — 目标岗位 (parsed_requirements JSONB)
- **skill_tree** — 技能树 (自引用树形, 0-10 评分)
- **interview_sessions** — 面试会话 (summary JSONB)
- **quest_log** — 学习任务
- **user_psychology_profile** — 心理画像
- **mood_log** — 情绪日志
- **knowledge_documents** — 知识库文档元数据
- Qdrant: `knowledge_chunks`, `conversation_memory`

## 核心业务流程

1. 注册/登录 → JWT
2. 上传简历 (PDF/Word) → LLM 结构化解析 → 初始化技能树
3. 创建目标岗位 (JD) → LLM 提取技能要求 → 检测 Gap
4. 开始面试 → Strategist(策略) → Interviewer(提问/SSE流式) → 用户回答 → Evaluator(隐式评分) → 循环
5. 结束面试 → 生成报告 → Celery 异步: 心理分析 + 任务生成 + 向量化存储
6. 成长看板: 技能雷达图、能力曲线、任务进度

## 开发约定

- 测试用 SQLite 内存数据库，无需启动 PostgreSQL: `pytest`
- 本地开发: `docker compose up -d postgres redis qdrant` 启动基础设施
- 数据库管理统一用: `python scripts/db_manage.py [init|migrate|rollback|status|create|reset]`
- 配置全部通过 `.env` 管理，参考 `.env.example`
- LLM/Embedding Provider 通过环境变量切换，支持热插拔

## 开发经验与踩坑记录

> 随着迭代持续更新此部分

### 已知问题
- `nul` 文件是 Windows 误创建的空文件，可忽略
- `frontend/node_modules/` 未被 gitignore（已在 untracked 中）

### v2 演进方向 (design-doc/v2)
- 引入 User Workspace 概念（Agent 写，用户读）
- Prompt 三层插件化: base → mode → target（后层覆盖前层）
- Plan-Execute-Observe 循环替代当前的 Strategist-Interviewer-Evaluator 循环
- 数据库可能从 PostgreSQL 迁移到 MongoDB（v2 设计文档中提到）
- 训练模式细分: behavioral / technical / system_design / hr
