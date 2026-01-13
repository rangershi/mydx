---
allowed-tools: [Bash, Read, Glob, TodoWrite, Edit, Grep, Task]
description: '统一 Git 工作流：多代理协作的 Issue/Commit/PR 自动化'
model: haiku
---

## Usage

```bash
# 默认：根据状态自动执行所需阶段
/git-commit-and-pr [--issue <ISSUE_ID>] [--message <COMMIT_MESSAGE>]

# 仅创建 Issue
/git-commit-and-pr --issue-only [--title <TITLE>] [--labels <l1,l2>]

# 全流程：Issue → Commit → PR
/git-commit-and-pr --all [--issue <ISSUE_ID>] [--base <BASE_BRANCH>]

# 仅创建 PR（工作目录需干净）
/git-commit-and-pr --pr [--issue <ISSUE_ID>] [--base <BASE_BRANCH>]
```

---

## 多代理架构设计

### 架构模式：Supervisor + Specialists

```
Orchestrator (命令层)
├── issue-creator agent     → Issue 内容分析与创建
├── quality-guard agent     → 增量预检与构建验证
├── commit-composer agent   → 提交信息生成
└── pr-composer agent       → PR 内容生成与创建
```

### 设计原则（基于 Multi-Agent Patterns 最佳实践）

| 原则 | 实现 |
|------|------|
| **Context Isolation** | 每个 Agent 独立上下文窗口，避免互相污染 |
| **Structured Handoff** | 使用明确的数据结构传递状态，避免 Telephone Game |
| **Direct Response** | Agent 可直接输出结果到用户，Orchestrator 不做二次合成 |
| **Failure Isolation** | 单个 Agent 失败不阻塞整体流程，提供降级策略 |

**⚠️ Telephone Game 问题与解决方案**

LangGraph 基准测试发现 supervisor 架构因"传话游戏"问题导致性能下降 50%——supervisor 转述 sub-agent 响应时丢失关键信息。

**解决方案：Direct Response 模式**
- Agent 创建 Issue/PR 后直接输出结果，Orchestrator 不做内容合成
- Orchestrator 仅负责调度与状态管理
- 需要保留原始格式时，使用 `forward_message` 模式直接传递

---

## 阶段定义

### Phase 0: 状态评估（Orchestrator 直接执行）

**并行执行以下检查：**

```bash
# 同时执行，无依赖关系
git status --short
git branch --show-current
git log -1 --format='%H %s' 2>/dev/null || echo "no-commits"
```

**分支策略判定：**
- 若在 `main`/`master`：要求用户提供 Issue ID 或创建 Issue 后切换分支
- 功能分支命名：`<type>/<issue-id>-<description>`

**模式识别：**

| 条件 | 执行阶段 |
|------|----------|
| 缺 Issue 或 `--issue-only` | Phase 1 |
| 有未提交修改且非 `--pr` | Phase 2 |
| 工作树干净且在功能分支 | Phase 3 |

---

### Phase 1: Issue 创建（Delegate to issue-creator agent）

**触发条件：** 缺少 Issue ID / `--issue-only` / 主分支需创建分支

**Agent 调用协议：**

```
Task tool → issue-creator agent

Prompt:
"基于当前对话上下文和代码变更创建 GitHub Issue。

输入上下文：
- git status 输出
- git diff --stat 输出（如有改动）
- 用户提供的参数：title/labels/assignees

职责：
1. 从对话历史提取需求背景
2. 分析代码变更范围与影响
3. 检查是否有重复 Issue
4. 生成结构化 Issue 内容
5. 使用 gh CLI + heredoc 创建
6. 返回 Issue 编号与链接"
```

**Direct Response 模式：** agent 创建成功后直接输出 Issue 信息，Orchestrator 不做二次合成。

**`--issue-only` 终止点：** 输出后续提交时引用 Issue 的提示。

---

### Phase 2: Commit 流程

#### Step 2.1: 质量门禁（Delegate to quality-guard agent）

**Agent 调用协议：**

```
Task tool → codeagent skill (backend: codex)

Prompt:
"执行增量预检并验证构建通过。

检测改动范围：
1. 识别改动文件类型（后端/前端/admin/shared）
2. 确定需要执行的检查序列

执行序列（按需）：
1. ./scripts/dx lint（必跑）
2. ./scripts/dx build backend（后端改动时）
3. ./scripts/dx build sdk（DTO/API 变更时，紧随 backend）
4. ./scripts/dx build front（前端改动时）
5. ./scripts/dx build admin（admin 改动时）

并行优化：
- lint 与 build backend 可并行（无依赖）
- build front 与 build admin 可并行（无依赖）

输出要求：
- 逐步报告执行结果
- 失败时明确说明阻塞原因
- 成功时返回简洁确认"
```

**失败处理：** 预检失败必须停止，输出修复建议。

#### Step 2.2: 提交生成（Delegate to commit-composer agent）

**Agent 调用协议：**

```
Task tool → codeagent skill (backend: codex)

Prompt:
"基于代码变更生成规范化提交信息。

输入：
- git diff --stat
- git diff（核心文件片段）
- Issue ID: #<id>

生成规范：
- Conventional Commits 格式
- 中文描述（2-4 条 bullet）
- 末尾 Refs: #<issue-id> 或 Closes: #<issue-id>

输出格式（heredoc）：
git commit -F - <<'MSG'
<type>: <概要>

变更说明：
- ...
- ...

Refs: #<issue-id>
MSG

执行提交后运行 git status 确认工作树干净。"
```

---

### Phase 3: PR 流程（Delegate to pr-composer agent）

**前置检查（Orchestrator 执行）：**
- 确认在功能分支且工作树干净
- 若有未提交修改，回退至 Phase 2

**Agent 调用协议：**

```
Task tool → codeagent skill (backend: codex)

Prompt:
"基于提交历史生成 PR 并创建。

分析内容：
- git log <base>..HEAD --oneline
- git diff <base>...HEAD --stat

生成内容：
1. PR 标题（简洁描述核心变更）
2. 变更概览（分模块说明）
3. 测试/验证结果
4. 风险评估与回滚策略
5. Issue 关联：Closes: #<issue-id>

高风险判定（需额外确认）：
- 目标分支为 main
- 涉及数据库 schema 变更
- 涉及认证/支付等核心模块

使用 heredoc 执行：
gh pr create --title '<标题>' --body-file - <<'MSG'
## 变更说明
...

## 测试结果
...

## 风险评估
...

Closes: #<issue-id>
MSG

创建成功后更新 Issue 评论并附 PR 链接。"
```

---

## Agent 协作规范

### 1. Handoff Protocol（Structured Handoff）

**核心原则**：使用明确的数据结构传递状态，避免自然语言传递导致的信息丢失。

| 源 Agent | 目标 Agent | 传递数据（结构化） |
|----------|------------|-------------------|
| Orchestrator | issue-creator | `{ gitStatus, diffStat, userParams: { title?, labels?, assignees? } }` |
| Orchestrator | quality-guard | `{ changedFiles: string[], changeTypes: ('backend'|'front'|'admin'|'shared')[] }` |
| issue-creator | Orchestrator | `{ issueId: number, url: string, title: string }` |
| quality-guard | Orchestrator | `{ passed: boolean, errors?: { step: string, message: string }[] }` |
| Orchestrator | commit-composer | `{ issueId: number, diff: string, diffStat: string }` |
| Orchestrator | pr-composer | `{ issueId: number, commitLog: string, baseBranch: string, riskLevel: 'high'|'medium'|'low' }` |

### 2. Direct Response 模式

**目的**：避免 Telephone Game 问题，Agent 直接输出关键信息到用户。

| 场景 | Agent 直接输出 | Orchestrator 行为 |
|------|---------------|------------------|
| Issue 创建成功 | Issue ID、URL、标题 | 仅记录状态，不转述 |
| 质量检查日志 | 执行步骤与结果 | 透传，不合成 |
| PR 创建成功 | PR 链接、后续动作提示 | 仅补充下一步指引 |
| 错误详情 | 具体错误信息与修复建议 | 不做二次解释 |

### 3. 错误传播与恢复（Failure Isolation）

```
Agent 失败 → 返回结构化错误 → Orchestrator 判定：
├── 可重试（网络/临时错误）→ 重试一次，记录 fallback
├── 需用户介入（权限/配置）→ 输出指导并停止
└── 致命错误（数据不一致）→ 输出诊断并停止

错误结构：{ type: 'retryable'|'user_action'|'fatal', message: string, suggestion?: string }
```

**降级策略**：
- `quality-guard` 超时 → 跳过预检，提示用户手动验证
- `commit-composer` 失败 → 回退到基础模板提交
- `pr-composer` 失败 → 提供手动创建 PR 的命令

---

## 并行执行优化

### 可并行操作

| 操作组 | 并行项 |
|--------|--------|
| 初始状态检查 | git status, git branch, git log |
| 增量预检 | lint ∥ build backend（无依赖时） |
| 分应用构建 | build front ∥ build admin |

### 串行强制点

```
lint → [若失败停止]
build backend → build sdk（SDK 依赖 backend 产物）
所有构建 → commit → push → PR
```

---

## 输出规范

### 成功输出

```
✅ 全流程完成

Issue: #<编号> <标题>
Commit: <hash> <主题>
PR: !<编号> <标题> → <URL>

📋 后续步骤：使用 /pr-review-loop 进行多轮评审与自动修复
```

---

## 自动触发 PR 评审循环

PR 创建成功后，**本命令内部**自动触发评审流程（无需外部 hook）。

### 执行流程

```
Phase 3 完成 → gh pr create 成功
            → 提取 PR 编号
            → 使用 Task tool 启动新 Agent（Context Isolation）
            → 新 Agent 执行 /dx:pr-review-loop --pr <PR_NUMBER>
```

### Phase 3.5: 自动启动评审循环（必须执行）

**在 Phase 3 的 `gh pr create` 成功后，立即执行以下步骤：**

1. **从 gh pr create 输出中提取 PR 编号**
   ```bash
   # gh pr create 输出格式：https://github.com/owner/repo/pull/123
   # 提取 PR 编号
   PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
   ```

2. **使用 Task tool 启动独立评审 Agent**
   ```
   Task tool:
   - subagent_type: "general-purpose"
   - description: "PR review loop for PR #${PR_NUMBER}"
   - prompt: |
       执行 /dx:pr-review-loop --pr ${PR_NUMBER}

       这是一个独立的评审任务，请按照 pr-review-loop 命令的流程执行。
   ```

3. **输出启动信息**
   ```
   🔗 自动启动 PR 评审循环...
      PR: #${PR_NUMBER}
      Context Isolation: 启动独立评审 Agent
   ```

**⚠️ 重要：此步骤是强制执行的，不可跳过。**

### 为什么需要 Context Isolation

- 避免 git-commit-and-pr 的上下文污染评审流程
- pr-review-loop 需要独立的上下文窗口进行三 Agent 并行评审
- 防止 Context Degradation（上下文退化）

### 示例输出

```
✅ 全流程完成

Issue: #123 添加用户认证功能
Commit: abc1234 feat(auth): implement user authentication
PR: !456 feat(auth): implement user authentication → https://github.com/org/repo/pull/456

🔗 自动启动 PR 评审循环...
   Context Isolation: 启动独立评审 Agent

---

[新 Agent 上下文开始]
🔄 第 1/3 轮评审开始...
```

### 部分完成输出

```
⚠️ 流程在 [阶段名] 停止

已完成：
- Issue: #<编号>

阻塞原因：
- lint 失败：<错误摘要>

修复后重新运行：/git-commit-and-pr --issue <编号>
```

---

## 关键约束

### Git 操作
- 命令在仓库根目录执行，统一 SSH 认证
- 所有多行文本使用 heredoc，禁止 `-m` 嵌入
- 禁止未确认的破坏性操作

### 分支策略
- 禁止在 main/master 直接提交
- 功能分支：`<type>/<issue-id>-<description>`

### 质量门禁
- 增量预检通过是提交前置条件
- 高风险改动需列出回滚方案

### Agent 调用
- 使用 Task tool 或 Skill tool 调用 agent/skill
- 每个 agent/skill 需明确输入/输出契约
- 优先使用 codeagent skill（支持多后端：codex/claude/gemini）

---

## 工作流衔接

### PR 创建后的评审闭环

本命令完成 Issue → Commit → PR 创建后，建议使用 `/pr-review-loop` 进行后续评审：

```bash
# PR 创建后自动进入评审循环
/pr-review-loop --pr <PR_NUMBER>

# 或自动识别当前分支 PR
/pr-review-loop
```

**pr-review-loop 能力**：
- 三 Agent 并行评审（codex-review + review + pr-comments-analyzer）
- 人工评论线程自动分析与优先级分类
- 自动修复 + 最多 3 轮迭代收敛
- 结构化评审报告发布到 PR 评论

**工作流完整链路**：
```
/git-commit-and-pr → 创建 Issue/Commit/PR
         ↓
/pr-review-loop → 三源并行评审 → 自动修复 → 评审通过
         ↓
人工审批 → 合并
```
