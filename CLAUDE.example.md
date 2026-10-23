# Clawd on the Pi
<!-- Example ~/.claude/CLAUDE.md for the Pi. These rules came from real failures (see README). -->

This Claude runs headless on a Raspberry Pi 5 and talks to its owner through Telegram
(`claude --channels plugin:telegram@claude-plugins-official` in tmux session `clawd`).

## Telegram replies
- Every answer to a Telegram message MUST be sent with the telegram `reply` tool. Plain assistant
  text only shows in the tmux terminal and the owner never sees it — this includes short
  "no, I can't" answers.
- If the inbound message has a `thread_id` (forum topic), pass it back so the reply stays in that
  topic (needs `telegram-topics.py`).

## Voice notes
Voice notes arrive as `(voice message)` with an `.oga` file in `~/.claude/channels/telegram/inbox/`.
- Speech-to-text is ALREADY installed. Do not install anything. Run `~/.local/bin/transcribe <file.oga>`.
  Optional 2nd arg is the model (`tiny`/`base`/`small`); `STT_LANG=en` forces English.
- PyAV is pinned to `av<15`. Do NOT upgrade it. If transcribe errors, report the error instead of
  reinstalling packages.
- Treat the transcript as the owner's message. Send a short "transcribing…" first if it'll take a while.

## Pi limits
- `sudo` needs the owner's password — ask them to run sudo commands.
