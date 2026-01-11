---
allowed-tools: [Bash, AskUserQuestion]
description: '环境诊断：检测并安装 codeagent-wrapper 及后端 CLI 依赖'
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

### 4. Claude LSP 服务 (推荐)

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

### 阶段 2：输出诊断报告

根据检测结果输出报告：

```
环境诊断报告

工具               | 状态     | 版本      | 说明
-------------------|----------|-----------|------------------
codeagent-wrapper  | 已安装   | v1.2.3    | 核心依赖
codex              | 已安装   | v1.0.0    | 支持 --codex 参数
gemini             | 未安装   | -         | 支持 --gemini 参数
Claude LSP 服务    | 完整     | -         | 代码智能分析

检测到项目语言: TypeScript/JS Python
已安装的 LSP 服务器: typescript-language-server pyright
```

### 阶段 3：警告信息

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

### 阶段 4：处理 Claude LSP 服务配置

#### 4.1 如果 LSP 环境变量未配置

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

#### 4.2 如果缺少语言服务器

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

#### 4.3 如果用户选择跳过

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

### 阶段 5：处理 codeagent-wrapper 未安装情况

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

### 阶段 6：安装失败处理

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
Claude LSP 服务    | 部分     | -

检测到项目语言: TypeScript/JS Python
LSP 服务器状态:
- typescript-language-server ✓
- pyright ✗ (未安装)

⚠️  警告: gemini CLI 未安装
   - 命令参数 --gemini 将无法使用

⚠️  警告: 缺少 Python 的 LSP 服务器 (pyright)
   - 是否要自动安装？

核心功能已就绪。如需完整功能，请安装缺失的依赖。
```

### 核心依赖缺失

```
环境诊断完成

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 未安装   | -
codex              | 未安装   | -
gemini             | 未安装   | -
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
