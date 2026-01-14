---
allowed-tools: [Bash, Read, Glob, TodoWrite, Edit, Grep, Task]
description: '统一 Git 工作流：Issue/Commit/PR 自动化'
model: haiku
---

## 用法

```bash
/git-commit-and-pr                           # 自动检测并执行所需阶段
/git-commit-and-pr --issue <ID>              # 指定关联 Issue
/git-commit-and-pr --issue-only              # 仅创建 Issue
/git-commit-and-pr --pr --base <BRANCH>      # 仅创建 PR
```

---

## 执行流程

### Step 1: 状态检测

并行执行：
```bash
git status --short
git branch --show-current
git log -1 --format='%H %s' 2>/dev/null || echo "no-commits"
```

根据状态决定执行阶段：
- 无 Issue 或 `--issue-only` → 执行 Issue 创建
- 有未提交修改 → 执行 Commit 流程
- 工作树干净且在功能分支 → 执行 PR 创建

**禁止在 main/master 直接提交。**

---

### Step 2: Issue 创建（可选）

**使用 Task 调用 `dx:issue-creator` agent：**
```
prompt: |
  分析当前对话历史和代码变更，创建 GitHub Issue。

  用户参数：
  - title: <用户提供的标题，如有>
  - labels: <用户提供的标签，如有>

  执行 git diff --stat 获取变更范围。
  使用 gh issue create 创建 Issue。
  输出 Issue 编号和链接。
```

`--issue-only` 时在此终止。

---

### Step 3: Commit 流程

#### 3.1 暂存变更

```bash
git add -A
git diff --cached --stat
```

#### 3.2 生成提交

分析 `git diff --cached` 内容，生成 commit message：

```bash
git commit -F - <<'EOF'
<type>: <概要>

变更说明：
- <变更项1>
- <变更项2>

Refs: #<issue-id>
EOF
```

type 类型：feat/fix/refactor/docs/chore/test

#### 3.3 确认提交

```bash
git status
git log -1 --oneline
```

---

### Step 4: PR 创建

#### 4.1 推送分支

```bash
git push -u origin HEAD
```

#### 4.2 分析变更

```bash
git log origin/master..HEAD --oneline
git diff origin/master...HEAD --stat
```

#### 4.3 创建 PR

```bash
gh pr create --title '<type>: <概要>' --body-file - <<'EOF'
## 变更说明

- <变更项>

## 测试

- [ ] 本地测试通过

Closes: #<issue-id>
EOF
```

---

## 输出格式

**成功：**
```
✅ 完成

Issue: #<编号> <标题>
Commit: <hash> <主题>
PR: #<编号> → <URL>
```

**部分完成：**
```
⚠️ 停止于 [阶段]

已完成：<列表>
阻塞：<原因>
继续：/git-commit-and-pr --issue <编号>
```
