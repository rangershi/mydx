---
allowed-tools: [Bash, AskUserQuestion, Edit, Read, Write]
description: '环境诊断：检测 Codex CLI、Gemini CLI 及其他依赖'
model: haiku
---

## 用法

```bash
/dx:doctor
```

---

## Step 1: 并行检测

**同时执行以下 4 个 Bash 调用（真正并行）：**

```bash
# 批次 1: CLI 版本检测
echo "=== CLI_VERSIONS ===";
echo "codex:" && (which codex && codex --version 2>/dev/null || echo "NOT_FOUND");
echo "gemini:" && (which gemini && gemini --version 2>/dev/null || echo "NOT_FOUND");
echo "opencode:" && (which opencode && opencode --version 2>/dev/null || echo "NOT_FOUND");
echo "agent-browser:" && (which agent-browser && agent-browser --version 2>/dev/null || echo "NOT_FOUND");
```

```bash
# 批次 2: 项目文件检测
echo "=== PROJECT_FILES ===";
echo "AGENTS.md:" && (test -f AGENTS.md && echo "FOUND" || echo "NOT_FOUND");
echo "opencode.json:" && (test -f opencode.json && echo "CONFIGURED" || echo "NOT_FOUND");
echo "instructions:" && (if [ -f opencode.json ]; then grep -q '"AGENTS.md"' opencode.json && grep -q '"ruler/' opencode.json && echo "VALID" || echo "INVALID"; else echo "SKIP"; fi);
```

```bash
# 批次 3: Claude 配置 + OpenCode 插件检测
# 注意：插件名可能带版本号（如 @1.3.0），使用模糊匹配
echo "=== CLAUDE_CONFIG ===";
echo "statusLine:" && (grep '"statusLine"' ~/.claude/settings.json 2>/dev/null && echo "CONFIGURED" || echo "NOT_CONFIGURED");
echo "LSP:" && (grep 'ENABLE_LSP_TOOLS' ~/.claude/settings.json 2>/dev/null && echo "CONFIGURED" || echo "NOT_CONFIGURED");
echo "autoUpdate:" && (grep 'FORCE_AUTOUPDATE_PLUGINS' ~/.claude/settings.json 2>/dev/null && echo "CONFIGURED" || echo "NOT_CONFIGURED");
echo "=== OPENCODE_PLUGINS ===";
echo "oh-my-opencode:" && (grep -q 'oh-my-opencode' ~/.config/opencode/opencode.json 2>/dev/null && echo "INSTALLED" || echo "NOT_INSTALLED");
echo "opencode-antigravity-auth:" && (grep -q 'opencode-antigravity-auth' ~/.config/opencode/opencode.json 2>/dev/null && echo "INSTALLED" || echo "NOT_INSTALLED");
echo "opencode-openai-codex-auth:" && (grep -q 'opencode-openai-codex-auth' ~/.config/opencode/opencode.json 2>/dev/null && echo "INSTALLED" || echo "NOT_INSTALLED");
```

```bash
# 批次 4: CLI 多版本检测
echo "=== MULTI_VERSION ===";
echo "claude/native:" && (test -x ~/.local/bin/claude && ~/.local/bin/claude --version 2>/dev/null || echo "none");
echo "claude/npm:" && (npm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none");
echo "claude/pnpm:" && (pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code || echo "none");
echo "claude/brew:" && (brew list claude 2>/dev/null || echo "none");
echo "codex/npm:" && (npm list -g @openai/codex 2>/dev/null | grep @openai/codex || echo "none");
echo "codex/pnpm:" && (pnpm list -g @openai/codex 2>/dev/null | grep @openai/codex || echo "none");
echo "opencode/npm:" && (npm list -g opencode 2>/dev/null | grep opencode || echo "none");
echo "opencode/brew:" && (brew list opencode 2>/dev/null || echo "none");
```

---

## Step 2: 输出报告

汇总结果，输出表格：

```
工具                           | 状态     | 版本
codex                          | <状态>   | <版本>
gemini                         | <状态>   | <版本>
opencode                       | <状态>   | <版本>
AGENTS.md                      | <状态>   | -
opencode.json                  | <状态>   | -
配置指令                       | <状态>   | -
oh-my-opencode                 | <状态>   | -
opencode-antigravity-auth      | <状态>   | -
opencode-openai-codex-auth     | <状态>   | -
ccstatusline                   | <状态>   | -
LSP 服务                       | <状态>   | -
插件自动更新                   | <状态>   | -
agent-browser                  | <状态>   | <版本>
```

多版本警告（如有）：列出各包管理器的安装情况。

---

## Step 3: 统一处理缺失项

**如检测到任何缺失项，统一询问一次：**

`AskUserQuestion`: 检测到以下缺失项，是否自动安装/配置所有？

确认后按顺序处理：

### 3.1 codex CLI 未安装

提示用户安装 Codex CLI：
- 参考 OpenAI 官方文档安装

### 3.2 gemini CLI 未安装

提示用户安装 Gemini CLI：
- 参考 Google 官方文档安装

### 3.3 opencode CLI 未安装

执行安装：
```bash
# brew 优先
brew install opencode || npm install -g opencode
```

### 3.4 AGENTS.md 未找到

提示用户：
- AGENTS.md 文件不存在，OpenCode 需要此文件作为项目指令入口
- 建议创建或检查文件路径

### 3.5 opencode.json 未配置

使用 Write 工具创建配置文件：

文件路径：`<项目根目录>/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "ruler/**/*.md"
  ]
}
```

### 3.6 配置指令无效

使用 Edit 工具修复 opencode.json，确保包含：
- `"AGENTS.md"`: 主配置文件
- `"ruler/**/*.md"`: 自动加载 ruler 目录下所有 .md 文件（因 OpenCode 不支持 @ 引用）

### 3.7 OpenCode 插件安装

**OpenCode 插件通过编辑 `~/.config/opencode/opencode.json` 的 `plugin` 数组安装。**

1. 先读取现有配置：
```bash
cat ~/.config/opencode/opencode.json
```

2. 使用 Edit 工具在 `plugin` 数组中添加缺失的插件：
   - `oh-my-opencode`
   - `opencode-antigravity-auth@latest`
   - `opencode-openai-codex-auth`

示例 plugin 配置：
```json
"plugin": [
  "oh-my-opencode",
  "opencode-antigravity-auth@latest",
  "opencode-openai-codex-auth"
]
```

3. 验证安装：
```bash
grep -E 'oh-my-opencode|opencode-antigravity-auth|opencode-openai-codex-auth' ~/.config/opencode/opencode.json
```

### 3.8 ccstatusline 未配置

使用 Edit 工具修改 `~/.claude/settings.json`，添加：
```json
"statusLine": "npx ccstatusline@latest"
```

### 3.9 LSP 未配置

使用 Edit 工具修改 `~/.claude/settings.json`，在 `env` 对象中添加：
```json
"ENABLE_LSP_TOOLS": "1"
```

### 3.10 Claude CLI 版本管理

**策略：仅保留 `~/.local/bin/claude` 原生版本，卸载其他所有安装方式。**

**如检测到非原生版本，立即执行卸载：**

```bash
# 卸载 npm 版本
npm uninstall -g @anthropic-ai/claude-code 2>/dev/null

# 卸载 pnpm 版本
pnpm uninstall -g @anthropic-ai/claude-code 2>/dev/null

# 卸载 brew 版本
brew uninstall claude 2>/dev/null
```

**如原生版本不存在，安装原生版本：**

```bash
curl -fsSL https://claude.ai/install.sh | sh
```

**验证结果：**

```bash
~/.local/bin/claude --version
```

### 3.11 Codex CLI 版本管理

**如检测到 npm 版本，卸载并统一使用 pnpm：**

```bash
npm uninstall -g @openai/codex 2>/dev/null
pnpm install -g @openai/codex@latest
```

**验证安装结果：**

```bash
codex --version
```

### 3.12 插件自动更新未配置

使用 Edit 工具修改 `~/.claude/settings.json`，在 `env` 对象中添加：
```json
"FORCE_AUTOUPDATE_PLUGINS": "1"
```

### 3.13 agent-browser 未安装

执行安装：
```bash
npm install -g agent-browser && agent-browser install
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

**修复完成后：**
输出最终状态表格，确认所有项目均为 ✅
