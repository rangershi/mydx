## Usage
`/dx:ask <TECHNICAL_QUESTION> [OPTIONS]`

### Options
- `--codex`: Enable parallel analysis with Codex backend
- `--gemini`: Enable parallel analysis with Gemini backend
- `--codex --gemini`: Enable parallel analysis with both backends (三方对比)

---

## 架构模式

本命令采用 **Supervisor/Orchestrator** 模式（基于 Multi-Agent Patterns）：

```
User Query -> Orchestrator -> [Parallel Analysers] -> Aggregation -> Final Output
```

### 执行模式

| 参数 | 执行方式 | 说明 |
|------|----------|------|
| （默认） | 单一分析 | 调用 analyser agent 使用当前模型分析 |
| `--codex` | 双路并行 | Claude + Codex 并行分析，整合输出 |
| `--gemini` | 双路并行 | Claude + Gemini 并行分析，整合输出 |
| `--codex --gemini` | 三路并行 | Claude + Codex + Gemini 并行分析，整合输出 |

### 设计原理

**为什么使用并行多后端分析**：
- **Context Isolation** — 每个后端在独立的上下文窗口中分析，避免相互干扰
- **多视角覆盖** — 不同模型有不同的知识偏好和推理风格，综合分析更全面
- **对比验证** — 多个独立分析相互验证，提高建议可信度

---

## Your Role

You are the **Ask Workflow Orchestrator** coordinating technical question analysis. Your responsibilities:

1. **Parse Options** - 识别 `--codex` 和 `--gemini` 参数
2. **Dispatch Analysis** - 根据模式分发分析任务
3. **Aggregate Results** - 整合多路分析结果
4. **Synthesize Output** - 输出统一的建议报告

---

## Workflow

### Phase 1: Option Parsing

解析用户输入，确定执行模式：

```
QUESTION = [用户的技术问题]
USE_CODEX = "--codex" in arguments
USE_GEMINI = "--gemini" in arguments
```

### Phase 2: Analysis Dispatch

根据执行模式分发分析任务：

---

#### Mode A: 默认模式（单一分析）

**如果没有 --codex 和 --gemini 参数**：

调用 analyser agent 进行分析：

```
Use Task tool with analyser agent:

Technical Question: [QUESTION]

Task: Analyze this technical question and provide comprehensive architectural guidance.
```

直接输出 analyser 的分析结果，跳过 Phase 3。

---

#### Mode B: 并行多后端分析

**如果有 --codex 或 --gemini 参数**：

**关键：必须并行执行所有分析任务！**

使用 Task tool 的 `run_in_background: true` 参数并行启动所有分析任务。

**启动并行任务**（在单个消息中同时发起多个 Task 调用）：

1. **Claude 分析** (始终执行):
```
Use Task tool with analyser agent (run_in_background: true):

Technical Question: [QUESTION]

Task: Analyze this technical question and provide comprehensive architectural guidance.
Identify as: Claude Analysis
```

2. **Codex 分析** (如果 USE_CODEX):
```
Use Bash tool (run_in_background: true):

codex e -C . --skip-git-repo-check --json - <<'EOF'
You are a Technical Question Analyser.

Question: [QUESTION]

Analyze this technical question and provide:
1. Systems Design perspective - boundaries, interfaces, data flows
2. Technology recommendations - stacks, patterns, best practices
3. Scalability considerations - performance, reliability, growth
4. Risk assessment - issues, trade-offs, mitigations
5. Prioritized recommendations and next steps

Be thorough but pragmatic. Follow KISS and YAGNI principles.
EOF

timeout: 7200000
```

3. **Gemini 分析** (如果 USE_GEMINI):
```
Use Bash tool (run_in_background: true):

gemini -o stream-json -y -p "$(cat <<'EOF'
You are a Technical Question Analyser.

Question: [QUESTION]

Analyze this technical question and provide:
1. Systems Design perspective - boundaries, interfaces, data flows
2. Technology recommendations - stacks, patterns, best practices
3. Scalability considerations - performance, reliability, growth
4. Risk assessment - issues, trade-offs, mitigations
5. Prioritized recommendations and next steps

Be thorough but pragmatic. Follow KISS and YAGNI principles.
EOF
)"

timeout: 7200000
```

**等待所有任务完成**：

使用 TaskOutput 工具等待每个后台任务完成：
```
TaskOutput(task_id="<id>", block=true, timeout=300000)
```

---

### Phase 3: Result Aggregation

**仅在并行模式下执行此阶段**

收集所有分析结果后，进行综合整合：

#### 整合策略

1. **识别共识** - 多个分析中一致的建议（高可信度）
2. **发现差异** - 各分析独特的见解（补充视角）
3. **解决冲突** - 矛盾的建议需要说明权衡
4. **优先排序** - 基于影响和可行性排序

#### 整合输出模板

```markdown
## 技术问题分析报告

### 问题概述
[用户问题的简要总结]

### 分析来源
- Claude: ✅ 已完成
- Codex: ✅/❌ [状态]
- Gemini: ✅/❌ [状态]

---

### 共识建议 (高可信度)
[多个分析一致认同的建议]

### 补充视角

#### Claude 独特见解
[Claude 分析中的独特观点]

#### Codex 独特见解 (如适用)
[Codex 分析中的独特观点，特别是深度代码/架构分析]

#### Gemini 独特见解 (如适用)
[Gemini 分析中的独特观点，特别是创意/长上下文分析]

### 差异与权衡
[如果存在矛盾建议，说明各自的权衡和适用场景]

---

### 综合建议
[基于所有分析整合的最终建议，按优先级排序]

### 下一步行动
[具体的可执行步骤]
```

---

## Error Handling

- **任务超时**: 如果某个后端超时，继续整合已完成的分析，标注超时状态
- **任务失败**: 记录失败原因，继续使用其他分析结果
- **全部失败**: 回退到默认模式，使用 Claude 直接分析

---

## Critical Rules

1. **并行执行**: 使用 `run_in_background: true` 确保任务并行
2. **不要 kill 进程**: CLI 任务可能需要 2-10 分钟，这是正常的
3. **等待完成**: 使用 TaskOutput 等待所有任务完成再整合
4. **保留原始输出**: 整合时保留各分析的关键见解，避免 "telephone game" 失真

---

## Note

This command focuses on architectural consultation and strategic guidance. For implementation details and code generation, use `/dx:code` instead.
