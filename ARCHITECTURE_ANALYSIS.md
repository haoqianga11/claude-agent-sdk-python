# Claude Agent SDK for Python - 架构分析与功能总结

## 项目概述

Claude Agent SDK for Python 是一个 Python 软件开发工具包，提供程序化访问 Claude Code 的能力。该 SDK 支持两种主要使用模式：简单查询和交互式对话，并提供了丰富的扩展功能。

## 核心功能模块

### 1. 简单查询功能 (`query()`)

**位置**: `src/claude_agent_sdk/query.py`

**特性**:
- **单向通信**: 发送提示，接收响应
- **无状态**: 每次查询独立，不维护会话状态
- **简单易用**: Fire-and-forget 风格，无需连接管理
- **适用场景**: 简单自动化、批处理、一次性查询

**使用示例**:
```python
from claude_agent_sdk import query

async for message in query(prompt="What is 2 + 2?"):
    print(message)
```

### 2. 交互式客户端 (`ClaudeSDKClient`)

**位置**: `src/claude_agent_sdk/client.py`

**特性**:
- **双向通信**: 可随时发送和接收消息
- **有状态**: 维护跨消息的对话上下文
- **交互式**: 支持基于响应的后续操作
- **流式支持**: 支持流式响应、中断和动态消息发送
- **控制流**: 支持中断和会话管理

**适用场景**:
- 构建聊天界面或对话式 UI
- 交互式调试或探索会话
- 多轮对话与上下文
- 需要对 Claude 响应做出反应的应用
- 实时应用与用户输入
- 需要中断能力的场景

### 3. SDK MCP 服务器

**位置**: `src/claude_agent_sdk/__init__.py` (tool 装饰器和 create_sdk_mcp_server 函数)

**特性**:
- **进程内运行**: 在 Python 应用程序内直接运行
- **高性能**: 无 IPC（进程间通信）开销
- **简化部署**: 单进程而非多进程
- **直接状态访问**: 可直接访问应用程序变量和状态
- **类型安全**: 直接 Python 函数调用，带类型提示

**与外部 MCP 服务器对比**:
- 外部 MCP 服务器需要单独进程，有 IPC 开销
- SDK MCP 服务器运行在同一进程，性能更好
- 更容易调试，所有代码在同一进程运行

**使用示例**:
```python
@tool("add", "Add two numbers", {"a": float, "b": float})
async def add_numbers(args):
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"Result: {result}"}]}

calculator = create_sdk_mcp_server(
    name="calculator",
    tools=[add_numbers]
)
```

### 4. 钩子系统 (Hooks)

**位置**: `src/claude_agent_sdk/types.py` (HookCallback, HookMatcher 等)

**特性**:
- **事件驱动**: 在 Claude 代理循环的特定点执行 Python 函数
- **自动化反馈**: 提供确定性处理和自动化反馈
- **多种事件**: 支持 PreToolUse、PostToolUse、SessionStart 等事件
- **灵活匹配**: 使用 HookMatcher 进行精确的事件匹配

**常见钩子事件**:
- `PreToolUse`: 工具使用前执行，可用于权限控制
- `PostToolUse`: 工具使用后执行，可用于结果处理
- `SessionStart`: 会话开始时执行，可用于添加上下文
- `SessionEnd`: 会话结束时执行，可用于清理工作

**使用示例**:
```python
async def check_bash_command(input_data, tool_use_id, context):
    command = input_data["tool_input"].get("command", "")
    if "dangerous" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Dangerous command detected"
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_bash_command])
        ]
    }
)
```

### 5. 权限管理系统

**位置**: `src/claude_agent_sdk/types.py` (PermissionMode, PermissionUpdate 等)

**权限模式**:
- `default`: 默认权限模式
- `acceptEdits`: 自动接受文件编辑
- `plan`: 计划模式
- `bypassPermissions`: 绕过权限检查

**权限更新类型**:
- `addRules`: 添加权限规则
- `replaceRules`: 替换权限规则
- `removeRules`: 移除权限规则
- `setMode`: 设置权限模式
- `addDirectories`: 添加允许目录
- `removeDirectories`: 移除允许目录

**工具权限控制**:
- `allowed_tools`: 允许使用的工具列表
- `can_use_tool`: 动态权限判断回调函数
- `permission_prompt_tool_name`: 权限提示工具名称

### 6. 消息类型系统

**位置**: `src/claude_agent_sdk/types.py`

**消息类型**:
- `UserMessage`: 用户消息
- `AssistantMessage`: 助手消息
- `SystemMessage`: 系统消息
- `ResultMessage`: 结果消息

**内容块类型**:
- `TextBlock`: 文本内容
- `ToolUseBlock`: 工具使用
- `ToolResultBlock`: 工具结果
- `ThinkingBlock`: 思考过程

## 内部架构组件

### 1. 传输层 (Transport Layer)

**位置**: `src/claude_agent_sdk/_internal/transport/`

**SubprocessCLITransport**:
- 管理 Claude Code CLI 的子进程通信
- 处理 stdin/stdout/stderr 流
- 支持 JSON 流协议
- 自动发现 Claude Code CLI 安装位置
- 处理进程启动、连接和清理

### 2. 消息解析器 (Message Parser)

**位置**: `src/claude_agent_sdk/_internal/message_parser.py`

- 解析来自 Claude Code CLI 的 JSON 流响应
- 将原始 JSON 转换为类型化的消息对象
- 处理消息流和分块
- 错误检测和恢复

### 3. 内部客户端 (Internal Client)

**位置**: `src/claude_agent_sdk/_internal/client.py`

- 共享的核心实现，被 query() 和 ClaudeSDKClient 使用
- 处理选项验证和配置
- 管理 SDK MCP 服务器
- 转换钩子格式
- 协调传输层和查询处理

### 4. 查询处理器 (Query Handler)

**位置**: `src/claude_agent_sdk/_internal/query.py`

- 处理控制协议
- 管理工具调用和权限
- 处理钩子执行
- 协调 MCP 服务器交互

## 错误处理系统

**位置**: `src/claude_agent_sdk/_errors.py`

**错误类型**:
- `ClaudeSDKError`: 基础错误类
- `CLINotFoundError`: Claude Code CLI 未找到
- `CLIConnectionError`: 连接问题
- `ProcessError`: 子进程失败
- `CLIJSONDecodeError`: JSON 解析错误

## 依赖关系

**核心依赖**:
- `anyio`: 异步运行时，提供异步 I/O 和任务组功能
- `mcp`: Model Context Protocol，用于 MCP 服务器实现

**开发依赖**:
- `pytest`: 测试框架
- `pytest-asyncio`: 异步测试支持
- `mypy`: 类型检查
- `ruff`: 代码检查和格式化

**运行时依赖**:
- Claude Code CLI (外部依赖，需要单独安装)

## 测试结构

- **单元测试**: `tests/` 目录，测试各个组件的独立功能
- **集成测试**: 需要 Claude Code 安装，测试组件间交互
- **端到端测试**: `e2e-tests/` 目录，需要 API 密钥，测试完整流程
- **示例代码**: `examples/` 目录，展示实际使用模式

## 配置选项

**ClaudeAgentOptions 主要配置**:
- `system_prompt`: 系统提示词
- `max_turns`: 最大对话轮数
- `allowed_tools`: 允许的工具列表
- `mcp_servers`: MCP 服务器配置
- `hooks`: 钩子配置
- `permission_mode`: 权限模式
- `cwd`: 工作目录
- `max_buffer_size`: 最大缓冲区大小

## 性能特点

- **异步设计**: 全面使用 async/await，支持高并发
- **流式处理**: 支持流式响应，减少延迟
- **内存效率**: 使用流式处理，避免大量数据在内存中累积
- **进程管理**: 高效的子进程管理，自动清理资源