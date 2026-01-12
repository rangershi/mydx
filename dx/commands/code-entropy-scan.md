---
allowed-tools: [Bash, Read, Glob, TodoWrite, Edit, Grep, SearchReplace, WebSearch]
description: '代码降熵扫描：识别并修复技术债务与规范违规'
model: sonnet
---

## Usage

```bash
# 执行完整扫描（默认：直接执行）
/code-entropy-scan

# 使用 Codex 后端执行
/code-entropy-scan --codex

# 使用 Gemini 后端执行
/code-entropy-scan --gemini
```

### Options
- `--codex`: 使用 codeagent-wrapper (Codex backend) 执行扫描和修复
- `--gemini`: 使用 codeagent-wrapper (Gemini backend) 执行扫描和修复

---

## 执行模式

用户通过参数直接指定执行模式，无需判断：

| 参数 | 执行方式 | 适用场景 |
|------|----------|----------|
| （默认） | 直接执行（当前模型） | 大多数任务，避免 Telephone Game |
| `--codex` | 委托 codeagent-wrapper (Codex) | 复杂任务、需要 Context Isolation |
| `--gemini` | 委托 codeagent-wrapper (Gemini) | 需要 Gemini 模型能力 |

### 模式传递机制

1. 解析参数，确定 `EXECUTION_MODE`:
   - 默认: `direct`
   - `--codex`: `codex`
   - `--gemini`: `gemini`

2. 根据 `EXECUTION_MODE` 决定执行方式：
   - `direct`: 使用 Edit/Read/Grep 等工具直接执行扫描和修复
   - `codex`/`gemini`: 委托给 `codeagent-wrapper --backend {mode}` 执行

3. 委托执行时的 prompt 格式：
   ```
   codeagent-wrapper --backend {mode} "执行代码降熵扫描第 N 阶段: {phase_description}"
   ```

---

命令会依次执行：
1. E2E 测试用例名称中文检查
2. E2E 测试重复实现检查
3. 分页 DTO 规范检查
4. 环境变量访问规范检查
5. 错误处理规范检查
6. Prisma 7.x 适配器规范检查
7. Prisma 7.x API 迁移检查
8. E2E 测试统一夹具检查
9. 独立脚本环境加载检查

扫描完成后直接在对话中展示报告，并询问是否需要修复。

## 背景与目标

代码熵（Code Entropy）会随时间累积，表现为：
- 命名不一致（中英文混用）
- 重复实现（未复用夹具函数）
- 规范偏离（未使用标准 DTO）

本命令通过自动化扫描与修复，降低技术债务，保持代码库健康。

## 检查项说明

### 1. E2E 测试用例名称中文检查（e2e-chinese）

**问题**：
E2E 测试用例名称（`it('...')` / `describe('...')`）中使用中文字符，影响国际化与工具链兼容性。

**扫描范围**：
- `apps/backend/e2e/**/*.e2e-spec.ts`

**检测规则**：
```typescript
// ❌ 错误示例
describe('用户认证测试', () => {
  it('应该成功登录', async () => { ... })
})

// ✅ 正确示例
describe('User Authentication', () => {
  it('should login successfully', async () => { ... })
})
```

**修复策略**：
1. 使用 AI 翻译服务将中文测试名称翻译为规范英文
2. 保持原有测试逻辑不变
3. 在注释中保留原始中文说明（可选）

### 2. E2E 测试重复实现检查（e2e-fixtures）

**问题**：
测试用例中重复实现了 `fixtures.ts` 已有的功能（如创建用户、创建角色等），未调用夹具函数。

**扫描范围**：
- `apps/backend/e2e/**/*.e2e-spec.ts`
- 参考 `apps/backend/e2e/fixtures/fixtures.ts`

**检测模式**（识别重复实现）：
```typescript
// fixtures.ts 提供的功能：
- createTestingApp()
- createTestUser()
- createAdminUser()
- createSuperAdminUser()
- createTestCharacter()
- createTestStory()
- createTestSSEStory()
- createTestSSECharacter()
- seedVerificationCode()
- generateTestJwtToken()
- createAuthRequest()
- createAdminAuthRequest()
- cleanupTestData()
- cleanupSSETestData()
- buildApiUrl()

// ❌ 重复实现示例
const user = await prisma.user.create({
  data: { email: 'test@example.com', password: '...' }
})
const token = jwtService.sign({ sub: user.id })

// ✅ 使用夹具
const { profile, token } = await createTestUser(app, 'test')
```

**检测逻辑**：
1. 搜索 E2E 文件中直接操作 `prisma.user.create()`、`prisma.character.create()` 等模式
2. 搜索手动构造 JWT token 的代码（未使用 `generateTestJwtToken()`）
3. 搜索手动拼接 API URL 的代码（未使用 `buildApiUrl()`）
4. 搜索手动创建 HTTP 请求的代码（未使用 `createAuthRequest()`）
5. 与 `fixtures.ts` 功能对比，生成重构建议

**修复策略**：
1. 替换重复实现为夹具函数调用
2. 确保测试逻辑保持一致
3. 删除冗余代码

### 3. 分页 DTO 规范检查（pagination）

**问题**：
Backend 接口需要分页的地方未使用统一的 `BasePaginationResponseDto` 标准。

**扫描范围**：
- `apps/backend/src/modules/**/dto/responses/*.response.dto.ts`
- `apps/backend/src/modules/**/controllers/*.controller.ts`

**标准规范**：
```typescript
// ✅ 请求端：继承 BasePaginationRequestDto
import { BasePaginationRequestDto } from '@/common/dto/base.pagination.request.dto'

export class ListItemsDto extends BasePaginationRequestDto {
  // 额外查询参数
}

// ✅ 响应端：使用 BasePaginationResponseDto
import { BasePaginationResponseDto } from '@/common/dto/base.pagination.response.dto'
import { ItemResponseDto } from './item.response.dto'

export class ItemPaginationResponseDto extends BasePaginationResponseDto<ItemResponseDto> {
  @ApiProperty({
    description: '数据列表',
    type: ItemResponseDto,
    isArray: true,
  })
  items: ItemResponseDto[]
}

// 或者使用工厂方法
export const ItemPaginationResponseDto = BasePaginationResponseDto.createPaginationResponseDto(ItemResponseDto)
```

**检测模式**（识别非标准分页）：
```typescript
// ❌ 自定义分页结构
export class CustomListResponseDto {
  data: Item[]
  total: number
  pageSize: number
  currentPage: number
}

// ❌ 手动实现分页逻辑
return {
  items: results,
  total: count,
  page: query.page,
  limit: query.limit,
}
```

**检测逻辑**：
1. 搜索包含 `page`、`limit`、`total`、`items` 等分页关键字的 Response DTO
2. 检查是否继承自 `BasePaginationResponseDto`
3. 搜索 Controller 返回值中手动构造分页结构的代码
4. 生成不符合规范的文件清单

**修复策略**：
1. 将自定义分页 DTO 改为继承 `BasePaginationResponseDto`
2. 使用 `new BasePaginationResponseDto(total, page, limit, items)` 构造返回值
3. 更新 OpenAPI 文档注解
4. 确保向后兼容（字段名称映射）

### 4. 环境变量访问规范检查（env-accessor）

**问题**：
直接访问 `process.env` 会绕过统一的环境配置入口，导致：
- 不同运行环境（本地、测试、CI）读取到的值来源不一致，难以排查
- 无法复用 `EnvService` 的缓存、阈值裁剪与调试开关逻辑
- 破坏 `ConfigModule` / `registerAs` 的依赖注入链路

**扫描范围**：
- `apps/backend/src/**/*.ts`
- `apps/backend/e2e/**/*.ts`
- 仅排除真正的基础封装文件（`apps/backend/src/common/env/env.accessor.ts`、`apps/backend/src/common/services/env.service.ts` 等），**不要排除 `apps/backend/src/config/**/*.ts`**，确保配置模块同样接受扫描

**检测规则**：
```bash
# 查找直接使用 process.env 的语句，过滤受允许的少量文件
rg "process\.env" apps/backend/src apps/backend/e2e \
  --glob '!*env.accessor.ts' \
  --glob '!*env.service.ts'
```

**修复策略**：
1. 静态配置/`registerAs`：使用 `defaultEnvAccessor` 或 `createEnvAccessor(process.env)`。
2. 业务服务/控制器：注入 `EnvService`，通过 `getString/getInt/isProd` 等方法读取。
3. 独立脚本：显式创建 accessor（`const env = createEnvAccessor(process.env)`）。
4. 若必须读取原始值，使用 `EnvService.getAccessor().raw(key)` 并注明原因。

```typescript
// ❌ 错误示例
const redisHost = process.env.REDIS_HOST || 'localhost'

// ✅ 配置层（registerAs）
const env = defaultEnvAccessor
export const redisConfig = registerAs('redis', () => ({
  host: env.str('REDIS_HOST', 'localhost'),
}))

// ✅ 运行期服务
@Injectable()
export class ExampleService {
  constructor(private readonly env: EnvService) {}

  getRedisHost() {
    return this.env.getString('REDIS_HOST', 'localhost')
  }
}
```

该检查项会产出“直读 process.env 文件清单”，修复后需验证对应模块功能与配置一致性。

### 5. 错误处理规范检查（error-handling）

**问题**：
后端业务代码在抛出异常时绕过了统一的 `DomainException` / `ErrorCode` 体系，直接使用 `BadRequestException('字符串')`、`HttpException` 或手写 `throw new Error()`，导致：
- 前端无法依赖 `error.code` 做文案映射
- 日志缺少结构化 `args` 和 `requestId`
- 无法复用模块内已经定义的领域异常类

**扫描范围**：
- `apps/backend/src/**/*.ts`
- `apps/backend/e2e/**/*.ts`（验证测试夹具同样遵守规范）
- 排除：
  - `apps/backend/src/common/exceptions/**/*.ts`（领域异常定义本身）
  - `apps/backend/src/common/filters/**/*.ts`（全局过滤器可以直接继承 Nest 异常）
  - `apps/backend/src/main.ts`（ValidationPipe 自定义 `BadRequestException`）

**检测规则**：
```bash
# 1. 搜索直接实例化 Nest 标准异常的语句（排除白名单文件）
rg "new (BadRequestException|UnauthorizedException|ForbiddenException|NotFoundException|HttpException|InternalServerErrorException)\(" \
  apps/backend/src apps/backend/e2e \
  --glob '!*spec.ts' \
  --glob '!*exception.ts' \
  --glob '!apps/backend/src/common/filters/**' \
  --glob '!apps/backend/src/main.ts'

# 2. 搜索 `throw new Error` / `Promise.reject(new Error())`
rg "new Error\(" apps/backend/src apps/backend/e2e --glob '!*spec.ts'

# 3. 搜索缺失 ErrorCode 的 DomainException 使用（code 关键字缺失）
rg "new DomainException\([^)]*$" -A3 apps/backend/src

# 4. 检查 DomainException 直接使用中文 message（避免后端返回中文文案）
rg "DomainException\([^)]*[\u4e00-\u9fa5]" apps/backend/src apps/backend/e2e \
  --glob '!*spec.ts' \
  --glob '!apps/backend/src/common/exceptions/**'
```

命中项将被自动标记，并附带文件路径、行号和建议替换的领域异常（若能推断）。

**修复策略**：
1. **优先复用现有异常类**：若模块 `exceptions/` 已存在对应错误（例如钱包余额不足），直接 `throw new InsufficientBalanceException(...)`。
2. **否则创建新的领域异常**：
   - 在模块 `exceptions/` 目录新增类，继承 `DomainException`。
   - 在构造函数中指定明确的 `ErrorCode` 与 `args`。
   - 为新异常补充 `.spec.ts` 单元测试。
3. **临时需求**：如确需直接抛出 `DomainException`，确保 payload 中包含 `code: ErrorCode.XXX`，并在 `args` 里补充必要上下文。

```typescript
// ❌ 错误示例
throw new BadRequestException('余额不足, 请充值')

// ✅ 正确示例（复用模块异常）
throw new InsufficientBalanceException({
  currentBalance: wallet.available,
  requestedAmount: dto.amount,
  isFromFreeze: false,
})

// ✅ 正确示例（直接使用 DomainException）
throw new DomainException('余额不足', {
  code: ErrorCode.WALLET_INSUFFICIENT_BALANCE,
  args: { current: wallet.available, required: dto.amount },
})
```

### 6. Prisma 7.x 适配器规范检查（prisma-adapter）

**问题**：
Prisma 7.x 强制要求使用 Driver Adapter 模式，直接 `new PrismaClient()` 会导致运行时错误。这是 Prisma 7.x 的重大破坏性变更，容易被忽略。

**扫描范围**：
- `apps/backend/e2e/**/*.ts`
- `apps/backend/prisma/scripts/**/*.ts`
- `apps/backend/*.ts`（根目录独立脚本）

**检测规则**：
```typescript
// ❌ 错误示例（Prisma 7.x 不支持）
const prisma = new PrismaClient()

// ✅ 正确示例（使用 Driver Adapter）
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

const pool = new Pool({ connectionString: defaultEnvAccessor.str('DATABASE_URL') })
const adapter = new PrismaPg(pool)
const prisma = new PrismaClient({ adapter })

// ✅ E2E 测试正确示例（使用 PrismaService）
const { app, moduleFixture } = await createProductionLikeTestingApp()
const prisma = moduleFixture.get<PrismaService>(PrismaService)
```

**检测逻辑**：
```bash
# 搜索未使用 adapter 的 PrismaClient 实例化
rg "new PrismaClient\(\s*\)" apps/backend/e2e apps/backend/prisma/scripts apps/backend/*.ts \
  --glob '!node_modules/**'
```

**修复策略**：
1. **E2E 测试**：使用 `createProductionLikeTestingApp()` 并从 `moduleFixture` 获取 `PrismaService`
2. **独立脚本**：手动创建 `Pool` + `PrismaPg` adapter + `PrismaClient({ adapter })`
3. 确保脚本结束时同时关闭 `prisma.$disconnect()` 和 `pool.end()`

---

### 7. Prisma 7.x API 迁移检查（prisma-api-migration）

**问题**：
Prisma 7.x 弃用了部分 API 用法，特别是 `findUnique` 对于非唯一字段的查询，需要改用 `findFirst`。

**扫描范围**：
- `apps/backend/src/**/*.ts`
- `apps/backend/e2e/**/*.ts`
- `apps/backend/prisma/scripts/**/*.ts`

**检测规则**：
```typescript
// ❌ 错误示例（Prisma 7.x 不支持非唯一字段的 findUnique）
const user = await prisma.user.findUnique({
  where: { email: 'test@example.com' }  // email 如果不是 @unique 字段
})

// ❌ 错误示例（复合索引语法变更）
await prisma.someModel.findUnique({
  where: { type_value: { type: 'A', value: 'B' } }  // 旧版复合键语法
})

// ✅ 正确示例
const user = await prisma.user.findFirst({
  where: { email: 'test@example.com' }
})

// ✅ 正确示例（Prisma 7.x 复合索引）
await prisma.someModel.findFirst({
  where: { type: 'A', value: 'B' }
})
```

**检测逻辑**：
```bash
# 搜索可能需要迁移的 findUnique 用法
rg "findUnique\(\s*\{[^}]*where:\s*\{[^}]*(email|phone|username)" \
  apps/backend/src apps/backend/e2e apps/backend/prisma/scripts

# 搜索旧版复合键语法
rg "_[a-zA-Z]+:\s*\{" apps/backend --glob '*.ts' | grep -i "findUnique\|findFirst"
```

**修复策略**：
1. 将非唯一字段的 `findUnique` 改为 `findFirst`
2. 复合索引从 `field1_field2: { field1, field2 }` 改为直接 `{ field1, field2 }`
3. 确保业务逻辑正确处理 `findFirst` 可能返回多条记录中的第一条

---

### 8. E2E 测试统一夹具检查（e2e-unified-fixtures）

**问题**：
E2E 测试应使用 `createProductionLikeTestingApp()` 统一夹具，而非手动创建 `Test.createTestingModule`。手动创建会导致：
- Prisma 7.x 适配器未正确配置
- 模块依赖不完整
- 测试环境与生产环境差异

**扫描范围**：
- `apps/backend/e2e/**/*.e2e-spec.ts`

**检测规则**：
```typescript
// ❌ 错误示例
const moduleFixture = await Test.createTestingModule({
  imports: [AppModule],
}).compile()
const app = moduleFixture.createNestApplication()
const prisma = new PrismaClient()  // 独立创建的 PrismaClient

// ✅ 正确示例
import { createProductionLikeTestingApp, cleanupTestData } from '../fixtures/fixtures'
import { PrismaService } from '../../src/prisma/prisma.service'

const { app, moduleFixture } = await createProductionLikeTestingApp()
const prisma = moduleFixture.get<PrismaService>(PrismaService)
```

**检测逻辑**：
```bash
# 搜索手动创建测试模块的模式
rg "Test\.createTestingModule" apps/backend/e2e --glob '*.e2e-spec.ts'

# 搜索未使用统一夹具的文件
rg -L "createProductionLikeTestingApp" apps/backend/e2e --glob '*.e2e-spec.ts'
```

**修复策略**：
1. 替换 `Test.createTestingModule` 为 `createProductionLikeTestingApp()`
2. 从 `moduleFixture` 获取 `PrismaService` 而非独立创建
3. 使用 `cleanupTestData()` 进行测试数据清理
4. 确保 `beforeAll/afterAll` 正确管理应用生命周期

---

### 9. 独立脚本环境加载检查（script-env-loading）

**问题**：
独立脚本（如数据迁移脚本）应使用统一的 `loadEnvironment()` 函数加载环境变量，而非手动配置 dotenv。手动配置会导致：
- `.env.local` 覆盖顺序不一致
- 环境判断逻辑重复
- 维护成本增加

**扫描范围**：
- `apps/backend/prisma/scripts/**/*.ts`
- `apps/backend/*.ts`（根目录独立脚本）

**检测规则**：
```typescript
// ❌ 错误示例（手动 dotenv 配置）
import * as dotenv from 'dotenv'
import * as path from 'path'

dotenv.config({ path: path.resolve(__dirname, '../../.env.development.local') })
dotenv.config({ path: path.resolve(__dirname, '../../.env.development') })

const databaseUrl = process.env.DATABASE_URL  // 直接访问 process.env

// ✅ 正确示例
import { loadEnvironment } from '../../src/common/env/load-environment'
loadEnvironment()

import { defaultEnvAccessor } from '../../src/common/env/env.accessor'

const databaseUrl = defaultEnvAccessor.str('DATABASE_URL')
```

**检测逻辑**：
```bash
# 搜索手动 dotenv 配置
rg "dotenv\.config" apps/backend/prisma/scripts apps/backend/*.ts

# 搜索未使用 loadEnvironment 的脚本
rg -L "loadEnvironment" apps/backend/prisma/scripts --glob '*.ts'

# 搜索直接访问 process.env.DATABASE_URL
rg "process\.env\.DATABASE_URL" apps/backend/prisma/scripts apps/backend/*.ts
```

**修复策略**：
1. 删除手动的 `dotenv.config()` 调用
2. 在文件顶部添加 `import { loadEnvironment } from '../../src/common/env/load-environment'` 和 `loadEnvironment()`
3. 将 `process.env.XXX` 替换为 `defaultEnvAccessor.str('XXX')`
4. 确保 `loadEnvironment()` 在所有其他 import 之前调用（除了该函数本身的 import）

---

## 工作流程

### 阶段 0：解析执行模式

命令启动后首先解析参数确定执行模式：

```
1. 解析命令参数
2. 确定 EXECUTION_MODE:
   - 无参数 → direct（直接执行）
   - --codex → codex（Codex 后端）
   - --gemini → gemini（Gemini 后端）
3. 根据模式选择执行方式
```

**执行方式分支**：

- **direct 模式**：使用 Edit/Read/Grep 等工具直接执行扫描和修复
- **codex/gemini 模式**：委托给 codeagent-wrapper 执行
  ```bash
  codeagent-wrapper --backend {mode} "执行代码降熵扫描: {task_description}"
  ```

### 阶段 1：执行扫描

根据 `EXECUTION_MODE` 执行九项检查：

**direct 模式**：直接使用下面的命令执行扫描
**codex/gemini 模式**：将扫描任务委托给 codeagent-wrapper

#### 1.1 E2E 中文测试名称扫描

```bash
# 搜索 describe/it 中的中文字符
grep --extended-regexp "(describe|it|test)\s*\(\s*['\"].*[\u4e00-\u9fa5]" \
  apps/backend/e2e/**/*.e2e-spec.ts
```

输出格式：
```
发现 15 处中文测试用例名称：

apps/backend/e2e/auth/auth.e2e-spec.ts:
  - Line 42: describe('用户认证测试', ...)
  - Line 58: it('应该成功登录', ...)

apps/backend/e2e/wallet/wallet.e2e-spec.ts:
  - Line 120: it('余额不足时应报错', ...)
```

#### 1.2 E2E 重复实现扫描

```bash
# 搜索直接操作 Prisma 的模式
grep "prisma\.(user|character|story|adminUser)\.create\(" \
  apps/backend/e2e/**/*.e2e-spec.ts

# 搜索手动构造 JWT 的模式
grep "jwtService\.sign\(" apps/backend/e2e/**/*.e2e-spec.ts

# 搜索手动拼接 URL 的模式
grep "'/api/v1/" apps/backend/e2e/**/*.e2e-spec.ts

# 搜索手动创建 request 的模式
grep "request\(.*\.getHttpServer\(\)\)" apps/backend/e2e/**/*.e2e-spec.ts
```

输出格式：
```
发现 23 处可复用夹具函数的代码：

apps/backend/e2e/character/character.e2e-spec.ts:
  - Line 78-85: 手动创建用户（建议使用 createTestUser）
  - Line 92: 手动拼接 URL（建议使用 buildApiUrl）

apps/backend/e2e/chat/chat.e2e-spec.ts:
  - Line 134: 手动生成 JWT（建议使用 generateTestJwtToken）
```

#### 1.3 分页 DTO 规范扫描

```bash
# 搜索自定义分页 DTO
grep -r "class.*ResponseDto" apps/backend/src/modules/**/dto/responses/ | \
  xargs grep -l "total.*page.*limit\|page.*limit.*total"

# 搜索未继承 BasePaginationResponseDto 的分页结构
grep -r "extends" apps/backend/src/modules/**/dto/responses/*.dto.ts | \
  grep -v "BasePaginationResponseDto"

# 搜索 Controller 中手动构造分页的代码
grep -r "return.*{.*items.*total.*page" apps/backend/src/modules/**/controllers/
```

输出格式：
```
发现 8 处未使用标准分页 DTO：

apps/backend/src/modules/character/dto/responses/character-list.response.dto.ts:
  - 自定义分页结构，应继承 BasePaginationResponseDto

apps/backend/src/modules/invite/controllers/invite.controller.ts:
  - Line 145: 手动构造分页返回值，应使用 BasePaginationResponseDto
```

#### 1.4 环境变量访问规范扫描

```bash
# 搜索未经封装的 process.env 访问（排除底层实现文件）
rg "process\.env" apps/backend/src apps/backend/e2e \
  --glob '!**/env.accessor.ts' \
  --glob '!**/env.service.ts'
```

输出格式：
```
发现 12 处直接访问 process.env：

apps/backend/src/modules/chat/chat.service.ts:
  - Line 42: const apiKey = process.env.OPENAI_API_KEY
apps/backend/src/common/utils/some-script.ts:
  - Line 10: if (process.env.NODE_ENV !== 'production') { ... }
```

所有命中项将被标记为需要替换为 `defaultEnvAccessor` 或 `EnvService`。

#### 1.5 错误处理规范扫描

```bash
# 搜索未经允许的标准异常使用
rg "new (BadRequestException|UnauthorizedException|ForbiddenException|NotFoundException|HttpException|InternalServerErrorException)\(" \
  apps/backend/src apps/backend/e2e \
  --glob '!*spec.ts' \
  --glob '!*exception.ts' \
  --glob '!apps/backend/src/common/filters/**' \
  --glob '!apps/backend/src/main.ts'

# 搜索 new Error / Promise.reject(new Error())
rg "new Error\(" apps/backend/src apps/backend/e2e --glob '!*spec.ts'
```

输出格式：
```
发现 7 处错误处理不符合规范的代码：

apps/backend/src/modules/chat/chat.service.ts:
  - Line 120: throw new BadRequestException('prompt missing')
    → 建议：创建 ChatPromptMissingException（继承 DomainException）

apps/backend/src/modules/user/controllers/user.controller.ts:
  - Line 90: return Promise.reject(new Error('unexpected'))
    → 建议：统一抛出 DomainException 并附带 ErrorCode
```

#### 1.6 Prisma 7.x 适配器规范扫描

```bash
# 搜索未使用 adapter 的 PrismaClient 实例化
rg "new PrismaClient\(\s*\)" apps/backend/e2e apps/backend/prisma/scripts \
  --glob '!node_modules/**'

# 检查根目录脚本
rg "new PrismaClient\(\s*\)" apps/backend/*.ts
```

输出格式：
```
发现 3 处 Prisma 7.x 适配器问题：

apps/backend/e2e/transaction/transaction.e2e-spec.ts:
  - Line 15: const prisma = new PrismaClient()
    → 建议：使用 createProductionLikeTestingApp() 并从 moduleFixture 获取 PrismaService

apps/backend/prisma/scripts/fix-legacy-data.ts:
  - Line 8: const prisma = new PrismaClient()
    → 建议：使用 Driver Adapter 模式
```

#### 1.7 Prisma 7.x API 迁移扫描

```bash
# 搜索可能需要迁移的 findUnique 用法（非唯一字段）
rg "findUnique.*where.*email" apps/backend/src apps/backend/e2e apps/backend/prisma/scripts

# 搜索旧版复合键语法
rg "_[a-zA-Z]+:\s*\{" apps/backend --glob '*.ts'
```

输出格式：
```
发现 2 处 Prisma 7.x API 迁移问题：

apps/backend/e2e/auth/auth.e2e-spec.ts:
  - Line 45: findUnique({ where: { email } })
    → 建议：如果 email 不是 @unique 字段，改用 findFirst

apps/backend/src/modules/settings/settings.repository.ts:
  - Line 78: findUnique({ where: { type_value: { type, value } } })
    → 建议：Prisma 7.x 复合键语法变更，改为 { type, value }
```

#### 1.8 E2E 测试统一夹具扫描

```bash
# 搜索手动创建测试模块的模式
rg "Test\.createTestingModule" apps/backend/e2e --glob '*.e2e-spec.ts'

# 搜索独立创建 PrismaClient 的测试
rg "new PrismaClient" apps/backend/e2e --glob '*.e2e-spec.ts'
```

输出格式：
```
发现 2 处 E2E 测试未使用统一夹具：

apps/backend/e2e/ai.model/virtual.model.delete-logic.e2e-spec.ts:
  - Line 20: Test.createTestingModule({ imports: [AppModule] })
    → 建议：使用 createProductionLikeTestingApp()

apps/backend/e2e/ai.model/virtual.model.cascade-delete.e2e-spec.ts:
  - Line 18: const prisma = new PrismaClient()
    → 建议：从 moduleFixture 获取 PrismaService
```

#### 1.9 独立脚本环境加载扫描

```bash
# 搜索手动 dotenv 配置
rg "dotenv\.config" apps/backend/prisma/scripts

# 搜索直接访问 process.env.DATABASE_URL
rg "process\.env\.DATABASE_URL" apps/backend/prisma/scripts apps/backend/*.ts

# 搜索未导入 loadEnvironment 的脚本
for f in apps/backend/prisma/scripts/*.ts; do
  if ! grep -q "loadEnvironment" "$f"; then
    echo "$f: 未使用 loadEnvironment"
  fi
done
```

输出格式：
```
发现 4 处独立脚本环境加载问题：

apps/backend/prisma/scripts/fix-old-data.ts:
  - Line 3-5: 手动 dotenv.config() 配置
    → 建议：使用 loadEnvironment()

apps/backend/check-examples.ts:
  - Line 8: process.env.DATABASE_URL
    → 建议：使用 defaultEnvAccessor.str('DATABASE_URL')
```

### 阶段 2：在对话中展示报告

扫描完成后，直接在对话中输出结构化报告：

```
📊 代码降熵扫描报告

扫描时间：2025-11-12 10:30:45
扫描范围：E2E 测试 + Backend 分页接口

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【汇总】

检查项               | 发现问题 | 风险等级
---------------------|----------|----------
E2E 中文测试名称     | 15       | 低
E2E 重复实现         | 23       | 中
分页 DTO 规范        | 8        | 中
环境变量访问规范     | 12       | 高
错误处理规范         | 7        | 高
Prisma 7.x 适配器    | 3        | 严重
Prisma 7.x API 迁移  | 2        | 高
E2E 统一夹具         | 2        | 高
脚本环境加载         | 4        | 中

总计：76 处技术债务

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【详细清单】

1️⃣ E2E 中文测试名称（15 处）

apps/backend/e2e/auth/auth.e2e-spec.ts:
  Line 42: describe('用户认证测试', ...)
  → 建议：describe('User Authentication', ...)

  Line 58: it('应该成功登录', ...)
  → 建议：it('should login successfully', ...)

[显示前5处，完整清单共15处]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ E2E 重复实现（23 处）

apps/backend/e2e/character/character.e2e-spec.ts:
  Line 78-85: 手动创建用户
  → 建议使用夹具：createTestUser(app, 'test')

[显示前5处，完整清单共23处]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ 分页 DTO 规范（8 处）

apps/backend/src/modules/character/dto/responses/character-list.response.dto.ts:
  自定义分页结构
  → 建议继承 BasePaginationResponseDto

[显示前5处，完整清单共8处]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ 环境变量访问规范（12 处）

apps/backend/src/modules/chat/chat.service.ts:
  Line 42: 直接读取 `process.env.OPENAI_API_KEY`
  → 建议：通过 `EnvService.getString('OPENAI_API_KEY')`

apps/backend/src/config/legacy.config.ts:
  Line 15: 使用 `process.env.NODE_ENV`
  → 建议：使用 `defaultEnvAccessor.nodeEnv()`

[显示前5处，完整清单共12处]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ 错误处理规范（7 处）

apps/backend/src/modules/chat/chat.service.ts:
  Line 120: throw new BadRequestException('prompt missing')
  → 建议：创建 ChatPromptMissingException 并返回 ErrorCode.CHAT_PROMPT_REQUIRED

apps/backend/src/modules/user/controllers/user.controller.ts:
  Line 90: return Promise.reject(new Error('unexpected'))
  → 建议：统一抛出 DomainException，附带 ErrorCode.USER_UNEXPECTED_STATE

[显示前5处，完整清单共7处]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【修复优先级建议】

1. 🔥 严重优先级：Prisma 7.x 适配器（3 处）- 直接导致运行时崩溃
2. 🔴 高优先级：Prisma 7.x API 迁移（2 处）- 导致查询失败
3. 🔴 高优先级：E2E 统一夹具（2 处）- 测试环境不一致
4. 🔴 高优先级：错误处理规范（7 处）- 影响统一错误码与前端提示
5. 🔴 高优先级：环境变量访问规范（12 处）- 影响配置一致性与安全
6. 🟠 次高优先级：脚本环境加载（4 处）- 影响脚本可维护性
7. 🟠 次高优先级：分页 DTO 规范（8 处）- 影响 API 一致性
8. 🟡 中优先级：E2E 重复实现（23 处）- 影响测试维护
9. 🟢 低优先级：E2E 中文名称（15 处）- 影响国际化

预估工作量：约 8 小时
```

### 阶段 3：询问用户是否修复

报告展示后，询问用户：

```
是否需要修复这些问题？

选项：
1. 全部修复（推荐）
2. 仅修复严重 + 高优先级（Prisma 7.x + 错误处理 + 环境变量）
3. 仅修复 Prisma 7.x 相关（适配器 + API 迁移 + E2E 夹具）
4. 修复配置相关（环境变量访问 + 脚本环境加载 + 分页 DTO）
5. 自定义选择（指定具体检查项）
6. 不修复，仅记录

请告诉我你的选择（输入数字或说明）
```

### 阶段 4：执行修复

根据 `EXECUTION_MODE` 执行修复：

**direct 模式**：使用 Edit 工具直接修改代码文件
**codex/gemini 模式**：将修复任务委托给 codeagent-wrapper

```bash
# codex/gemini 模式下的委托执行示例
codeagent-wrapper --backend {mode} "
执行代码降熵修复任务:
- 修复范围: {selected_checks}
- 扫描报告: {scan_report_summary}
- 修复策略: 按照检查项说明执行修复
- 验证要求: 修复后运行 lint 和受影响的测试
"
```

#### 4.1 修复 E2E 中文测试名称

对于每个中文测试名称：

1. 提取中文字符串
2. 调用翻译服务（可使用 Web Search + AI）
3. 替换为英文名称
4. 保留原中文作为注释（可选）

```typescript
// 修复前
describe('用户认证测试', () => {
  it('应该成功登录', async () => { ... })
})

// 修复后
describe('User Authentication', () => {
  // 用户认证测试
  it('should login successfully', async () => {
    // 应该成功登录
    ...
  })
})
```

#### 4.2 修复 E2E 重复实现

对于每个重复实现：

1. 识别功能类型（创建用户/角色/故事等）
2. 查找对应的夹具函数
3. 替换为夹具函数调用
4. 调整变量名与后续引用

```typescript
// 修复前
const user = await prisma.user.create({
  data: { email: 'test@example.com', password: '...' }
})
const token = jwtService.sign({ sub: user.id })
const response = await request(app.getHttpServer())
  .get('/api/v1/users/me')
  .set('Authorization', `Bearer ${token}`)

// 修复后
const { profile, token } = await createTestUser(app, 'test')
const response = await createAuthRequest(app, token.accessToken)
  .get('users/me')
```

#### 4.3 修复分页 DTO 规范

对于每个非标准分页接口：

1. 创建或更新 Response DTO，继承 `BasePaginationResponseDto`
2. 更新 Controller 返回值构造逻辑
3. 更新 OpenAPI 文档注解
4. 确保字段名称向后兼容

```typescript
// 修复前（DTO）
export class CharacterListResponseDto {
  characters: CharacterResponseDto[]
  total: number
  page: number
  pageSize: number
}

// 修复后（DTO）
export class CharacterPaginationResponseDto extends BasePaginationResponseDto<CharacterResponseDto> {
  @ApiProperty({
    description: '角色列表',
    type: CharacterResponseDto,
    isArray: true,
  })
  items: CharacterResponseDto[]
}

// 修复前（Controller）
return {
  characters: results,
  total: count,
  page: query.page,
  pageSize: query.limit,
}

// 修复后（Controller）
return new CharacterPaginationResponseDto(
  count,
  query.page,
  query.limit,
  results,
)
```

#### 4.4 修复环境变量访问规范

对于每处 `process.env` 命中：

1. 判定使用场景：
   - **配置注册/静态上下文**：使用 `defaultEnvAccessor`。
   - **Nest 服务/控制器**：注入 `EnvService`。
   - **脚本或 CLI**：`const env = createEnvAccessor(process.env)` 并复用 accessor。
2. 替换原有读取逻辑，必要时封装成私有方法以避免重复。
3. 为关键阈值使用 `EnvService` 内部的 `clampNumber` 等 helper，保持一致行为。
4. 添加最小默认值与日志（如适用），确保与旧逻辑一致。

```typescript
// 修复前
if (process.env.DEBUG_MODE === 'true') {
  enableDebug()
}

// 修复后（服务内）
if (this.env.isAdminDebugEnabled()) {
  enableDebug()
}

// 修复后（配置层）
const env = defaultEnvAccessor
export const loggerConfig = registerAs('logger', () => ({
  level: env.str('LOGGER_LEVEL', 'info'),
}))
```

修复完毕后，更新对应模块的单元/集成测试，并在 MR 描述中列出受影响的环境变量。

#### 4.5 修复错误处理规范

针对每个命中项：

1. 判断是否已有对应领域异常（检查模块 `exceptions/index.ts`）。
2. 若存在，直接替换为该异常类；如无，则新增异常并在 `@ai/shared` 中补充 `ErrorCode`。
3. 更新抛出点，删除 `BadRequestException` / `HttpException` 等直接使用。
4. 确保 `message` 使用简洁的英文描述（检测到中文需改写），业务多语言交给前端。
5. 如确需临时抛出 `DomainException`，确保 `payload.code` 引用共享枚举，`args` 填写调试信息。
6. 更新相关测试断言（E2E/集成）以匹配新的 `error.code`。

```typescript
// 修复前
throw new UnauthorizedException('token 无效')

// 修复后（新增异常 + 统一错误码）
throw new InvalidAuthTokenException(token)

// 或直接复用 DomainException
throw new DomainException('token 无效', {
  code: ErrorCode.AUTH_INVALID_CREDENTIALS,
  args: { token },
  status: HttpStatus.UNAUTHORIZED,
})
```

修复完成后，务必确认：
- Swagger 文档自动更新的错误响应依然正确
- 新增异常的 `.spec.ts` 已验证 `code/status/args`
- 对外响应仍保持向后兼容（字段结构不变）

#### 4.6 修复 Prisma 7.x 适配器规范

针对每个命中项：

1. **E2E 测试文件**：
   - 删除 `new PrismaClient()` 和相关 import
   - 替换为 `createProductionLikeTestingApp()` 获取 app
   - 从 `moduleFixture.get<PrismaService>(PrismaService)` 获取 prisma 实例
   - 更新 `beforeAll/afterAll` 生命周期管理

2. **独立脚本文件**：
   - 添加 Driver Adapter 依赖 import
   - 创建 `Pool` 实例
   - 创建 `PrismaPg` adapter
   - 使用 `new PrismaClient({ adapter })`
   - 在 `finally` 块中同时关闭 `prisma.$disconnect()` 和 `pool.end()`

```typescript
// 修复前
const prisma = new PrismaClient()

// 修复后（独立脚本）
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

const pool = new Pool({ connectionString: defaultEnvAccessor.str('DATABASE_URL') })
const adapter = new PrismaPg(pool)
const prisma = new PrismaClient({ adapter })

// 在脚本结束时
.finally(async () => {
  await prisma.$disconnect()
  await pool.end()
})
```

#### 4.7 修复 Prisma 7.x API 迁移

针对每个命中项：

1. **`findUnique` 非唯一字段**：
   - 检查字段是否有 `@unique` 约束
   - 如果没有，改为 `findFirst`
   - 确保业务逻辑正确处理可能的多条记录

2. **复合索引语法**：
   - 将 `field1_field2: { field1, field2 }` 改为 `{ field1, field2 }`
   - 更新相关测试用例

```typescript
// 修复前
const user = await prisma.user.findUnique({
  where: { email: 'test@example.com' }
})

// 修复后
const user = await prisma.user.findFirst({
  where: { email: 'test@example.com' }
})

// 复合索引修复前
await prisma.setting.findUnique({
  where: { type_value: { type: 'A', value: 'B' } }
})

// 复合索引修复后
await prisma.setting.findFirst({
  where: { type: 'A', value: 'B' }
})
```

#### 4.8 修复 E2E 测试统一夹具

针对每个命中项：

1. 删除 `Test.createTestingModule` 相关代码
2. 导入 `createProductionLikeTestingApp` 和 `cleanupTestData`
3. 导入 `PrismaService` 类型
4. 更新 `beforeAll` 使用统一夹具
5. 更新 `afterAll` 使用 `cleanupTestData`

```typescript
// 修复前
import { Test } from '@nestjs/testing'
import { PrismaClient } from '@prisma/client'

let app: INestApplication
let prisma: PrismaClient

beforeAll(async () => {
  const moduleFixture = await Test.createTestingModule({
    imports: [AppModule],
  }).compile()
  app = moduleFixture.createNestApplication()
  await app.init()
  prisma = new PrismaClient()
})

// 修复后
import { createProductionLikeTestingApp, cleanupTestData } from '../fixtures/fixtures'
import { PrismaService } from '../../src/prisma/prisma.service'

let app: INestApplication
let prisma: PrismaService

beforeAll(async () => {
  const { app: testApp, moduleFixture } = await createProductionLikeTestingApp()
  app = testApp
  prisma = moduleFixture.get<PrismaService>(PrismaService)
})

afterAll(async () => {
  await cleanupTestData(prisma, testUserPrefix)
  await app.close()
})
```

#### 4.9 修复独立脚本环境加载

针对每个命中项：

1. 删除手动的 `dotenv` 导入和配置
2. 在文件顶部添加 `loadEnvironment` 导入和调用
3. 添加 `defaultEnvAccessor` 导入
4. 将 `process.env.XXX` 替换为 `defaultEnvAccessor.str('XXX')`

```typescript
// 修复前
import * as dotenv from 'dotenv'
import * as path from 'path'

dotenv.config({ path: path.resolve(__dirname, '../../.env.development.local') })
dotenv.config({ path: path.resolve(__dirname, '../../.env.development') })

const databaseUrl = process.env.DATABASE_URL

// 修复后
// Prisma 7: 使用统一环境加载器
import { loadEnvironment } from '../../src/common/env/load-environment'
loadEnvironment()

import { defaultEnvAccessor } from '../../src/common/env/env.accessor'

const databaseUrl = defaultEnvAccessor.str('DATABASE_URL')
```

### 阶段 5：验证与测试

根据 `EXECUTION_MODE` 执行验证：

**direct 模式**：直接使用 Bash 工具执行验证命令
**codex/gemini 模式**：验证任务作为修复任务的一部分由 codeagent-wrapper 执行

修复完成后：

1. 执行 `./scripts/dx lint` 检查代码风格
2. 执行 `./scripts/dx build backend` 验证编译
3. 运行受影响的 E2E 测试：
   ```bash
   # 对每个修改的测试文件
   ./scripts/dx test e2e backend <modified-test-file>
   ```
4. 如果是分页 DTO 修复，执行 `./scripts/dx build sdk` 更新 SDK
5. 针对环境变量访问改动，运行对应模块的单元/集成测试（如 Chat/Payment 模块）并核对 `.env.*` 示例文件
6. 针对错误处理改动，运行对应模块的 API/E2E 冒烟用例，确认响应 `error.code` 与 `args` 与预期一致，并检查日志是否生成 requestId
7. 生成验证报告

### 阶段 6：在对话中展示修复报告

修复完成后，直接在对话中输出结果：

```
✅ 代码降熵修复完成

修复时间：2025-11-12 11:45:30

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【修复汇总】

检查项             | 修复成功 | 修复失败 | 跳过
-------------------|----------|----------|------
E2E 中文测试名称   | 15       | 0        | 0
E2E 重复实现       | 21       | 2        | 0
分页 DTO 规范      | 8        | 0        | 0
环境变量访问规范   | 12       | 0        | 0
错误处理规范       | 7        | 0        | 0

总计：63 处修复成功，2 处失败

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【失败项说明】

❌ apps/backend/e2e/complex/complex.e2e-spec.ts (Line 234)
   原因：手动实现逻辑复杂，无法直接替换为夹具函数
   建议：人工审查并重构

❌ apps/backend/e2e/legacy/legacy.e2e-spec.ts (Line 89)
   原因：依赖旧版 Prisma 模型，夹具函数不兼容
   建议：升级测试或创建专用夹具

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【测试结果】

✅ 代码风格检查：通过
✅ 后端编译：通过
✅ E2E 测试：42/44 通过（2 个需人工审查）
✅ SDK 构建：通过（分页 DTO 变更已更新）
✅ 环境变量一致性校验：通过（已对照 `.env.*` 与运行配置）
✅ 错误处理冒烟：通过（抽样请求返回正确的 error.code 与 requestId）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【后续行动】

建议执行：
1. 审查并手动修复 2 处失败项
2. 使用 /git-commit-and-pr 提交代码
3. 可选：配置 ESLint 规则防止回退
```

## 角色职责

1. **扫描分析师**：执行多模式扫描，识别技术债务
2. **翻译协调者**：调用 AI 翻译服务处理中文测试名称
3. **重构建议者**：分析重复实现，生成最优夹具调用方案
4. **规范守护者**：确保分页 DTO 符合项目标准
5. **环境守护者**：审查并统一所有环境变量访问方式
6. **异常守护者**：检查错误处理是否遵循 DomainException / ErrorCode 体系
7. **Prisma 迁移专家**：识别 Prisma 7.x 不兼容用法，指导 Driver Adapter 和 API 迁移
8. **测试架构守护者**：确保 E2E 测试使用统一夹具，保持测试环境一致性
9. **脚本规范守护者**：确保独立脚本使用统一的环境加载和数据库连接模式
10. **测试验证者**：运行受影响的测试，确保修复不引入回归
11. **报告生成器**：生成结构化、可操作的扫描与修复报告

## Delegation

- **翻译服务**：对于中文测试名称，可使用 Web Search 查询专业翻译或调用 AI 模型
- **测试执行**：通过 `./scripts/dx test e2e backend <file>` 验证修复
- **环境配置校验**：必要时调用 `defaultEnvAccessor`/`EnvService` 辅助函数，或编写临时脚本校验配置读取结果
- **异常审查**：参考 `apps/backend/src/common/exceptions` 与 `@ai/shared/constants/error-codes.ts`，确保新异常和错误码同步
- **代码格式化**：通过 `./scripts/dx lint` 自动修复格式问题

## 输出约定

扫描完成后的输出格式：

```
✅ 扫描完成：发现 76 处技术债务

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 扫描汇总：
- E2E 中文测试名称：15 处（低风险）
- E2E 重复实现：23 处（中风险）
- 分页 DTO 规范：8 处（中风险）
- 环境变量访问规范：12 处（高风险）
- 错误处理规范：7 处（高风险）
- Prisma 7.x 适配器：3 处（严重风险）
- Prisma 7.x API 迁移：2 处（高风险）
- E2E 统一夹具：2 处（高风险）
- 脚本环境加载：4 处（中风险）

[详细报告见下方]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

是否需要修复这些问题？

选项：
1. 全部修复（推荐）
2. 仅修复严重 + 高优先级（Prisma 7.x + 错误处理 + 环境变量）
3. 仅修复 Prisma 7.x 相关（适配器 + API 迁移 + E2E 夹具）
4. 修复配置相关（环境变量访问 + 脚本环境加载 + 分页 DTO）
5. 自定义选择
6. 不修复，仅记录

⚠️ 建议：优先处理 Prisma 7.x 适配器（严重，直接导致运行时崩溃）
```

- 报告直接在对话中展示，使用结构化格式
- 使用表格和代码块展示清晰的对比
- 高亮风险等级与优先级
- 遵循仓库中文输出规范

## Key Constraints

### 扫描约束

- 覆盖 `apps/backend/e2e/**/*`、`apps/backend/src/modules/**/*`、`apps/backend/src/common/**/*`、`apps/backend/src/config/**/*`、`apps/backend/prisma/scripts/**/*`
- 不修改测试逻辑，仅优化结构与命名
- 对于复杂的重复实现，生成建议而非强制修复
- 环境变量访问扫描需忽略 `env.accessor.ts`、`env.service.ts` 等底层实现文件
- 错误处理扫描需跳过全局过滤器、ValidationPipe 等白名单文件，避免误报
- Prisma 7.x 适配器扫描需检查 E2E 测试和独立脚本中的 `new PrismaClient()` 用法
- 脚本环境加载扫描需检查 `prisma/scripts/` 目录下所有 `.ts` 文件
- E2E 统一夹具扫描需检查 `Test.createTestingModule` 和独立 `PrismaClient` 实例化

### 修复约束

- 所有修复必须经用户确认
- 修复后必须运行受影响的测试
- 分页 DTO 修复需确保 API 向后兼容
- 失败的修复需标记并生成人工审查清单
- 环境变量访问修复必须替换为 `defaultEnvAccessor` 或 `EnvService`，并更新对应配置示例
- 错误处理修复必须附带明确的 `ErrorCode` 与 `.spec.ts` 测试，禁止重新启用标准异常
- Prisma 7.x 适配器修复必须使用 Driver Adapter 模式，E2E 测试使用 `PrismaService`，独立脚本使用 `Pool` + `PrismaPg`
- Prisma 7.x API 迁移需验证字段是否有 `@unique` 约束，避免误改
- E2E 统一夹具修复后必须验证测试通过，确保 `beforeAll/afterAll` 生命周期正确
- 独立脚本环境加载修复必须确保 `loadEnvironment()` 在所有其他 import 之前调用

### 翻译约束

- 测试名称翻译遵循 BDD 风格：
  - `describe()` 用名词短语（如 "User Authentication"）
  - `it()` 用 "should + 动词" 格式（如 "should login successfully"）
- 保持原有语义，避免过度意译
- 可选：在注释中保留原中文（便于理解）

### 测试验证约束

- E2E 测试修复后必须逐个运行相关测试文件
- 分页 DTO 修复后必须运行 `./scripts/dx build sdk`
- 任何测试失败需回滚该文件的修复
- 环境变量访问修复后需执行至少一个受影响模块的集成测试或功能冒烟测试
- 错误处理修复后需调用对应 API/E2E 用例，确认响应结构与日志 requestId

### 质量门禁

- 修复后必须通过 `./scripts/dx lint`
- 修复后必须通过 `./scripts/dx build backend`
- 受影响的 E2E 测试必须全部通过
- 如涉及环境变量，需同步更新 `.env.example`/`.env.*` 模板并通过评审
- 涉及错误处理的改动需补充/更新异常类单测，确保 `code/status/args` 一致

## Success Criteria

- ✅ 扫描报告结构清晰，问题分类准确
- ✅ 修复建议可操作，优先级合理
- ✅ 自动修复准确率 > 95%（少量复杂场景需人工）
- ✅ 修复后所有测试通过，无回归
- ✅ API 兼容性保持，前端无感知
- ✅ 报告可追溯，便于后续审计
- ✅ 不存在直接访问 `process.env` 的业务代码（仅限底层封装）
- ✅ 所有业务抛错均携带统一的 `DomainException` / `ErrorCode`
- ✅ 不存在未使用 Driver Adapter 的 `new PrismaClient()` 调用
- ✅ 不存在 Prisma 7.x 已弃用的 API 用法（如非唯一字段的 `findUnique`）
- ✅ 所有 E2E 测试使用 `createProductionLikeTestingApp()` 统一夹具
- ✅ 所有独立脚本使用 `loadEnvironment()` 和 `defaultEnvAccessor` 访问环境变量

## 示例场景

### 示例 1：默认模式（直接执行）

```
用户：/code-entropy-scan

助手：
开始代码降熵扫描...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 阶段 1/9：检查 E2E 测试用例名称中的中文字符...
  ✅ 扫描完成：发现 15 处中文测试名称

🔍 阶段 2/9：检查 E2E 测试重复实现...
  ✅ 扫描完成：发现 23 处可复用夹具函数的代码

🔍 阶段 3/9：检查分页 DTO 规范...
  ✅ 扫描完成：发现 8 处未使用标准分页 DTO

🔍 阶段 4/9：检查环境变量访问规范...
  ✅ 扫描完成：发现 12 处直接访问 process.env 的代码

🔍 阶段 5/9：检查错误处理规范...
  ✅ 扫描完成：发现 7 处未使用 DomainException / ErrorCode 的代码

🔍 阶段 6/9：检查 Prisma 7.x 适配器规范...
  ✅ 扫描完成：发现 3 处未使用 Driver Adapter 的 PrismaClient

🔍 阶段 7/9：检查 Prisma 7.x API 迁移...
  ✅ 扫描完成：发现 2 处需要迁移的 API 用法

🔍 阶段 8/9：检查 E2E 测试统一夹具...
  ✅ 扫描完成：发现 2 处未使用 createProductionLikeTestingApp

🔍 阶段 9/9：检查独立脚本环境加载...
  ✅ 扫描完成：发现 4 处未使用 loadEnvironment 的脚本

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 扫描汇总：
总计发现 76 处技术债务

[展示详细报告...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

是否需要修复这些问题？

选项：
1. 全部修复（推荐）
2. 仅修复严重 + 高优先级（Prisma 7.x + 错误处理 + 环境变量）
3. 仅修复 Prisma 7.x 相关（适配器 + API 迁移 + E2E 夹具）
4. 修复配置相关（环境变量访问 + 脚本环境加载 + 分页 DTO）
5. 自定义选择
6. 不修复，仅记录

⚠️ 建议：优先处理 Prisma 7.x 适配器（严重，直接导致运行时崩溃）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用户：1（全部修复）

助手：
开始修复...

[执行修复流程]

✅ 修复完成！

[展示修复报告]

建议使用 /git-commit-and-pr 提交代码
```

### 示例 2：使用 Codex 后端

```
用户：/code-entropy-scan --codex

助手：
检测到 EXECUTION_MODE: codex
将使用 codeagent-wrapper (Codex backend) 执行扫描和修复

开始代码降熵扫描...

执行命令：
codeagent-wrapper --backend codex "执行代码降熵扫描，依次检查:
1. E2E 测试用例名称中文检查
2. E2E 测试重复实现检查
3. 分页 DTO 规范检查
...（共9项检查）
输出结构化扫描报告"

[等待 Codex 后端执行完成]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 扫描汇总（由 Codex 执行）：
总计发现 76 处技术债务

[展示详细报告...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

是否需要修复这些问题？
[选项列表...]

用户：1（全部修复）

助手：
执行命令：
codeagent-wrapper --backend codex "执行代码降熵修复任务:
- 修复范围: 全部 9 项检查
- 修复策略: 按照检查项说明执行修复
- 验证要求: 修复后运行 lint 和受影响的测试"

[等待 Codex 后端执行完成]

✅ 修复完成！

[展示修复报告]

建议使用 /git-commit-and-pr 提交代码
```

### 示例 3：使用 Gemini 后端

```
用户：/code-entropy-scan --gemini

助手：
检测到 EXECUTION_MODE: gemini
将使用 codeagent-wrapper (Gemini backend) 执行扫描和修复

开始代码降熵扫描...

执行命令：
codeagent-wrapper --backend gemini "执行代码降熵扫描，依次检查:
1. E2E 测试用例名称中文检查
2. E2E 测试重复实现检查
...（共9项检查）"

[等待 Gemini 后端执行完成]

[后续流程与 Codex 模式类似]
```

---

自动化识别技术债务，保持代码库低熵运行，让重构成为日常而非负担。
