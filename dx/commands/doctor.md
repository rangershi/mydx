---
allowed-tools: [Bash, AskUserQuestion, Edit, Read]
description: '环境诊断：检测并安装 codeagent-wrapper 及后端 CLI 依赖'
model: haiku
---

## 用法

```bash
/dx:doctor
```

---

## Step 1: 并行检测

**同时执行以下 6 个 Bash 调用：**

```bash
# 1. codeagent-wrapper
which codeagent-wrapper && codeagent-wrapper --version 2>/dev/null || echo "NOT_FOUND"
```

```bash
# 2. codex CLI
which codex && codex --version 2>/dev/null || echo "NOT_FOUND"
```

```bash
# 3. gemini CLI
which gemini && gemini --version 2>/dev/null || echo "NOT_FOUND"
```

```bash
# 4. ccstatusline 配置
grep '"statusLine"' ~/.claude/settings.json 2>/dev/null || echo "NOT_CONFIGURED"
```

```bash
# 5. CLI 多版本检测
echo "=== npm ===" && npm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none"
echo "=== pnpm ===" && pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none"
echo "=== brew ===" && brew list claude 2>/dev/null || echo "none"
```

```bash
# 6. LSP 配置
grep 'ENABLE_LSP_TOOLS' ~/.claude/settings.json 2>/dev/null || echo "NOT_CONFIGURED"
```

---

## Step 2: 输出报告

汇总结果，输出表格：

```
工具               | 状态     | 版本
codeagent-wrapper  | <状态>   | <版本>
codex              | <状态>   | <版本>
gemini             | <状态>   | <版本>
ccstatusline       | <状态>   | -
LSP 服务           | <状态>   | -
```

多版本警告（如有）：列出各包管理器的安装情况。

---

## Step 3: 处理缺失项

按以下顺序处理：

### 3.1 codeagent-wrapper 未安装

`AskUserQuestion`: 是否自动安装？

```bash
curl -fsSL https://raw.githubusercontent.com/anthropics/claude-code-sdk-python/main/codeagent/install.sh | bash
```

### 3.2 ccstatusline 未配置

`AskUserQuestion`: npx(推荐) / bunx / 跳过

选择后 Edit `~/.claude/settings.json` 添加：
```json
"statusLine": "npx ccstatusline@latest"
```

### 3.3 LSP 未配置

`AskUserQuestion`: 是否启用 LSP？

Edit `~/.claude/settings.json` 添加：
```json
"env": { "ENABLE_LSP_TOOLS": "1" }
```

### 3.4 CLI 多版本

`AskUserQuestion`: 保留哪个包管理器？

卸载其他版本：
```bash
npm uninstall -g @anthropic-ai/claude-code    # 如选择移除 npm
pnpm remove -g @anthropic-ai/claude-code      # 如选择移除 pnpm
brew uninstall claude                          # 如选择移除 brew
```

---

## 输出格式

**全部就绪：**
```
✅ 所有依赖已就绪
```

**有缺失：**
```
⚠️ <工具> 未安装/未配置
```
