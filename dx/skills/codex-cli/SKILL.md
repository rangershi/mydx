---
name: codex-cli
description: Execute Codex CLI directly without wrapper. Use for code analysis, refactoring, and automated code changes with full control over CLI parameters.
---

# Codex CLI Direct Integration

## Overview

Execute Codex CLI commands directly (without codex-wrapper). Provides full control over CLI parameters, JSON stream parsing, and session management.

## When to Use

- Need direct control over Codex CLI parameters
- Debugging Codex behavior without wrapper abstraction
- Custom timeout or model configurations
- When codex-wrapper is unavailable

## Command Structure

### Basic Command Format

```bash
# New session
codex e -C <workdir> --skip-git-repo-check --json <task>

# New session from stdin (recommended for complex tasks)
codex e -C <workdir> --skip-git-repo-check --json - <<'EOF'
<task content>
EOF

# Resume session
codex e --skip-git-repo-check --json resume <session_id> <task>

# Resume session from stdin
codex e --skip-git-repo-check --json resume <session_id> - <<'EOF'
<task content>
EOF
```

### CLI Parameters

| Parameter | Description |
|-----------|-------------|
| `e` | Execute subcommand (required) |
| `-C <dir>` | Working directory (new sessions only) |
| `--json` | Enable JSON stream output (required for parsing) |
| `--skip-git-repo-check` | Skip git repository validation |
| `--model <model>` | Specify model (e.g., `gpt-4`, `o3-mini`) |
| `--dangerously-bypass-approvals-and-sandbox` | YOLO mode - skip all approvals |
| `resume <session_id>` | Continue a previous session |
| `-` | Read task from stdin |

## Usage Examples

### Basic Code Analysis

```bash
# Simple task (direct argument)
codex e -C /path/to/project --skip-git-repo-check --json "explain the main function in @src/main.ts"

# Complex task (HEREDOC - recommended)
codex e -C /path/to/project --skip-git-repo-check --json - <<'EOF'
analyze @src/utils.ts and:
1. Identify performance bottlenecks
2. Suggest improvements
3. Check for edge cases
EOF
```

### With Model Selection

```bash
codex e -C . --skip-git-repo-check --model o3-mini --json - <<'EOF'
refactor @src/parser.ts to use async/await instead of callbacks
EOF
```

### Resume Session

```bash
# First session returns: thread_id in JSON output
codex e -C . --skip-git-repo-check --json - <<'EOF'
add error handling to @src/api.ts
EOF
# Extract thread_id from output: "thread_id":"019a7247-ac9d-71f3-89e2-a823dbd8fd14"

# Continue the session
codex e --skip-git-repo-check --json resume 019a7247-ac9d-71f3-89e2-a823dbd8fd14 - <<'EOF'
now add retry logic for network failures
EOF
```

### YOLO Mode (No Approvals)

```bash
codex e -C . --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --json - <<'EOF'
fix all ESLint errors in @src/
EOF
```

## JSON Output Format

Codex outputs a stream of JSON events. Key events to parse:

### Event Types

```json
// Session start - contains thread_id (session ID)
{"type":"thread.started","thread_id":"019a7247-ac9d-71f3-89e2-a823dbd8fd14"}

// Agent message - contains the response
{"type":"item.completed","item":{"type":"agent_message","text":"Response text here..."}}

// Session complete
{"type":"thread.completed","thread_id":"019a7247-ac9d-71f3-89e2-a823dbd8fd14"}
```

### Extracting Results

To extract the agent message and session ID from JSON stream:

```bash
# Using jq to extract agent_message
codex e -C . --skip-git-repo-check --json "task" 2>/dev/null | \
  jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'

# Extract thread_id (session ID)
codex e -C . --skip-git-repo-check --json "task" 2>/dev/null | \
  jq -r 'select(.type=="thread.started") | .thread_id'
```

### Simple Shell Parsing (without jq)

```bash
# Extract agent_message text using grep/sed
codex e -C . --skip-git-repo-check --json "task" 2>/dev/null | \
  grep '"type":"agent_message"' | \
  sed 's/.*"text":"\([^"]*\)".*/\1/'

# Extract thread_id
codex e -C . --skip-git-repo-check --json "task" 2>/dev/null | \
  grep '"thread.started"' | \
  sed 's/.*"thread_id":"\([^"]*\)".*/\1/'
```

## Invocation Pattern

All automated executions should use HEREDOC syntax through the Bash tool:

```
Bash tool parameters:
- command: codex e -C <workdir> --skip-git-repo-check --json - <<'EOF'
  <task content>
  EOF
- timeout: 7200000
- description: <brief description>
```

## Timeout Control

Codex CLI does not have built-in timeout. Use the Bash tool's timeout parameter:

```
Bash tool:
- timeout: 7200000 (2 hours, recommended default)
```

Or use system timeout command:

```bash
timeout 7200 codex e -C . --skip-git-repo-check --json - <<'EOF'
long running task
EOF
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (required) |
| `CODEX_HOME` | Codex configuration directory |

## Comparison with codex-wrapper

| Feature | codex (direct) | codex-wrapper |
|---------|----------------|---------------|
| JSON parsing | Manual (jq/grep) | Automatic |
| Session ID extraction | Manual | Automatic |
| Timeout handling | External (Bash/timeout) | Built-in |
| Error formatting | Raw JSON | Human-readable |
| Parallel execution | N/A | `--parallel` mode |
| Logging | None | Automatic log files |
| Multi-backend | Codex only | Codex/Claude/Gemini |

## When to Use stdin (`-`)

Use stdin mode when task contains:
- Newlines (`\n`)
- Quotes (`"`, `'`, `` ` ``)
- Dollar signs (`$`)
- Backslashes (`\`)
- Length > 800 characters

```bash
# Direct argument (simple tasks only)
codex e -C . --json "simple task"

# Stdin with HEREDOC (recommended for all complex tasks)
codex e -C . --json - <<'EOF'
Complex task with "quotes", $variables, and
multiple lines
EOF
```

## Error Handling

Codex CLI exit codes:
- `0`: Success
- `1`: General error
- Other: Command-specific errors

Check stderr for error messages:

```bash
codex e -C . --json "task" 2>&1 | grep -i error
```

## Notes

- Requires Codex CLI installed and authenticated (`codex auth`)
- JSON output goes to stdout, progress/errors to stderr
- Always use `--json` flag for automation (enables structured output)
- `--skip-git-repo-check` allows running in any directory
- Session IDs (`thread_id`) are UUIDs, save them for resume functionality
- For production use, consider codex-wrapper for better error handling and logging
