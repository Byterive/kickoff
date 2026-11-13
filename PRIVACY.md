---
title: kickoff privacy policy
summary: What kickoff reads, writes and sends, how long data is kept, and how to contact us.
keywords: [kickoff, privacy, data, policy]
status: confirmed
updated: 2026-11-13
---

# kickoff privacy

This page says what kickoff does with your data. It applies to kickoff version 1.4 and later releases of that line, until a newer version of this file replaces it. Date: 2026-11-13.

## What it reads
The files in the project folder where you start it, and `~/.claude/kickoff/config.json` for your settings.

## What it writes and where
In your project folder: `CLAUDE.md`, `PROJECT_STATUS.md`, `DECISIONS.md`, `NEXT.md`, `.gitignore`, a git hook, plan files, the `INDEX.md` files, and the project's plugin on and off list. `/kickoff:upgrade` lists changes first and writes only after your yes, and it never overwrites.

kickoff also installs three hooks. They run on your computer as Python scripts: two block a recursive forced delete and a Claude co-author line in a commit, and a Stop hook rebuilds the `INDEX.md` files in a kickoff project after each turn. Set `KICKOFF_DISABLED_HOOKS` to turn them off (`rmrf`, `coauthor`, `reindex`, comma-separated).

## What it sends and to whom
kickoff has no network code of its own and sends nothing anywhere. Its commands run inside Claude Code, so what Claude reads in a session is handled by Claude Code like any other session text. kickoff adds no separate connection.

Some profiles suggest companion plugins by name. Nothing is installed without your yes.

## How long data is kept
The files stay in your project folder until you delete them. kickoff keeps nothing anywhere else.

## Who it is for
We do not design kickoff for people under 18, and we do not knowingly collect data from them.

## Other software
kickoff runs inside Claude Code. Claude Code and the other tools it works with handle your data under their own terms. This page covers only kickoff.

## Contact
Use the contact details on [byterive.com](https://byterive.com). We do not publish an email address for privacy questions yet.

*Independent project by Byterive. Not affiliated with or endorsed by Anthropic.* · [byterive.com](https://byterive.com)
