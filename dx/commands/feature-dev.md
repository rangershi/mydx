---
description: Guided feature development with codebase understanding and architecture focus
argument-hint: Optional feature description [--codex|--gemini]
---

## Usage
`/dx:feature-dev [FEATURE_DESCRIPTION] [OPTIONS]`

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply, identify and ask about all underspecified details, design elegant architectures, then implement.

---

## 执行模式

用户通过参数直接指定执行模式：

| 参数 | 执行模式 | 适用场景 |
|------|----------|----------|
| （默认） | 直接执行 | 大多数任务，使用 Task tool 调用 agents |
| `--codex` | 委托 Codex CLI | 复杂任务、需要深度推理和 Context Isolation |
| `--gemini` | 委托 Gemini CLI | Gemini 后端任务 |

### 设计原理（基于 Multi-Agent Patterns）

**默认直接执行**使用 Task tool 调用 agents，适合大多数场景：
- **避免 Telephone Game** — 直接调用减少信息传递层级
- **Context 共享** — Orchestrator 可直接读取 agent 返回的文件列表

**委托模式**使用对应 CLI，适用于需要 Context Isolation 的场景：
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

### 2B. --codex/--gemini 模式：使用 CLI 并行执行

**--codex 模式**：使用 Codex CLI 并行执行多个探索任务：

```bash
# Task 1: Explore similar features
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Find features similar to [feature] and trace through their implementation comprehensively.
Return a list of 5-10 key files to read.
EOF
) &
pid1=$!

# Task 2: Explore architecture
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Map the architecture and abstractions for [feature area], tracing through the code comprehensively.
Return a list of 5-10 key files to read.
EOF
) &
pid2=$!

# Task 3: Explore patterns
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Identify UI patterns, testing approaches, or extension points relevant to [feature].
Return a list of 5-10 key files to read.
EOF
) &
pid3=$!

wait $pid1 $pid2 $pid3
```

**--gemini 模式**：使用 Gemini CLI 并行执行：

```bash
# Task 1
(gemini -o stream-json -y -p "$(cat <<'EOF'
Find features similar to [feature] and trace through their implementation.
Return a list of 5-10 key files.
EOF
)") &
pid1=$!

# Task 2
(gemini -o stream-json -y -p "$(cat <<'EOF'
Map the architecture for [feature area].
Return a list of 5-10 key files.
EOF
)") &
pid2=$!

wait $pid1 $pid2
```

---

**后续操作**（两种模式通用）：
1. Once the agents return, please read all files identified by agents to build deep understanding
2. Present comprehensive summary of findings and patterns discovered

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

### 3.1 需求澄清（显性调用 @product-requirements skill）

**触发条件**: 功能需求需要结构化澄清，或需要生成正式 PRD 文档时

**调用方式**:
```
调用 @product-requirements skill 进行交互式需求澄清：

Context:
- Feature Name: {feature_name}
- Initial Request: $ARGUMENTS
- Codebase Findings: [Phase 2 探索结果摘要]

Task: 通过质量评分（100分制）和迭代对话，将功能需求转化为清晰的 PRD 文档。

Expected Output:
- 质量分达到 90+ 的 PRD 文档
- 保存到 docs/{feature_name}-prd.md
```

**Skill 职责**（基于 tool-design 原则）:
- **What**: 交互式需求澄清，质量评分，专业 PRD 生成
- **When**: 功能需求不够清晰、需要结构化文档、复杂功能需要质量门控时
- **Returns**: `docs/{feature_name}-prd.md` 文件，供架构设计阶段使用

**何时跳过 Skill**:
- 需求已经非常清晰（用户明确表示不需要 PRD）
- 简单功能改动（如 UI 微调、配置变更）
- 用户已提供完整需求文档

### 3.2 补充澄清（Skill 之后或代替 Skill）

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

### 4B. --codex/--gemini 模式：使用 CLI 并行设计

**--codex 模式**：使用 Codex CLI 并行设计多个方案：

```bash
# Architecture 1: Minimal changes
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Design architecture for [feature] with focus on minimal changes.
Prioritize smallest change and maximum reuse of existing code.
Include specific files to create/modify.
EOF
) &
pid1=$!

# Architecture 2: Clean architecture
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Design architecture for [feature] with focus on clean architecture.
Prioritize maintainability and elegant abstractions.
Include specific files to create/modify.
EOF
) &
pid2=$!

# Architecture 3: Pragmatic balance
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Design architecture for [feature] with pragmatic balance.
Balance speed and quality appropriately.
Include specific files to create/modify.
EOF
) &
pid3=$!

wait $pid1 $pid2 $pid3
```

**--gemini 模式**：类似方式使用 `gemini -o stream-json -y -p "$(cat <<'EOF' ... EOF)"`

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

**--codex 模式**：使用 Codex CLI 委托实现：

```bash
codex e -C . --skip-git-repo-check --json - <<'EOF'
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

**--gemini 模式**：使用 Gemini CLI 委托实现：

```bash
gemini -o stream-json -y -p "$(cat <<'EOF'
Implement [feature] following the chosen architecture.

## Architecture Decision
[Insert chosen architecture from Phase 4]

## Files to Create/Modify
[List from architecture design]

## Requirements
- Follow codebase conventions strictly
- Write clean, well-documented code
EOF
)"
```

**⚠️ Critical Rules**：
- **NEVER kill CLI processes** — 长时间运行是正常的（通常 2-10 分钟）
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

### 6B. --codex/--gemini 模式：使用 CLI 并行审查

**--codex 模式**：使用 Codex CLI 并行执行代码审查：

```bash
# Review 1: Simplicity
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Review the recent code changes for simplicity, DRY principles, and elegance.
Report issues with confidence >= 80 only.
Include file:line references for each issue.
EOF
) &
pid1=$!

# Review 2: Bugs
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Review the recent code changes for bugs and functional correctness.
Report issues with confidence >= 80 only.
Include file:line references for each issue.
EOF
) &
pid2=$!

# Review 3: Conventions
(codex e -C . --skip-git-repo-check --json - <<'EOF'
Review the recent code changes for project conventions and abstractions.
Report issues with confidence >= 80 only.
Include file:line references for each issue.
EOF
) &
pid3=$!

wait $pid1 $pid2 $pid3
```

**--gemini 模式**：类似方式使用 `gemini -o stream-json -y -p "$(cat <<'EOF' ... EOF)"`

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
