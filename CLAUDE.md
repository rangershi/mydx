# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DX (Developer Experience Toolkit) 是一个 Claude Code 插件，提供团队内部使用的开发者体验工具集。通过命令、Agent 和工作流自动化开发流程。

## 架构

```
mydx/
├── .claude-plugin/marketplace.json    # 插件注册配置
└── dx/
    ├── commands/           # /dx:* 命令定义 (Markdown)
    ├── agents/             # 通用 Agent 定义
    ├── skills/             # Skills 集成
    │   ├── codex-cli/      # Codex CLI 直接调用
    │   ├── gemini-cli/     # Gemini CLI 直接调用
    │   └── product-requirements/  # PRD 生成 (90+ 质量门控)
    ├── hooks/hooks.json    # PR 创建后自动触发评审
    ├── bmad/agents/        # BMAD 敏捷工作流 (po/architect/sm/dev/qa/review)
    ├── feature-dev/agents/ # 功能开发工作流 (explorer/architect/reviewer)
    └── requirements-driven-workflow/agents/  # 需求驱动工作流
```

## 核心命令

| 命令 | 用途 |
|------|------|
| `/dx:doctor` | 环境诊断，检测 Codex CLI、Gemini CLI 等依赖 |
| `/dx:dev` | 轻量级开发流程（简单任务） |
| `/dx:feature-dev` | 功能开发（7 阶段流程，中等复杂度） |
| `/dx:requirements-pilot` | 需求驱动开发（90+ 质量门控） |
| `/dx:bmad-pilot` | 完整敏捷流程（PO→架构→SM→开发→QA→Review） |
| `/dx:ask` | 技术咨询（支持 --codex --gemini 多后端并行） |
| `/dx:pr-review-loop` | PR 评审循环 |

## 后端选择

- **默认 (Claude)**: 通用任务、快速迭代
- **--codex**: 深度代码理解、复杂重构、超出上下文承载时使用
- **--gemini**: 多模态理解、超长上下文

## CLI 直接调用

### Codex CLI

```bash
codex e -C . --skip-git-repo-check --json - <<'EOF'
<task>
EOF
```

### Gemini CLI

```bash
gemini -o stream-json -y -p "$(cat <<'EOF'
<task>
EOF
)"
```

### 并行执行

```bash
# Task 1
(codex e -C . --skip-git-repo-check --json - <<'EOF'
task1 content
EOF
) &
pid1=$!

# Task 2
(codex e -C . --skip-git-repo-check --json - <<'EOF'
task2 content
EOF
) &
pid2=$!

wait $pid1 $pid2
```

**关键规则**:
- 永远不要 kill CLI 进程（2-10 分钟运行是正常的）
- 使用 `timeout: 7200000`

## 开发此插件

### 添加新命令

1. 在 `dx/commands/` 创建 `.md` 文件
2. 在 `.claude-plugin/marketplace.json` 的 `commands` 数组注册

### 添加新 Agent

1. 在 `dx/agents/` 或对应工作流目录创建 `.md` 文件
2. 在 `.claude-plugin/marketplace.json` 的 `agents` 数组注册

### 添加新 Skill

1. 在 `dx/skills/<skill-name>/` 创建 `SKILL.md`
2. 在 `.claude-plugin/marketplace.json` 的 `skills` 数组注册

## Hooks

- `PostToolUse`: PR 创建后自动触发 `/dx:pr-review-loop`

## 工作流复杂度选择

```
大型功能/多角色协作 → /dx:bmad-pilot
需求需确认/质量门控 → /dx:requirements-pilot
单功能/需架构设计   → /dx:feature-dev
简单改动/快速迭代   → /dx:dev
```
