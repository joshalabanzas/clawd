#!/bin/bash
# Starts Clawd (Claude Code + Telegram channel plugin) in tmux session "clawd".
# Run at boot by cron:  @reboot /path/to/clawd/start-clawd.sh >> ~/start-clawd.log 2>&1
export PATH="$HOME/.local/bin:$HOME/.bun/bin:/usr/local/bin:/usr/bin:/bin"
WORKDIR="${CLAWD_WORKDIR:-$HOME}"   # folder Clawd works in (its CLAUDE.md + projects)
tmux has-session -t clawd 2>/dev/null && exit 0
# wait up to 2 min for internet
for i in $(seq 1 24); do curl -s -m5 -o /dev/null https://api.telegram.org && break; sleep 5; done
cd "$WORKDIR"
# Optional: pin a Claude Code version, e.g. CLAWD_CLAUDE_VERSION=2.1.296. Some releases fail to start the
# Telegram plugin at launch (it only comes up after a manual /mcp reconnect), which is useless at boot.
# A pinned version also turns off auto-update, so it stays pinned.
CLAUDE_BIN=claude
UPDATER=""
if [ -n "$CLAWD_CLAUDE_VERSION" ] && [ -x "$HOME/.local/share/claude/versions/$CLAWD_CLAUDE_VERSION" ]; then
  CLAUDE_BIN="$HOME/.local/share/claude/versions/$CLAWD_CLAUDE_VERSION"
  UPDATER="-e DISABLE_AUTOUPDATER=1"
fi
tmux new-session -d -s clawd -e PATH="$PATH" $UPDATER "$CLAUDE_BIN --channels plugin:telegram@claude-plugins-official"
