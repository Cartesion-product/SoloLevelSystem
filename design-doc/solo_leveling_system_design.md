# **《我独自升级系统》**

Solo Leveling System

系统架构设计 & 产品设计文档

Version 1.0 \| 2026-02-06

基于 AI Agent 的智能面试辅导与职业成长伴侣系统

目录

# **第一部分**

## 产品设计 (PRD)

## 1.1 产品愿景与定位

《我独自升级系统》是一个基于 AI Agent
的智能面试辅导平台，定位为"职业成长的数字孞生导师"。系统的核心理念是"陪伴与个性化"------它不是冷冰冰的刷题工具，而是一个能够感知用户状态、管理用户知识资产、持续追踪能力成长的闭环系统。

**核心价值主张：**帮助求职者通过 AI 模拟面试，在 3-5
轮对话中发现简历与实际能力的差距，获得任务驱动的学习建议，持续提升面试成功率。

## 1.2 目标用户与使用场景

### 1.2.1 用户画像

------------------ ----------------------------------------------------------
  **维度**           **描述**

  主要用户           AI 应用开发岗位求职者（Prompt工程、Agent开发、RAG应用等）

  使用频率           每 2-3 天一次模拟面试，持续迭代

  核心痛点           难以客观评估简历匹配度、缺乏真实练习机会、不清楚薄弱环节

  期望体验           "严师+伙伴"结合，能引导思考也能直言不讳
------------------ ----------------------------------------------------------

### 1.2.2 用户旅程地图

+-----------------------------------------------------------------------+
| **第一次使用流程**                                                    |
|                                                                       |
| ① 注册/登录 → 创建个人档案                                            |
|                                                                       |
| ② 上传简历（PDF/Word）+ 填写目标岗位 JD                               |
|                                                                       |
| ③ 可选：上传历史面试会议记录、知识库文档                              |
|                                                                       |
| ④ 系统解析简历 → 初始化技能树 → 匹配度分析                            |
|                                                                       |
| ⑤ 开始第一次模拟面试（守城阶段 → 攻城阶段）                           |
|                                                                       |
| ⑥ 生成面试报告 + 学习计划 + 每日任务                                  |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| **日常使用流程**                                                      |
|                                                                       |
| ① 登录 → 查看待验收任务 + 每日激励语                                  |
|                                                                       |
| ② 可选：更新简历/JD、补充新的面试记录                                 |
|                                                                       |
| ③ 开始模拟面试（Agent 基于上次计划、待验收任务、新增 Gap 进行提问）   |
|                                                                       |
| ④ 面试结束 → 生成报告 → 异步更新技能树/心理画像/知识库                |
|                                                                       |
| ⑤ 用户确认是否更新个人知识库（或自动更新开关）                        |
+-----------------------------------------------------------------------+

## 1.3 功能优先级矩阵 (MoSCoW)

------------ -------------------- -------------------------------------- ----------
  **优先级**   **功能模块**         **说明**                               **版本**

  Must Have    简历上传与智能解析   多模板结构化解析，支持 PDF/Word        v1.0

  Must Have    目标岗位 JD 管理     多 JD 管理，默认 JD 设定               v1.0

  Must Have    多轮模拟面试         守城+攻城两阶段，动态难度调节          v1.0

  Must Have    多 Agent 协作编排    Strategist/Interviewer/Evaluator       v1.0
                                    实时協作                               

  Must Have    面试复盘报告         表现评估、Gap 分析、技能点评分         v1.0

  Must Have    任务驱动学习计划     基于 Gap 生成可追踪任务                v1.0

  Must Have    技能树管理           动态生成/更新，树形结构 + 0-10评分     v1.0

  Must Have    个人知识库           用户上传文档自动向量化，支持增删管理   v1.0

  Must Have    混合记忆系统         热/温/冷三层记忆架构                   v1.0

  Should Have  心理画像分析         异步性格/情绪分析，每日激励语          v1.0

  Should Have  成长轨迹可视化       技能树雷达图、能力曲线图               v1.5

  Could Have   语音交互             WebSocket + STT/TTS 实时语音对练       v2.0

  Could Have   PageIndex 深度检索   长文档推理式检索集成                   v2.0

  Won\'t Have  工作助手扩展         入职后周报、代码复盘等                 未来
  (Now)                                                                    
------------ -------------------- -------------------------------------- ----------

## 1.4 交互设计原则

### 1.4.1 Agent 人格定义

系统采用"严师 + 伙伴"双模式人格，通过动态参数 stress_level
控制语气转换：

------------------ -------------- ---------------------------------------- ------------------
  **stress_level**   **人格模式**   **行为表现**                             **触发条件**

  0.0 - 0.3          温和 Mentor    多用"比如\..."、"你觉得\..."，引导思考   用户初次使用 /
                                                                             信心低

  0.3 - 0.7          专业面试官     正常提问节奏，适度追问                   默认模式

  0.7 - 1.0          严肃 Tech Lead 直接指出问题，"这是基础面试必挂项"       简单题连续答错
------------------ -------------- ---------------------------------------- ------------------

### 1.4.2 主动破冰机制 (MVP 文字版)

当用户回复过于简短（Token 数 \< 阈值）或超时未回复时，触发三级引导策略：

-   **Level 1 (引导)：**"这块是不是有点卡壳？可以试着从 \[X\]
    这个角度说说看。"

-   **Level 2 (追问)：**"如果太抽象，我们换个具体场景\..."

-   **Level 3 (跳过)：**"这个知识点我们还得再复习，先看下一个。"

# **第二部分**

## 系统架构设计

## 2.1 架构总览

系统采用 DDD（领域驱动设计）+ 微服务思想的分层架构，前后端分离，后端基于
FastAPI + LangGraph
构建。架构的核心设计目标是"高内聚、低耦合"，确保未来可以灵活扩展语音交互、PageIndex、工作助手等能力。

----------------- -------------- --------------------- --------------------------------
  **层次**          **组件**       **技术栈**            **职责**

  表现层            Web 前端       React/Next.js +       用户界面、对话交互、可视化展示
  (Presentation)                   TailwindCSS           

  接入层 (Gateway)  API Gateway    FastAPI + SSE         RESTful API、流式响应、认证鉴权

  编排层            Agent 引擎     LangGraph + LangChain 多 Agent 状态机编排、流程控制
  (Orchestration)                                        

  领域层 (Domain)   业务领域服务   Python + Pydantic     4大领域上下文的业务逻辑

  数据层 (Data)     持久化服务     PostgreSQL + Qdrant + 结构化存储、向量检索、缓存
                                   Redis                 

  基础设施 (Infra)  LLM Provider   OpenAI/自定义         模型调用、Embedding 生成
                                   Provider              
----------------- -------------- --------------------- --------------------------------

## 2.2 领域驱动设计 (DDD)

系统划分为 4 个核心领域上下文（Bounded
Context），每个领域独立变化、独立部署：

---------------- ------------------- --------------------------------------------------
  **领域**         **核心实体**        **职责范围**

  Interview        InterviewSession    控制面试流程、状态机流转、对话管理、实时交互逻辑
  Context (面试域) Evaluation Message  

  Capability       SkillTree SkillNode 维护一人一库的技能点状态，计算当前能力与目标距离
  Context (能力域) GapAnalysis         

  Knowledge        Document            混合检索引擎、用户知识库管理、题库管理
  Context (知识域) KnowledgeChunk      
                   QuestionBank        

  Growth Context   Quest LearningPlan  任务生成、进度追踪、心理画像、成长曲线
  (成长域)         PsychologyProfile   
                   Achievement         
---------------- ------------------- --------------------------------------------------

## 2.3 技术栈总览

--------------- ------------------------- --------------------------------------
  **类别**        **技术选型**              **用途**

  后端框架        FastAPI                   RESTful API、SSE
                                            流式响应、WebSocket（v2.0）

  Agent 编排      LangGraph + LangChain     多 Agent 状态机、图编排、工具调用

  关系型数据库    PostgreSQL                用户信息、技能树、学习计划、任务日志

  向量数据库      Qdrant                    知识库向量检索、对话记忆片段

  缓存            Redis                     热数据缓存、Session 状态、消息队列

  前端框架        React/Next.js +           用户界面、响应式设计
                  TailwindCSS               

  LLM Provider    可插拔 Provider 架构      支持 OpenAI、自定义接入

  文档解析        Unstructured / PyMuPDF    PDF/Word 解析、文本提取

  向量化          OpenAI Embedding / BGE    文本向量化入库
--------------- ------------------------- --------------------------------------

# **第三部分**

## Agent 编排设计 (LangGraph)

## 3.1 全局状态对象 (InterviewState)

这是在各 Agent
节点之间流转的核心数据结构，承载了面试过程中的所有上下文信息：

class InterviewState(TypedDict):

\# \-\-- 基础上下文 \-\--

user_id: str

session_id: str

resume_context: dict \# 简历解析结构化结果

jd_context: dict \# 目标岗位 JD 解析结果

skill_tree_snapshot: dict \# 当前技能树快照

pending_quests: List\[dict\] \# 待验收任务列表

\# \-\-- 实时对话流 \-\--

messages: List\[BaseMessage\] \# 对话历史

current_topic: str \# 当前技术点

question_count: int \# 已提问数

max_questions: int \# 本轮最大提问数

\# \-\-- 策略控制 \-\--

stress_level: float \# 0.0-1.0 压力值

silence_count: int \# 连续简短回答次数

phase: Literal\[\'defense\',\'attack\',\'feedback\'\]

difficulty: Literal\[\'easy\',\'medium\',\'hard\',\'expert\'\]

\# \-\-- 分析结果 \-\--

identified_gaps: List\[dict\] \# 识别的薄弱点

evaluation_scores: List\[dict\] \# 各题评分

session_summary: str \# 本次面试总结

## 3.2 核心节点设计 (Nodes)

系统包含 5 个核心节点，分为实时流（3个）和异步流（2个）：

--------------- ------------ -------------- --------------------------------------------
  **节点**        **别名**     **运行模式**   **核心职责**

  Strategist      策略家       实时同步       决定提问策略、阶段切换、难度调节、破冰触发

  Interviewer     面试官       实时同步       生成具体问题、动态人格语气、调用检索引擎

  Evaluator       评估者       实时同步       隐式评分、Gap 识别、技能树更新指令

  PsychoAnalyst   心理分析师   异步离线       性格标签更新、情绪曲线、每日激励语生成

  QuestMaster     任务大师     异步离线       基于 Gap 生成任务、更新学习计划、更新知识库
--------------- ------------ -------------- --------------------------------------------

### 3.2.1 节点详细逻辑

**Node A: Strategist (策略家)** --- 只思考，不说话

它是系统的"大脑"，根据当前状态决定下一步行动：

-   **阶段判断：**简历项目未问完 → 保持 defense；简历挖完 → 切换
    attack（向量库找题）

-   **破冰触发：**silence_count \> 2 → 指示切换到引导模式或更换话题

-   **难度调节：**连续答对 → 提升难度；连续答错 → 降低难度但提升
    stress_level

-   **路由决策：**深挖（Deep Dive）vs 广度测试（Wide Check）

**Node B: Interviewer (面试官)** --- 系统的"嘴巴"

负责生成具体的文字回复，根据 Strategist 的指令执行：

-   **动态 Persona：**根据 stress_level 切换语气风格

-   **数据源调用：**根据指令查询 PostgreSQL（简历、技能树）或
    Qdrant（题库、知识库）

-   **主动破冰：**当收到破冰指令时，执行三级引导策略

**Node C: Evaluator (评估者)** --- 隐式评分引擎

在用户回答后立即运行，不发出可见输出：

-   **关键点检测：**用户回答是否命中核心知识点 → 更新评分

-   **逻辑清晰度：**回答的结构性和深度 → 更新 identified_gaps

-   **难度调节建议：**回答完美 → 建议提升难度；回答糟糕 → 记录 Gap

**Node D: PsychoAnalyst (心理分析师)** --- 异步观察者

面试结束后异步触发，不影响实时体验：

-   **情绪分析：**分析对话中的情绪模式（焦虑、自信、迷茫、放弃）

-   **性格标签更新：**更新 personality_tags（visual_learner /
    defensive_under_pressure 等）

-   **每日激励语：**基于昨日任务完成情况 + 心理状态生成个性化激励

**Node E: QuestMaster (任务大师)** --- 异步任务引擎

面试结束后异步触发：

-   **任务生成：**读取 identified_gaps → 生成任务驱动型学习任务

-   **知识库更新：**根据用户设置（自动/手动）决定是否将本次模拟入库

-   **技能树更新：**根据评估结果更新技能节点评分和状态

## 3.3 状态流转图 (State Graph)

以下是 LangGraph 的核心状态流转逻辑：

\[用户进入\] → \[Init\] → 加载简历/JD/技能树/待验收任务

↓

\[Strategist\] ←────────────────────┐

│ 决策：下一题策略/阶段切换 │

↓ │

\[Interviewer\] │

│ 生成问题 → SSE流式输出 │

↓ │

\[等待用户输入\] │

│ │

├─ 用户回答 → \[Evaluator\] ───┘

│ │ 评分 + Gap识别

│ │

│ ├─ 未达最大题数 → 回到 Strategist

│ └─ 达到最大题数 / /end → \[Feedback\]

│

└─ 用户回复过短 → silence_count++ → Strategist

\[Feedback\] → 生成本次报告 → \[END\]

↓ (异步触发)

\[PsychoAnalyst\] → 更新心理画像

\[QuestMaster\] → 生成任务 + 更新技能树

## 3.4 提问策略设计

系统采用"守城-攻城"两阶段提问策略，确保提问的针对性和进阶性：

----------- ------------------------ ------------------------------ -----------------------
  **阶段**    **数据源**               **目标**                       **示例**

  Defense     PostgreSQL:简历+技能树   验证简历真实性，深挖项目细节   "你简历提到用 Kafka，但
  (守城)                                                              QPS 只有
                                                                      100，为什么引入？"

  Attack      Qdrant:题库+知识库       寻找能力 Gap，对标 JD 要求     "岗位要求
  (攻城)                                                              LangGraph，它和
                                                                      LangChain 核心区别是？"
----------- ------------------------ ------------------------------ -----------------------

# **第四部分**

## 混合记忆策略设计

## 4.1 三层记忆架构总览

系统采用"热-温-冷"三层记忆架构，模拟人类记忆的分层机制。核心原则是：近期信息保留完整细节，远期信息压缩为摘要和向量片段，关键事件永久保留。

---------- -------------- ------------------------------------ ---------------- --------------
  **层级**   **存储介质**   **数据内容**                         **生命周期**     **访问速度**

  热数据     Redis          当前 Session 完整对话 + 近 3 次      Session 结束后 7 毫秒级
  (Hot)                     Session 摘要                         天自动过期       

  温数据     PostgreSQL     Session                              永久保存         十毫秒级
  (Warm)                    摘要、评估结果、Gap分析、任务状态                     

  冷数据     Qdrant         对话片段向量、知识点向量、情绪标记   永久保存         百毫秒级
  (Cold)                                                                          
---------- -------------- ------------------------------------ ---------------- --------------

## 4.2 记忆流转机制

记忆的流转是自动化的，由后台任务触发：

### 4.2.1 实时阶段（面试进行中）

-   **写入热层：**每轮对话实时写入 Redis，包含完整的 messages 列表

-   **上下文组装：**Agent 启动时从 Redis 加载当前 Session + 近 3 次
    Session 摘要作为上下文

### 4.2.2 Session 结束后（异步任务）

1.  **生成摘要：**LLM
    将完整对话压缩为结构化摘要（关键问题、用户回答要点、评估结果）

2.  **写入温层：**摘要存入 PostgreSQL 的 interview_sessions 表

3.  **写入冷层：**有价值的对话片段（答错的题、发现的
    Gap、情绪变化点）向量化后存入 Qdrant

4.  **缓存更新：**更新 Redis 中的"近 3 次摘要"缓存

### 4.2.3 定期维护（后台定时任务）

-   **Redis TTL 过期：**7 天未访问的 Session 完整对话自动清除（摘要已在
    PG 中）

-   **Qdrant 去重：**定期检查向量片段，合并语义相似度超过 0.95 的片段

-   **技能树合并：**当某技能节点被评估超过 5
    次后，计算加权平均分作为稳定评分

## 4.3 上下文组装策略

每次面试开始时，Agent 的上下文按以下优先级组装，确保 Token 可控：

------------ -------------------------------- --------------- -----------------------
  **优先级**   **内容**                         **来源**        **估算 Token**

  P0 (必须)    System Prompt +                  PostgreSQL      \~2000
               当前简历结构化数据 + JD                          

  P1 (必须)    当前技能树快照 + 待验收任务      PostgreSQL      \~500

  P2 (必须)    本次 Session 对话历史            Redis           动态增长

  P3 (重要)    近 3 次 Session 摘要             Redis 缓存      \~800

  P4 (可选)    相关知识片段（按当前话题检索）   Qdrant          \~500

  P5 (可选)    心理画像摘要                     PostgreSQL      \~200
------------ -------------------------------- --------------- -----------------------

+-----------------------------------------------------------------------+
| **Token 控制策略**                                                    |
|                                                                       |
| P0-P2 总计约 2500+ Token，预留空间给动态对话。                        |
|                                                                       |
| 当本次 Session 对话超过 4000 Token 时，自动对早期对话进行摘要压缩。   |
|                                                                       |
| P4/P5 仅在 Token 余量充足时加载。                                     |
+-----------------------------------------------------------------------+

# **第五部分**

## 数据模型设计

## 5.1 PostgreSQL 核心表结构

### 5.1.1 用户表 (users)

CREATE TABLE users (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

username VARCHAR(100) UNIQUE NOT NULL,

email VARCHAR(255) UNIQUE NOT NULL,

password_hash VARCHAR(255) NOT NULL,

settings JSONB DEFAULT \'{}\',

\-- settings 包含: auto_update_knowledge (bool), default_resume_id, etc.

created_at TIMESTAMP DEFAULT NOW(),

updated_at TIMESTAMP DEFAULT NOW()

);

### 5.1.2 简历表 (resumes)

CREATE TABLE resumes (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

title VARCHAR(255), \-- "后端开发简历"、"AI开发简历"

template_type VARCHAR(50), \-- \'ai_dev\', \'backend\', \'fullstack\',
\'data\'

is_default BOOLEAN DEFAULT false,

raw_file_url TEXT, \-- 原始文件存储路径

parsed_data JSONB NOT NULL, \-- 结构化解析结果 (见下方模板)

created_at TIMESTAMP DEFAULT NOW(),

updated_at TIMESTAMP DEFAULT NOW()

);

\-- 确保每个用户只有一个默认简历

CREATE UNIQUE INDEX idx_resume_default

ON resumes(user_id) WHERE is_default = true;

**parsed_data 结构化模板示例（AI开发方向）：**

{

\"basic_info\": {

\"name\": \"\", \"phone\": \"\", \"email\": \"\",

\"education\": \[{\"school\": \"\", \"degree\": \"\", \"major\": \"\",
\"period\": \"\"}\]

},

\"skills\": {

\"languages\": \[\"Python\", \"JavaScript\"\],

\"frameworks\": \[\"FastAPI\", \"LangChain\", \"LangGraph\"\],

\"databases\": \[\"PostgreSQL\", \"Qdrant\", \"Redis\"\],

\"tools\": \[\"Docker\", \"Git\"\],

\"domains\": \[\"RAG\", \"Agent开发\", \"Prompt工程\"\]

},

\"projects\": \[{

\"name\": \"智能客服系统\",

\"role\": \"核心开发者\",

\"period\": \"2024.06-2024.12\",

\"tech_stack\": \[\"LangChain\", \"FastAPI\", \"Qdrant\"\],

\"description\": \"基于 RAG 的多轮对话客服系统\",

\"responsibilities\": \[\"设计 Agent 编排流程\", \"实现混合检索\"\],

\"achievements\": \[\"准确率提升 35%\", \"响应时间 \< 2s\"\],

\"challenges\": \"多轮对话上下文管理与 Token 控制\"

}\],

\"work_experience\": \[{

\"company\": \"\", \"position\": \"\", \"period\": \"\",

\"responsibilities\": \[\], \"achievements\": \[\]

}\]

}

5.1.3 目标岗位表 (target_jobs)

CREATE TABLE target_jobs (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

company_name VARCHAR(255),

position_name VARCHAR(255) NOT NULL,

jd_text TEXT NOT NULL,

parsed_requirements JSONB, \-- 解析后的技能要求列表

is_default BOOLEAN DEFAULT false,

created_at TIMESTAMP DEFAULT NOW()

);

### 5.1.4 技能树表 (skill_tree)

CREATE TABLE skill_tree (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

skill_name VARCHAR(255) NOT NULL,

parent_skill_id UUID REFERENCES skill_tree(id),

proficiency_score SMALLINT DEFAULT 0 CHECK (proficiency_score BETWEEN 0
AND 10),

evaluation_comment TEXT, \-- LLM 生成的评价说明

source_type VARCHAR(50) DEFAULT \'resume_claimed\',

\-- \'resume_claimed\': 简历自述

\-- \'verified\': 面试验证

\-- \'inferred_gap\': 系统检测的盲区

focus_status VARCHAR(50) DEFAULT \'dormant\',

\-- \'active_learning\': 当前攻克重点

\-- \'mastered\': 已掌握

\-- \'dormant\': 休眠

assess_count INTEGER DEFAULT 0,

last_assessed_at TIMESTAMP,

created_at TIMESTAMP DEFAULT NOW(),

updated_at TIMESTAMP DEFAULT NOW()

);

CREATE INDEX idx_skill_user ON skill_tree(user_id);

CREATE INDEX idx_skill_gap ON skill_tree(user_id, source_type);

CREATE INDEX idx_skill_focus ON skill_tree(user_id, focus_status);

### 5.1.5 面试会话表 (interview_sessions)

CREATE TABLE interview_sessions (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

resume_id UUID REFERENCES resumes(id),

job_id UUID REFERENCES target_jobs(id),

session_type VARCHAR(50) NOT NULL, \-- \'simulated\', \'real_review\'

status VARCHAR(50) DEFAULT \'in_progress\',

\-- \'in_progress\', \'completed\', \'abandoned\'

summary JSONB, \-- 结构化摘要

\-- {overall_score, strengths, weaknesses, key_moments, gap_list}

question_count INTEGER DEFAULT 0,

duration_seconds INTEGER,

created_at TIMESTAMP DEFAULT NOW(),

completed_at TIMESTAMP

);

### 5.1.6 任务日志表 (quest_log)

CREATE TABLE quest_log (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

session_id UUID REFERENCES interview_sessions(id),

target_skill_id UUID REFERENCES skill_tree(id),

quest_title VARCHAR(255) NOT NULL,

quest_detail TEXT NOT NULL,

status VARCHAR(50) DEFAULT \'generated\',

\-- \'generated\', \'in_progress\', \'submitted\', \'verified_pass\',
\'verified_fail\'

verification_method VARCHAR(50),

\-- \'verbal_quiz\', \'code_review\', \'concept_explain\'

due_date DATE,

created_at TIMESTAMP DEFAULT NOW(),

completed_at TIMESTAMP

);

### 5.1.7 心理画像表 (user_psychology_profile)

CREATE TABLE user_psychology_profile (

user_id UUID PRIMARY KEY REFERENCES users(id),

personality_tags JSONB DEFAULT \'\[\]\',

\-- e.g. \[\"visual_learner\", \"defensive_under_pressure\"\]

confidence_score FLOAT DEFAULT 0.5,

resilience_score FLOAT DEFAULT 0.5,

preferred_style VARCHAR(50) DEFAULT \'balanced\',

\-- \'encouraging\', \'challenging\', \'balanced\'

daily_motivation TEXT, \-- 今日激励语

updated_at TIMESTAMP DEFAULT NOW()

);

CREATE TABLE mood_log (

id SERIAL PRIMARY KEY,

user_id UUID NOT NULL REFERENCES users(id),

session_id UUID REFERENCES interview_sessions(id),

detected_mood VARCHAR(50),

trigger_event TEXT,

recorded_at TIMESTAMP DEFAULT NOW()

);

### 5.1.8 知识库文档表 (knowledge_documents)

CREATE TABLE knowledge_documents (

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

user_id UUID NOT NULL REFERENCES users(id),

doc_name VARCHAR(255) NOT NULL,

doc_type VARCHAR(50), \-- \'interview_note\', \'tech_book\', \'blog\',
\'bagua\'

file_url TEXT,

chunk_count INTEGER DEFAULT 0, \-- 切片数量

status VARCHAR(50) DEFAULT \'processing\',

\-- \'processing\', \'ready\', \'failed\'

domain_tags TEXT\[\], \-- \[\'redis\', \'distributed_system\'\]

created_at TIMESTAMP DEFAULT NOW()

);

## 5.2 Qdrant 向量库设计

### 5.2.1 Collection: knowledge_chunks (知识片段)

用于存储用户上传文档的向量化片段，支持按用户、类型、难度等过滤检索：

{

\"id\": \"chunk_uuid\",

\"vector\": \[\...\], // 768 or 1536 dim

\"payload\": {

\"user_id\": \"user_uuid\",

\"doc_id\": \"doc_uuid\",

\"content\": \"文本内容\...\",

\"category\": \"redis\",

\"tags\": \[\"persistence\", \"AOF\", \"RDB\"\],

\"difficulty_level\": 3,

\"source_type\": \"tech_book\"

}

}

### 5.2.2 Collection: conversation_memory (对话记忆片段)

存储有价值的对话片段，用于语义去重和历史分析：

{

\"id\": \"memory_uuid\",

\"vector\": \[\...\],

\"payload\": {

\"user_id\": \"user_uuid\",

\"session_id\": \"session_uuid\",

\"speaker\": \"user\",

\"content\": \"我不太清楚 AOF 重写的过程\...\",

\"intent\": \"admit_ignorance\",

\"topic\": \"Redis AOF\",

\"emotion_detected\": \"hesitant\",

\"is_gap_moment\": true,

\"timestamp\": 1706800000

}

}

# **第六部分**

## API 接口设计

## 6.1 核心 API 清单

---------- ------------------------------- ------------- --------------------------------------
  **模块**   **接口**                        **方法**      **说明**

  用户       /api/auth/register              POST          用户注册

  用户       /api/auth/login                 POST          用户登录，返回 JWT

  用户       /api/users/settings             PUT           更新用户设置（自动更新开关等）

  简历       /api/resumes                    POST          上传简历文件，触发解析

  简历       /api/resumes/{id}               GET/PUT/DEL   查看/更新/删除简历

  简历       /api/resumes/{id}/set-default   POST          设置默认简历

  岗位       /api/jobs                       POST/GET      创建/获取目标岗位

  岗位       /api/jobs/{id}/set-default      POST          设置默认岗位

  面试       /api/interviews/start           POST          开始模拟面试（初始化 Session）

  面试       /api/interviews/{id}/chat       POST(SSE)     发送消息，SSE流式返回 Agent回复

  面试       /api/interviews/{id}/end        POST          结束面试，触发报告生成

  面试       /api/interviews/{id}/report     GET           获取面试报告

  技能       /api/skills/tree                GET           获取当前技能树

  任务       /api/quests                     GET           获取任务列表（支持状态过滤）

  任务       /api/quests/{id}/status         PUT           更新任务状态

  知识库     /api/knowledge/upload           POST          上传文档，触发向量化入库

  知识库     /api/knowledge/documents        GET           获取知识库文档列表

  知识库     /api/knowledge/documents/{id}   DELETE        删除文档及其向量片段

  成长       /api/growth/dashboard           GET           成长看板（技能概览+任务进度+激励语）
---------- ------------------------------- ------------- --------------------------------------

## 6.2 SSE 流式响应设计

面试对话采用 Server-Sent Events 实现流式输出，提升用户体验：

// SSE 事件类型定义

event: thinking // Agent 正在思考（加载状态）

event: chunk // 文本片段流式输出

event: metadata // 当前阶段、难度、题号等元数据

event: done // 本轮回复结束

event: session_end // 面试结束，附带报告摘要

# **第七部分**

## 简历解析模板体系

## 7.1 模板路由逻辑

系统根据用户选择的目标岗位方向，自动匹配对应的简历解析模板。模板定义了不同岗位方向重点关注的字段和解析规则：

-------------- ----------------------------------- --------------------------------------
  **模板类型**   **适用岗位**                        **重点解析字段**

  ai_dev         AI应用开发、Prompt工程、Agent开发   AI框架、模型经验、RAG实践、Agent编排

  backend        后端开发、微服务架构                系统设计、数据库、中间件、并发处理

  fullstack      全栈开发                            前端框架、API设计、部署运维

  data           数据工程、数据分析                  ETL、数据仓库、SQL优化、可视化

  generic        通用/未分类                         通用技能提取、项目经验、教育背景
-------------- ----------------------------------- --------------------------------------

## 7.2 解析流程

1.  **文件解析：**PDF/Word → Unstructured/PyMuPDF 提取纯文本

2.  **模板匹配：**根据用户选择的目标岗位方向 → 选择对应模板

3.  **LLM 结构化：**将纯文本 + 模板 Schema 发送给 LLM → 返回结构化 JSON

4.  **校验入库：**Pydantic 校验结构化结果 → 存入 resumes.parsed_data

5.  **技能树初始化：**基于解析结果自动生成初始技能树（source_type =
    \'resume_claimed\'）

# **第八部分**

## 迭代路线图

## 8.1 分阶段实现计划

------------ ---------- ---------------------- ---------------------------------------------------
  **阶段**     **周期**   **目标**               **核心交付物**

  Phase 0      1-2周      项目脚手架 + 数据库 +  FastAPI项目结构、PG/Qdrant/Redis搭建、用户认证API
  基础搭建                基础API                

  Phase 1      3-4周      完整的模拟面试流程     简历解析、LangGraph核心图、多轮对话、SSE流式输出
  核心MVP                                        

  Phase 2      2-3周      全量记忆 + 个性化      三层记忆架构、技能树动态更新、心理画像
  智能记忆                                       

  Phase 3      2-3周      个人知识库构建 +       文档上传解析、向量化入库、混合检索引擎
  知识库                  混合检索               

  Phase 4      2周        报告 + 任务 + 可视化   面试报告、任务系统、技能树可视化
  报告与成长                                     

  Phase 5      持续       Web 端用户界面         React前端、对话界面、仪表盘、技能树图
  前端界面                                       
------------ ---------- ---------------------- ---------------------------------------------------

## 8.2 后续扩展规划

---------- ---------------------- ----------------------------------------
  **版本**   **功能**               **技术要点**

  v1.5       成长轨迹可视化         技能树雷达图、能力曲线、情绪日志可视化

  v2.0       语音交互               WebSocket + STT/TTS + VAD 主动破冰

  v2.0       PageIndex 集成         长文档推理式检索，"图书馆"能力

  v3.0       多岗位模板扩展         更多解析模板、行业题库

  Future     工作助手扩展           入职后周报、代码复盘、OKR追踪
---------- ---------------------- ----------------------------------------

# **第九部分**

## 工程结构设计

## 9.1 后端目录结构 (DDD 分层)

solo-leveling-system/

├── app/

│ ├── main.py \# FastAPI 入口

│ ├── config.py \# 配置管理

│ ├── dependencies.py \# 依赖注入

│ │

│ ├── api/ \# 接入层 (Presentation)

│ │ ├── v1/

│ │ │ ├── auth.py \# 认证接口

│ │ │ ├── resumes.py \# 简历接口

│ │ │ ├── jobs.py \# 岗位接口

│ │ │ ├── interviews.py \# 面试接口

│ │ │ ├── skills.py \# 技能接口

│ │ │ ├── quests.py \# 任务接口

│ │ │ ├── knowledge.py \# 知识库接口

│ │ │ └── growth.py \# 成长看板接口

│ │ └── schemas/ \# Pydantic 请求/响应模型

│ │

│ ├── domain/ \# 领域层 (Domain)

│ │ ├── interview/ \# 面试域

│ │ │ ├── models.py \# 领域实体

│ │ │ ├── service.py \# 业务逻辑

│ │ │ └── repository.py \# 数据访问

│ │ ├── capability/ \# 能力域

│ │ ├── knowledge/ \# 知识域

│ │ └── growth/ \# 成长域

│ │

│ ├── agents/ \# 编排层 (Orchestration)

│ │ ├── graph.py \# LangGraph 主图定义

│ │ ├── state.py \# InterviewState 定义

│ │ ├── nodes/

│ │ │ ├── strategist.py \# 策略家节点

│ │ │ ├── interviewer.py \# 面试官节点

│ │ │ ├── evaluator.py \# 评估者节点

│ │ │ ├── psycho_analyst.py \# 心理分析师节点

│ │ │ └── quest_master.py \# 任务大师节点

│ │ ├── prompts/ \# Prompt 模板

│ │ └── tools/ \# Agent 工具 (DB查询/检索等)

│ │

│ ├── infrastructure/ \# 基础设施层

│ │ ├── database.py \# PostgreSQL 连接

│ │ ├── vector_store.py \# Qdrant 客户端

│ │ ├── cache.py \# Redis 客户端

│ │ ├── llm_provider.py \# LLM Provider 抽象层

│ │ ├── embedding.py \# Embedding 服务

│ │ └── file_parser.py \# 文件解析服务

│ │

│ └── tasks/ \# 异步任务

│ ├── post_interview.py \# 面试后异步任务

│ └── knowledge_indexing.py \# 知识库索引任务

│

├── alembic/ \# 数据库迁移

├── tests/ \# 测试

├── docker-compose.yml \# 容器编排

├── requirements.txt

└── README.md

## 9.2 前端建议

前端推荐方案按优先级排序：

--------------- ----------------------------- -------------------------- ------------------
  **方案**        **优势**                      **劣势**                   **适合场景**

  Next.js +       生态成熟、组件丰富、SSR支持   需要 JS/TS 基础            正式产品（推荐）
  shadcn/ui                                                                

  Streamlit       纯 Python、半天出原型         定制性差、不适合复杂交互   MVP 快速验证

  Gradio          纯 Python、原生支持对话界面   同上                       纯对话原型

  魔改开源模板    成品化程度高                  需要理解原代码             快速上线
--------------- ----------------------------- -------------------------- ------------------

+-----------------------------------------------------------------------+
| **建议策略**                                                          |
|                                                                       |
| Phase 0-2：用 Streamlit 快速出原型，专注后端 Agent 逻辑。             |
|                                                                       |
| Phase 3+：迁移到 Next.js + shadcn/ui 构建正式前端。                   |
|                                                                       |
| 关键：后端 API 设计良好，前端可以随时替换，不影响核心逻辑。           |
+-----------------------------------------------------------------------+
