# DX - Developer Experience Toolkit

团队内部使用的开发者体验工具集，提供符合团队流程的命令和自动化 Agent。

## 功能

- **Commands**: 用户触发的开发流程命令
- **Agents**: 自动化执行的智能代理

## 安装

此插件作为 mydx 插件集的一部分自动加载。

## 使用

### Commands

```bash
/dx:<command-name>
```

### Agents

Agent 会根据场景自动触发，或通过特定关键词激活。

## 添加新组件

### 添加 Command

1. 在 `commands/` 目录创建 `.md` 文件
2. 在 `marketplace.json` 的 `commands` 数组中注册

### 添加 Agent

1. 在 `agents/` 目录创建 `.md` 文件
2. 在 `marketplace.json` 的 `agents` 数组中注册

## 目录结构

```
dx/
├── .claude-plugin/
│   └── marketplace.json    # 插件配置
├── commands/               # 命令定义
├── agents/                 # Agent 定义
└── README.md
```
