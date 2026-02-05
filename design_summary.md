# 《我独自升级系统》- AI面试智能体系统设计总结

> **版本**: v1.0  
> **日期**: 2024-02-05  
> **状态**: 架构设计阶段

---

## 一、项目概述

### 1.1 核心定位
基于LLM和多Agent技术的智能面试陪练系统，通过个性化的对话式训练，帮助求职者提升面试能力。

### 1.2 核心价值
- **智能陪练**: AI学习伙伴式的友好交互，非严肃考官
- **全量记忆**: 一人一库，持续积累用户数据
- **个性化训练**: 基于用户画像和历史表现的针对性提问
- **成长可视化**: 技能树、学习计划、进步追踪

### 1.3 目标用户
- **主要用户**: 准备AI应用开发岗位面试的求职者
- **初期规模**: 个人使用，单用户深度验证

---

## 二、技术架构

### 2.1 技术栈选型

```
┌─────────────────────────────────────────────┐
│  前端层: React/Vue + WebSocket               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  API层: FastAPI (REST + WebSocket)           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Agent层: LangChain + LangGraph              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │决策Agent │→ │分析Agent │→ │总结Agent │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ↓
┌──────────────┬──────────────┬──────────────┐
│ PostgreSQL   │   Qdrant     │    Redis     │
│ (结构化数据) │  (向量检索)   │   (缓存)     │
└──────────────┴──────────────┴──────────────┘
```

| 技术组件 | 选型 | 理由 |
|---------|------|------|
| **后端框架** | FastAPI | 高性能异步、原生WebSocket支持 |
| **LLM编排** | LangChain + LangGraph | 成熟的Agent框架、状态机支持 |
| **关系数据库** | PostgreSQL | JSONB字段支持、成熟稳定 |
| **向量数据库** | Qdrant | 语义检索、过滤能力强 |
| **缓存** | Redis | 会话管理、热数据缓存 |
| **LLM API** | OpenAI/通用Provider | 多模态支持、灵活切换 |

### 2.2 核心设计原则

1. **分层记忆架构**: 避免全量加载，分层检索
2. **JSONB灵活存储**: 适应复杂数据结构，便于扩展
3. **Agent职责解耦**: 每个Agent专注单一职责
4. **异步优先**: 耗时任务异步处理，提升体验

---

## 三、分层记忆架构（核心创新）

### 3.1 记忆层级设计

```
┌─────────────────────────────────────────────────┐
│ Layer 1: 短期记忆 (Session Memory)              │
│ • 存储: Redis (TTL 1小时)                        │
│ • 内容: 当前会话完整对话                          │
│ • 用途: 实时上下文                                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: 工作记忆 (Working Memory)              │
│ • 存储: PostgreSQL                               │
│ • 内容: 最近3次面试的压缩摘要                     │
│ • 用途: "上次vs这次"对比                          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: 长期记忆 (Long-term Memory)            │
│ • 存储: PostgreSQL + Qdrant                      │
│ • 内容: 所有历史面试的结构化数据                  │
│ • 用途: 语义检索相关片段                          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Layer 4: 知识库 (Knowledge Base)                │
│ • 存储: Qdrant                                   │
│ • 内容: 向量化的用户知识、面经、文档              │
│ • 用途: 混合检索增强生成                          │
└─────────────────────────────────────────────────┘
```

### 3.2 上下文构建策略

**Prompt中的信息优先级**:
1. 当前会话（最近10轮对话）- **完整加载**
2. 当前学习计划和进度 - **完整加载**
3. 最近3次面试摘要 - **压缩加载**（每次1-2句话）
4. 语义相关历史 - **Top-K检索**（只要5条最相关）
5. 用户画像核心信息 - **精简加载**（只列前5个技能）

**Token控制目标**: 单次Prompt控制在 2000-3000 tokens以内

---

## 四、数据库设计

### 4.1 PostgreSQL核心表结构

#### 表关系图

```
users (用户表)
  ↓
  ├─→ resumes (简历表)
  │     • 支持多简历，有is_default标识
  │     • parsed_data (JSONB) 存储解析结果
  │     • extracted_skills (TEXT[]) 快速匹配
  │
  ├─→ job_descriptions (岗位JD表)
  │     • 关联resume_id形成配对
  │     • match_analysis (JSONB) 存储匹配结果
  │
  ├─→ interview_sessions (面试会话表)
  │     • 关联resume_id和jd_id
  │     • round_number追踪第N次面试
  │     • summary (JSONB) 存储总结报告
  │     ↓
  │     └─→ conversations (对话记录表)
  │           • sequence_number保证顺序
  │           • metadata (JSONB) 存储评分、话题
  │
  ├─→ learning_plans (学习计划表)
  │     • 关联session_id，知道计划来源
  │     • completed_tasks (JSONB) 追踪进度
  │     • progress (0-100) 完成百分比
  │
  ├─→ skill_assessments (技能评估表)
  │     • skill_path构建技能树层级
  │     • score_change追踪进步
  │     • assessment_data (JSONB) 详细评估
  │
  ├─→ interview_meetings (真实面试记录表)
  │     • parsed_content (JSONB) 结构化内容
  │     • synced_to_knowledge标记同步状态
  │
  └─→ user_knowledge_base (用户知识库元数据表)
        • source_type和source_id追溯来源
        • vector_id关联Qdrant
        • access_count实现LRU策略
```

#### 关键设计特点

| 设计点 | 说明 | 优势 |
|-------|------|------|
| **JSONB字段** | 存储复杂嵌套结构 | 灵活扩展、避免频繁改表 |
| **时间戳索引** | 所有表都有created_at/updated_at | 快速查询近期数据 |
| **版本管理** | is_default、round_number等 | 支持多版本、追踪变化 |
| **TEXT数组** | 技能列表、标签 | GIN索引、快速搜索 |
| **关联设计** | 外键+ON DELETE策略 | 数据一致性保证 |

### 4.2 核心表字段详解

#### users (用户表)
```sql
id, username, email, password_hash
settings (JSONB) - 用户偏好设置，如{"auto_update_knowledge": false}
created_at, updated_at, last_login, is_active
```

#### resumes (简历表)
```sql
id, user_id, title, target_position
original_filename, file_url, file_type
parsed_data (JSONB) - 完整的解析结果
extracted_skills (TEXT[]) - ["Python", "FastAPI", ...]
version, is_default - 版本控制
parse_status, parse_error - 异步解析状态
created_at, updated_at
```

**parsed_data结构示例**:
```json
{
  "basic_info": {
    "name": "张三",
    "education": [{"school": "XX大学", "degree": "本科", ...}]
  },
  "work_experience": [...],
  "projects": [...],
  "skills": {
    "programming": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"]
  }
}
```

#### interview_sessions (面试会话表)
```sql
id, user_id, resume_id, jd_id
session_type - "mock"(模拟) / "real"(真实)
status - "ongoing"/"completed"/"paused"/"cancelled"
start_time, end_time, duration_seconds
round_number - 第几次面试，用于"上次vs这次"
metadata (JSONB) - Agent配置、用户情绪等
summary (JSONB) - 面试总结报告
knowledge_updated, knowledge_updated_at - 知识库同步标记
created_at, updated_at
```

**summary结构示例**:
```json
{
  "overall_score": 7.5,
  "dimensions": {
    "technical_skills": 8.0,
    "communication": 7.0,
    "problem_solving": 7.5
  },
  "strengths": ["项目经验丰富", "技术理解深入"],
  "weaknesses": ["表达不够简洁", "缺少某些技术点"],
  "improvement_suggestions": ["建议学习XX", "多练习YY"]
}
```

#### conversations (对话记录表)
```sql
id, session_id, role, content
sequence_number - 对话顺序
metadata (JSONB) - 消息类型、话题、评分、用时
created_at
```

#### learning_plans (学习计划表)
```sql
id, user_id, session_id, title, description
plan_data (JSONB) - 完整的学习计划
progress (0-100) - 完成进度
status - "active"/"completed"/"archived"
completed_tasks (JSONB) - 已完成的任务列表
start_date, target_end_date, actual_end_date
created_at, updated_at
```

**plan_data结构示例**:
```json
{
  "goals": {
    "short_term": ["1周内掌握XX"],
    "mid_term": ["1月内完成YY"],
    "long_term": ["3月内达到某水平"]
  },
  "learning_paths": [
    {
      "topic": "LangChain基础",
      "priority": "high",
      "resources": ["官方文档", "教程链接"],
      "estimated_hours": 10,
      "tasks": ["阅读文档", "完成练习"]
    }
  ],
  "milestones": [
    {"title": "完成XX", "deadline": "2024-03-01", "completed": false}
  ]
}
```

#### skill_assessments (技能评估表)
```sql
id, user_id, session_id
skill_name, skill_category, skill_path - 技能信息
assessment_data (JSONB) - 详细评估数据
previous_score, score_change - 进步追踪
assessed_at, created_at, updated_at
UNIQUE(session_id, skill_name) - 每次面试对每个技能只评估一次
```

**assessment_data结构示例**:
```json
{
  "level": "intermediate",
  "score": 7.5,
  "confidence": 0.8,
  "evidence": ["能够独立开发API", "理解异步编程"],
  "gaps": ["缺少性能优化经验"],
  "assessed_by": "interview_session",
  "last_practiced": "2024-02-01"
}
```

### 4.3 Qdrant向量数据库设计

#### 集合1: user_memories（用户记忆向量）

```python
{
  "collection_name": "user_memories",
  "vector_size": 1536,  # text-embedding-3-large
  "distance": "Cosine",
  "payload": {
    "user_id": str,           # 用户ID
    "source_type": str,       # conversation/summary/skill/experience
    "source_id": str,         # 源记录ID
    "content": str,           # 文本内容
    "timestamp": int,         # Unix时间戳
    "importance": float,      # 重要性评分 0-10
    "metadata": dict          # 其他元数据
  }
}
```

**向量化内容**:
- 每条重要对话（问题+回答组合）
- 每次面试的总结摘要
- 技能评估的证据描述
- 项目经验的详细描述

**检索策略**:
```python
# 查询时带过滤条件
filter_conditions = {
  "must": [
    {"key": "user_id", "match": {"value": user_id}},
    {"key": "importance", "range": {"gte": 7.0}}  # 只检索重要记忆
  ],
  "should": [
    {"key": "source_type", "match": {"value": "summary"}},  # 优先总结
    {"key": "timestamp", "range": {"gte": recent_timestamp}}  # 优先近期
  ]
}
```

#### 集合2: general_knowledge（通用知识库）

```python
{
  "collection_name": "general_knowledge",
  "vector_size": 1536,
  "payload": {
    "category": str,      # interview_question/concept/best_practice
    "skill_area": str,    # Python/FastAPI/LangChain等
    "difficulty": str,    # beginner/intermediate/advanced
    "content": str,       # 知识内容
    "source": str         # 知识来源
  }
}
```

### 4.4 Redis缓存设计

```python
# 键设计模式
{
  # 当前会话对话历史
  "session:{session_id}:messages": "list",  # TTL 1小时
  
  # 用户近期记忆摘要
  "user:{user_id}:recent_memory": "string",  # JSON, TTL 30分钟
  
  # 简历解析结果缓存
  "resume:{resume_id}:parsed": "string",  # JSON, TTL 1天
  
  # LLM响应缓存
  "llm:cache:{query_hash}": "string",  # JSON, TTL 1周
}
```

---

## 五、多Agent工作流设计

### 5.1 Agent架构图

```
┌─────────────────────────────────────────────────┐
│              Interview State (状态)              │
│  • user_profile (用户画像)                       │
│  • recent_memory (近期记忆)                      │
│  • learning_plan (学习计划)                      │
│  • messages (对话历史)                           │
│  • skill_assessments (技能评估)                  │
│  • interview_round (当前轮次)                    │
└─────────────────────────────────────────────────┘
                    ↓
         ┌──────────────────────┐
         │   Decision Agent     │ ← 决策者：控制流程
         │   (决策者)           │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  Question Generator  │ ← 生成个性化问题
         │  (问题生成)          │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  Wait User Answer    │ ← 等待用户输入
         │  (等待输入)          │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  User Analysis       │ ← 分析回答质量
         │  (用户分析)          │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  Summary Agent       │ ← 生成总结报告
         │  (面试总结)          │
         └──────────────────────┘
```

### 5.2 Agent职责定义

#### 1. Decision Agent（决策者）
**职责**:
- 决定下一步做什么（继续提问/总结/结束）
- 选择话题方向和难度
- 控制面试节奏

**输入**: 
- 当前状态（已进行轮次、对话历史）
- 用户画像
- 学习计划

**输出**:
- 下一个话题
- 难度级别
- 是否继续标识

**决策逻辑**:
```
如果 round >= max_rounds:
    → 进入总结阶段
否则:
    基于学习计划 + 历史表现 → 选择下一话题
    基于技能评估 → 确定难度
```

#### 2. Question Generator Agent（问题生成）
**职责**:
- 生成个性化面试问题
- 根据用户回答进行追问

**输入**:
- 当前话题
- 用户简历亮点
- 检索到的参考问题

**输出**:
- 友好自然的面试问题

**生成策略**:
```
1. 从Qdrant检索相关问题
2. 结合用户简历定制问题
3. 保持"AI学习伙伴"的友好语气
4. 避免生硬的"考试式"提问
```

#### 3. User Analysis Agent（用户分析）
**职责**:
- 评估用户回答质量
- 更新技能评估
- 识别情绪和性格

**输入**:
- 问题内容
- 用户回答

**输出**:
- 多维度评分（技术准确性、表达清晰度、深度广度）
- 识别的技能点
- 情绪/性格特征

**评估维度**:
```json
{
  "technical_accuracy": 8.0,
  "communication_clarity": 7.0,
  "depth_breadth": 7.5,
  "identified_skills": ["Python", "FastAPI"],
  "emotional_state": "confident" / "nervous" / "neutral"
}
```

#### 4. Summary Agent（面试总结）
**职责**:
- 生成面试总结报告
- 生成学习计划
- 更新技能树

**输入**:
- 完整对话历史
- 技能评估汇总

**输出**:
- 总结报告（优势、待提升点、建议）
- 学习计划
- 技能树更新数据

**生成内容**:
```json
{
  "summary": {
    "overall_score": 7.5,
    "strengths": [...],
    "weaknesses": [...],
    "suggestions": [...]
  },
  "learning_plan": {...},
  "skill_updates": {...}
}
```

### 5.3 LangGraph工作流

```python
from langgraph.graph import StateGraph, END

# 状态定义
class InterviewState(TypedDict):
    user_id: str
    session_id: str
    messages: list
    interview_round: int
    should_continue: bool
    # ... 其他字段

# 构建工作流
workflow = StateGraph(InterviewState)

# 添加节点
workflow.add_node("decision", decision_agent)
workflow.add_node("generate_question", question_generator_agent)
workflow.add_node("wait_user_answer", wait_for_user_input)
workflow.add_node("analyze_answer", user_analysis_agent)
workflow.add_node("summary", summary_agent)

# 定义边（流程）
workflow.set_entry_point("decision")

# 条件分支
workflow.add_conditional_edges(
    "decision",
    lambda state: "continue" if state["should_continue"] else "end",
    {
        "continue": "generate_question",
        "end": "summary"
    }
)

# 线性流程
workflow.add_edge("generate_question", "wait_user_answer")
workflow.add_edge("wait_user_answer", "analyze_answer")
workflow.add_edge("analyze_answer", "decision")  # 循环回决策
workflow.add_edge("summary", END)

# 编译
app = workflow.compile()
```

---

## 六、核心业务流程

### 6.1 首次使用流程

```
用户 → 上传简历
     ↓
   解析简历 (异步任务)
     ↓
   填写岗位JD
     ↓
   [可选] 上传历史面试记录
     ↓
   等待解析完成
     ↓
   生成匹配分析报告
     ↓
   创建面试会话
     ↓
   开始模拟面试
     ↓
   (3-5轮对话)
     ↓
   生成面试报告 + 学习计划
     ↓
   [可选] 更新知识库
```

**API流程**:
```
POST /api/v1/interview/init
{
  "resume_file": <file>,
  "jd_content": "...",
  "meeting_notes": "..." (可选)
}
→ 返回: { session_id, match_analysis, ready: true }

WebSocket /ws/interview/{session_id}
→ 实时对话交互

POST /api/v1/interview/{session_id}/complete
{
  "update_knowledge": true/false
}
→ 返回: { summary, learning_plan, skill_updates }
```

### 6.2 日常使用流程（第2+次）

```
用户登录
     ↓
   查看上次学习计划
     ↓
   [可选] 更新简历/JD
     ↓
   [可选] 补充面试记录
     ↓
   开始新一轮模拟面试
     ↓
   LLM参考:
     • 上次计划完成情况
     • round_number (知道是第N次)
     • 最近3次面试的变化
     ↓
   生成新的报告和计划
     ↓
   [根据设置] 自动更新知识库
```

**关键点**:
- LLM能看到"上次建议学习XX，现在掌握了吗？"
- round_number让LLM知道这是第几次面试
- 通过时间戳对比简历/JD的更新

### 6.3 知识库更新机制

**触发方式**:
1. 用户手动选择更新
2. 用户设置中开启"自动更新"开关

**更新内容**:
```python
def update_knowledge_base(session_id):
    session = get_session(session_id)
    
    # 1. 提取重要对话片段
    important_conversations = extract_important_qa(
        session.conversations,
        threshold=7.0  # 只要评分>=7的
    )
    
    # 2. 提取技能证据
    skill_evidence = [
        {
            "skill": skill.skill_name,
            "evidence": skill.assessment_data["evidence"]
        }
        for skill in session.skill_assessments
        if skill.assessment_data["score"] >= 7.0
    ]
    
    # 3. 向量化并存入Qdrant
    for item in important_conversations + skill_evidence:
        vector = embed(item["content"])
        qdrant_client.upsert(
            collection_name="user_memories",
            points=[{
                "id": generate_id(),
                "vector": vector,
                "payload": {
                    "user_id": session.user_id,
                    "source_type": item["type"],
                    "source_id": session_id,
                    "content": item["content"],
                    "timestamp": now(),
                    "importance": item["score"]
                }
            }]
        )
    
    # 4. 更新元数据表
    save_to_user_knowledge_base(...)
```

---

## 七、全量记忆检索实现

### 7.1 上下文加载函数

```python
def load_user_context(user_id: str, session_id: str) -> dict:
    """
    分层加载用户上下文
    """
    context = {}
    
    # Layer 1: 当前会话（从Redis）
    context["current_session"] = redis.lrange(
        f"session:{session_id}:messages", 0, -1
    )
    
    # Layer 2: 近期记忆（最近3次面试摘要）
    recent_sessions = db.query(InterviewSession)\
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == 'completed'
        )\
        .order_by(InterviewSession.created_at.desc())\
        .limit(3).all()
    
    context["recent_memory"] = [
        {
            "round": s.round_number,
            "date": s.created_at,
            "key_insights": extract_key_insights(s.summary)  # 压缩
        }
        for s in recent_sessions
    ]
    
    # Layer 3: 语义相关记忆（从Qdrant检索）
    current_topic = extract_current_topic(context["current_session"])
    context["relevant_memory"] = qdrant_client.search(
        collection_name="user_memories",
        query_vector=embed(current_topic),
        query_filter={
            "must": [
                {"key": "user_id", "match": {"value": user_id}},
                {"key": "importance", "range": {"gte": 7.0}}
            ]
        },
        limit=5  # 只要Top-5
    )
    
    # Layer 4: 当前学习计划
    context["learning_plan"] = db.query(LearningPlan)\
        .filter(
            LearningPlan.user_id == user_id,
            LearningPlan.status == 'active'
        ).first()
    
    return context
```

### 7.2 Prompt构建策略

```python
def build_interview_prompt(state: InterviewState) -> str:
    """
    精简版Prompt，控制token数量
    """
    prompt = f"""
你是一位友好的AI面试陪练，名叫"升级助手"。

# 用户档案（精简版）
- 目标岗位：{state['user_profile']['target_position']}
- 核心技能：{', '.join(state['user_profile']['top_skills'][:5])}
- 经验亮点：{state['user_profile']['highlights_summary']}

# 最近进展
{format_recent_memory(state['recent_memory'])}
# 输出示例: "第2次面试(2天前): Python基础不错，需加强FastAPI。第3次(昨天): FastAPI有进步。"

# 当前学习计划
- 上次建议：{state['learning_plan']['current_focus']}
- 完成情况：{state['learning_plan']['progress']}%

# 本次面试重点
- 这是第{state['interview_round']}轮提问
- 话题：{state['current_topic']}

# 相关历史（参考）
{format_relevant_memory(state['relevant_memory'][:3])}

---
最近对话：
{format_messages(state['messages'][-10:])}

请提出下一个问题（友好、探索性）。
"""
    return prompt
```

**Token控制**:
- 用户档案：~200 tokens
- 最近进展：~300 tokens
- 学习计划：~200 tokens
- 相关历史：~400 tokens
- 最近对话：~1000 tokens
- **总计**: ~2100 tokens（在安全范围内）

---

## 八、MVP功能清单

### 8.1 Phase 1: MVP（4-6周）

**必须有的功能**:
- [x] 用户注册/登录
- [x] 简历上传（支持PDF、文本）
- [x] 简历解析（提取结构化信息）
- [x] 岗位JD填写
- [x] 简历-JD匹配分析
- [x] 3-5轮模拟面试对话
- [x] 会话管理（开始、暂停、继续、结束）
- [x] 面试总结报告生成
- [x] 学习计划生成
- [x] 对话历史存储

**数据库需求**:
- PostgreSQL: users, resumes, job_descriptions, interview_sessions, conversations, learning_plans
- Redis: 会话缓存

**可以延后**:
- ~~向量检索（先用简单的规则匹配）~~
- ~~技能树可视化~~
- ~~真实面试复盘~~
- ~~知识库自动更新~~

### 8.2 Phase 2: 智能记忆（2-3周）

**新增功能**:
- [x] Qdrant向量数据库集成
- [x] 用户知识库构建
- [x] 语义检索增强提问
- [x] 个性化问题生成
- [x] 技能评估记录

**数据库新增**:
- Qdrant: user_memories, general_knowledge
- PostgreSQL: skill_assessments, user_knowledge_base

### 8.3 Phase 3: 深度分析（2-3周）

**新增功能**:
- [x] 技能树可视化
- [x] 成长轨迹图表
- [x] 真实面试会议记录解析
- [x] 知识库自动更新开关
- [x] 学习计划进度追踪

**数据库新增**:
- PostgreSQL: interview_meetings

---

## 九、关键优化点说明

### 9.1 为什么用JSONB而不是多张关联表？

**JSONB的优势**:
- ✅ 灵活扩展：简历格式多样，JSONB避免频繁改表
- ✅ 原子操作：解析结果一次性存储，不用多次INSERT
- ✅ 查询能力：PostgreSQL对JSONB支持丰富（索引、查询）
- ✅ 版本兼容：后续增加字段不影响现有数据

**适用场景**:
- 简历解析结果（结构不固定）
- 面试总结报告（每次格式可能不同）
- 学习计划（动态调整）
- 技能评估详情（证据和gaps描述）

**不适用场景**:
- 高频查询的关键字段（应提取为独立列）
- 需要JOIN的关联关系
- 需要强约束的字段

### 9.2 为什么要有round_number字段？

**作用**:
1. **时间维度追踪**: 知道这是用户的第几次面试
2. **对比分析**: 便于生成"第3次相比第2次的进步"
3. **LLM上下文**: 让LLM知道"这是第N次面试了"
4. **个性化提问**: 第1次偏基础，第3次可以深挖

**实现**:
```python
# 创建会话时自动计算
def create_session(user_id):
    last_round = db.query(InterviewSession)\
        .filter(InterviewSession.user_id == user_id)\
        .order_by(InterviewSession.round_number.desc())\
        .first()
    
    new_round = (last_round.round_number + 1) if last_round else 1
    
    session = InterviewSession(
        user_id=user_id,
        round_number=new_round,
        ...
    )
```

### 9.3 为什么用Redis缓存会话？

**Redis的作用**:
1. **实时性**: 对话过程中频繁读写，Redis延迟低
2. **减轻数据库压力**: 不用每条消息都写PostgreSQL
3. **自动过期**: TTL机制自动清理过期会话
4. **批量写入**: 会话结束后一次性写入PostgreSQL

**流程**:
```
用户发消息 → 写入Redis → 立即返回
         ↓
   (会话进行中，只在Redis)
         ↓
   会话结束 → 从Redis读取 → 批量写入PostgreSQL
         ↓
   Redis自动过期（TTL 1小时）
```

### 9.4 为什么skill_assessments是独立表？

**独立表的优势**:
1. **历史追踪**: 记录每次面试对每个技能的评估
2. **进步可视化**: 通过`score_change`字段看到提升
3. **技能树构建**: `skill_path`字段支持层级关系
4. **灵活查询**: 可以单独查询某技能的历史变化

**如果放在session的JSONB里**:
- ❌ 难以追踪单个技能的历史变化
- ❌ 无法高效查询"Python这个技能的进步曲线"
- ❌ 技能树构建困难

---

## 十、技术实现要点

### 10.1 异步处理

**耗时任务列表**:
- 简历解析（PDF提取、OCR、LLM结构化）
- 会议记录解析
- 向量化（Embedding生成）
- 知识库更新

**实现方案**:
```python
# 使用FastAPI的BackgroundTasks
from fastapi import BackgroundTasks

@app.post("/api/v1/resume/upload")
async def upload_resume(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    # 1. 先保存文件
    file_url = await save_to_storage(file)
    
    # 2. 创建简历记录（状态=pending）
    resume = create_resume_record(
        file_url=file_url,
        parse_status="pending"
    )
    
    # 3. 后台异步解析
    background_tasks.add_task(
        parse_resume_async,
        resume.id
    )
    
    # 4. 立即返回
    return {"resume_id": resume.id, "status": "parsing"}

# 轮询查询解析进度
@app.get("/api/v1/resume/{resume_id}/status")
async def get_parse_status(resume_id: str):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    return {
        "status": resume.parse_status,
        "error": resume.parse_error
    }
```

### 10.2 流式输出

**WebSocket实现**:
```python
from fastapi import WebSocket

@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    while True:
        # 接收用户消息
        user_message = await websocket.receive_text()
        
        # 更新状态
        state = load_session_state(session_id)
        state["messages"].append({"role": "user", "content": user_message})
        
        # 流式调用LLM
        async for chunk in llm_stream(state):
            # 实时发送给前端
            await websocket.send_text(chunk)
        
        # 保存完整回复
        save_session_state(session_id, state)
```

### 10.3 错误处理

**数据库回滚**:
```python
from sqlalchemy.exc import SQLAlchemyError

def create_interview_session(data):
    try:
        # 开启事务
        session = Session()
        
        # 创建会话
        interview = InterviewSession(**data)
        session.add(interview)
        
        # 初始化其他相关记录
        plan = LearningPlan(session_id=interview.id, ...)
        session.add(plan)
        
        # 提交
        session.commit()
        return interview.id
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Failed to create session: {e}")
        raise
    finally:
        session.close()
```

**LLM API重试**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_llm_with_retry(prompt: str):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

---

## 十一、开发路线图

### 阶段1: 基础架构搭建（Week 1-2）
- [x] FastAPI项目初始化
- [x] PostgreSQL数据库设计和迁移脚本
- [x] Redis连接配置
- [x] 用户认证系统
- [x] 基础CRUD接口

### 阶段2: MVP核心功能（Week 3-4）
- [x] 简历上传和解析
- [x] JD管理
- [x] 匹配分析
- [x] 简单的对话接口（固定问题模板）
- [x] 会话管理

### 阶段3: Agent集成（Week 5-6）
- [x] LangChain/LangGraph集成
- [x] 多Agent工作流实现
- [x] 个性化问题生成
- [x] 面试总结和学习计划生成

### 阶段4: 向量检索（Week 7-8）
- [x] Qdrant集成
- [x] 用户知识库构建
- [x] 语义检索实现
- [x] 记忆增强提问

### 阶段5: 优化和扩展（Week 9-10）
- [ ] 技能树可视化
- [ ] 前端界面完善
- [ ] 性能优化
- [ ] 真实面试复盘功能

---

## 十二、预期成果

### MVP阶段
- ✅ 完整的面试模拟流程
- ✅ 个性化的面试报告
- ✅ 针对性的学习计划
- ✅ 基础的记忆管理

### 完整版
- ✅ 智能化的上下文记忆
- ✅ 可视化的技能树
- ✅ 自动化的知识库更新
- ✅ 多轮面试的进步追踪

---

## 附录

### A. 环境依赖

```bash
# Python依赖
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
qdrant-client==1.7.0
langchain==0.1.0
langgraph==0.0.20
openai==1.6.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
tenacity==8.2.3

# 其他服务
PostgreSQL 15+
Redis 7.0+
Qdrant 1.7+
```

### B. 数据库迁移脚本

使用Alembic进行数据库版本管理：

```bash
# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial schema"

# 执行迁移
alembic upgrade head
```

### C. API文档

FastAPI自动生成文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**文档版本**: v1.0  
**最后更新**: 2024-02-05  
**维护者**: 系统架构师  
**状态**: 设计完成，待开发实现
