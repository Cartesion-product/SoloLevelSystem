# 「我独自升级系统」架构设计参考文档

> 本文档总结了基于 Anthropic Claude Cowork 产品设计理念，针对 AI 面试训练系统「我独自升级系统」所提炼的核心设计思路、方法论与实现方案，供代码实现阶段参考。

---

## 一、核心设计理念

### 1.1 从「对话助手」到「自主 Agent」

普通 AI 助手的模式是：**用户问 → AI 答 → 用户再问**，是被动响应的。

本系统要实现的是 Cowork 式的主动 Agent 模式：

- Agent 拥有**持久化的用户状态空间（Workspace）**，每次启动时加载上下文
- Agent **主动规划**本次训练内容，而不是等用户指定每道题
- Agent **自动更新**用户技能画像，下次训练自动适配
- 用户感受到的是系统「记得我、了解我、帮我进化」

### 1.2 三层能力分层

参考 Cowork 插件体系的三层结构：

| 层级 | 类比 Cowork | 在本系统中的含义 |
|------|-------------|-----------------|
| 第一层：基础能力 | Anthropic 官方插件 | 通用面试技巧、评分标准、反馈格式 |
| 第二层：模式能力 | 领域插件（法律/金融） | 行为面 / 技术面 / 系统设计面 / HR 面 |
| 第三层：定制能力 | 企业私有插件 | 目标公司画像、个人薄弱点专项训练 |

后层覆盖前层的冲突规则，三层合并生成最终 Prompt。

### 1.3 Plan-Execute-Observe 循环

借鉴 Cowork 的任务执行模型，每次训练 Session 都是一个完整闭环：

```
加载工作区状态 → 规划本次训练 → 执行问答轮次 → 观察评估回答 → 汇总 → 更新工作区
```

关键点：**工作区在每次 Session 结束后进化**，下次 Session 的规划基于进化后的状态，形成真正的「独自升级」效果。

---

## 二、用户工作区设计（User Workspace）

### 2.1 设计原则

- **工作区即上下文**：Agent 启动时优先加载工作区，不从零开始对话
- **Agent 写，用户读**：工作区由 Agent 自动维护，用户通过 Dashboard 查看进度
- **版本化**：简历、训练计划保留历史，用户能看到成长轨迹

### 2.2 工作区目录结构

```
Workspace/
├── profile/
│   ├── user_meta.json          # 基本信息、目标岗位、求职阶段
│   ├── skill_radar.json        # 技能雷达图（实时更新）
│   └── weak_points.json        # 薄弱点列表（Agent 自动标记）
│
├── resume/
│   ├── v1_raw.md               # 原始简历
│   ├── v2_optimized.md         # AI 优化版本
│   └── changelog.json          # 修改记录
│
├── targets/
│   ├── company_A.json          # 目标公司画像（JD 解析结果）
│   └── company_B.json
│
├── sessions/
│   ├── 2026-02-25_behavioral/
│   │   ├── questions.json
│   │   ├── answers.json
│   │   ├── feedback.json
│   │   └── score.json
│   └── ...
│
└── plans/
    ├── current_plan.json       # 当前训练计划（Agent 生成）
    └── history/
```

### 2.3 MongoDB Schema 示例

```json
// skill_radar collection
{
  "user_id": "xxx",
  "updated_at": "2026-02-25T10:00:00Z",
  "skills": {
    "system_design":   {"score": 72, "trend": "up",     "sessions": 8},
    "algorithms":      {"score": 58, "trend": "stable", "sessions": 12},
    "behavioral":      {"score": 85, "trend": "up",     "sessions": 6},
    "ml_fundamentals": {"score": 63, "trend": "down",   "sessions": 4}
  },
  "weak_points": [
    {"topic": "distributed systems",  "confidence": 0.3, "last_practiced": "2026-02-20"},
    {"topic": "dynamic programming",  "confidence": 0.4, "last_practiced": "2026-02-22"}
  ]
}
```

---

## 三、分层 Prompt 插件化设计

### 3.1 插件目录结构

```
plugins/
├── base/                        # 第一层：基础能力（所有模式共享）
│   ├── interviewer_persona.md   # 面试官人设
│   ├── feedback_format.md       # 反馈格式规范
│   └── scoring_rubric.md        # 评分标准
│
├── modes/                       # 第二层：训练模式插件
│   ├── behavioral/
│   │   ├── system_prompt.md     # STAR 法则引导
│   │   ├── question_bank.json
│   │   └── eval_criteria.md     # 评估维度
│   ├── technical/
│   │   ├── system_prompt.md
│   │   ├── question_bank.json
│   │   └── eval_criteria.md
│   ├── system_design/
│   │   ├── system_prompt.md
│   │   ├── scenarios.json
│   │   └── eval_criteria.md
│   └── hr/
│       ├── system_prompt.md
│       └── eval_criteria.md
│
└── targets/                     # 第三层：公司定制（最高优先级）
    ├── google/
    │   ├── override.md          # 覆盖基础层的特定规则
    │   └── focus_areas.json
    └── bytedance/
        ├── override.md
        └── focus_areas.json
```

### 3.2 插件加载器实现

```python
from pathlib import Path

class PromptPluginLoader:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)

    def load(self, mode: str, target_company: str = None) -> str:
        """三层合并：base + mode + target（后层覆盖前层）"""
        layers = []

        # 第一层：基础
        layers.append(self._load_layer("base"))

        # 第二层：训练模式
        layers.append(self._load_layer(f"modes/{mode}"))

        # 第三层：公司定制（可选）
        if target_company:
            override_path = self.plugin_dir / "targets" / target_company / "override.md"
            if override_path.exists():
                layers.append(self._load_file(override_path))

        return self._merge_layers(layers)

    def _merge_layers(self, layers: list[dict]) -> str:
        merged = {}
        for layer in layers:
            merged.update(layer)
        return self._render_prompt(merged)
```

### 3.3 使用示例

```python
loader = PromptPluginLoader("plugins/")

# 通用技术面
system_prompt = loader.load(mode="technical")

# 针对 Google 的系统设计面
system_prompt = loader.load(mode="system_design", target_company="google")
```

---

## 四、LangGraph Plan-Execute-Observe 实现

### 4.1 Session Graph 结构

```
[START]
   │
   ▼
load_workspace ──► plan_session
                        │
                        ▼
                 ┌─ execute_round ◄────┐
                 │       │             │
                 │       ▼             │
                 │  observe_answer     │
                 │       │             │
                 │   [continue?] ──yes─┘
                 │       │
                 │       no
                 │       ▼
                 └► summarize_session
                          │
                          ▼
                   update_workspace
                          │
                          ▼
                        [END]
```

### 4.2 State 定义

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class SessionState(TypedDict):
    # 工作区数据（Session 开始时加载）
    user_profile: dict
    skill_radar: dict
    weak_points: list

    # 当前 Session 配置
    mode: str                    # behavioral / technical / system_design / hr
    target_company: str | None
    system_prompt: str           # 插件加载器生成

    # 执行状态
    plan: dict                   # 本次训练计划
    rounds: Annotated[list, operator.add]   # 每轮问答记录（累积）
    current_round: int
    max_rounds: int

    # 评估结果
    round_scores: Annotated[list, operator.add]
    round_feedbacks: Annotated[list, operator.add]

    # 最终输出
    session_summary: dict | None
    workspace_updates: dict | None
```

### 4.3 各节点实现

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatAnthropic(model="claude-opus-4-6")

def load_workspace(state: SessionState) -> dict:
    """加载用户工作区，初始化 Prompt 插件"""
    workspace = WorkspaceManager(state["user_id"])
    return {
        "user_profile": workspace.get_profile(),
        "skill_radar": workspace.get_skill_radar(),
        "weak_points": workspace.get_weak_points(),
        "system_prompt": PromptPluginLoader("plugins/").load(
            mode=state["mode"],
            target_company=state.get("target_company")
        )
    }

def plan_session(state: SessionState) -> dict:
    """基于工作区状态智能规划本次训练"""
    prompt = f"""
    基于用户当前状态制定本次训练计划：
    - 技能雷达：{state['skill_radar']}
    - 薄弱点：{state['weak_points']}
    - 训练模式：{state['mode']}

    输出 JSON 格式，包含：题目数量、重点考察方向、难度分布
    """
    plan = llm.invoke([HumanMessage(content=prompt)])
    parsed = parse_json(plan.content)
    return {
        "plan": parsed,
        "current_round": 0,
        "max_rounds": parsed.get("total_questions", 3)
    }

def execute_round(state: SessionState) -> dict:
    """基于计划和历史记录生成当前题目"""
    context = build_round_context(state)
    question = llm.invoke([
        SystemMessage(content=state["system_prompt"]),
        HumanMessage(content=context)
    ])
    return {
        "rounds": [{"question": question.content, "round": state["current_round"]}]
    }

def observe_answer(state: SessionState) -> dict:
    """评估用户回答，输出评分和反馈"""
    last_round = state["rounds"][-1]
    eval_prompt = f"""
    题目：{last_round['question']}
    用户回答：{last_round['answer']}
    评估标准：{load_eval_criteria(state['mode'])}

    输出 JSON：score(1-10)、strengths、improvements、reference_points
    """
    feedback = llm.invoke([HumanMessage(content=eval_prompt)])
    parsed = parse_json(feedback.content)
    return {
        "round_scores": [parsed["score"]],
        "round_feedbacks": [parsed],
        "current_round": state["current_round"] + 1
    }

def summarize_session(state: SessionState) -> dict:
    """汇总本次 Session 的整体表现"""
    summary_prompt = f"""
    训练模式：{state['mode']}
    各轮得分：{state['round_scores']}
    各轮反馈：{state['round_feedbacks']}

    生成：整体表现、进步点、仍需加强方向、下次训练建议
    """
    summary = llm.invoke([HumanMessage(content=summary_prompt)])
    return {"session_summary": parse_json(summary.content)}

def update_workspace(state: SessionState) -> dict:
    """将本次 Session 结果写回工作区，更新技能雷达和薄弱点"""
    workspace = WorkspaceManager(state["user_id"])

    avg_score = sum(state["round_scores"]) / len(state["round_scores"])
    workspace.update_skill_score(state["mode"], avg_score)

    new_weak_points = extract_weak_points(state["round_feedbacks"])
    workspace.update_weak_points(new_weak_points)

    workspace.save_session(state)
    return {"workspace_updates": {"status": "done"}}

def should_continue(state: SessionState) -> str:
    """条件边：判断是否继续下一轮"""
    if state["current_round"] < state["max_rounds"]:
        return "continue"
    return "summarize"
```

### 4.4 构建 Graph

```python
def build_interview_graph():
    graph = StateGraph(SessionState)

    graph.add_node("load_workspace",    load_workspace)
    graph.add_node("plan_session",      plan_session)
    graph.add_node("execute_round",     execute_round)
    graph.add_node("observe_answer",    observe_answer)
    graph.add_node("summarize_session", summarize_session)
    graph.add_node("update_workspace",  update_workspace)

    graph.set_entry_point("load_workspace")
    graph.add_edge("load_workspace",    "plan_session")
    graph.add_edge("plan_session",      "execute_round")
    graph.add_edge("execute_round",     "observe_answer")
    graph.add_conditional_edges(
        "observe_answer",
        should_continue,
        {"continue": "execute_round", "summarize": "summarize_session"}
    )
    graph.add_edge("summarize_session", "update_workspace")
    graph.add_edge("update_workspace",  END)

    return graph.compile()
```

---

## 五、整体架构全貌

```
用户发起训练请求（选择 mode + 目标公司）
              │
              ▼
     LangGraph Session Graph
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
读取 Workspace        加载 Prompt 插件
（技能雷达             （base + mode +
 薄弱点                 target 三层合并）
 历史 sessions）
    │                    │
    └─────────┬──────────┘
              │
              ▼
         plan_session
     （基于工作区状态
       智能规划本次训练）
              │
    ┌─────────┴───────────────────┐
    │    Execute-Observe 循环      │
    │  出题 → 等待用户回答 → 评估  │
    │    重复 N 轮（自动决定）     │
    └─────────────────────────────┘
              │
              ▼
      summarize_session
              │
              ▼
      update_workspace
    （技能雷达进化
      薄弱点更新
      Session 存档）
              │
              ▼
     下次 Session 启动时
    工作区已进化，计划自适应 ✓
```

---

## 六、技术栈选型

| 模块 | 技术选型 | 说明 |
|------|----------|------|
| Agent 框架 | LangGraph | Plan-Execute-Observe 循环实现 |
| LLM | Claude Opus 4.6 | 高质量推理，用于规划、评估、总结 |
| 数据库 | MongoDB | 工作区数据、Session 记录、技能雷达 |
| API 框架 | FastAPI | 后端接口 |
| Prompt 管理 | 文件系统 + 自定义加载器 | 插件化 Prompt，可独立迭代 |
| 向量存储 | 按需集成（RAG 用于题库检索） | 可扩展 |

---

## 七、给 Opus 4.6 的实现说明

在新对话窗口中，请遵循以下原则对项目代码进行修改：

1. **工作区优先**：每个 Agent 节点在操作前，先确认是否需要读取工作区状态，避免从零开始生成内容。

2. **Prompt 插件化**：不要将 Prompt 硬编码在函数内，应通过 `PromptPluginLoader` 加载，支持 mode 和 target_company 两个维度的组合。

3. **State 不可变原则**：LangGraph 节点只返回需要更新的字段，不修改传入的 state 对象。累积型字段（rounds、scores、feedbacks）使用 `Annotated[list, operator.add]`。

4. **工作区写回**：`update_workspace` 节点是唯一负责持久化的节点，其他节点只读工作区，不写入数据库。

5. **插件三层优先级**：target > mode > base，后层覆盖前层的同名配置项。

6. **Session 完整性**：每次训练的 questions、answers、feedback、score 必须作为一个完整的 session 对象存入工作区历史。

---

*文档版本：v1.0 | 生成于 2026-02-25 | 基于 Claude Cowork 设计理念*
