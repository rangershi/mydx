---
allowed-tools: [Bash, AskUserQuestion]
description: '环境诊断：检测并安装 codeagent-wrapper 及后端 CLI 依赖'
model: sonnet
---

## Usage

```bash
/dx:doctor
```

检测当前系统的开发环境配置，确保必要的工具已正确安装。

## 检测项

### 1. codeagent-wrapper (必需)

统一的多后端代码代理封装，是 DX 工具集的核心依赖。

**检测命令**：

```bash
which codeagent-wrapper || command -v codeagent-wrapper
codeagent-wrapper --version 2>/dev/null
```

### 2. codex CLI (可选)

OpenAI Codex CLI，用于支持 `--codex` 参数。

**检测命令**：

```bash
which codex || command -v codex
codex --version 2>/dev/null
```

### 3. gemini CLI (可选)

Google Gemini CLI，用于支持 `--gemini` 参数。

**检测命令**：

```bash
which gemini || command -v gemini
gemini --version 2>/dev/null
```

### 4. ccstatusline 插件 (推荐)

Claude Code 状态行插件，提供实时状态显示和增强的命令行体验。

**说明**：
- ccstatusline 无需全局安装，通过 `npx` 或 `bunx` 直接运行
- 需要在 `~/.claude/settings.json` 中配置 `statusLine` 字段
- 配置后立即生效，无需重启

**检测命令**：

```bash
# 检测 Claude Code settings.json 中是否配置了 statusLine
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

if [ -f "$CLAUDE_SETTINGS" ]; then
    if grep -q '"statusLine"' "$CLAUDE_SETTINGS" 2>/dev/null; then
        # 提取配置值
        STATUS_LINE_CONFIG=$(grep -o '"statusLine"[^,}]*' "$CLAUDE_SETTINGS" | sed 's/"statusLine":[[:space:]]*"\([^"]*\)".*/\1/')
        echo "已配置: $STATUS_LINE_CONFIG"
    else
        echo "未配置"
    fi
else
    echo "settings.json 不存在"
fi
```

**配置路径**: `~/.claude/settings.json`（全局配置，非项目级别）

### 5. Claude/Codex CLI 多版本检测 (重要)

检测 `claude` 和 `codex` CLI 是否通过多个包管理器重复安装，避免升级冲突。

**检测命令**：

```bash
# 检测 claude CLI 的所有安装位置
CLAUDE_PATHS=""

# npm global
NPM_CLAUDE=$(npm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code)
if [ -n "$NPM_CLAUDE" ]; then
    CLAUDE_PATHS="$CLAUDE_PATHS npm:$(npm root -g)/@anthropic-ai/claude-code"
fi

# pnpm global
PNPM_CLAUDE=$(pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code)
if [ -n "$PNPM_CLAUDE" ]; then
    CLAUDE_PATHS="$CLAUDE_PATHS pnpm:$(pnpm root -g)/@anthropic-ai/claude-code"
fi

# yarn global
YARN_CLAUDE=$(yarn global list 2>/dev/null | grep claude-code)
if [ -n "$YARN_CLAUDE" ]; then
    CLAUDE_PATHS="$CLAUDE_PATHS yarn:$(yarn global dir)/node_modules/@anthropic-ai/claude-code"
fi

# brew
BREW_CLAUDE=$(brew list claude 2>/dev/null)
if [ -n "$BREW_CLAUDE" ]; then
    CLAUDE_PATHS="$CLAUDE_PATHS brew:$(brew --prefix)/bin/claude"
fi

# 检测 codex CLI 的所有安装位置
CODEX_PATHS=""

# npm global
NPM_CODEX=$(npm list -g @openai/codex 2>/dev/null | grep codex)
if [ -n "$NPM_CODEX" ]; then
    CODEX_PATHS="$CODEX_PATHS npm:$(npm root -g)/@openai/codex"
fi

# pnpm global
PNPM_CODEX=$(pnpm list -g @openai/codex 2>/dev/null | grep codex)
if [ -n "$PNPM_CODEX" ]; then
    CODEX_PATHS="$CODEX_PATHS pnpm:$(pnpm root -g)/@openai/codex"
fi

# yarn global
YARN_CODEX=$(yarn global list 2>/dev/null | grep codex)
if [ -n "$YARN_CODEX" ]; then
    CODEX_PATHS="$CODEX_PATHS yarn:$(yarn global dir)/node_modules/@openai/codex"
fi

# brew
BREW_CODEX=$(brew list codex 2>/dev/null)
if [ -n "$BREW_CODEX" ]; then
    CODEX_PATHS="$CODEX_PATHS brew:$(brew --prefix)/bin/codex"
fi
```

**多版本问题**：
- 不同包管理器安装的版本可能不一致
- 升级时可能只更新了其中一个，导致版本混乱
- PATH 优先级可能导致使用非预期版本

### 6. Claude LSP 服务 (推荐)

Claude Code 的 LSP 支持需要两部分配置：
1. **启用 LSP 环境变量** - 在 settings.json 中设置 `ENABLE_LSP_TOOLS`
2. **安装语言服务器** - 安装项目所需语言的 LSP 服务器

> 详细配置指南请参考：[Claude Code LSP 配置指南](../doc/claude-lsp-setup.md)

**检测内容**：

1. **检查 LSP 环境变量**
   ```bash
   grep -o 'ENABLE_LSP_TOOLS[^,}]*' ~/.claude/settings.json 2>/dev/null
   ```

2. **检测项目语言并检查对应 LSP 服务器**

   | 语言 | 检测文件 | LSP 服务器 | 检测命令 |
   |------|----------|------------|----------|
   | TypeScript/JS | `package.json`, `tsconfig.json` | typescript-language-server | `which typescript-language-server` |
   | Python | `*.py`, `requirements.txt`, `pyproject.toml` | pyright | `which pyright` |
   | Go | `go.mod`, `*.go` | gopls | `which gopls` |
   | Rust | `Cargo.toml`, `*.rs` | rust-analyzer | `which rust-analyzer` |
   | Java | `pom.xml`, `build.gradle` | jdtls | `which jdtls` |
   | C/C++ | `*.c`, `*.cpp`, `CMakeLists.txt` | clangd | `which clangd` |

**LSP 服务器安装命令**：

```bash
# TypeScript/JavaScript
npm install -g typescript-language-server typescript

# Python
npm install -g pyright
# 或: pip install pyright

# Go
go install golang.org/x/tools/gopls@latest

# Rust
rustup component add rust-analyzer
# 或 macOS: brew install rust-analyzer

# Java (需要 Java 21+)
brew install jdtls

# C/C++
# macOS:
xcode-select --install
# 或: brew install llvm
```

## 工作流程

### 阶段 1：环境检测

执行以下检测：

```bash
# 1. 检查 codeagent-wrapper
if command -v codeagent-wrapper &> /dev/null; then
    CODEAGENT_STATUS="已安装"
    CODEAGENT_VERSION=$(codeagent-wrapper --version 2>/dev/null || echo "未知")
else
    CODEAGENT_STATUS="未安装"
    CODEAGENT_VERSION="-"
fi

# 2. 检查 codex CLI
if command -v codex &> /dev/null; then
    CODEX_STATUS="已安装"
    CODEX_VERSION=$(codex --version 2>/dev/null || echo "未知")
else
    CODEX_STATUS="未安装"
    CODEX_VERSION="-"
fi

# 3. 检查 gemini CLI
if command -v gemini &> /dev/null; then
    GEMINI_STATUS="已安装"
    GEMINI_VERSION=$(gemini --version 2>/dev/null || echo "未知")
else
    GEMINI_STATUS="未安装"
    GEMINI_VERSION="-"
fi

# 4. 检查 Claude LSP 服务
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
LSP_ENV="未配置"

# 4.1 检查 LSP 环境变量
if [ -f "$CLAUDE_SETTINGS" ]; then
    if grep -q '"ENABLE_LSP_TOOLS"' "$CLAUDE_SETTINGS" 2>/dev/null; then
        LSP_ENV="已配置"
    fi
fi

# 4.2 检测项目语言
DETECTED_LANGS=""
MISSING_LSP=""

# TypeScript/JavaScript
if [ -f "package.json" ] || [ -f "tsconfig.json" ] || ls *.ts *.js 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS TypeScript/JS"
    if ! command -v typescript-language-server &> /dev/null; then
        MISSING_LSP="$MISSING_LSP typescript-language-server"
    fi
fi

# Python
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || ls *.py 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS Python"
    if ! command -v pyright &> /dev/null; then
        MISSING_LSP="$MISSING_LSP pyright"
    fi
fi

# Go
if [ -f "go.mod" ] || ls *.go 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS Go"
    if ! command -v gopls &> /dev/null; then
        MISSING_LSP="$MISSING_LSP gopls"
    fi
fi

# Rust
if [ -f "Cargo.toml" ] || ls *.rs 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS Rust"
    if ! command -v rust-analyzer &> /dev/null; then
        MISSING_LSP="$MISSING_LSP rust-analyzer"
    fi
fi

# Java
if [ -f "pom.xml" ] || [ -f "build.gradle" ] || ls *.java 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS Java"
    if ! command -v jdtls &> /dev/null; then
        MISSING_LSP="$MISSING_LSP jdtls"
    fi
fi

# C/C++
if [ -f "CMakeLists.txt" ] || ls *.c *.cpp *.h *.hpp 2>/dev/null | head -1 > /dev/null; then
    DETECTED_LANGS="$DETECTED_LANGS C/C++"
    if ! command -v clangd &> /dev/null; then
        MISSING_LSP="$MISSING_LSP clangd"
    fi
fi

# 判断 LSP 状态
if [ "$LSP_ENV" = "已配置" ] && [ -z "$MISSING_LSP" ]; then
    LSP_STATUS="完整"
elif [ "$LSP_ENV" = "已配置" ] && [ -n "$MISSING_LSP" ]; then
    LSP_STATUS="部分（缺少:$MISSING_LSP）"
else
    LSP_STATUS="未配置"
fi

# 5. 检查 ccstatusline 插件配置
CCSTATUSLINE_STATUS="未配置"
CCSTATUSLINE_CONFIG=""

# 检测 Claude Code settings.json 中是否配置了 statusLine
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ -f "$CLAUDE_SETTINGS" ]; then
    if grep -q '"statusLine"' "$CLAUDE_SETTINGS" 2>/dev/null; then
        CCSTATUSLINE_STATUS="已配置"
        CCSTATUSLINE_CONFIG=$(grep -o '"statusLine"[^,}]*' "$CLAUDE_SETTINGS" | sed 's/"statusLine":[[:space:]]*"\([^"]*\)".*/\1/')
    fi
fi

### 阶段 2：输出诊断报告

根据检测结果输出报告：

```
环境诊断报告

工具               | 状态     | 版本      | 说明
-------------------|----------|-----------|------------------
codeagent-wrapper  | 已安装   | v1.2.3    | 核心依赖
codex              | 已安装   | v1.0.0    | 支持 --codex 参数
gemini             | 未安装   | -         | 支持 --gemini 参数
ccstatusline       | 已配置   | npx       | 状态行增强
Claude LSP 服务    | 完整     | -         | 代码智能分析

检测到项目语言: TypeScript/JS Python
已安装的 LSP 服务器: typescript-language-server pyright
```

### 阶段 2.5：CLI 多版本检测

检测 `claude` 和 `codex` CLI 是否存在多个安装：

```bash
# 统计 claude CLI 安装数量
CLAUDE_INSTALL_COUNT=0
CLAUDE_INSTALLS=""

# 检测各包管理器
if npm list -g @anthropic-ai/claude-code 2>/dev/null | grep -q claude-code; then
    CLAUDE_INSTALL_COUNT=$((CLAUDE_INSTALL_COUNT + 1))
    CLAUDE_VERSION_NPM=$(npm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code | sed 's/.*@//')
    CLAUDE_INSTALLS="$CLAUDE_INSTALLS\n  - npm: v$CLAUDE_VERSION_NPM"
fi

if pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep -q claude-code; then
    CLAUDE_INSTALL_COUNT=$((CLAUDE_INSTALL_COUNT + 1))
    CLAUDE_VERSION_PNPM=$(pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep claude-code | awk '{print $2}')
    CLAUDE_INSTALLS="$CLAUDE_INSTALLS\n  - pnpm: v$CLAUDE_VERSION_PNPM"
fi

if yarn global list 2>/dev/null | grep -q claude-code; then
    CLAUDE_INSTALL_COUNT=$((CLAUDE_INSTALL_COUNT + 1))
    CLAUDE_VERSION_YARN=$(yarn global list 2>/dev/null | grep claude-code | sed 's/.*@//')
    CLAUDE_INSTALLS="$CLAUDE_INSTALLS\n  - yarn: v$CLAUDE_VERSION_YARN"
fi

if brew list claude 2>/dev/null >/dev/null; then
    CLAUDE_INSTALL_COUNT=$((CLAUDE_INSTALL_COUNT + 1))
    CLAUDE_VERSION_BREW=$(brew info claude 2>/dev/null | head -1 | awk '{print $3}')
    CLAUDE_INSTALLS="$CLAUDE_INSTALLS\n  - brew: v$CLAUDE_VERSION_BREW"
fi

# 统计 codex CLI 安装数量
CODEX_INSTALL_COUNT=0
CODEX_INSTALLS=""

if npm list -g @openai/codex 2>/dev/null | grep -q codex; then
    CODEX_INSTALL_COUNT=$((CODEX_INSTALL_COUNT + 1))
    CODEX_VERSION_NPM=$(npm list -g @openai/codex 2>/dev/null | grep codex | sed 's/.*@//')
    CODEX_INSTALLS="$CODEX_INSTALLS\n  - npm: v$CODEX_VERSION_NPM"
fi

if pnpm list -g @openai/codex 2>/dev/null | grep -q codex; then
    CODEX_INSTALL_COUNT=$((CODEX_INSTALL_COUNT + 1))
    CODEX_VERSION_PNPM=$(pnpm list -g @openai/codex 2>/dev/null | grep codex | awk '{print $2}')
    CODEX_INSTALLS="$CODEX_INSTALLS\n  - pnpm: v$CODEX_VERSION_PNPM"
fi

if yarn global list 2>/dev/null | grep -q codex; then
    CODEX_INSTALL_COUNT=$((CODEX_INSTALL_COUNT + 1))
    CODEX_VERSION_YARN=$(yarn global list 2>/dev/null | grep codex | sed 's/.*@//')
    CODEX_INSTALLS="$CODEX_INSTALLS\n  - yarn: v$CODEX_VERSION_YARN"
fi

if brew list codex 2>/dev/null >/dev/null; then
    CODEX_INSTALL_COUNT=$((CODEX_INSTALL_COUNT + 1))
    CODEX_VERSION_BREW=$(brew info codex 2>/dev/null | head -1 | awk '{print $3}')
    CODEX_INSTALLS="$CODEX_INSTALLS\n  - brew: v$CODEX_VERSION_BREW"
fi
```

**如果检测到多版本安装**，输出警告：

```
⚠️  警告: 检测到 claude CLI 存在多个安装 (共 3 个)
  - npm: v1.0.16
  - pnpm: v1.0.14
  - brew: v1.0.15

   当前使用: $(which claude) -> npm 版本

   多版本可能导致:
   - 升级时版本不一致
   - PATH 优先级导致使用非预期版本
   - 命令行为不可预测
```

### 阶段 3：警告信息

**如果 ccstatusline 插件未配置**：

```
⚠️  警告: ccstatusline 状态行未配置
   - 缺少状态行增强功能
   - 插件无需安装，通过 npx/bunx 直接运行
   - 需在 ~/.claude/settings.json 中添加 statusLine 配置
   - 是否要自动配置？
```

**如果 codex CLI 未安装**：

```
⚠️  警告: codex CLI 未安装
   - 命令参数 --codex 将无法使用
   - 安装方式: npm install -g @openai/codex 或参考官方文档
```

**如果 gemini CLI 未安装**：

```
⚠️  警告: gemini CLI 未安装
   - 命令参数 --gemini 将无法使用
   - 安装方式: 参考 Google Gemini CLI 官方文档
```

**如果 Claude LSP 服务不完整**：

情况一：环境变量未配置
```
⚠️  警告: Claude LSP 环境变量未配置
   - 代码智能分析功能将受限（跳转定义、查找引用等）
   - 启用方式: 在 ~/.claude/settings.json 的 env 中添加 "ENABLE_LSP_TOOLS": "1"
```

情况二：缺少语言服务器
```
⚠️  警告: 缺少以下语言的 LSP 服务器
   - 检测到项目使用: TypeScript/JS Python
   - 缺少 LSP 服务器: typescript-language-server pyright
   - 是否要自动安装？
```

情况三：环境变量已配置但需要重启
```
⚠️  提示: 已配置 LSP 环境变量
   - 如果刚刚修改过配置，请重启 Claude Code 使其生效
```

### 阶段 4：处理 ccstatusline 插件配置

#### 4.1 如果未配置 statusLine

使用 `AskUserQuestion` 询问用户：

**问题**：ccstatusline 状态行未配置，是否要启用？

**选项**：
   - 选项 1: 使用 npx（推荐，兼容性好）
   - 选项 2: 使用 bunx（更快，需安装 bun）
   - 选项 3: 手动配置
   - 选项 4: 跳过

**如果用户选择自动配置（选项1或2）**：

1. 使用 Read 工具读取 `~/.claude/settings.json`
2. 使用 Edit 工具添加/更新 `statusLine` 配置：

   - 选项 1 (npx)：
   ```json
   {
     "statusLine": "npx ccstatusline@latest"
   }
   ```

   - 选项 2 (bunx)：
   ```json
   {
     "statusLine": "bunx ccstatusline@latest"
   }
   ```

3. 如果 settings.json 不存在，使用 Write 工具创建

**如果用户选择手动配置**：

输出：
```
请手动编辑 ~/.claude/settings.json，添加以下配置：

{
  "statusLine": "npx ccstatusline@latest"
}

或使用 bunx（更快）：

{
  "statusLine": "bunx ccstatusline@latest"
}

配置后立即生效，无需重启。
```

**配置成功后输出**：

```
✅ ccstatusline 状态行已配置

配置文件: ~/.claude/settings.json
配置内容: "statusLine": "npx ccstatusline@latest"

配置已立即生效，无需重启 Claude Code。

首次运行时，ccstatusline 会显示交互式配置界面，您可以：
- 自定义状态行显示内容
- 配置颜色和样式
- 添加自定义命令和文本

详细信息: https://github.com/sirmalloc/ccstatusline
```

#### 4.2 如果用户选择跳过

输出：
```
已跳过 ccstatusline 配置。

如需后续配置，请在 ~/.claude/settings.json 中添加：

{
  "statusLine": "npx ccstatusline@latest"
}

或访问项目主页了解更多：
https://github.com/sirmalloc/ccstatusline
```

### 阶段 5：处理 Claude LSP 服务配置

#### 5.1 如果 LSP 环境变量未配置

使用 `AskUserQuestion` 询问用户：

**问题**：Claude LSP 环境变量未配置，是否要启用？

**选项**：
   - 选项 1: 自动启用（推荐）
   - 选项 2: 手动启用
   - 选项 3: 跳过

**如果用户选择自动启用**：

使用 `jq` 或 Read+Edit 编辑 `~/.claude/settings.json`，在 `env` 部分添加：
```json
"ENABLE_LSP_TOOLS": "1"
```

#### 5.2 如果缺少语言服务器

使用 `AskUserQuestion` 询问用户：

**问题**：检测到项目使用 [语言列表]，但缺少对应的 LSP 服务器 [缺失列表]，是否要自动安装？

**选项**：
   - 选项 1: 自动安装全部（推荐）
   - 选项 2: 选择性安装
   - 选项 3: 跳过

**如果用户选择自动安装**：

根据缺失的 LSP 服务器执行安装命令：

```bash
# TypeScript/JavaScript
npm install -g typescript-language-server typescript

# Python
npm install -g pyright

# Go
go install golang.org/x/tools/gopls@latest

# Rust
rustup component add rust-analyzer 2>/dev/null || brew install rust-analyzer

# Java
brew install jdtls

# C/C++ (macOS)
xcode-select --install 2>/dev/null || brew install llvm
```

**安装成功后输出**：
```
✅ LSP 服务器安装完成

已安装:
- typescript-language-server (TypeScript/JS)
- pyright (Python)

⚠️  重要：请重启 Claude Code 使配置生效！

重启后可使用以下功能：
- goToDefinition (跳转定义)
- findReferences (查找引用)
- hover (悬停信息)
- documentSymbol (文档符号)
- getDiagnostics (诊断信息)
```

#### 5.3 如果用户选择跳过

输出：
```
已跳过 LSP 配置。如需后续配置：

1. 启用 LSP 环境变量:
   编辑 ~/.claude/settings.json，在 env 中添加 "ENABLE_LSP_TOOLS": "1"

2. 安装语言服务器:
   npm install -g typescript-language-server  # TypeScript/JS
   npm install -g pyright                      # Python
   go install golang.org/x/tools/gopls@latest # Go

详细指南: doc/claude-lsp-setup.md
```

### 阶段 6：处理 CLI 多版本安装

如果检测到 `claude` 或 `codex` CLI 存在多个安装（安装数量 > 1）：

#### 6.1 显示多版本详情

```
检测到 CLI 多版本安装

claude CLI (共 3 个安装):
  - npm: v1.0.16 ← 当前使用
  - pnpm: v1.0.14
  - brew: v1.0.15

codex CLI (共 2 个安装):
  - npm: v0.1.5
  - yarn: v0.1.4 ← 当前使用
```

#### 6.2 询问用户处理方式

使用 `AskUserQuestion` 询问用户：

**问题**：检测到 [CLI名称] 存在多个安装，这可能导致升级时版本混乱。是否要清理？

**选项**：
   - 选项 1: 保留 npm 版本，卸载其他（推荐）
   - 选项 2: 保留 pnpm 版本，卸载其他
   - 选项 3: 保留 yarn 版本，卸载其他
   - 选项 4: 保留 brew 版本，卸载其他
   - 选项 5: 跳过，保持现状

> 注：只显示用户实际安装的选项

#### 6.3 执行清理

**如果用户选择清理**：

```bash
# 卸载 npm 版本
npm uninstall -g @anthropic-ai/claude-code

# 卸载 pnpm 版本
pnpm remove -g @anthropic-ai/claude-code

# 卸载 yarn 版本
yarn global remove @anthropic-ai/claude-code

# 卸载 brew 版本
brew uninstall claude

# 同理处理 codex
npm uninstall -g @openai/codex
pnpm remove -g @openai/codex
yarn global remove @openai/codex
brew uninstall codex
```

#### 6.4 升级到最新版本

清理完成后，使用保留的包管理器升级到最新版本：

```bash
# npm
npm install -g @anthropic-ai/claude-code@latest
npm install -g @openai/codex@latest

# pnpm
pnpm add -g @anthropic-ai/claude-code@latest
pnpm add -g @openai/codex@latest

# yarn
yarn global add @anthropic-ai/claude-code@latest
yarn global add @openai/codex@latest

# brew
brew upgrade claude
brew upgrade codex
```

#### 6.5 输出清理结果

```
✅ CLI 多版本清理完成

claude CLI:
  - 已卸载: pnpm, brew
  - 保留: npm v1.0.16 → 已升级到 v1.0.17

codex CLI:
  - 已卸载: yarn
  - 保留: npm v0.1.5 → 已升级到 v0.1.6

现在可以正常升级，不会出现版本冲突。
```

#### 6.6 如果用户选择跳过

输出：

```
已跳过 CLI 多版本清理。

注意：多版本安装可能导致：
- 升级时只更新其中一个版本
- 不同终端使用不同版本
- 命令行为不可预测

如需后续清理，可再次运行 /dx:doctor
```

### 阶段 7：处理 codeagent-wrapper 未安装情况

如果 `codeagent-wrapper` 未安装：

1. 使用 `AskUserQuestion` 询问用户是否要自动安装：
   - 选项 1: 自动安装（推荐）- 下载并运行官方安装脚本
   - 选项 2: 手动安装 - 显示安装命令供用户复制

2. **如果用户选择自动安装**：

   执行安装命令：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/cexll/myclaude/master/install.sh | bash
   ```

   - 如果安装成功，输出成功消息并重新检测版本
   - 如果安装失败，输出错误信息并提示用户手动安装

3. **如果用户选择手动安装**：

   输出以下信息：
   ```
   请手动执行以下命令安装 codeagent-wrapper：

   curl -fsSL https://raw.githubusercontent.com/cexll/myclaude/master/install.sh | bash

   或者访问以下链接获取更多安装选项：
   https://github.com/cexll/myclaude/blob/master/install.sh
   ```

### 阶段 8：安装失败处理

如果自动安装失败，输出：

```
安装失败

自动安装过程中遇到错误。请尝试手动安装：

1. 下载安装脚本：
   curl -fsSL https://raw.githubusercontent.com/cexll/myclaude/master/install.sh -o install.sh

2. 查看脚本内容（可选）：
   cat install.sh

3. 执行安装：
   bash install.sh

如果问题持续，请访问：
https://github.com/cexll/myclaude/issues
```

## 输出格式

### 全部检测通过

```
环境诊断完成

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 已安装   | v1.2.3
codex              | 已安装   | v1.0.0
gemini             | 已安装   | v2.0.0
ccstatusline       | 已配置   | npx
Claude LSP 服务    | 完整     | -

检测到项目语言: TypeScript/JS
已安装的 LSP 服务器: typescript-language-server ✓

✅ 所有依赖已就绪，全部功能可用。
```

### 部分功能可用

```
环境诊断完成

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 已安装   | v1.2.3
codex              | 已安装   | v1.0.0
gemini             | 未安装   | -
ccstatusline       | 未配置   | -
Claude LSP 服务    | 部分     | -

检测到项目语言: TypeScript/JS Python
LSP 服务器状态:
- typescript-language-server ✓
- pyright ✗ (未安装)

⚠️  警告: gemini CLI 未安装
   - 命令参数 --gemini 将无法使用

⚠️  警告: ccstatusline 状态行未配置
   - 是否要自动配置？

⚠️  警告: 缺少 Python 的 LSP 服务器 (pyright)
   - 是否要自动安装？

核心功能已就绪。如需完整功能，请安装缺失的依赖。
```

### 检测到多版本安装

```
环境诊断完成

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 已安装   | v1.2.3
claude             | 多版本   | -
codex              | 多版本   | -
gemini             | 已安装   | v2.0.0
ccstatusline       | 已配置   | bunx
Claude LSP 服务    | 完整     | -

⚠️  警告: 检测到 claude CLI 存在多个安装 (共 3 个)
  - npm: v1.0.16 ← 当前使用
  - pnpm: v1.0.14
  - brew: v1.0.15

⚠️  警告: 检测到 codex CLI 存在多个安装 (共 2 个)
  - npm: v0.1.5 ← 当前使用
  - yarn: v0.1.4

多版本可能导致升级时版本混乱，是否要清理？
```

### 核心依赖缺失

```
环境诊断完成

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 未安装   | -
codex              | 未安装   | -
gemini             | 未安装   | -
ccstatusline       | 未安装   | -
Claude LSP 服务    | 未配置   | -

❌ 错误: codeagent-wrapper 未安装（核心依赖）

是否要自动安装 codeagent-wrapper？
```

### 安装成功

```
安装成功

codeagent-wrapper 已成功安装 (v1.2.3)

现在可以正常使用 dx 工具集了。
```

## 注意事项

- 安装脚本需要网络连接
- 某些系统可能需要 sudo 权限
- 如果使用代理，确保代理配置正确
- codex 和 gemini CLI 为可选依赖，不影响核心功能
- 未安装可选 CLI 时，对应的 `--codex` 或 `--gemini` 参数将不可用
- **多版本检测**：如果通过多个包管理器（npm、pnpm、yarn、brew）安装了同一 CLI，建议清理到只保留一个，避免升级时版本冲突
- **ccstatusline 插件**：
  - 无需全局安装，通过 npx/bunx 直接运行
  - 需在 `~/.claude/settings.json` 中添加 `statusLine` 配置
  - 配置后立即生效，无需重启 Claude Code
  - 推荐使用 npx（兼容性好）或 bunx（速度快）
  - 详细配置: https://github.com/sirmalloc/ccstatusline

## ccstatusline 配置说明

### 什么是 ccstatusline

ccstatusline 是一个 Claude Code 状态行增强插件，提供：
- 实时状态显示
- 自定义状态栏内容
- 交互式配置界面
- 支持自定义命令和文本
- 颜色和样式自定义

### 配置方法

1. **在 Claude Code 设置中启用**

   编辑 `~/.claude/settings.json`（Windows: `%USERPROFILE%\.claude\settings.json`）：

   ```json
   {
     "statusLine": "npx ccstatusline@latest"
   }
   ```

   或使用 bunx（更快，需先安装 bun）：

   ```json
   {
     "statusLine": "bunx ccstatusline@latest"
   }
   ```

2. **首次运行配置**

   配置后，首次启动 Claude Code 时会显示交互式配置界面：
   - 自定义状态行显示内容
   - 配置颜色和样式
   - 添加自定义命令和文本
   - 实时预览效果

3. **后续调整**

   配置存储在 `~/.config/ccstatusline/settings.json`，可以：
   - 重新运行 `npx ccstatusline@latest` 进入配置界面
   - 直接编辑配置文件

### 特点

- **无需全局安装**：通过 npx/bunx 直接运行，自动获取最新版本
- **立即生效**：配置后无需重启 Claude Code
- **轻量级**：不占用系统资源，按需加载
- **自定义性强**：完全可配置的状态栏内容

### 详细信息

项目主页: https://github.com/sirmalloc/ccstatusline

## Claude LSP 服务说明

### 配置要求

Claude LSP 服务需要两部分配置：

1. **启用 LSP 环境变量**

   在 `~/.claude/settings.json` 的 `env` 部分添加：
   ```json
   {
     "env": {
       "ENABLE_LSP_TOOLS": "1"
     }
   }
   ```

2. **安装语言服务器**

   根据项目使用的语言安装对应的 LSP 服务器：
   ```bash
   # TypeScript/JavaScript
   npm install -g typescript-language-server typescript

   # Python
   npm install -g pyright

   # Go
   go install golang.org/x/tools/gopls@latest

   # Rust
   rustup component add rust-analyzer

   # Java
   brew install jdtls

   # C/C++
   xcode-select --install  # 或 brew install llvm
   ```

**保存配置后需重启 Claude Code 才能生效。**

### LSP 功能

启用后可使用以下功能：
- `goToDefinition` - 跳转到符号定义
- `findReferences` - 查找所有引用
- `hover` - 悬停显示类型信息
- `documentSymbol` - 列出文档符号
- `getDiagnostics` - 获取诊断信息

### 经验总结

> 以下是配置 LSP 过程中的经验教训，避免走弯路。

**1. 需要安装语言服务器**

Claude Code 的 LSP 功能依赖系统已安装的语言服务器。仅设置环境变量是不够的，还需要安装对应语言的 LSP 服务器。

**2. 不需要 MCP 服务器**

网上很多教程提到使用 `cclsp` 等 MCP 服务器，但这会增加不必要的复杂度：
- 需要安装额外的 npm 包
- 需要配置 `.mcp.json`（settings.json 不支持 mcpServers 字段）
- `cclsp setup` 是交互式命令，无法在自动化脚本中使用
- 直接安装语言服务器更简单直接

**3. 常见问题**

- **Q: 设置了环境变量但 LSP 不工作？**
  - A: 需要安装对应语言的 LSP 服务器，仅设置环境变量是不够的

- **Q: 修改配置后没有效果？**
  - A: 必须重启 Claude Code 才能生效

- **Q: 如何验证 LSP 是否工作？**
  - A: 在对话中请求 Claude "跳转到 xxx 函数的定义"，如果能精确定位说明 LSP 工作正常

- **Q: 支持哪些语言？**
  - A: 取决于安装的语言服务器，常见的有 TypeScript、Python、Go、Rust、Java、C/C++ 等
