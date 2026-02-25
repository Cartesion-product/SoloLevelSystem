# Solo Leveling System / 我独自升级系统

> AI Agent 驱动的智能面试辅导与职业成长伴侣平台

一个基于 LangGraph 多 Agent 协作的模拟面试系统。通过上传简历和目标岗位 JD，系统自动进行"守城-攻城"两阶段模拟面试，实时评估能力 Gap，生成个性化学习任务，帮助求职者持续提升面试表现。

---

## Features

- **智能简历解析** — 上传 PDF/Word 简历，LLM 自动结构化解析（5 套岗位模板）
- **多 Agent 协作面试** — Strategist（策略家）、Interviewer（面试官）、Evaluator（评估者）三节点实时协作
- **SSE 流式对话** — 面试对话逐字流式输出，体验接近真实对话
- **动态难度调节** — 根据回答质量自动调整难度和面试官语气（温和 Mentor ↔ 严肃 Tech Lead）
- **三层记忆架构** — 热层 Redis / 温层 PostgreSQL / 冷层 Qdrant，模拟人类记忆分层
- **技能树管理** — 自动从简历/JD 生成技能树，面试验证后动态更新评分
- **任务驱动学习** — 基于 Gap 自动生成学习任务，支持多种验收方式
- **个人知识库** — 上传技术文档，自动分片向量化，面试时智能检索
- **心理画像分析** — 异步分析情绪模式，生成每日个性化激励语
- **成长看板** — 技能雷达图、能力曲线、任务进度一目了然

## Tech Stack

| 类别 | 选型 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| Agent 编排 | LangGraph + LangChain |
| LLM | 可插拔架构（OpenAI / DeepSeek，配置切换） |
| 关系型数据库 | PostgreSQL 16 |
| 向量数据库 | Qdrant |
| 缓存 | Redis 7 |
| 异步任务 | Celery + Redis |
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia |
| 数据库迁移 | Alembic |
| 部署 | Docker Compose |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                      │
│         Element Plus  /  Pinia  /  Vue Router            │
└──────────────────────────┬──────────────────────────────┘
                           │  REST + SSE
┌──────────────────────────▼──────────────────────────────┐
│                   FastAPI Gateway                        │
│              JWT Auth  /  CORS  /  SSE                   │
├─────────────────────────────────────────────────────────┤
│              LangGraph Agent Orchestration               │
│                                                         │
│   ┌──────────┐   ┌─────────────┐   ┌──────────┐        │
│   │Strategist│──▶│ Interviewer │──▶│Evaluator │──┐     │
│   │ (策略家) │   │  (面试官)   │   │ (评估者) │  │     │
│   └──────────┘   └─────────────┘   └──────────┘  │     │
│        ▲                                          │     │
│        └──────────────────────────────────────────┘     │
│                                                         │
│   异步节点 (Celery):                                     │
│   ┌───────────────┐   ┌─────────────┐                   │
│   │PsychoAnalyst  │   │ QuestMaster │                   │
│   │ (心理分析师)  │   │ (任务大师)  │                   │
│   └───────────────┘   └─────────────┘                   │
├─────────────────────────────────────────────────────────┤
│                    Domain Layer (DDD)                    │
│   Interview域  /  Capability域  /  Knowledge域  /  Growth域 │
├───────────┬───────────────┬─────────────────────────────┤
│ PostgreSQL│    Qdrant     │          Redis               │
│  (温层)   │   (冷层)      │          (热层)              │
└───────────┴───────────────┴─────────────────────────────┘
```

## Project Structure

```
SoloLevelSystem/
├── app/
│   ├── main.py                     # FastAPI 入口
│   ├── config.py                   # Pydantic Settings 配置
│   ├── dependencies.py             # JWT 认证等依赖注入
│   │
│   ├── api/                        # 接入层
│   │   ├── v1/
│   │   │   ├── auth.py             # 注册/登录/设置
│   │   │   ├── resumes.py          # 简历 CRUD + 上传解析
│   │   │   ├── jobs.py             # 目标岗位管理
│   │   │   ├── interviews.py       # 模拟面试 + SSE 流式对话
│   │   │   ├── skills.py           # 技能树查询
│   │   │   ├── quests.py           # 学习任务管理
│   │   │   ├── knowledge.py        # 知识库上传/管理
│   │   │   └── growth.py           # 成长看板
│   │   └── schemas/                # Pydantic 请求/响应模型
│   │
│   ├── domain/                     # 领域层 (DDD)
│   │   ├── interview/              # 面试域: User, Resume, TargetJob, Session
│   │   ├── capability/             # 能力域: SkillTree
│   │   ├── knowledge/              # 知识域: KnowledgeDocument
│   │   └── growth/                 # 成长域: Quest, PsychologyProfile, MoodLog
│   │
│   ├── agents/                     # 编排层 (LangGraph)
│   │   ├── graph.py                # 状态机主图定义
│   │   ├── state.py                # InterviewState 类型
│   │   ├── nodes/                  # Agent 节点实现
│   │   │   ├── strategist.py       # 策略家 — 决策引擎
│   │   │   ├── interviewer.py      # 面试官 — 问题生成
│   │   │   ├── evaluator.py        # 评估者 — 隐式评分
│   │   │   ├── psycho_analyst.py   # 心理分析师 (异步)
│   │   │   └── quest_master.py     # 任务大师 (异步)
│   │   └── prompts/                # Prompt 模板
│   │
│   ├── infrastructure/             # 基础设施层
│   │   ├── database.py             # SQLAlchemy async 引擎
│   │   ├── cache.py                # Redis 客户端
│   │   ├── vector_store.py         # Qdrant 客户端
│   │   ├── llm_provider.py         # LLM Provider (OpenAI/DeepSeek)
│   │   ├── embedding.py            # Embedding 服务
│   │   └── file_parser.py          # PDF/Word 文件解析
│   │
│   └── tasks/                      # Celery 异步任务
│       ├── celery_app.py
│       ├── post_interview.py       # 面试后处理 (摘要/心理/任务/向量化)
│       └── knowledge_indexing.py   # 知识库文档分片向量化
│
├── alembic/                        # 数据库迁移
│   └── versions/
│       └── 001_initial_schema.py   # 9 张核心表
│
├── frontend/                       # Vue 3 前端
│   ├── src/
│   │   ├── api/                    # Axios 封装 + SSE 客户端
│   │   ├── stores/                 # Pinia 状态管理
│   │   ├── router/                 # Vue Router + 路由守卫
│   │   └── views/                  # 页面组件
│   │       ├── LoginView.vue       # 登录/注册
│   │       ├── LayoutView.vue      # 侧边栏布局
│   │       ├── DashboardView.vue   # 成长看板
│   │       ├── InterviewView.vue   # 模拟面试对话
│   │       ├── ResumesView.vue     # 简历管理
│   │       ├── JobsView.vue        # 目标岗位
│   │       ├── SkillsView.vue      # 技能树
│   │       ├── QuestsView.vue      # 学习任务
│   │       └── KnowledgeView.vue   # 知识库
│   └── package.json
│
├── scripts/
│   └── db_manage.py               # 数据库初始化/迁移管理脚本
│
├── tests/                          # 测试
│   ├── conftest.py
│   └── test_auth.py
│
├── docker-compose.yml              # 容器编排
├── Dockerfile
├── requirements.txt
├── .env.example
└── pytest.ini
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose（推荐，可一键启动所有基础设施）

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/SoloLevelSystem.git
cd SoloLevelSystem

# 复制环境变量模板并填写
cp .env.example .env
```

编辑 `.env`，**必须修改**的配置项：

```bash
# 选择 LLM Provider (openai 或 deepseek)
LLM_PROVIDER=openai

# 填写你的 API Key
OPENAI_API_KEY=sk-your-actual-key

# 生产环境务必更换
SECRET_KEY=your-random-secret-key
```

### 2. 启动方式

#### 方式 A: Docker Compose 一键启动（推荐）

```bash
# 启动全部服务 (PostgreSQL, Redis, Qdrant, API, Celery Worker)
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f app
```

服务启动后：
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

#### 方式 B: 本地开发（手动启动）

**Step 1 — 启动基础设施**

```bash
# 仅启动数据库服务
docker compose up -d postgres redis qdrant
```

**Step 2 — 后端**

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（自动建库 + 执行全部迁移）
python scripts/db_manage.py init

# 启动 API 服务
uvicorn app.main:app --reload --port 8000

# 另开终端，启动 Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info
```

**Step 3 — 前端**

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器: http://localhost:3000（自动代理 `/api` 到后端 8000 端口）

### 3. 数据库管理

所有数据库操作通过 `scripts/db_manage.py` 统一管理：

```bash
# 初始化：自动创建数据库 + 执行全部迁移
python scripts/db_manage.py init

# 执行待迁移（升级到最新版本）
python scripts/db_manage.py migrate

# 回滚 1 个版本
python scripts/db_manage.py rollback

# 回滚 N 个版本
python scripts/db_manage.py rollback 3

# 查看当前迁移状态
python scripts/db_manage.py status

# 基于 Model 变更自动生成新迁移文件
python scripts/db_manage.py create "add xxx table"

# 重置数据库（删除全部表并重新迁移，危险操作需确认）
python scripts/db_manage.py reset
```

## API Endpoints

启动后访问 http://localhost:8000/docs 查看完整的 Swagger 文档。

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/register` | 用户注册 |
| `POST` | `/api/auth/login` | 用户登录，返回 JWT |
| `PUT` | `/api/users/settings` | 更新用户设置 |
| `POST` | `/api/resumes` | 上传简历（multipart），触发 LLM 解析 |
| `GET` | `/api/resumes` | 简历列表 |
| `GET/PUT/DELETE` | `/api/resumes/{id}` | 简历 CRUD |
| `POST` | `/api/resumes/{id}/set-default` | 设置默认简历 |
| `POST` | `/api/jobs` | 创建目标岗位，自动解析 JD |
| `GET` | `/api/jobs` | 岗位列表 |
| `POST` | `/api/jobs/{id}/set-default` | 设置默认岗位 |
| `POST` | `/api/interviews/start` | 开始模拟面试 |
| `POST` | `/api/interviews/{id}/chat` | 发送消息，**SSE 流式**返回 |
| `POST` | `/api/interviews/{id}/end` | 结束面试 |
| `GET` | `/api/interviews/{id}/report` | 获取面试报告 |
| `GET` | `/api/skills/tree` | 获取技能树 |
| `GET` | `/api/quests` | 任务列表（支持 `?status=` 过滤） |
| `PUT` | `/api/quests/{id}/status` | 更新任务状态 |
| `POST` | `/api/knowledge/upload` | 上传知识文档 |
| `GET` | `/api/knowledge/documents` | 文档列表 |
| `DELETE` | `/api/knowledge/documents/{id}` | 删除文档及向量 |
| `GET` | `/api/growth/dashboard` | 成长看板 |

## Core Workflow

```
用户注册/登录
    │
    ▼
上传简历 (PDF/Word) ──▶ LLM 结构化解析 ──▶ 初始化技能树
    │
    ▼
创建目标岗位 (JD) ──▶ LLM 提取技能要求 ──▶ 检测 Gap 技能
    │
    ▼
开始模拟面试
    │
    ├──▶ Strategist 决策: 守城/攻城/难度/话题
    │       │
    │       ▼
    ├──▶ Interviewer 提问: 动态语气 + SSE 流式
    │       │
    │       ▼
    ├──▶ 用户回答
    │       │
    │       ▼
    ├──▶ Evaluator 隐式评分 + Gap 识别
    │       │
    │       ▼
    └──── 循环直到结束
            │
            ▼
    生成面试报告 (评分/亮点/弱点)
            │
            ▼ (Celery 异步)
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
  心理分析  任务生成  向量化存储
  更新画像  更新技能树 写入 Qdrant
```

## LLM Configuration

系统支持 OpenAI 和 DeepSeek 两个 Provider，通过环境变量切换：

**使用 OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o
# 可选: 使用代理
# OPENAI_BASE_URL=https://your-proxy.com/v1
```

**使用 DeepSeek:**
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
```

Embedding Provider 独立配置，支持 OpenAI / DeepSeek / **Ollama**，可以与 LLM Provider 不同：

**使用 OpenAI Embedding:**
```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**使用 Ollama 本地 Embedding（无需 API Key，离线可用）:**
```bash
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text    # 或 mxbai-embed-large, bge-m3 等
EMBEDDING_DIMENSION=768              # 需与所选模型的输出维度一致
OLLAMA_BASE_URL=http://localhost:11434
```

> 使用 Ollama 前需先拉取模型：`ollama pull nomic-embed-text`
>
> 常见 Ollama Embedding 模型与维度：
>
> | 模型 | 维度 | 说明 |
> |------|------|------|
> | `nomic-embed-text` | 768 | 轻量高效，推荐 |
> | `mxbai-embed-large` | 1024 | 更高精度 |
> | `bge-m3` | 1024 | 多语言支持好 |
> | `snowflake-arctic-embed` | 1024 | 高质量检索 |
>
> **注意：** 更换 Embedding 模型后，`EMBEDDING_DIMENSION` 必须同步修改，且 Qdrant 中已有的 collection 需要删除重建（维度不匹配会报错）。

## Database Schema

系统包含 9 张核心表：

| 表名 | 说明 |
|------|------|
| `users` | 用户账号与设置 |
| `resumes` | 简历（含 `parsed_data` JSONB 结构化数据） |
| `target_jobs` | 目标岗位（含 `parsed_requirements` JSONB） |
| `skill_tree` | 技能树（自引用树形结构，0-10 评分） |
| `interview_sessions` | 面试会话（含 `summary` JSONB 报告） |
| `quest_log` | 学习任务日志 |
| `user_psychology_profile` | 心理画像（性格标签/自信指数/激励语） |
| `mood_log` | 情绪日志 |
| `knowledge_documents` | 知识库文档元数据 |

Qdrant 向量集合：

| Collection | 说明 |
|------------|------|
| `knowledge_chunks` | 知识文档切片向量 |
| `conversation_memory` | 有价值的对话片段向量 |

## Testing

```bash
# 运行全部测试
pytest

# 带覆盖率
pytest --cov=app

# 只跑认证测试
pytest tests/test_auth.py -v
```

> 测试使用 SQLite 内存数据库，无需启动 PostgreSQL。

## Environment Variables Reference

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `SECRET_KEY` | `change-me-in-production` | JWT 签名密钥 |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL 连接串 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接串 |
| `QDRANT_HOST` | `localhost` | Qdrant 地址 |
| `QDRANT_PORT` | `6333` | Qdrant 端口 |
| `LLM_PROVIDER` | `openai` | LLM 提供商 (`openai` / `deepseek`) |
| `OPENAI_API_KEY` | — | OpenAI API Key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI 模型 |
| `OPENAI_BASE_URL` | — | OpenAI 代理地址（可选） |
| `DEEPSEEK_API_KEY` | — | DeepSeek API Key |
| `DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek 模型 |
| `EMBEDDING_PROVIDER` | `openai` | Embedding 提供商 (`openai` / `deepseek` / `ollama`) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding 模型名称 |
| `EMBEDDING_DIMENSION` | `1536` | 向量维度（需与模型输出维度一致） |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery Broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery Backend |
| `UPLOAD_DIR` | `uploads` | 文件上传目录 |
| `MAX_UPLOAD_SIZE_MB` | `20` | 最大上传文件大小 |

## License

MIT
