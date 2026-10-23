#!/usr/bin/env python3
"""Patch the Claude Code Telegram channel plugin so Clawd replies in the same forum topic.

Stock plugin (0.0.7) drops message_thread_id: inbound meta has no topic and the reply tool never
sends one, so every reply lands in General. This adds a `thread_id` meta field + reply argument.
Idempotent. Re-run after a plugin update, then restart Clawd:
    python3 telegram-topics.py   (on claude-pi)
"""
import glob
import os
import sys

MARK = "/* clawd-topics-patch */"
paths = sorted(glob.glob(os.path.expanduser(
    "~/.claude/plugins/cache/claude-plugins-official/telegram/*/server.ts")))
if not paths:
    sys.exit("telegram plugin server.ts not found")

EDITS = [
    # 1. inbound: tell Claude which topic the message is in
    ("""        ...(msgId != null ? { message_id: String(msgId) } : {}),
        user: from.username ?? String(from.id),""",
     """        ...(msgId != null ? { message_id: String(msgId) } : {}),
        ...(ctx.message?.is_topic_message && ctx.message?.message_thread_id != null
          ? { thread_id: String(ctx.message.message_thread_id) } : {}), """ + MARK + """
        user: from.username ?? String(from.id),"""),
    # 2. typing indicator in the right topic
    ("""  void bot.api.sendChatAction(chat_id, 'typing').catch(() => {})""",
     """  void bot.api.sendChatAction(chat_id, 'typing', ctx.message?.is_topic_message && ctx.message?.message_thread_id != null
    ? { message_thread_id: ctx.message.message_thread_id } : {}).catch(() => {}) """ + MARK),
    # 3. reply tool schema
    ("""          reply_to: {
            type: 'string',
            description: 'Message ID to thread under. Use message_id from the inbound <channel> block.',
          },""",
     """          reply_to: {
            type: 'string',
            description: 'Message ID to thread under. Use message_id from the inbound <channel> block.',
          },
          thread_id: {
            type: 'string',
            description: 'Forum topic to post in. ALWAYS pass thread_id from the inbound <channel> block when it has one, so the reply stays in the same topic.',
          }, """ + MARK),
    # 4. reply handler: read it
    ("""        const reply_to = args.reply_to != null ? Number(args.reply_to) : undefined
        const files = (args.files as string[] | undefined) ?? []""",
     """        const reply_to = args.reply_to != null ? Number(args.reply_to) : undefined
        const thread_id = args.thread_id != null && args.thread_id !== '' ? Number(args.thread_id) : undefined """ + MARK + """
        const topicOpt = thread_id != null ? { message_thread_id: thread_id } : {}
        const files = (args.files as string[] | undefined) ?? []"""),
    # 5. text chunks
    ("""              ...(shouldReplyTo ? { reply_parameters: { message_id: reply_to } } : {}),
              ...(parseMode ? { parse_mode: parseMode } : {}),""",
     """              ...(shouldReplyTo ? { reply_parameters: { message_id: reply_to } } : {}),
              ...(parseMode ? { parse_mode: parseMode } : {}),
              ...topicOpt,"""),
    # 6. files
    ("""          const opts = reply_to != null && replyMode !== 'off'
            ? { reply_parameters: { message_id: reply_to } }
            : undefined""",
     """          const opts = {
            ...(reply_to != null && replyMode !== 'off' ? { reply_parameters: { message_id: reply_to } } : {}),
            ...topicOpt,
          }"""),
    # 7. instructions
    ("""Reply with the reply tool — pass chat_id back.""",
     """Reply with the reply tool — pass chat_id back, and if the tag has thread_id (a forum topic) ALWAYS pass that thread_id too so the reply stays in the same topic."""),
]

for path in paths:
    src = open(path).read()
    if MARK in src:
        print(f"already patched: {path}")
        continue
    for old, new in EDITS:
        if src.count(old) != 1:
            sys.exit(f"patch anchor not found (plugin changed?) in {path}:\n{old[:80]}")
        src = src.replace(old, new)
    os.replace(path, path + ".orig") if not os.path.exists(path + ".orig") else None
    open(path, "w").write(src)
    print(f"patched: {path}")
