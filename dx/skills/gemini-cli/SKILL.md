---
name: gemini-cli
description: Execute Gemini CLI for AI-powered code analysis and generation with session management. Use when you need to leverage Google's Gemini models for complex reasoning tasks.
---

# Gemini CLI Integration

## Overview

Execute Gemini CLI commands with JSON streaming output, session management, and resume capability. Integrates Google's Gemini AI models into Claude Code workflows.

## When to Use

- Complex reasoning tasks requiring advanced AI capabilities
- Code generation and analysis with Gemini models
- Tasks requiring Google's latest AI technology
- Multi-turn conversations with session continuity
- Alternative perspective on code problems

## Usage

**Run with uv** (recommended, timeout 7200000ms):

```bash
# New session
uv run scripts/gemini.py "<prompt>" [working_dir]

# New session with HEREDOC (recommended for complex prompts)
uv run scripts/gemini.py - [working_dir] <<'EOF'
<multi-line prompt>
EOF

# Resume session
uv run scripts/gemini.py resume <session_id> "<prompt>" [working_dir]

# Resume session with HEREDOC
uv run scripts/gemini.py resume <session_id> - [working_dir] <<'EOF'
<continue task>
EOF
```

**Direct execution** (alternative):
```bash
python3 scripts/gemini.py "<prompt>" [working_dir]
```

## Command Formats

### New Session

```bash
# Simple prompt (direct argument)
gemini.py "explain this code" /path/to/project

# Complex prompt (stdin with HEREDOC)
gemini.py - /path/to/project <<'EOF'
Analyze the following code and:
1. Identify potential bugs
2. Suggest improvements
3. Check for security issues
EOF
```

### Resume Session

```bash
# Resume with direct argument
gemini.py resume <session_id> "continue the analysis"

# Resume with HEREDOC
gemini.py resume abc123-session-id - <<'EOF'
Now add error handling to the functions we discussed
EOF
```

## Environment Variables

- **GEMINI_MODEL**: Configure model (default: `gemini-2.5-pro`)
  - Example: `export GEMINI_MODEL=gemini-2.5-flash`

## Timeout Control

- **Fixed**: 7200000 milliseconds (2 hours), immutable
- **Bash tool**: Always set `timeout: 7200000` for double protection

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `prompt` or `-` | Yes | Task prompt or `-` for stdin |
| `working_dir` | No | Working directory (default: current) |
| `session_id` | Resume only | Session ID from previous run |

## Return Format

```text
Model response text here...

---
SESSION_ID: abc123-xyz789-session-id
```

Error format (stderr):
```text
ERROR: Error message
```

## Invocation Pattern

When calling via Bash tool, always include the timeout parameter:

```yaml
Bash tool parameters:
- command: uv run scripts/gemini.py - <<'EOF'
  <prompt content>
  EOF
- timeout: 7200000
- description: <brief description of the task>
```

## Examples

### Basic Query

```bash
uv run scripts/gemini.py "explain quantum computing"
# timeout: 7200000
```

### Code Analysis with HEREDOC

```bash
uv run scripts/gemini.py - /path/to/project <<'EOF'
Review the code in this project and:
1. Check for security vulnerabilities
2. Identify performance bottlenecks
3. Suggest architectural improvements
EOF
# timeout: 7200000
```

### Multi-turn Conversation (Resume)

```bash
# First session - analyze code
uv run scripts/gemini.py - <<'EOF'
Analyze the authentication system in this codebase
EOF
# Output includes: SESSION_ID: gemini-abc123

# Continue the conversation
uv run scripts/gemini.py resume gemini-abc123 - <<'EOF'
Now help me add OAuth2 support based on your analysis
EOF
# timeout: 7200000
```

### With Specific Model

```bash
export GEMINI_MODEL=gemini-2.5-flash
uv run scripts/gemini.py "quick summary of this file"
```

### Code Review with Special Characters

```bash
uv run scripts/gemini.py - <<'EOF'
Fix the regex pattern /\d+/ in the parser.
Current code uses:
  const re = /\d+/;
  if ($input.match(re)) { ... }
Handle edge cases properly.
EOF
```

## CLI Arguments (Internal)

The wrapper builds these Gemini CLI arguments:

| Argument | Description |
|----------|-------------|
| `-o stream-json` | Enable JSON stream output for parsing |
| `-y` | Auto-confirm (non-interactive mode) |
| `-m <model>` | Specify model |
| `-r <session_id>` | Resume previous session |
| `-p <prompt>` | Prompt text |

New session:
```
gemini -o stream-json -y -m gemini-2.5-pro -p "prompt"
```

Resume session:
```
gemini -o stream-json -y -m gemini-2.5-pro -r <session_id> -p "prompt"
```

## JSON Output Events

The wrapper parses these JSON events from Gemini:

```json
// Session initialization
{"type":"init","session_id":"xyz789"}

// Streaming message (delta mode)
{"type":"message","role":"assistant","content":"Hi","delta":true,"session_id":"xyz789"}

// Completion
{"type":"result","status":"success","session_id":"xyz789"}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 124 | Timeout |
| 127 | Gemini CLI not found |
| 130 | Interrupted (Ctrl+C) |

## Notes

- **Recommended**: Use `uv run` for automatic Python environment management
- **Alternative**: Direct execution `./gemini.py` uses system Python via shebang
- Python implementation using standard library (zero dependencies)
- Cross-platform compatible (Windows/macOS/Linux)
- PEP 723 compliant (inline script metadata)
- Requires Gemini CLI installed and authenticated
- JSON streaming output enabled by default (`-o stream-json`)
- Auto-confirm enabled (`-y`) for non-interactive execution
- Every execution returns a session ID for resuming conversations
- Streaming output shown on stderr during execution, final message on stdout
