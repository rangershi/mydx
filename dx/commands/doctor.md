---
allowed-tools: [Bash, AskUserQuestion]
description: '环境诊断：检测并安装 codeagent-wrapper 及后端 CLI 依赖'
model: sonnet
---

## Usage

```bash
/dx:doctor
```

## 检测项

### 1. codeagent-wrapper (必需)
```bash
which codeagent-wrapper && codeagent-wrapper --version 2>/dev/null
```

### 2. codex CLI (可选)
```bash
which codex && codex --version 2>/dev/null
```

### 3. gemini CLI (可选)
```bash
which gemini && gemini --version 2>/dev/null
```

### 4. ccstatusline (推荐)
```bash
grep -q '"statusLine"' ~/.claude/settings.json 2>/dev/null
```
配置: 在 `~/.claude/settings.json` 添加 `"statusLine": "npx ccstatusline@latest"`

### 5. CLI 多版本检测
检测 npm/pnpm/yarn/brew 是否重复安装 claude/codex CLI，避免升级冲突。

```bash
# 检测各包管理器安装情况
npm list -g @anthropic-ai/claude-code 2>/dev/null | grep -q claude-code
pnpm list -g @anthropic-ai/claude-code 2>/dev/null | grep -q claude-code
yarn global list 2>/dev/null | grep -q claude-code
brew list claude 2>/dev/null
```

### 6. LSP 服务

检测环境变量：
```bash
grep -q 'ENABLE_LSP_TOOLS' ~/.claude/settings.json
```

语言服务器映射：
- TypeScript/JS → typescript-language-server
- Python → pyright
- Go → gopls
- Rust → rust-analyzer
- Java → jdtls
- C/C++ → clangd

安装命令：
```bash
npm install -g typescript-language-server typescript  # TS/JS
npm install -g pyright                                # Python
go install golang.org/x/tools/gopls@latest           # Go
rustup component add rust-analyzer                    # Rust
brew install jdtls                                    # Java
xcode-select --install                                # C/C++
```

## 工作流程

### 阶段 1：检测并输出报告

执行所有检测项，输出表格：
```
工具               | 状态     | 版本
codeagent-wrapper  | 已安装   | v1.2.3
codex              | 已安装   | v1.0.0
gemini             | 未安装   | -
ccstatusline       | 已配置   | npx
LSP 服务           | 完整     | -
```

如有多版本安装，显示警告并列出各包管理器的版本。

### 阶段 2：处理缺失项

#### ccstatusline 未配置
使用 `AskUserQuestion` 询问：npx(推荐) / bunx / 手动 / 跳过
- 自动配置：Edit `~/.claude/settings.json`，添加 `"statusLine": "npx ccstatusline@latest"`
- 手动配置：输出配置说明
- 跳过：输出跳过提示

#### LSP 未配置
1. 环境变量未配置：询问是否添加 `"ENABLE_LSP_TOOLS": "1"` 到 settings.json
2. 缺少语言服务器：询问是否自动安装，执行对应安装命令
3. 安装成功：提示重启 Claude Code

#### CLI 多版本
如检测到多版本：
1. 显示所有安装及版本
2. 询问保留哪个包管理器
3. 卸载其他版本，升级保留版本

#### codeagent-wrapper 未安装
询问是否自动安装：
```bash
curl -fsSL https://raw.githubusercontent.com/cexll/myclaude/master/install.sh | bash
```

## 输出示例

全部就绪：
```
工具               | 状态     | 版本
codeagent-wrapper  | 已安装   | v1.2.3
codex              | 已安装   | v1.0.0
ccstatusline       | 已配置   | npx
LSP 服务           | 完整     | -

✅ 所有依赖已就绪
```

部分缺失：
```
工具               | 状态     | 版本
codeagent-wrapper  | 已安装   | v1.2.3
codex              | 未安装   | -
ccstatusline       | 未配置   | -
LSP 服务           | 部分     | -

⚠️ codex CLI 未安装
⚠️ ccstatusline 未配置，是否启用？
⚠️ 缺少 Python LSP (pyright)，是否安装？
```
