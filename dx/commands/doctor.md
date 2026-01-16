---
allowed-tools: [Bash, AskUserQuestion, Edit, Read]
description: '环境诊断：检测 Codex CLI、Gemini CLI 及其他依赖'
model: haiku
---

## 用法

```bash
/dx:doctor
```

---

## Step 1: 并行检测

**同时执行以下 5 个 Bash 调用：**

```bash
# 1. codex CLI
which codex && codex --version 2>/dev/null || echo "NOT_FOUND"
```

```bash
# 2. gemini CLI
which gemini && gemini --version 2>/dev/null || echo "NOT_FOUND"
```

```bash
# 3. ccstatusline 配置
grep '"statusLine"' ~/.claude/settings.json 2>/dev/null || echo "NOT_CONFIGURED"
```

```bash
# 4. CLI 多版本检测（claude/codex）
echo "=== claude / npm ===" && npm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none"
echo "=== claude / pnpm ===" && pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none"
echo "=== claude / brew ===" && brew list claude 2>/dev/null || echo "none"
echo "=== codex / npm ===" && npm list -g @openai/codex 2>/dev/null | grep @openai/codex || echo "none"
echo "=== codex / pnpm ===" && pnpm list -g @openai/codex 2>/dev/null | grep @openai/codex || echo "none"
```

```bash
# 5. LSP 配置
grep 'ENABLE_LSP_TOOLS' ~/.claude/settings.json 2>/dev/null || echo "NOT_CONFIGURED"
```

```bash
# 6. 插件自动更新配置
grep 'FORCE_AUTOUPDATE_PLUGINS' ~/.claude/settings.json 2>/dev/null || echo "NOT_CONFIGURED"
```

---

## Step 2: 输出报告

汇总结果，输出表格：

```
工具               | 状态     | 版本
codex              | <状态>   | <版本>
gemini             | <状态>   | <版本>
ccstatusline       | <状态>   | -
LSP 服务           | <状态>   | -
插件自动更新       | <状态>   | -
```

多版本警告（如有）：列出各包管理器的安装情况。

---

## Step 3: 处理缺失项

按以下顺序处理：

### 3.1 codex CLI 未安装

提示用户安装 Codex CLI：
- 参考 OpenAI 官方文档安装

### 3.2 gemini CLI 未安装

提示用户安装 Gemini CLI：
- 参考 Google 官方文档安装

### 3.3 ccstatusline 未配置

`AskUserQuestion`: npx(推荐) / bunx / 跳过

选择后 Edit `~/.claude/settings.json` 添加：
```json
"statusLine": "npx ccstatusline@latest"
```

### 3.4 LSP 未配置

`AskUserQuestion`: 是否启用 LSP？

Edit `~/.claude/settings.json` 添加：
```json
"env": { "ENABLE_LSP_TOOLS": "1" }
```

### 3.5 CLI 多版本处理

**如检测到多版本，立即执行卸载（仅保留 pnpm）：**

```bash
# 卸载 npm 版本
npm uninstall -g @anthropic-ai/claude-code 2>/dev/null
npm uninstall -g @openai/codex 2>/dev/null

# 卸载 brew 版本
brew uninstall claude 2>/dev/null
```

### 3.6 更新到最新版本

**立即执行更新：**

```bash
pnpm install -g @anthropic-ai/claude-code@latest @openai/codex@latest
```

**验证安装结果：**

```bash
claude --version && codex --version
```

### 3.7 插件自动更新未配置

**如未配置 FORCE_AUTOUPDATE_PLUGINS，立即启用：**

Edit `~/.claude/settings.json` 在 `env` 对象中添加：
```json
"FORCE_AUTOUPDATE_PLUGINS": "1"
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
