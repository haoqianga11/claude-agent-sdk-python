# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Lint and Style
```bash
# Check for issues and fix automatically
python -m ruff check src/ tests/ --fix
python -m ruff format src/ tests/
```

### Type Checking
```bash
# Type check source code only
python -m mypy src/
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_client.py

# Run with coverage
python -m pytest tests/ --cov=claude_agent_sdk
```

### Dependencies
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run examples (requires Claude Code installation)
python examples/quick_start.py
```

## Architecture Overview

This is the Python SDK for Claude Code, providing programmatic access to Claude Code's capabilities. The SDK supports two main usage patterns:

### Core Components

1. **`query()` function** - Simple one-shot queries
   - Located in `src/claude_agent_sdk/query.py`
   - Unidirectional: send prompt, receive responses
   - Stateless: each query is independent
   - Best for simple automation and batch processing

2. **`ClaudeSDKClient` class** - Interactive bidirectional conversations
   - Located in `src/claude_agent_sdk/client.py`
   - Maintains conversation state across multiple messages
   - Supports streaming, interrupts, and dynamic message sending
   - Best for chat interfaces and interactive applications

### Internal Architecture

- **Transport layer** (`src/claude_agent_sdk/_internal/transport/`) - Manages subprocess communication with Claude Code CLI
- **Message parsing** (`src/claude_agent_sdk/_internal/message_parser.py`) - Handles JSON message protocol
- **Internal client** (`src/claude_agent_sdk/_internal/client.py`) - Core implementation shared by both query() and ClaudeSDKClient

### Key Features

1. **SDK MCP Servers** - In-process MCP servers that run within your Python application
   - Created using `@tool` decorator and `create_sdk_mcp_server()`
   - Better performance than external MCP servers (no IPC overhead)
   - Direct access to application state

2. **Hooks** - Python functions that execute at specific points in the Claude agent loop
   - Support for PreToolUse, PostToolUse, and other hook events
   - Enable automated feedback and deterministic processing

3. **Type Safety** - Full type annotations using mypy
   - All public APIs have comprehensive type hints
   - Strict mypy configuration enforced

### Error Handling

The SDK provides specific error types in `src/claude_agent_sdk/_errors.py`:
- `CLINotFoundError` - Claude Code CLI not found
- `CLIConnectionError` - Connection issues
- `ProcessError` - Subprocess failures
- `CLIJSONDecodeError` - JSON parsing errors

### Testing Structure

- Unit tests in `tests/` directory
- Integration tests require Claude Code installation
- End-to-end tests in `e2e-tests/` (requires API key)
- Examples in `examples/` directory demonstrate real usage patterns

### Dependencies

- **Core**: `anyio` (async runtime), `mcp` (Model Context Protocol)
- **Dev**: `pytest`, `pytest-asyncio`, `mypy`, `ruff`
- **Runtime**: Claude Code CLI (external dependency, must be installed separately)
