---
name: ai-project-handoff
description: Migrate a project between different AI assistants (e.g. Gemini, ChatGPT, Claude, Kimi) via a standardized PROJECT-HANDOFF markdown file so work can continue seamlessly on another AI. Use when the user wants to export/transfer/move/hand off a project or conversation from another AI to this one, continue here a project started on another AI, or generate a portable project context/handoff file for another AI. Covers manual export-import (paste a prompt into the source AI, then import the resulting file) and browser-assisted auto-fetch of conversations.
---

# AI Project Handoff

Transfer a project's working context between AI assistants using one standardized markdown file. The user supplies the direction; execute the matching workflow.

## Routing

- User wants to **bring a project INTO this AI** (from Gemini/ChatGPT/Claude/...) → [Import workflow](#import-workflow)
- User wants to **export the CURRENT project OUT to another AI** → [Export workflow](#export-workflow)
- User has an **official data export** from ChatGPT/Claude/Gemini (ZIP, conversations.json, Takeout folder) → [Extract workflow](#extract-workflow)
- User asks about the format itself → read `references/format.md`

## Import workflow

1. Get the handoff file: user pastes its content, drops the file, or gives a path/URL. If the user only has raw conversation text (no handoff file), offer to distill it into the format first — treat as export with source text provided.
2. Read `references/format.md` for the field spec. Run `scripts/validate_handoff.py <file>`; if sections are missing, note the gaps instead of blocking.
3. **Present a project journey recap to the user** — a short chronological narrative of how the project got to today (origin → milestones → turning points → current state), so the *user* re-familiarizes themselves, not just the AI. Use §11 if the file has it; otherwise derive it from §3 (decisions), §6 (done) and §10 (appendix), and mark uncertain parts as 待确认.
4. **Restate understanding** in 3-6 sentences: goal, current status, immediate next step. Together with the recap this is the user's confirmation checkpoint.
5. **Check files** per `files_mode`:
   - `local-paths`: verify each indexed path exists; report missing ones and ask how to obtain them.
   - `links`: list the links/repos and ask whether to clone/download now.
   - `none`: state that only conversation context carries over; user moves files themselves (USB/cloud/git).
6. Ask at most 3 high-value clarifying questions about open items (§8 of the file), then **continue the work from §7 (next steps)** without redoing completed work.
7. Adopt §9 instructions (tone, constraints, conventions) for the rest of the session.

## Export workflow

1. Determine what this session's project is: scan the conversation for goal, decisions, artifacts, pending tasks. If multiple projects, ask which one.
2. Fill `assets/PROJECT-HANDOFF-template.md` following `references/format.md`. Be specific: decisions include *why*, next steps are actionable and ordered, file entries carry role + state.
3. Choose `files_mode` with the user: `local-paths` (project lives on this machine / in a repo), `links` (cloud/repo URLs), or `none`.
4. Run `scripts/validate_handoff.py` on the result; fix any missing required sections.
5. Deliver the file. Also give the user this paste-ready import instruction for the target AI:

> 附件是一份 PROJECT-HANDOFF 项目交接文件，来自另一个 AI。请完整阅读，然后：1）用时间线的方式给我讲一遍这个项目的历程（怎么开始、经历了哪些阶段、有哪些关键转折、为什么是现在这个样子），帮我重新熟悉项目；2）用几句话复述你对项目目标、当前状态和下一步的理解。我确认后，从"待办与下一步"继续工作，不要重复已完成的工作。

### Exporting on the SOURCE AI (user is still on the other AI)

Give the user a paste-ready export prompt to run on the source AI; it produces the handoff file there. Keep the prompt generic and self-contained — the source AI has no access to this skill. Base it on the template's section list (see `references/source-guides.md` for the ready-made prompt and per-AI quirks).

### Auto-fetch mode (browser bridge available)

When the user asks to pull the conversation automatically and a browser-control capability (e.g. kimi-webbridge) is available:

1. Confirm the source AI site and which conversation to take; the user must be logged in in their own browser.
2. Navigate to the conversation, extract the visible chat text (scroll fully first), save raw text to the workspace.
3. Run the normal export distillation over that raw text.
4. Warn: selectors/page structures change; if extraction fails, fall back to the paste-prompt method and tell the user.

## Extract workflow

For users who already downloaded the official data export (see `references/source-guides.md` for how to get it per platform):

1. Unzip the export if needed. Locate `conversations.json` (ChatGPT), `conversations.json`/`conversations.jsonl` (Claude), or the Takeout `Gemini/` folder of `.html` files (Gemini).
2. Run `scripts/extract_conversation.py <path> --list` and let the user pick the project conversation; extract with `--index N -o raw-conversation.md`.
3. Distill the raw markdown into the handoff format per `references/format.md` — never ship the raw transcript as the handoff. Then continue with steps 3-5 of the Export workflow.
4. Note: official exports contain chat transcripts only. Platform *memories* (ChatGPT saved memories, Claude memory) are separate — direct the user to copy those manually from the settings page into §9 or the appendix if relevant.

## Principles

- **Summary over transcript**: the handoff file is a decision-and-state document, not a chat log. Appendix (§10) is optional.
- **Never invent history**: only encode what the conversation or files actually show. Mark uncertain items as 待确认 in §8.
- **Language**: write the handoff file in the project's working language unless the user asks otherwise.
