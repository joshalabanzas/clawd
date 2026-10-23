#!/bin/bash
# Starts Clawd (Claude Code + Telegram channel plugin) in tmux session "clawd".
# Run at boot by cron:  @reboot /path/to/clawd/start-clawd.sh >> ~/start-clawd.log 2>&1
export PATH="$HOME/.local/bin:$HOME/.bun/bin:/usr/local/bin:/usr/bin:/bin"
WORKDIR="${CLAWD_WORKDIR:-$HOME}"   # folder Clawd works in (its CLAUDE.md + projects)
tmux has-session -t clawd 2>/dev/null && exit 0
# wait up to 2 min for internet
for i in $(seq 1 24); do curl -s -m5 -o /dev/null https://api.telegram.org && break; sleep 5; done
cd "$WORKDIR"
tmux new-session -d -s clawd -e PATH="$PATH" "claude --channels plugin:telegram@claude-plugins-official"
