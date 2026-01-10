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

#### 方式一：通过 Claude Code 安装（推荐）

```bash
# 在 Claude Code 中运行
claude /plugin add https://github.com/rangershi/mydx
```

或在 Claude Code 交互模式中：
```bash
/plugin add https://github.com/rangershi/mydx
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

### 后端选择

可以通过参数选择不同的执行后端：

| 参数 | 后端 | 说明 |
|------|------|------|
| (默认) | Claude | 使用 Claude 当前模型直接执行 |
| `--codex` | OpenAI Codex | 委托给 Codex CLI 执行 |
| `--gemini` | Google Gemini | 委托给 Gemini CLI 执行 |

### 各后端能力特点

| 后端 | 擅长领域 | 推荐场景 |
|------|----------|----------|
| **Claude** | 通用任务、文档生成、提示词工程、快速迭代 | 简单任务、需要快速响应、Token 敏感场景 |
| **Codex** | 深度代码理解、复杂算法、大规模重构、精确依赖追踪 | 复杂调试、性能优化、架构重构、需要强推理的任务 |
| **Gemini** | 多模态理解、长上下文处理、创意生成 | 需要处理图片/文档、超长代码分析、创意性任务 |

**选择建议**：
- **默认使用 Claude**：大多数日常开发任务
- **使用 Codex**：遇到复杂问题、需要深度分析、或任务超出当前上下文承载能力时
- **使用 Gemini**：需要多模态能力或处理超长上下文时

### 示例

```bash
# 使用 Claude 执行（默认）
/dx:dev 实现用户登录功能

# 委托给 Codex 执行（复杂任务）
/dx:dev --codex 重构认证模块并优化性能

# 委托给 Gemini 执行
/dx:dev --gemini 分析这个截图中的 UI 并实现
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

### 技术咨询 (`/dx:ask`) - 多后端并行分析

> **特色功能**：支持多个 AI 后端并行分析同一问题，综合多视角得出更可靠的建议。

**架构模式**: Supervisor/Orchestrator (Multi-Agent Patterns)

```
User Query -> Orchestrator -> [Parallel Analysers] -> Aggregation -> Final Output
```

| 参数 | 分析方式 | 说明 |
|------|----------|------|
| (默认) | 单一分析 | 使用 Claude 分析 |
| `--codex` | 双路并行 | Claude + Codex 并行分析 |
| `--gemini` | 双路并行 | Claude + Gemini 并行分析 |
| `--codex --gemini` | 三路并行 | Claude + Codex + Gemini 三方对比 |

**示例**：

```bash
# 默认模式：使用 Claude 分析
/dx:ask 如何设计一个高可用的消息队列系统

# 双路并行：Claude + Codex 分析（适合需要深度代码分析的问题）
/dx:ask --codex 这个微服务架构有什么潜在问题

# 三路并行：获取最全面的分析（适合重要架构决策）
/dx:ask --codex --gemini 我们应该选择 Kafka 还是 RabbitMQ
```

**输出特点**：
- **共识建议** - 多个后端一致认同的建议（高可信度）
- **独特见解** - 各后端独特的分析视角
- **差异权衡** - 矛盾建议的权衡说明

## 主要命令

| 命令 | 说明 |
|------|------|
| `/dx:doctor` | 环境诊断，检测并安装依赖 |
| `/dx:ask` | 技术问题咨询（支持多后端并行分析） |
| `/dx:dev` | 轻量级开发流程 |
| `/dx:code` | 代码生成 |
| `/dx:bugfix` | Bug 修复 |
| `/dx:code-entropy-scan` | 代码熵扫描分析 |
| `/dx:git-commit-and-pr` | 提交代码并创建 PR |
| `/dx:pr-review-loop` | PR 评审循环 |
| `/dx:bmad-pilot` | BMAD 敏捷流程 |
| `/dx:feature-dev` | 功能开发流程 |
| `/dx:requirements-pilot` | 需求驱动开发流程 |

## 工作流详解

### BMAD 工作流 (`bmad/`)

**BMAD (Business Model Agile Development)** 是一套完整的敏捷开发流程，模拟真实团队协作。

| Agent | 角色 | 职责 |
|-------|------|------|
| `bmad-po` | Product Owner | 需求分析、用户故事编写 |
| `bmad-architect` | 架构师 | 技术方案设计、架构决策 |
| `bmad-sm` | Scrum Master | 流程协调、任务分配 |
| `bmad-dev` | 开发者 | 代码实现 |
| `bmad-qa` | QA 工程师 | 测试用例设计、质量保证 |
| `bmad-review` | 代码审查 | Code Review |
| `bmad-orchestrator` | 编排器 | 协调各角色工作流 |

**入口命令**: `/dx:bmad-pilot`

### Requirements-Driven 工作流 (`requirements-driven-workflow/`)

**需求驱动开发流程**，强调从需求确认到代码实现的完整链路。

| Agent | 职责 |
|-------|------|
| `requirements-generate` | 生成技术规格文档 |
| `requirements-code` | 基于规格实现代码 |
| `requirements-review` | 代码质量评审 |
| `requirements-testing` | 测试用例生成与执行 |

**流程**:
1. **Phase 0**: 仓库扫描（了解现有代码库）
2. **Phase 1**: 需求确认（交互式澄清，90+ 质量分）
3. **用户审批门控**（必须获得用户确认才进入实现）
4. **Phase 2**: 实现（规格生成 → 代码实现 → 评审 → 测试）

**入口命令**: `/dx:requirements-pilot`

### Feature-Dev 工作流 (`feature-dev/`)

**功能开发工作流**，专注于单个功能的完整开发周期。

| Agent | 职责 |
|-------|------|
| `code-explorer` | 代码库探索、模式识别 |
| `code-architect` | 功能架构设计 |
| `code-reviewer` | 代码审查与质量评估 |

**入口命令**: `/dx:feature-dev`

## Skills 说明

Skills 提供专业领域知识和外部工具集成能力。

### codeagent (`skills/codeagent/`)

统一的多后端代码代理封装，通过 `codeagent-wrapper` 调用不同的 AI 后端。

**核心命令**:
```bash
codeagent-wrapper --backend {codex|gemini|claude} "task description"
```

**支持的后端**:

| 后端 | 擅长领域 |
|------|----------|
| `codex` | 深度代码理解、复杂算法、大规模重构 |
| `gemini` | 多模态理解、长上下文处理、创意生成 |
| `claude` | 通用任务、文档生成、快速迭代 |

> 详细的后端能力对比请参考上方「执行模式 > 各后端能力特点」部分。

**关键规则**:
- 长时间运行是正常的（2-10 分钟）
- **永远不要 kill codeagent 进程**
- 使用 `timeout: 7200000` 配置

### product-requirements (`skills/product-requirements/`)

产品需求文档处理技能，帮助解析和结构化产品需求。

**功能**:
- PRD 解析与结构化
- 需求拆分为用户故事
- 验收标准生成

## 目录结构

```
mydx/
├── .claude-plugin/
│   └── marketplace.json    # 插件配置
├── dx/
│   ├── commands/           # 命令定义
│   ├── agents/             # Agent 定义
│   ├── skills/             # Skills 定义
│   │   ├── codeagent/      # 多后端代码代理 (codex/gemini/claude)
│   │   └── product-requirements/  # 产品需求处理
│   ├── hooks/              # Hooks 配置（标准 Claude Code 格式）
│   ├── bmad/               # BMAD 敏捷工作流
│   │   ├── commands/       # BMAD 入口命令
│   │   └── agents/         # BMAD 角色代理
│   ├── feature-dev/        # 功能开发工作流
│   │   ├── commands/       # 入口命令
│   │   └── agents/         # 开发代理
│   └── requirements-driven-workflow/  # 需求驱动工作流
│       ├── commands/       # 入口命令
│       └── agents/         # 需求代理
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
