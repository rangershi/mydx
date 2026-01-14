---
allowed-tools: [Bash, Read, Glob, TodoWrite, Edit, Grep, Task]
description: '统一 Git 工作流：多代理协作的 Issue/Commit/PR 自动化'
model: haiku
---

## Usage

```bash
/git-commit-and-pr [--issue <ID>] [--message <MSG>]  # 默认：自动执行所需阶段
/git-commit-and-pr --issue-only [--title <T>] [--labels <l1,l2>]  # 仅创建 Issue
/git-commit-and-pr --all [--issue <ID>] [--base <BRANCH>]  # 全流程
/git-commit-and-pr --pr [--issue <ID>] [--base <BRANCH>]  # 仅创建 PR
```

---

## 架构

```
Orchestrator
├── issue-creator agent     → Issue 创建
├── quality-guard agent     → 增量预检
├── commit-composer agent   → 提交生成
└── pr-composer agent       → PR 创建
```

**核心原则**：Agent 直接输出结果，Orchestrator 不做二次合成（避免 Telephone Game）。

---

## Phase 0: 状态评估

**并行执行：**
```bash
git status --short
git branch --show-current
git log -1 --format='%H %s' 2>/dev/null || echo "no-commits"
```

**模式识别：**
| 条件 | 执行阶段 |
|------|----------|
| 缺 Issue 或 `--issue-only` | Phase 1 |
| 有未提交修改且非 `--pr` | Phase 2 |
| 工作树干净且在功能分支 | Phase 3 |

**分支规则**：禁止在 main/master 直接提交，功能分支命名 `<type>/<issue-id>-<desc>`

---

## Phase 1: Issue 创建

**调用 issue-creator agent：**
```
输入：git status, git diff --stat, 用户参数 (title/labels/assignees)
职责：
1. 从对话历史提取需求背景
2. 分析代码变更范围
3. 使用 gh CLI + heredoc 创建 Issue
4. 直接输出 Issue 编号与链接
```

`--issue-only` 时在此终止。

---

## Phase 2: Commit 流程

### Step 2.1: 质量门禁

**调用 quality-guard agent：**
```
执行序列（按需）：
1. ./scripts/dx lint（必跑）
2. ./scripts/dx build backend（后端改动）
3. ./scripts/dx build sdk（DTO/API 变更，紧随 backend）
4. ./scripts/dx build front（前端改动）
5. ./scripts/dx build admin（admin 改动）

并行：lint ∥ build backend，build front ∥ build admin
失败时停止并输出修复建议
```

### Step 2.2: 提交生成

**调用 commit-composer agent：**
```
输入：git diff --stat, git diff, Issue ID
输出格式：
git commit -F - <<'MSG'
<type>: <概要>

变更说明：
- ...

Refs: #<issue-id>
MSG

执行后 git status 确认工作树干净
```

---

## Phase 3: PR 创建

**前置检查**：确认在功能分支且工作树干净，否则回退 Phase 2

**调用 pr-composer agent：**
```
分析：git log <base>..HEAD --oneline, git diff <base>...HEAD --stat

生成：
1. PR 标题
2. 变更概览
3. 测试结果
4. 风险评估（高风险：main分支/数据库schema/认证支付）
5. Closes: #<issue-id>

执行：
gh pr create --title '<标题>' --body-file - <<'MSG'
## 变更说明
...
## 测试结果
...
## 风险评估
...
Closes: #<issue-id>
MSG
```

---

## 输出规范

**成功：**
```
✅ 全流程完成

Issue: #<编号> <标题>
Commit: <hash> <主题>
PR: #<编号> <标题> → <URL>

📋 后续步骤：/dx:pr-review-loop --pr <编号>
```

**部分完成：**
```
⚠️ 流程在 [阶段名] 停止

已完成：
- Issue: #<编号>

阻塞原因：<错误摘要>
修复后重新运行：/git-commit-and-pr --issue <编号>
```

---

## 关键约束

- 所有多行文本使用 heredoc，禁止 `-m` 嵌入
- 增量预检通过是提交前置条件
- Agent 失败时提供降级策略（跳过/模板/手动命令）
- 使用 Task tool 调用 agent，优先 codeagent skill (backend: codex)
