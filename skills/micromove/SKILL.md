---
name: micromove
description: Manage MicroMove work-break reminders, snooze or pause them, and offer the configured exercise-page link when the user wants a short movement break.
---

Use the bundled Python CLI at `../../scripts/micromove.py`, resolving it relative to this SKILL.md. Quote its absolute path in shell commands. Python 3.10+ is required; no API key or package installation is needed.

For first setup or a missing reminder, run `doctor`. A successful `enable` or `snooze` only saves preferences: it does not verify plugin loading, hook trust or visible delivery. Explain any unverified integration, and guide the user through `../../docs/INSTALL.md`. With a requested installation test, run `probe`, then finish the response and let the real host event fire. Never invoke `hook` manually to make this test appear successful. A historical `last_hook` is diagnostic evidence only, not proof of current trust or visible UI delivery. If Python cannot start, report the missing runtime and installation prerequisite instead of claiming success.

- “开启提醒”: run `enable`. Explain that defaults are 11:00 and 16:00 in the computer's local timezone, checked at session start and response end, not while the host is idle.
- “现在动一下”: run `start`; show the returned configured URL as a link. If it is absent, explain that the team's exercise page has not been connected. Do not invent exercise instructions or claim that a timer is running.
- “10 分钟后提醒”: run `snooze 10`. Other requested durations use the corresponding minutes. Explain delivery occurs on the next eligible host event after that time.
- “暂停提醒”: run `pause`; no follow-up reminder until explicitly re-enabled.
- “我做完了”: run `done` only after the user reports completion. No streaks, guilt, calorie estimates or competitive scoring.
- Configuration: `configure --times 11:00 16:00` or `configure --url <user-provided URL>`; preserve options the user did not change.
- Diagnostics: `status` reports state; `demo` previews content without consuming a scheduled reminder. Do not call `check` just to preview: it consumes a due slot.

Reminder tone: gentle, optional, brief. After a reminder the user may continue coding without responding. Never interrupt or redirect an unrelated task. Hooks output a short host message, not native clickable buttons; offer “现在动一下 / 10 分钟后提醒” as conversational choices. Do not silently create recurring host automations or OS background jobs.

Preferences, snooze time, deduplication keys, a pending installation probe, and the latest hook's event name, timestamp and script path are stored in `~/.micromove/state.sqlite3` (or `MICROMOVE_DATA_DIR` for tests). The plugin does not read source code or persist conversation text. No external service is contacted by the CLI.
