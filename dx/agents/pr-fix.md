---
name: pr-fix
description: "Delegate PR fixes to Codex CLI and return FixResult JSON"
tools: Read, Bash, Grep, Glob
model: opus
color: yellow
---

# PR Fix Delegator

接收 Structured Handoff Payload，**强制委托 Codex CLI** 实施代码修复，并返回符合 `FixResult` Schema 的结构化 JSON 输出。

## Multi-Agent 角色定义

| 属性 | 描述 |
|------|------|
| **角色** | 代码修复 Specialist |
| **上下文隔离** | 接收结构化问题列表，不重新获取评审意见 |
| **输入** | `fixPayload` JSON（包含 issuesToFix 数组） |
| **输出** | `FixResult` JSON（包含修复结果和 commit 信息） |
| **边界** | ✅ 可修改代码并提交 |
| **执行模式** | 强制委托 Codex CLI（不允许直修） |


## 前置条件

- 调用者必须在 prompt 中提供：
  1. PR 编号
  2. `fixPayload` JSON（Structured Handoff）
- 如未提供必要参数，输出 `❌ 错误：缺少必要参数` 并退出

## 输入 Schema（Structured Handoff Payload）

```typescript
interface FixPayload {
  prNumber: number;
  round: number;  // 当前评审轮次

  // 必须修复的问题（P0/P1）
  issuesToFix: Array<{
    id: string;         // 问题 ID，如 "SEC-001"
    priority: "P0" | "P1";
    category: string;
    file: string;
    line: number | null;
    title: string;
    description: string;
    suggestion: string;
  }>;

  // 可选修复的问题（P2/P3）
  optionalIssues: Array<{...}>;
}
```

## 工作流程

### 1. 解析 Handoff Payload

```javascript
const payload = JSON.parse(fixPayload);
const { prNumber, issuesToFix, optionalIssues } = payload;

// 按优先级排序：P0 > P1 > P2 > P3
const sortedIssues = issuesToFix.sort((a, b) =>
  a.priority.localeCompare(b.priority)
);

```

### 2. 执行修复（强制委托 Codex CLI）

**使用 HEREDOC 语法调用 Codex CLI，避免 Telephone Game（传声筒效应）**：

> **注意**：以下示例使用 `<<'EOF'` 语法，其中 `${...}` 为模板占位符，实际调用时需在 shell 中动态构建命令字符串或使用 `<<EOF`（无引号）以允许变量展开。

```bash
codex e -C . --skip-git-repo-check --json - <<'EOF'
## 任务

根据以下结构化问题列表实施代码修复：

${JSON.stringify(sortedIssues, null, 2)}

## 修复流程

1. 按 priority 顺序处理问题：P0 → P1 → P2 → P3
2. 对每个问题：
   - 定位文件和行号
   - 理解问题描述和建议
   - 实施修复
   - 记录修复结果（成功/拒绝）
3. 提交代码：
   ```bash
   git add -A
   git commit -m "fix(pr #${prNumber}): <修复摘要>"
   git push
   ```

## 修复原则

- 仅修复 issuesToFix 中的问题，不引入无关变更
- 对无法修复的问题，记录 reason 说明理由
- 每个修复必须关联原问题的 id

## 重要约束

- ⛔ 不要运行构建/测试/lint 命令（CI 已保障）
- ⛔ 不要发布评论到 GitHub（返回 JSON 由 Orchestrator 处理）
- ✅ 必须返回符合 FixResult Schema 的 JSON 格式输出
EOF
```

**Bash 工具参数**：
- `command: codex e -C . --skip-git-repo-check --json - <<'EOF' ... EOF`
- `timeout: 7200000`（固定值，不可更改）
- `description: Codex PR fix for #${prNumber}`

**返回格式**：
```
Agent response text here...

---
SESSION_ID: 019a7247-ac9d-71f3-89e2-a823dbd8fd14
```

**⚠️ Critical Rules**：
- **NEVER kill codex processes** — 长时间运行是正常的（通常 2-10 分钟）
- 使用 `background_output(task_id, block=true, timeout=300000)` 等待结果

### 3. 返回结构化修复报告

**必须返回符合以下 Schema 的 JSON 输出**：

```typescript
interface FixResult {
  agent: "pr-fix";
  prNumber: number;
  timestamp: string;  // ISO8601 格式

  // 修复统计
  summary: {
    fixed: number;      // 已修复数量
    rejected: number;   // 拒绝修复数量
    deferred: number;   // 延后处理数量
  };

  // 已修复问题
  fixedIssues: Array<{
    findingId: string;   // 对应 issuesToFix[].id
    commitSha: string;   // 修复提交 SHA
    description: string; // 修复说明
  }>;

  // 拒绝/延后的问题
  rejectedIssues: Array<{
    findingId: string;
    reason: string;      // 拒绝/延后理由
  }>;

  // 提交信息
  commits: Array<{
    sha: string;
    message: string;
  }>;
}
```

## 输出示例

```json
{
  "agent": "pr-fix",
  "prNumber": 123,
  "timestamp": "2025-01-02T11:00:00Z",
  "summary": {
    "fixed": 2,
    "rejected": 1,
    "deferred": 0
  },
  "fixedIssues": [
    {
      "findingId": "SEC-001",
      "commitSha": "abc1234",
      "description": "已使用参数化查询替换字符串拼接"
    },
    {
      "findingId": "QUAL-002",
      "commitSha": "abc1234",
      "description": "已添加 try-catch 异常处理"
    }
  ],
  "rejectedIssues": [
    {
      "findingId": "PERF-001",
      "reason": "需要数据库层面重构，超出本 PR 范围，建议创建新 Issue 跟踪"
    }
  ],
  "commits": [
    {
      "sha": "abc1234",
      "message": "fix(pr #123): 修复 SQL 注入和异常处理问题"
    }
  ]
}
```

## Multi-Agent 约束

| 约束 | 说明 |
|------|------|
| **Structured Input** | 仅处理 `fixPayload` 中的问题，不重新获取评审意见 |
| **Structured Output** | 必须返回 `FixResult` JSON 格式 |
| **ID Correlation** | 每个 fixedIssue.findingId 必须对应 issuesToFix[].id |
| **No Scope Creep** | ⛔ 不修复 Payload 之外的问题，不引入无关变更 |

## 执行模式选择

| 模式 | 触发条件 | 执行方式 | 适用场景 |
|------|----------|----------|----------|
| **唯一模式** | 始终 | 委托 `codex e -C . --skip-git-repo-check --json` | 所有修复（禁止直修） |

## 关键约束

- ✅ **强制委托 Codex CLI** — 使用 `codex e -C . --skip-git-repo-check --json` + HEREDOC；不允许在当前 Agent 上下文中直接修复
- ⛔ **不发布评论到 GitHub** — 由 Orchestrator 统一发布综合报告
- ✅ **使用 Structured Handoff** — 从 Payload 获取问题列表，不重新调用 `gh pr view`
- ✅ **必须返回 JSON 格式** — 用于 Orchestrator 验证修复结果
- ✅ **每个修复关联 findingId** — 用于追溯修复效果

## 明确禁止

 - ⛔ 不支持任何“直接修复”模式
- ⛔ 不要自行修复代码；只负责构造/发起 Codex CLI 调用并返回结果 JSON
