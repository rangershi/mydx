# OmO Multi-Agent Orchestration

OmO (Oh-My-OpenCode) is a multi-agent orchestration skill that uses Sisyphus as the primary coordinator to delegate tasks to specialized agents.

## Quick Start

```
/omo <your task>
```

## Agent Hierarchy

| Agent | Role | Execution Method |
|-------|------|------------------|
| sisyphus | Primary orchestrator | Claude Code (current context) |
| oracle | Technical advisor (EXPENSIVE) | Task tool (subagent_type: "general-purpose") |
| librarian | External research | Task tool (subagent_type: "Explore") |
| explore | Codebase search (FREE) | Task tool (subagent_type: "Explore") |
| develop | Code implementation | Codex CLI or Gemini CLI |
| frontend-ui-ux-engineer | UI/UX specialist | Gemini CLI |
| document-writer | Documentation | Gemini CLI |

## How It Works

1. `/omo` loads Sisyphus as the entry point
2. Sisyphus analyzes your request via Intent Gate
3. Based on task type, Sisyphus either:
   - Executes directly (simple tasks)
   - Delegates to specialized agents via Task tool (complex tasks)
   - Fires parallel agents (exploration)

## Examples

```bash
# Refactoring
/omo Help me refactor this authentication module

# Feature development
/omo I need to add a new payment feature with frontend UI and backend API

# Research
/omo What authentication scheme does this project use?
```

## Agent Delegation

Sisyphus delegates via Claude Code's Task tool:

```
# Delegate to oracle for architecture advice
Task tool:
- subagent_type: "general-purpose"
- prompt: |
    You are oracle, a technical advisor...
    Analyze the authentication architecture.

# Delegate to explore for codebase search
Task tool:
- subagent_type: "Explore"
- prompt: Find all authentication-related files...

# Delegate to develop for code implementation (Codex)
Bash tool:
codex e -C . --skip-git-repo-check --json - <<'EOF'
Implement the authentication module...
EOF

# Delegate to frontend-ui-ux-engineer (Gemini)
Bash tool:
gemini -o stream-json -y -p "$(cat <<'EOF'
Design the login form UI...
EOF
)"
```

## Requirements

- Claude Code with Task tool support
- Backend CLIs: codex, gemini (optional, for specific agents)
