---
allowed-tools: [Bash, AskUserQuestion]
description: '环境诊断：检测并安装 codeagent-wrapper 依赖'
---

## Usage

```bash
/dx:doctor
```

检测当前系统的开发环境配置，确保必要的工具已正确安装。

## 检测项

### 1. codeagent-wrapper

检测 `codeagent-wrapper` 是否已安装且为最新版本。

**检测命令**：

```bash
# 检查是否安装
which codeagent-wrapper || command -v codeagent-wrapper

# 检查版本（如果已安装）
codeagent-wrapper --version 2>/dev/null
```

## 工作流程

### 阶段 1：环境检测

执行以下检测：

```bash
# 1. 检查 codeagent-wrapper 是否存在
if command -v codeagent-wrapper &> /dev/null; then
    echo "codeagent-wrapper 已安装"
    codeagent-wrapper --version
else
    echo "codeagent-wrapper 未安装"
fi
```

### 阶段 2：输出诊断报告

根据检测结果输出报告：

```
环境诊断报告

工具               | 状态     | 版本
-------------------|----------|--------
codeagent-wrapper  | 已安装   | v1.2.3
                   | 或       |
codeagent-wrapper  | 未安装   | -
```

### 阶段 3：处理未安装情况

如果 `codeagent-wrapper` 未安装：

1. 使用 `AskUserQuestion` 询问用户是否要自动安装：
   - 选项 1: 自动安装（推荐）- 下载并运行官方安装脚本
   - 选项 2: 手动安装 - 显示安装命令供用户复制

2. **如果用户选择自动安装**：

   执行安装命令：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/rangershi/mydx/master/install.sh | bash
   ```

   - 如果安装成功，输出成功消息并重新检测版本
   - 如果安装失败，输出错误信息并提示用户手动安装

3. **如果用户选择手动安装**：

   输出以下信息：
   ```
   请手动执行以下命令安装 codeagent-wrapper：

   curl -fsSL https://raw.githubusercontent.com/rangershi/mydx/master/install.sh | bash

   或者访问以下链接获取更多安装选项：
   https://github.com/rangershi/mydx/blob/master/install.sh
   ```

### 阶段 4：安装失败处理

如果自动安装失败，输出：

```
安装失败

自动安装过程中遇到错误。请尝试手动安装：

1. 下载安装脚本：
   curl -fsSL https://raw.githubusercontent.com/rangershi/mydx/master/install.sh -o install.sh

2. 查看脚本内容（可选）：
   cat install.sh

3. 执行安装：
   bash install.sh

如果问题持续，请访问：
https://github.com/rangershi/mydx/issues
```

## 输出格式

### 检测通过

```
环境诊断完成

codeagent-wrapper: 已安装 (v1.2.3)

所有依赖已就绪。
```

### 需要安装

```
环境诊断完成

codeagent-wrapper: 未安装

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
