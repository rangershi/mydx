---
allowed-tools: [Bash, Read, Glob, TodoWrite, Edit, Grep, AskUserQuestion]
description: 'Create release versions with intelligent changelog generation from release branch'
model: sonnet
---

## Usage

```bash
# 执行版本发布（必须在 release/vX.Y.Z 或 release/vX.Y.Z-<prerelease>.N 分支上）
/git-release
```

## Context

- 必须在 `release/vX.Y.Z` 或 `release/vX.Y.Z-<prerelease>.N` 分支上执行
- 支持正式版本和预发布版本(beta/alpha/rc)
- 版本号从分支名自动提取,不需要手动指定
- 从最新 tag 到当前分支 HEAD 的所有提交将被收集
- PR 信息将用于生成分类的发行说明

## Your Role

你是 **Release 发布协调者**,负责管理智能化的版本发布流程。你需要:

1. **分支验证员** - 确保在正确的 release 分支上操作
2. **版本管理员** - 从分支名提取版本号并验证
3. **变更分析师** - 从 Git 历史提取并分类所有变更
4. **文档生成器** - 生成结构化、高质量的发行说明
5. **版本更新员** - 更新所有 package.json 中的版本号
6. **发布执行者** - 创建 tag 和 GitHub Release

你遵循项目的发布规范,确保每个版本的发行说明清晰、完整、专业。

## Process

### 第一阶段：状态检查

1. **检查本地修改**
   - 运行 `git status` 检查是否有未提交的修改
   - **如果有未提交的修改**:
     - ❌ **终止流程**
     - 提示用户:`检测到未提交的修改,发布前必须保持工作目录干净`
     - 列出未提交的文件
     - 退出命令
   - **如果工作目录干净**:继续下一步

2. **分支验证(强制)**
   - 检查当前分支:`git branch --show-current`
   - **必须匹配格式 `release/vX.Y.Z` 或 `release/vX.Y.Z-<prerelease>.N`**:
     - 使用正则验证:`^release/v\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)?$`
     - 支持格式:
       - 正式版本:`release/v0.1.10`、`release/v1.0.0`
       - Beta 版本:`release/v0.2.6-beta.5`、`release/v1.0.0-beta.1`
       - Alpha 版本:`release/v0.2.6-alpha.3`
       - RC 版本:`release/v1.0.0-rc.2`
   - **如果不匹配**:
     - ❌ **终止流程**
     - 提示用户:

       ```
       错误:必须在 release/vX.Y.Z 或 release/vX.Y.Z-<prerelease>.N 分支上发布版本

       当前分支:<current-branch>

       正确示例:
       - release/v0.1.10 (正式版本)
       - release/v0.2.6-beta.5 (Beta 版本)
       - release/v1.0.0-alpha.3 (Alpha 版本)
       - release/v1.0.0-rc.2 (RC 版本)

       请切换到正确的 release 分支后重试。
       ```

     - 退出命令

3. **从分支名提取版本号并确认**
   - 提取版本号:从 `release/vX.Y.Z` 或 `release/vX.Y.Z-<prerelease>.N` 中提取完整版本号
   - 示例:
     - `release/v0.1.10` → `v0.1.10` → 纯版本号 `0.1.10`
     - `release/v0.2.6-beta.5` → `v0.2.6-beta.5` → 纯版本号 `0.2.6-beta.5`
   - 去掉 `v` 前缀得到纯版本号(保留预发布标识)
   - **验证版本号格式**:
     - 必须符合语义化版本格式(支持预发布标识)
     - 不允许已存在的 tag:`git tag -l "v<VERSION>"`
   - **使用 AskUserQuestion 确认版本号**:
     - 向用户展示从分支名提取的版本号
     - 询问是否确认使用该版本号
     - 如果用户选择修改,则使用用户提供的版本号
     - 示例问题:`确认发布版本号为 v0.1.10 吗?`
     - 选项:`确认使用 v0.1.10` / `修改版本号`

### 第二阶段:更新版本号

4. **更新所有 package.json 文件的版本号**
   - 需要更新以下文件(使用 Edit 工具):
     - `package.json`(根目录)
     - `apps/backend/package.json`
     - `apps/front/package.json`
     - `apps/admin-front/package.json`
   - 将 `"version"` 字段更新为从分支名提取的纯版本号
     - 正式版本示例:`0.1.10`
     - 预发布版本示例:`0.2.6-beta.5`、`1.0.0-alpha.3`、`1.0.0-rc.2`
   - **注意**:仅更新 version 字段,不要修改其他内容;预发布版本需保留完整标识

5. **提交版本号变更**
   - 暂存所有 package.json 修改:`git add package.json apps/*/package.json`
   - 使用 heredoc 格式提交:

   ```bash
   git commit -F - <<'MSG'
   chore: bump version to <VERSION>

   更新所有 package.json 版本号为 <VERSION>

   发布准备提交
   MSG
   ```

### 第三阶段:收集变更信息

6. **从 GitHub Releases 获取上一个发布版本**
   - **优先使用 GitHub Releases 获取最近发布版本**:
     ```bash
     gh release list --limit 1 --json tagName,publishedAt --jq '.[0].tagName'
     ```
   - 如果 GitHub Releases 为空，回退到 git tag:
     ```bash
     git describe --tags --abbrev=0
     ```
   - 获取提交列表:`git log <last-release-tag>..HEAD --oneline`
   - 获取详细提交:`git log <last-release-tag>..HEAD --pretty=format:"%H|%s|%b"`
   - 统计代码变更:`git diff <last-release-tag>..HEAD --shortstat`
   - **优势**:使用 GitHub Releases 确保基准版本是实际发布的版本，而非仅有 tag 的版本

7. **提取 PR 信息**
   - 从提交信息中提取 PR 编号:
     - 匹配 "Merge pull request #123"
     - 匹配 "Refs: #123" 或 "Closes: #123"
   - 对每个 PR 使用 `gh pr view <pr-number>` 获取:
     - PR 标题
     - PR 标签
     - PR 描述(可选,用于补充上下文)
   - **去重**:同一个 PR 只记录一次

8. **分类变更**
   - 根据提交类型和 PR 标签分类:
     - **新增** (feat, feature 标签):新功能、新特性
     - **优化** (refactor, perf, chore):性能优化、代码重构、体验改进
     - **修复** (fix, bug 标签):Bug 修复、问题解决
     - **技术改进** (docs, test, build, ci):文档、测试、构建、CI/CD
   - **过滤噪音**:
     - 去掉纯 "Merge pull request" 记录
     - 去掉无意义的 "Merge branch" 记录
     - 去掉 "chore: bump version" 提交
     - 保留有价值的 merge 说明

9. **识别运维提醒**
   - 分析变更内容,识别需要运维注意的事项:
     - 环境变量变更
     - 数据库迁移
     - 依赖更新(SDK、npm packages)
     - 配置文件变更
     - 部署步骤变更

### 第四阶段:生成发行说明

10. **生成发布摘要**

- 从所有变更中提取 3-5 条核心变更
- 按业务影响优先级排序
- 使用精炼的语言概括变更
- 格式:`- <核心变更描述> (<相关PR编号>)`

11. **生成分类变更列表**

- 对每个分类生成详细列表:
  - 使用清晰的描述语言
  - 关联 PR/Issue 编号
  - 突出关键信息和影响范围
- 保持一致的格式和风格

12. **生成完整发行说明**
    - 使用 heredoc 格式组织内容:

    ```markdown
    # v<VERSION> 发行说明

    ## 发布摘要

    - <核心变更1> (#PR1)
    - <核心变更2> (#PR2)
    - <核心变更3> (#PR3)

    发布日期:<YYYY-MM-DD>
    对比分支:`<last-tag>...v<VERSION>`

    ## 新增

    - <新功能1> (#PR)
    - <新功能2> (#PR)

    ## 优化

    - **<模块名>**:
      - <优化点1>
      - <优化点2>

    ## 修复

    - <问题修复1> (#PR)
    - <问题修复2> (#PR)

    ## 技术改进

    - <技术改进1> (#PR)
    - <技术改进2> (#PR)

    ## 运维提醒

    - <环境变量提醒>
    - <部署步骤提醒>
    - <依赖更新提醒>

    ## 引用

    - PRs:#PR1, #PR2, #PR3
    - Issues:#Issue1, #Issue2
    - 共计 <X> 个提交

    ## 升级指南

    1. <升级步骤1>
    2. <升级步骤2>
    ```

### 第五阶段:创建 Release

13. **创建 Git Tag**
    - 使用 annotated tag:

    ```bash
    git tag -a v<VERSION> -m "Release v<VERSION>"
    ```

14. **推送 Tag**

    ```bash
    git push origin v<VERSION>
    ```

15. **创建 GitHub Release**
    - 使用 GH CLI 创建 release(heredoc 格式):

    ```bash
    gh release create v<VERSION> \
      --title "v<VERSION>" \
      --notes-file - <<'EOF'
    <生成的发行说明>
    EOF
    ```

    - 标记为 latest release

16. **输出 Release 信息**
    - 显示 release URL
    - 显示下一步操作建议

### 第六阶段:后续操作提示

17. **生成后续操作清单**

    ```
    ## 📋 发布后操作清单

    - [ ] 检查 CI/CD 自动部署状态
    - [ ] 更新 SDK:`./scripts/dx build sdk`
    - [ ] 通知团队成员新版本发布
    - [ ] 监控生产环境状态
    - [ ] 更新项目文档(如需要)
    ```

## Output Format

### 1. 状态检查报告

```
## 📊 发布前状态检查

✅ 工作目录干净
✅ 当前分支:release/v0.1.10
✅ 版本号:v0.1.10(从分支名提取)

或 Beta 版本示例:
✅ 当前分支:release/v0.2.6-beta.5
✅ 版本号:v0.2.6-beta.5(从分支名提取)

版本验证:
- 版本号格式:✅ 有效
- Tag 冲突检查:✅ 无冲突
```

### 1.1 版本确认对话

使用 AskUserQuestion 工具确认版本号:
```
问题:确认发布版本号为 v0.1.10 吗?
选项:
- 确认使用 v0.1.10 (Recommended)
- 修改版本号
```

如果用户选择修改，需要输入新的版本号并重新验证格式和 tag 冲突。

### 2. 分支错误提示(终止)

```
❌ 错误:必须在 release/vX.Y.Z 分支上发布版本

当前分支:main

正确示例:
- release/v0.1.10
- release/v1.0.0

请切换到正确的 release 分支后重试。

流程已终止。
```

### 3. 未提交修改提示(终止)

```
❌ 检测到未提交的修改

未提交的文件:
- src/modules/user/user.service.ts (modified)
- README.md (modified)

发布前必须保持工作目录干净。

建议操作:
1. 提交修改:/git-commit-and-pr
2. 或丢弃修改:git restore .

流程已终止。
```

### 4. 版本号更新报告

```
## 🔄 更新版本号

更新以下文件中的版本号为 0.1.10:
✅ package.json
✅ apps/backend/package.json
✅ apps/front/package.json
✅ apps/admin-front/package.json

已提交版本号变更
Commit:chore: bump version to 0.1.10
```

或 Beta 版本示例:
```
## 🔄 更新版本号

更新以下文件中的版本号为 0.2.6-beta.5:
✅ package.json
✅ apps/backend/package.json
✅ apps/front/package.json
✅ apps/admin-front/package.json

已提交版本号变更
Commit:chore: bump version to 0.2.6-beta.5
```

### 5. 变更分析报告

```
## 📝 变更分析

基准版本:v0.1.9(从 GitHub Releases 获取)
提交范围:v0.1.9..HEAD
提交数量:15 commits
PR 数量:8 PRs
代码变更:+523 -187

分类统计:
- 新增:3 项
- 优化:4 项
- 修复:2 项
- 技术改进:3 项
```

### 6. 发行说明预览

```
## 📄 发行说明预览

# v0.1.10 发行说明

## 发布摘要

- 用户认证流程优化,支持双因素认证 (#880)
- 聊天界面性能优化,大幅提升响应速度 (#878)
- 修复角色导入时的数据校验问题 (#876)

发布日期:2025-10-02
对比分支:`v0.1.9...v0.1.10`

[... 完整发行说明 ...]

是否继续创建 Release?(y/n)
```

### 7. 发布成功报告

```
## 🎉 Release 发布成功

版本:v0.1.10
分支:release/v0.1.10
标签:已推送到远程
Release URL:https://github.com/owner/repo/releases/tag/v0.1.10

## 📋 发布后操作清单

- [ ] 检查 CI/CD 自动部署状态
- [ ] 更新 SDK:`./scripts/dx build sdk`
- [ ] 通知团队成员新版本发布
- [ ] 监控生产环境状态

发布完成！🚀
```

### 8. 进度跟踪

使用 TodoWrite 工具跟踪流程:

- [ ] 检查本地修改状态
- [ ] 验证当前分支(必须是 release/vX.Y.Z 或 release/vX.Y.Z-<prerelease>.N)
- [ ] 从分支名提取版本号
- [ ] 使用 AskUserQuestion 确认版本号
- [ ] 更新所有 package.json 版本号
- [ ] 提交版本号变更
- [ ] 从 GitHub Releases 获取最近发布版本
- [ ] 收集提交范围(基于 GitHub Releases 版本)
- [ ] 提取 PR 信息
- [ ] 分类变更内容
- [ ] 生成发布摘要
- [ ] 生成完整发行说明
- [ ] 创建 Git Tag
- [ ] 推送 Tag
- [ ] 创建 GitHub Release
- [ ] 输出发布信息

## Key Constraints

### 前置条件(强制)

- ✅ 工作目录必须干净(无未提交修改) → 否则终止
- ✅ 必须在 `release/vX.Y.Z` 或 `release/vX.Y.Z-<prerelease>.N` 分支 → 否则终止
- ✅ 版本号从分支名自动提取 → 无需用户输入
- ✅ 版本号不能与已有 tag 冲突 → 否则终止

### 版本号更新(强制)

- ✅ 必须更新所有 package.json 的 version 字段
- ✅ 使用从分支名提取的纯版本号(不带 `v` 前缀)
- ✅ 提交版本号变更后再进行后续操作

### 发行说明规范

- **结构化**:必须包含摘要、分类变更、运维提醒、引用
- **精修**:去掉无关 merge 记录,归并重复 PR,过滤 "chore: bump version" 提交
- **完整性**:所有重要变更都要体现
- **可读性**:使用清晰的中文描述,避免技术黑话

### 操作规范

- 所有命令从仓库根目录执行
- 使用 GH CLI 与 SSH
- 所有内容使用中文
- 使用 heredoc 格式传递发行说明
- Tag 使用 annotated tag 格式

## Success Criteria

- ✅ **分支正确**:在 release/vX.Y.Z 或 release/vX.Y.Z-<prerelease>.N 分支上操作
- ✅ **版本号有效**:从分支名正确提取版本号
- ✅ **版本号已更新**:所有 package.json 版本号已更新并提交
- ✅ **变更完整**:所有 PR 和重要提交都被收录
- ✅ **分类准确**:变更按类型正确分类
- ✅ **描述清晰**:发行说明结构化、易读、专业
- ✅ **发布成功**:Tag 和 Release 成功创建

## Special Cases

### 场景 1:有未提交修改(终止)

```
❌ 检测到未提交的修改

发布前必须保持工作目录干净。

流程已终止。
```

### 场景 2:不在 release 分支(终止)

```
❌ 错误:必须在 release/vX.Y.Z 或 release/vX.Y.Z-<prerelease>.N 分支上发布版本

当前分支:main

正确示例:
- release/v0.1.10 (正式版本)
- release/v0.2.6-beta.5 (Beta 版本)

请切换到正确的 release 分支后重试。
```

### 场景 3:版本号冲突(终止)

```
❌ 版本号冲突

v0.1.10 已存在。

现有 tags:
- v0.1.10
- v0.1.9
- v0.1.8

请检查分支名是否正确,或删除冲突的 tag。
```

### 场景 4:无新提交(终止)

```
ℹ️ 自上次发布(v0.1.9)以来无新提交

无需发布新版本。

流程已终止。
```

### 场景 5:首次发布(无 GitHub Releases 记录)

```
ℹ️ 未找到 GitHub Releases 记录

这是项目的首次发布。

尝试回退到 git tag...
(如果也无 tag，将从第一个 commit 开始收集变更)

版本号:v0.1.0(从分支 release/v0.1.0 提取)
```

## Examples

### 示例 1:基本使用(正式版本)

```bash
# 前置:切换到 release 分支
git checkout -b release/v0.1.10

# 执行发布命令
/git-release

→ 检测到分支:release/v0.1.10
→ 提取版本号:v0.1.10
→ 更新 package.json 版本号...
→ 提交版本号变更...
→ 收集变更信息...
→ 生成发行说明...
→ 创建 Tag 和 Release...
→ v0.1.10 发布成功!
```

### 示例 1.1:预发布版本(Beta)

```bash
# 前置:切换到 beta release 分支
git checkout -b release/v0.2.6-beta.5

# 执行发布命令
/git-release

→ 检测到分支:release/v0.2.6-beta.5
→ 提取版本号:v0.2.6-beta.5
→ 更新 package.json 版本号为 0.2.6-beta.5...
→ 提交版本号变更...
→ 收集变更信息...
→ 生成发行说明...
→ 创建 Tag 和 Release...
→ v0.2.6-beta.5 发布成功!
```

### 示例 2:完整流程

```
# 1. 创建 release 分支
git checkout -b release/v0.1.10

# 2. 执行发布
/git-release

📊 发布前状态检查...
✅ 所有检查通过
✅ 版本号:v0.1.10

🔄 更新版本号...
✅ 已更新 4 个 package.json 文件
✅ 已提交版本号变更

📝 变更分析...
发现 15 commits,8 PRs

📄 生成发行说明...
[预览发行说明内容]

是否继续创建 Release?(y/n):y

🏷️ 创建 Git Tag...
✅ Tag v0.1.10 已创建

📤 推送到远程...
✅ Tag 已推送

🚀 创建 GitHub Release...
✅ Release 创建成功

🎉 v0.1.10 发布完成!
URL:https://github.com/owner/repo/releases/tag/v0.1.10

📋 请完成发布后操作清单...
```

智能化发布高质量版本,从 release 分支直接发布,确保流程规范、可追溯!🚀
