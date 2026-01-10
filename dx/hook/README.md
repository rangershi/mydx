# DX Plugin Post-Command Hooks

命令完成后触发的钩子配置，支持 Context Isolation。

## 配置文件

`post-command-hooks.json` 定义了哪些命令完成后应该触发哪些后续命令。

## 配置格式

```json
{
  "hooks": {
    "<source-command>": {
      "enabled": true,
      "onSuccess": {
        "command": "<target-command>",
        "description": "钩子描述",
        "condition": "条件（可选）",
        "autoRun": true,
        "contextIsolation": true
      }
    }
  }
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用此钩子 |
| `command` | string | 成功后要执行的命令 |
| `description` | string | 钩子用途描述 |
| `condition` | string | 触发条件（可选） |
| `autoRun` | boolean | `true`: 自动执行；`false`: 提示用户确认 |
| `contextIsolation` | boolean | `true`: 清除上下文后执行（使用 Task tool 启动新 Agent） |

## 已配置的钩子

### git-commit-and-pr → pr-review-loop

当 `/git-commit-and-pr` 成功创建 PR 后，**自动**启动 `/pr-review-loop` 进行多轮评审。

**配置**：
- `autoRun: true` - 不询问用户，直接执行
- `contextIsolation: true` - 清除上下文，启动独立 Agent

**流程链路**：
```
/git-commit-and-pr → 创建 Issue/Commit/PR
         ↓
Post-Command Hook 触发
         ↓
Task tool 启动新 Agent（Context Isolation）
         ↓
/pr-review-loop --pr <PR_NUMBER> → 三源并行评审 → 自动修复
```

**为什么需要 Context Isolation**：
- 避免 git-commit-and-pr 的上下文污染评审流程
- pr-review-loop 需要独立的上下文窗口进行三 Agent 并行评审
- 防止 Context Degradation（上下文退化）

## 实现方式

当 `contextIsolation: true` 时，使用 Task tool 启动新 Agent：

```
Task tool:
- subagent_type: "general-purpose"
- description: "PR review loop for PR #<NUMBER>"
- prompt: |
    执行 /pr-review-loop --pr <PR_NUMBER>

    这是一个独立的评审任务，请按照 pr-review-loop 命令的流程执行。
```

## 扩展新钩子

在 `post-command-hooks.json` 中添加新的命令映射：

```json
{
  "hooks": {
    "your-command": {
      "enabled": true,
      "onSuccess": {
        "command": "/next-command",
        "description": "描述",
        "autoRun": true,
        "contextIsolation": true
      }
    }
  }
}
```
