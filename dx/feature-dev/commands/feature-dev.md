---
description: Guided feature development with codebase understanding and architecture focus
argument-hint: Optional feature description [--codex|--gemini]
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply, identify and ask about all underspecified details, design elegant architectures, then implement.

---

## 执行模式

用户通过参数直接指定执行模式：

| 参数 | 执行模式 | 适用场景 |
|------|----------|----------|
| （默认） | 直接执行 | 大多数任务，使用 Task tool 调用 agents |
| `--codex` | 委托 codeagent-wrapper (Codex) | 复杂任务、需要深度推理和 Context Isolation |
| `--gemini` | 委托 codeagent-wrapper (Gemini) | Gemini 后端任务 |

### 设计原理（基于 Multi-Agent Patterns）

**默认直接执行**使用 Task tool 调用 agents，适合大多数场景：
- **避免 Telephone Game** — 直接调用减少信息传递层级
- **Context 共享** — Orchestrator 可直接读取 agent 返回的文件列表

**委托模式**使用 codeagent-wrapper，适用于需要 Context Isolation 的场景：
- 任务复杂度超出当前上下文承载能力
- 需要并行执行多个独立任务
- 需要特定后端的专项能力

---

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific, concrete questions rather than making assumptions. Wait for user answers before proceeding with implementation. Ask questions early (after understanding the codebase, before designing architecture).
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Use TodoWrite**: Track all progress throughout

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

Initial request: $ARGUMENTS

**Actions**:
1. Create todo list with all phases
2. If feature unclear, ask user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding and confirm with user

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

根据执行模式选择不同的方式：

---

### 2A. 默认模式：使用 Task tool

**使用 Task tool 启动 2-3 个 code-explorer agents 并行执行**：

```
Task tool parameters:
- subagent_type: "Explore"
- prompt: "Find features similar to [feature] and trace through their implementation comprehensively. Return a list of 5-10 key files."
```

**Example agent prompts**:
- "Find features similar to [feature] and trace through their implementation comprehensively"
- "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
- "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"

---

### 2B. --codex/--gemini 模式：使用 codeagent-wrapper

**使用 codeagent-wrapper --parallel 并行执行多个探索任务**：

```bash
codeagent-wrapper --parallel --backend {codex|gemini} <<'EOF'
---TASK---
id: explore-similar
workdir: .
---CONTENT---
Find features similar to [feature] and trace through their implementation comprehensively.
Return a list of 5-10 key files to read.

---TASK---
id: explore-architecture
workdir: .
---CONTENT---
Map the architecture and abstractions for [feature area], tracing through the code comprehensively.
Return a list of 5-10 key files to read.

---TASK---
id: explore-patterns
workdir: .
---CONTENT---
Identify UI patterns, testing approaches, or extension points relevant to [feature].
Return a list of 5-10 key files to read.
EOF
```

---

**后续操作**（两种模式通用）：
1. Once the agents return, please read all files identified by agents to build deep understanding
2. Present comprehensive summary of findings and patterns discovered

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:
1. Review the codebase findings and original feature request
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs
3. **Present all questions to the user in a clear, organized list**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

根据执行模式选择不同的方式：

---

### 4A. 默认模式：使用 Task tool

**使用 Task tool 启动 2-3 个 code-architect agents 并行执行**：

```
Task tool parameters:
- subagent_type: "Plan"
- prompt: "Design architecture for [feature] with focus on [minimal changes / clean architecture / pragmatic balance]. Include specific files to create/modify."
```

**Different focuses**:
- Minimal changes (smallest change, maximum reuse)
- Clean architecture (maintainability, elegant abstractions)
- Pragmatic balance (speed + quality)

---

### 4B. --codex/--gemini 模式：使用 codeagent-wrapper

**使用 codeagent-wrapper --parallel 并行设计多个方案**：

```bash
codeagent-wrapper --parallel --backend {codex|gemini} <<'EOF'
---TASK---
id: arch-minimal
workdir: .
---CONTENT---
Design architecture for [feature] with focus on minimal changes.
Prioritize smallest change and maximum reuse of existing code.
Include specific files to create/modify.

---TASK---
id: arch-clean
workdir: .
---CONTENT---
Design architecture for [feature] with focus on clean architecture.
Prioritize maintainability and elegant abstractions.
Include specific files to create/modify.

---TASK---
id: arch-pragmatic
workdir: .
---CONTENT---
Design architecture for [feature] with pragmatic balance.
Balance speed and quality appropriately.
Include specific files to create/modify.
EOF
```

---

**后续操作**（两种模式通用）：
1. Review all approaches and form your opinion on which fits best for this specific task
2. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**
3. **Ask user which approach they prefer**

---

## Phase 5: Implementation

**Goal**: Build the feature

**DO NOT START WITHOUT USER APPROVAL**

根据执行模式选择不同的方式：

---

### 5A. 默认模式：直接实现

**使用 Edit, Write, MultiEdit 工具直接实现代码**：

1. Wait for explicit user approval
2. Read all relevant files identified in previous phases
3. Implement following chosen architecture
4. Follow codebase conventions strictly
5. Write clean, well-documented code
6. Update todos as you progress

---

### 5B. --codex/--gemini 模式：委托实现

**使用 codeagent-wrapper 委托实现**：

```bash
codeagent-wrapper --backend {codex|gemini} - <<'EOF'
Implement [feature] following the chosen architecture.

## Architecture Decision
[Insert chosen architecture from Phase 4]

## Files to Create/Modify
[List from architecture design]

## Requirements
- Follow codebase conventions strictly
- Write clean, well-documented code
- Include necessary tests

## Constraints
- Do NOT run tests (CI will handle)
- Return summary of changes made
EOF
```

**⚠️ Critical Rules（来自 codeagent SKILL.md）**：
- **NEVER kill codeagent processes** — 长时间运行是正常的（通常 2-10 分钟）
- `timeout: 7200000`（固定值）

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct

根据执行模式选择不同的方式：

---

### 6A. 默认模式：使用 Task tool

**使用 Task tool 启动 3 个 code-reviewer agents 并行执行**：

```
Task tool parameters:
- subagent_type: "general-purpose"
- prompt: "Review the code changes for [focus area]. Report issues with confidence >= 80 only."
```

**Different focuses**:
- Simplicity/DRY/elegance
- Bugs/functional correctness
- Project conventions/abstractions

---

### 6B. --codex/--gemini 模式：使用 codeagent-wrapper

**使用 codeagent-wrapper --parallel 并行执行代码审查**：

```bash
codeagent-wrapper --parallel --backend {codex|gemini} <<'EOF'
---TASK---
id: review-simplicity
workdir: .
---CONTENT---
Review the recent code changes for simplicity, DRY principles, and elegance.
Report issues with confidence >= 80 only.
Include file:line references for each issue.

---TASK---
id: review-bugs
workdir: .
---CONTENT---
Review the recent code changes for bugs and functional correctness.
Report issues with confidence >= 80 only.
Include file:line references for each issue.

---TASK---
id: review-conventions
workdir: .
---CONTENT---
Review the recent code changes for project conventions and abstractions.
Report issues with confidence >= 80 only.
Include file:line references for each issue.
EOF
```

---

**后续操作**（两种模式通用）：
1. Consolidate findings and identify highest severity issues that you recommend fixing
2. **Present findings to user and ask what they want to do** (fix now, fix later, or proceed as-is)
3. Address issues based on user decision

---

## Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:
1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

---
