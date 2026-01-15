#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Gemini CLI wrapper with JSON streaming, session management, and cross-platform support.

Usage:
    # New session
    uv run gemini.py "<prompt>" [workdir]
    python3 gemini.py "<prompt>" [workdir]
    ./gemini.py "<prompt>" [workdir]

    # Resume session
    uv run gemini.py resume <session_id> "<prompt>" [workdir]
    python3 gemini.py resume <session_id> "<prompt>" [workdir]

    # Stdin mode (for complex prompts)
    echo "prompt" | uv run gemini.py -
    uv run gemini.py - [workdir] <<'EOF'
    multi-line prompt
    EOF

    # Resume with stdin
    uv run gemini.py resume <session_id> - [workdir] <<'EOF'
    continue task
    EOF
"""
import json
import subprocess
import sys
import os
import signal

DEFAULT_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
DEFAULT_WORKDIR = '.'
TIMEOUT_MS = 7_200_000  # 2 hours in milliseconds
DEFAULT_TIMEOUT = TIMEOUT_MS // 1000
FORCE_KILL_DELAY = 5


def log_error(message: str):
    """Output error message to stderr"""
    sys.stderr.write(f"ERROR: {message}\n")
    sys.stderr.flush()


def log_warn(message: str):
    """Output warning message to stderr"""
    sys.stderr.write(f"WARN: {message}\n")
    sys.stderr.flush()


def log_info(message: str):
    """Output info message to stderr"""
    sys.stderr.write(f"INFO: {message}\n")
    sys.stderr.flush()


def read_stdin():
    """Read prompt from stdin"""
    if sys.stdin.isatty():
        log_error("Stdin mode requires piped input")
        sys.exit(1)
    return sys.stdin.read()


def parse_args():
    """Parse command line arguments

    Formats:
        gemini.py "<prompt>" [workdir]
        gemini.py - [workdir]
        gemini.py resume <session_id> "<prompt>" [workdir]
        gemini.py resume <session_id> - [workdir]
    """
    args = sys.argv[1:]

    if len(args) < 1:
        log_error('Usage: gemini.py "<prompt>" [workdir]')
        log_error('       gemini.py resume <session_id> "<prompt>" [workdir]')
        sys.exit(1)

    result = {
        'mode': 'new',
        'session_id': None,
        'prompt': None,
        'workdir': DEFAULT_WORKDIR,
        'use_stdin': False
    }

    # Check for resume mode
    if args[0] == 'resume':
        if len(args) < 3:
            log_error('Resume mode requires: resume <session_id> "<prompt>" [workdir]')
            sys.exit(1)
        result['mode'] = 'resume'
        result['session_id'] = args[1]
        if not result['session_id'] or result['session_id'].strip() == '':
            log_error('Resume mode requires non-empty session_id')
            sys.exit(1)

        # prompt or stdin marker
        if args[2] == '-':
            result['use_stdin'] = True
            result['prompt'] = read_stdin()
        else:
            result['prompt'] = args[2]

        # optional workdir
        if len(args) > 3:
            result['workdir'] = args[3]
    else:
        # New session mode
        if args[0] == '-':
            result['use_stdin'] = True
            result['prompt'] = read_stdin()
        else:
            result['prompt'] = args[0]

        # optional workdir
        if len(args) > 1 and args[1] != '-':
            result['workdir'] = args[1]

    if not result['prompt'] or result['prompt'].strip() == '':
        log_error('Prompt cannot be empty')
        sys.exit(1)

    return result


def build_gemini_args(args) -> list:
    """Build gemini CLI arguments

    New session: gemini -o stream-json -y -m <model> -p <prompt>
    Resume:      gemini -o stream-json -y -m <model> -r <session_id> -p <prompt>
    """
    gemini_args = [
        'gemini',
        '-o', 'stream-json',  # JSON stream output for parsing
        '-y',                  # Auto-confirm (non-interactive)
        '-m', DEFAULT_MODEL,
    ]

    # Add resume flag if in resume mode
    if args['mode'] == 'resume' and args['session_id']:
        gemini_args.extend(['-r', args['session_id']])

    # Add prompt
    gemini_args.extend(['-p', args['prompt']])

    return gemini_args


def parse_json_stream(process, timeout_sec: int):
    """Parse JSON stream output from Gemini CLI

    Expected events:
        {"type":"init","session_id":"xyz789"}
        {"type":"message","role":"assistant","content":"Hi","delta":true,"session_id":"xyz789"}
        {"type":"result","status":"success","session_id":"xyz789"}

    Returns: (message, session_id, exit_code)
    """
    message_parts = []
    session_id = None

    try:
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                # Non-JSON line, might be progress output
                log_info(f"Non-JSON: {line[:100]}")
                continue

            event_type = event.get('type', '')

            # Extract session_id from any event that has it
            if 'session_id' in event and event['session_id'] and not session_id:
                session_id = event['session_id']
                log_info(f"Session ID: {session_id}")

            # Handle init event
            if event_type == 'init':
                log_info("Gemini session initialized")
                continue

            # Handle message event (streaming content)
            if event_type == 'message':
                content = event.get('content', '')
                if content:
                    # Delta mode: accumulate parts
                    if event.get('delta', False):
                        message_parts.append(content)
                        # Print streaming content to stderr for visibility
                        sys.stderr.write(content)
                        sys.stderr.flush()
                    else:
                        # Full message (non-delta)
                        message_parts = [content]
                continue

            # Handle result event (completion)
            if event_type == 'result':
                status = event.get('status', '')
                if status == 'success':
                    log_info("Gemini completed successfully")
                else:
                    log_warn(f"Gemini result status: {status}")
                continue

            # Handle error event
            if event_type == 'error':
                error_msg = event.get('message', event.get('error', 'Unknown error'))
                log_error(f"Gemini error: {error_msg}")
                continue

        # Wait for process to complete
        returncode = process.wait(timeout=timeout_sec)

        # Read any remaining stderr
        stderr_output = process.stderr.read()
        if stderr_output:
            sys.stderr.write(stderr_output)
            sys.stderr.flush()

        message = ''.join(message_parts)
        return message, session_id, returncode

    except subprocess.TimeoutExpired:
        log_error(f'Gemini execution timeout ({timeout_sec}s)')
        return None, session_id, 124


def main():
    log_info('Gemini CLI wrapper started')
    args = parse_args()

    log_info(f"Mode: {args['mode']}")
    log_info(f"Prompt length: {len(args['prompt'])}")
    log_info(f"Working dir: {args['workdir']}")
    if args['session_id']:
        log_info(f"Resume session: {args['session_id']}")

    gemini_args = build_gemini_args(args)
    log_info(f"Command: {' '.join(gemini_args[:6])}...")

    timeout_sec = DEFAULT_TIMEOUT
    log_info(f"Timeout: {timeout_sec}s")

    # Change working directory if specified
    if args['workdir'] != DEFAULT_WORKDIR:
        try:
            os.chdir(args['workdir'])
            log_info(f"Changed to: {os.getcwd()}")
        except FileNotFoundError:
            log_error(f"Working directory not found: {args['workdir']}")
            sys.exit(1)
        except PermissionError:
            log_error(f"Permission denied: {args['workdir']}")
            sys.exit(1)

    process = None

    def signal_handler(signum, frame):
        """Handle interrupt signals"""
        log_warn(f"Received signal {signum}")
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=FORCE_KILL_DELAY)
            except subprocess.TimeoutExpired:
                process.kill()
        sys.exit(130)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        log_info(f"Starting gemini with model {DEFAULT_MODEL}")

        process = subprocess.Popen(
            gemini_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        log_info(f"Gemini PID: {process.pid}")

        # Parse JSON stream
        message, session_id, returncode = parse_json_stream(process, timeout_sec)

        # Output results
        if message:
            # Print newline after streaming output
            sys.stderr.write("\n")
            sys.stderr.flush()

            # Print final message to stdout
            print(message)

            # Print session ID for resume capability
            if session_id:
                print("\n---")
                print(f"SESSION_ID: {session_id}")
        else:
            if returncode == 124:
                log_error("Timeout: no message received")
            else:
                log_error("No agent message in output")

        if returncode != 0 and returncode != 124:
            log_error(f'Gemini exited with status {returncode}')

        sys.exit(returncode if returncode else 0)

    except subprocess.TimeoutExpired:
        log_error(f'Gemini execution timeout ({timeout_sec}s)')
        if process is not None:
            process.kill()
            try:
                process.wait(timeout=FORCE_KILL_DELAY)
            except subprocess.TimeoutExpired:
                pass
        sys.exit(124)

    except FileNotFoundError:
        log_error("gemini command not found in PATH")
        log_error("Please install Gemini CLI: https://github.com/google-gemini/gemini-cli")
        sys.exit(127)

    except KeyboardInterrupt:
        log_warn("Interrupted by user")
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=FORCE_KILL_DELAY)
            except subprocess.TimeoutExpired:
                process.kill()
        sys.exit(130)


if __name__ == '__main__':
    main()
