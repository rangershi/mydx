# DX - Developer Experience Toolkit

团队内部使用的开发者体验工具集，提供符合团队流程的命令和自动化 Agent。

## 功能

- **Commands**: 用户触发的开发流程命令
- **Agents**: 自动化执行的智能代理
- **Skills**: 专业领域知识和工具集成
- **Workflows**: BMAD、Requirements-Driven 等完整开发流程

## 快速开始

### 1. 环境检测

首次使用前，运行环境诊断命令检测依赖是否已安装：

```bash
/dx:doctor
```

该命令会检测 `codeagent-wrapper` 等必要工具是否已安装，如未安装会提示自动安装。

### 2. 安装插件

#### 方式一：通过插件市场安装（推荐）

```bash
# 在 Claude Code 中运行
/install-plugin https://github.com/rangershi/mydx
```

安装完成后，插件会自动加载，无需额外配置。

#### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/rangershi/mydx.git

# 在 Claude Code 中加载插件
claude --plugin-dir /path/to/mydx
```

#### 方式三：项目级安装

将插件克隆到项目的 `.claude-plugin/` 目录下，Claude Code 会自动识别并加载：

```bash
cd your-project
git clone https://github.com/rangershi/mydx.git .claude-plugin/mydx
```

## 执行模式

默认情况下，大多数命令使用 **Claude 当前模型** 进行分析和执行。

### 开发命令 (`/dx:dev`)

可以通过参数选择不同的执行后端：

| 参数 | 说明 |
|------|------|
| (默认) | 使用 Claude 当前模型直接执行 |
| `--codex` | 委托给 OpenAI Codex CLI 执行 |
| `--gemini` | 委托给 Google Gemini CLI 执行 |

**示例**：

```bash
# 使用 Claude 执行（默认）
/dx:dev 实现用户登录功能

# 委托给 Codex 执行
/dx:dev --codex 实现用户登录功能

# 委托给 Gemini 执行
/dx:dev --gemini 实现用户登录功能
```

### PR 评审循环 (`/dx:pr-review-loop`) - 特殊说明

> **注意**：此命令与其他命令不同，**默认使用 Codex (codeagent-wrapper)** 进行代码修复，而非 Claude。
>
> 这是因为 PR 评审循环涉及多轮复杂修复，使用 Codex 可以更好地处理 Context Isolation。

| 参数 | 说明 |
|------|------|
| (默认) | 使用 Codex (codeagent-wrapper) 执行代码修复 |
| `--nocodex` | 使用 Claude 当前模型直接执行修复 |

**示例**：

```bash
# 默认模式：使用 Codex 修复（推荐，适合复杂问题）
/dx:pr-review-loop

# nocodex 模式：使用 Claude 直接修复
# 适合简单问题，可减少 token 消耗约 15 倍
/dx:pr-review-loop --nocodex

# 指定 PR 编号
/dx:pr-review-loop --pr 123
/dx:pr-review-loop --pr 123 --nocodex
```

## 主要命令

| 命令 | 说明 |
|------|------|
| `/dx:doctor` | 环境诊断，检测并安装依赖 |
| `/dx:dev` | 轻量级开发流程 |
| `/dx:code` | 代码生成 |
| `/dx:bugfix` | Bug 修复 |
| `/dx:code-entropy-scan` | 代码熵扫描分析 |
| `/dx:git-commit-and-pr` | 提交代码并创建 PR |
| `/dx:pr-review-loop` | PR 评审循环 |
| `/bmad:bmad-pilot` | BMAD 敏捷流程 |
| `/feature-dev:feature-dev` | 功能开发流程 |
| `/requirements-driven-workflow:requirements-pilot` | 需求驱动开发流程 |

## 目录结构

```
mydx/
├── .claude-plugin/
│   └── marketplace.json    # 插件配置
├── dx/
│   ├── commands/           # 命令定义
│   ├── agents/             # Agent 定义
│   ├── skills/             # Skills 定义
│   ├── hooks/              # Hooks 配置（标准 Claude Code 格式）
│   ├── bmad/               # BMAD 工作流
│   ├── feature-dev/        # 功能开发工作流
│   └── requirements-driven-workflow/  # 需求驱动工作流
└── README.md
```

## 添加新组件

### 添加 Command

1. 在 `dx/commands/` 目录创建 `.md` 文件
2. 在 `.claude-plugin/marketplace.json` 的对应插件 `commands` 数组中注册

### 添加 Agent

1. 在 `dx/agents/` 目录创建 `.md` 文件
2. 在 `.claude-plugin/marketplace.json` 的对应插件 `agents` 数组中注册

## 致谢

本项目大量代码来源于以下项目，在此表示感谢：

- [cexll/myclaude](https://github.com/cexll/myclaude) - 本项目的主要代码基础，包括 codeagent-wrapper、命令、Agent 等核心组件
- [Anthropic Claude Code](https://claude.ai/claude-code) - Claude Code 官方插件系统和最佳实践

## License

- **本项目新增/修改的代码**：采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) 协议，放弃所有版权，可自由使用
- **继承的代码**：按照原项目的协议授权
