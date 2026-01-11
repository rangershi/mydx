# Claude Code LSP 配置指南

Claude Code 的 LSP 功能需要两部分配置：
1. **启用 LSP 环境变量**
2. **安装语言服务器**

## 第一步：启用 LSP 环境变量

编辑 `~/.claude/settings.json`，在 `env` 部分添加：

```json
{
  "env": {
    "ENABLE_LSP_TOOLS": "1"
  }
}
```

## 第二步：安装语言服务器

根据项目使用的语言，安装对应的 LSP 服务器：

### TypeScript / JavaScript

```bash
npm install -g typescript-language-server typescript
```

### Python

```bash
npm install -g pyright
# 或
pip install pyright
```

### Go

```bash
go install golang.org/x/tools/gopls@latest
```

### Rust

```bash
rustup component add rust-analyzer
# 或 macOS:
brew install rust-analyzer
```

### Java

```bash
# 需要 Java 21+
brew install jdtls
```

### C / C++

```bash
# macOS - 安装 Xcode Command Line Tools
xcode-select --install

# 或安装 LLVM
brew install llvm
```

## 第三步：重启 Claude Code

**保存配置后必须重启 Claude Code 才能生效！**

## 验证安装

重启后，在对话中请求 Claude：
- "跳转到 xxx 函数的定义"
- "查找 xxx 的所有引用"

如果 Claude 能精确定位而非进行文本搜索，说明 LSP 配置成功。

## LSP 功能

配置成功后可使用：
- `goToDefinition` - 跳转到符号定义
- `findReferences` - 查找所有引用
- `hover` - 悬停显示类型信息
- `documentSymbol` - 列出文档符号
- `getDiagnostics` - 获取诊断信息

---

## 常见问题

**Q: 设置了环境变量但 LSP 不工作？**

需要安装对应语言的 LSP 服务器，仅设置环境变量是不够的。

**Q: 修改配置后没有效果？**

必须重启 Claude Code 才能生效。

**Q: 需要使用 MCP 服务器（如 cclsp）吗？**

不需要。直接安装语言服务器更简单：
- MCP 服务器需要额外配置 `.mcp.json`
- `cclsp setup` 是交互式命令，不便于自动化
- 直接安装语言服务器即可满足需求

**Q: settings.json 支持 mcpServers 字段吗？**

不支持。MCP 服务器需要通过 `.mcp.json` 文件配置，但使用本指南的方式不需要 MCP。

---

## 参考资料

- [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server)
- [pyright](https://github.com/microsoft/pyright)
- [gopls](https://pkg.go.dev/golang.org/x/tools/gopls)
- [rust-analyzer](https://rust-analyzer.github.io/)
