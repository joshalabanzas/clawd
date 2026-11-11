# 🦀 Clawd

<p align="center"><img src="assets/clawd.gif" width="220" alt="Clawd, a small orange pixel creature"></p>

**Claude Code running 24/7 on a Raspberry Pi, which I talk to through Telegram.** I can DM it or
@ it in a group, send voice notes, and it replies in the same forum topic I asked in.

It's built on the official Telegram channel plugin
(`claude --channels plugin:telegram@claude-plugins-official`). This repo holds the parts that make
it work well day to day: starting at boot, speech-to-text, a topic-reply patch, and the rules it
follows.

Because the Pi is always on and Telegram works on any phone or laptop, Clawd is reachable wherever I am,
with no VPN or open ports. The bot polls Telegram from the Pi, so nothing has to reach in.

```
phone / laptop ──Telegram──▶ Telegram servers ◀──polls── Raspberry Pi
                                                         └─ tmux "clawd": Claude Code + Telegram channel plugin
                                                            ├─ transcribe  (voice notes → text, on-device)
                                                            └─ your projects folder (CLAUDE.md, code, notes)
```

It shares the Pi with two sibling bots of mine: Huginn (AI news digest) and Muninn (Telegram → calendar).

| File | What it does |
|---|---|
| `start-clawd.sh` | Starts Clawd in a tmux session `clawd` at boot (waits for internet first). Set `CLAWD_WORKDIR` to the folder it should work in, and optionally `CLAWD_CLAUDE_VERSION` to pin a Claude Code release. |
| `transcribe` | Voice notes → text with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) on the Pi's CPU (int8, ~5 s for a short note). |
| `telegram-topics.py` | Patches the plugin so replies land in the **same forum topic** as the question. Without it, every reply goes to General. Idempotent; re-run after plugin updates. |
| `CLAUDE.example.md` | The rules Clawd follows: always reply through the tool, how to handle voice notes. |

## Setup

1. Install the Telegram channel plugin in Claude Code and pair your bot (token from @BotFather).
   The plugin stores it in `~/.claude/channels/telegram/.env`.
2. Copy `CLAUDE.example.md` to `~/.claude/CLAUDE.md` (or merge it in).
3. Voice notes (optional):
   ```bash
   python3 -m venv ~/.local/share/stt-venv
   ~/.local/share/stt-venv/bin/pip install faster-whisper "av<15"
   sed "1s|.*|#!$HOME/.local/share/stt-venv/bin/python|" transcribe > ~/.local/bin/transcribe
   chmod +x ~/.local/bin/transcribe
   ```
4. Forum topics (optional): `python3 telegram-topics.py`, then restart Clawd.
5. Boot (`crontab -e`): `@reboot /path/to/clawd/start-clawd.sh >> ~/start-clawd.log 2>&1`
   To pin a version, put it in front: `@reboot CLAWD_CLAUDE_VERSION=2.1.296 /path/to/clawd/start-clawd.sh …`
   (`ls ~/.local/share/claude/versions` shows the ones you have).

## Things I learned the hard way

- **Plain text from a channel bot goes nowhere.** If Claude answers without calling the `reply`
  tool, the answer only shows in tmux. The fix is a hard rule in its `CLAUDE.md`.
- **Health-checking the plugin kills the running bot.** `claude mcp list` starts a second plugin
  instance that takes over the Telegram poller. Don't run it while Clawd is up.
- **Pin your Python deps.** PyAV 19 broke faster-whisper's decoder, so `transcribe` decodes the
  audio itself and the venv pins `av<15`.
- **The stock plugin ignores forum topics.** Hence `telegram-topics.py`.
- **A Claude Code update can break it at boot.** One release only started the Telegram plugin after a
  manual `/mcp` reconnect, so after a reboot Clawd was silent. Pinning the last good version with
  `CLAWD_CLAUDE_VERSION` (which also turns off auto-update) fixed it. Unpin once a newer release works.

## Troubleshooting

- `tmux ls` says "no server running": Clawd exited and won't come back until reboot. Run `start-clawd.sh`.
- Clawd seems to ignore you: `tmux capture-pane -pt clawd -S -40` and look for a prompt waiting
  on input, or an answer it typed into the terminal instead of sending.

## License

MIT, see [LICENSE](LICENSE).
