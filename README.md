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

## 推荐开发流程

### 第一步：方案讨论

开始任何开发任务前，建议先使用 `/dx:ask` 进行技术方案讨论：

```bash
# 单独使用 Claude 分析
/dx:ask 如何实现用户认证模块

# 重要决策时使用多后端并行分析
/dx:ask --codex --gemini 微服务拆分方案设计
```

### 第二步：选择开发流程

根据功能复杂度（主要考虑上下文长度需求）从高到低选择合适的开发流程：

| 复杂度 | 命令 | 适用场景 | 上下文需求 |
|--------|------|----------|------------|
| **高** | `/dx:bmad-pilot` | 大型功能、需要完整敏捷流程（PO→架构→SM→开发→QA→Review） | 最长 |
| **中高** | `/dx:requirements-pilot` | 中大型功能、需要严格需求确认和质量门控 | 较长 |
| **中** | `/dx:feature-dev` | 单个功能开发、需要架构设计和代码审查 | 中等 |
| **低** | `/dx:dev` | 简单功能、快速迭代、小改动 | 最短 |

### 选择建议

```
┌─────────────────────────────────────────────────────────────────┐
│                        功能复杂度评估                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  需要多角色协作？需要完整敏捷流程？                               │
│       ↓ 是                                                      │
│  ┌─────────────────┐                                            │
│  │ /dx:bmad-pilot  │  ← 模拟完整团队：PO、架构师、SM、开发、QA    │
│  └─────────────────┘                                            │
│       ↓ 否                                                      │
│                                                                 │
│  需要严格需求确认？需要质量门控（90+分）？                        │
│       ↓ 是                                                      │
│  ┌─────────────────────────┐                                    │
│  │ /dx:requirements-pilot  │  ← 需求驱动：扫描→确认→实现→测试     │
│  └─────────────────────────┘                                    │
│       ↓ 否                                                      │
│                                                                 │
│  需要架构设计？需要代码审查？                                     │
│       ↓ 是                                                      │
│  ┌──────────────────┐                                           │
│  │ /dx:feature-dev  │  ← 功能开发：探索→架构→实现→审查            │
│  └──────────────────┘                                           │
│       ↓ 否                                                      │
│                                                                 │
│  ┌───────────┐                                                  │
│  │ /dx:dev   │  ← 轻量开发：快速实现                             │
│  └───────────┘                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 示例场景

```bash
# 场景 1：大型电商系统重构
/dx:ask --codex 电商系统微服务拆分方案
/dx:bmad-pilot 重构订单模块为独立微服务

# 场景 2：新增支付功能
/dx:ask 支付模块技术选型
/dx:requirements-pilot 实现支付宝支付集成

# 场景 3：添加用户头像上传
/dx:feature-dev 实现用户头像上传功能

# 场景 4：修复登录 bug
/dx:dev 修复登录页面验证码不显示问题
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

**命令参数**:

| 参数 | 说明 |
|------|------|
| `--skip-scan` | 跳过仓库扫描阶段（不推荐，会失去代码库上下文） |
| `--skip-tests` | 跳过 QA 测试阶段 |
| `--direct-dev` | 跳过 SM 计划阶段，架构完成后直接进入开发 |
| `--codex` | Agent 使用 Codex 后端执行（适合复杂任务） |
| `--gemini` | Agent 使用 Gemini 后端执行 |

**示例**:

```bash
# 完整流程（推荐）
/dx:bmad-pilot 开发电商订单系统

# 快速开发模式（跳过 SM 规划）
/dx:bmad-pilot --direct-dev 实现商品搜索功能

# 跳过测试
/dx:bmad-pilot --skip-tests 添加数据导出功能

# 使用 Codex 处理复杂任务
/dx:bmad-pilot --codex 重构整体架构

# 组合参数（快速原型）
/dx:bmad-pilot --direct-dev --skip-tests 快速验证 POC
```

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

**命令参数**:

| 参数 | 说明 |
|------|------|
| `--skip-scan` | 跳过仓库扫描阶段（不推荐，会失去代码库上下文） |
| `--skip-tests` | 跳过测试阶段（适合简单改动或文档更新） |
| `--codex` | Agent 使用 Codex 后端执行（适合复杂任务） |
| `--gemini` | Agent 使用 Gemini 后端执行 |

**示例**:

```bash
# 完整流程（推荐）
/dx:requirements-pilot 实现用户积分系统

# 跳过测试（简单任务）
/dx:requirements-pilot --skip-tests 添加配置项

# 使用 Codex 处理复杂任务
/dx:requirements-pilot --codex 重构支付模块

# 组合参数
/dx:requirements-pilot --skip-scan --skip-tests 更新错误提示文案
```

### Feature-Dev 工作流 (`feature-dev/`)

**功能开发工作流**，专注于单个功能的完整开发周期。

| Agent | 职责 |
|-------|------|
| `code-explorer` | 代码库探索、模式识别 |
| `code-architect` | 功能架构设计 |
| `code-reviewer` | 代码审查与质量评估 |

**入口命令**: `/dx:feature-dev`

**命令参数**:

| 参数 | 说明 |
|------|------|
| `--codex` | 使用 Codex 后端执行探索、架构和实现（适合复杂功能） |
| `--gemini` | 使用 Gemini 后端执行 |

**示例**:

```bash
# 默认模式（Claude 直接执行）
/dx:feature-dev 实现用户头像上传功能

# 使用 Codex 处理复杂功能
/dx:feature-dev --codex 实现实时消息推送系统

# 使用 Gemini
/dx:feature-dev --gemini 实现图片处理功能
```

### Dev 轻量开发流程

**轻量级端到端开发流程**，适合简单功能和快速迭代。

**流程**:
1. **需求澄清**（交互式问答）
2. **技术分析**（代码库探索）
3. **开发文档**（生成 dev-plan.md）
4. **开发执行**（实现代码）
5. **覆盖验证**（测试验证）

**入口命令**: `/dx:dev`

**命令参数**:

| 参数 | 说明 |
|------|------|
| `--codex` | 委托 Codex 后端执行分析和开发（适合复杂度超预期的任务） |
| `--gemini` | 委托 Gemini 后端执行 |

**示例**:

```bash
# 默认模式（Claude 直接执行，推荐）
/dx:dev 添加用户登录功能

# 使用 Codex（任务复杂度超预期时）
/dx:dev --codex 实现复杂的权限校验逻辑

# 使用 Gemini
/dx:dev --gemini 实现图片压缩功能
```

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

交互式需求澄清技能，通过质量评分和迭代对话生成专业 PRD 文档。

**核心能力**:
- 100 分制需求质量评分（90+ 门控）
- 五维度评估：业务价值、功能需求、用户体验、技术约束、范围优先级
- 交互式澄清对话
- 专业 PRD 文档生成（保存到 `docs/{feature-name}-prd.md`）

**在 Workflow 中的集成**:

| Workflow | 调用时机 | 触发条件 |
|----------|----------|----------|
| `/dx:bmad-pilot` | Phase 1.5（PO 分析前） | 需求描述不清晰（质量分 < 90） |
| `/dx:requirements-pilot` | Phase 1.5（需求确认时） | 推荐始终调用以确保质量 |
| `/dx:feature-dev` | Phase 3.1（澄清问题时） | 功能需求需要结构化文档 |

**Skill 设计原则**（基于 tool-design）:
- **What**: 交互式需求澄清，生成专业 PRD 文档
- **When**: 需求不清晰、需要结构化文档、需要质量门控时
- **Returns**: `docs/{feature-name}-prd.md` 文件，供后续阶段使用

## 目录结构

```
mydx/
├── .claude-plugin/
│   └── marketplace.json    # 插件配置
├── dx/
│   ├── commands/           # 所有命令定义（统一 /dx:* 前缀）
│   ├── agents/             # 通用 Agent 定义
│   ├── skills/             # Skills 定义
│   │   ├── codeagent/      # 多后端代码代理 (codex/gemini/claude)
│   │   └── product-requirements/  # 产品需求处理
│   ├── hooks/              # Hooks 配置（标准 Claude Code 格式）
│   ├── bmad/               # BMAD 敏捷工作流
│   │   └── agents/         # BMAD 角色代理 (po/architect/sm/dev/qa/review)
│   ├── feature-dev/        # 功能开发工作流
│   │   └── agents/         # 开发代理 (explorer/architect/reviewer)
│   └── requirements-driven-workflow/  # 需求驱动工作流
│       └── agents/         # 需求代理 (generate/code/review/testing)
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
