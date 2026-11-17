# Source-AI Export Guides

## Official data exports (use with `scripts/extract_conversation.py`)

Best fidelity: the platforms' own GDPR/Takeout exports contain full transcripts.

- **ChatGPT**: Settings → Data Controls → Export data → download link arrives by email → unzip → `conversations.json` (one JSON array; each conversation has a `mapping` of message nodes). Note: saved *memories* are NOT in this export — copy them manually from Settings → Personalization → Memory.
- **Claude**: Settings → Privacy → Export data → emailed link (expires after 24h) → `conversations.json` (or `.jsonl`). Anthropic states this export cannot be re-imported into Claude — it is for leaving, which is exactly our use case. Claude *Projects* knowledge/instructions live outside chats; ask the user to paste them separately.
- **Gemini**: Google Takeout → select "Gemini Apps" → export → folder of per-conversation `.html` files (labels are localized: "You:"/"Gemini:" or "你:"/"Gemini:"). The extractor handles both; other locales may need the `_SPEAKER_RE` regex extended.

The extractor auto-detects the platform from file structure. Run with `--list` first — exports contain ALL conversations, so always let the user pick the right one.

## The universal export prompt

Give this to the user to paste into the source AI (works on Gemini, ChatGPT, Claude, and most chat AIs). Adapt wording to the conversation language.

```text
我们之后要在另一个 AI 上继续这个项目。请基于我们的全部对话，生成一份"项目交接文件"，纯 markdown 输出在一个代码块里，严格遵守以下结构：

开头是 YAML frontmatter：
---
handoff_version: "1.0"
project_name: <项目名>
source_ai: <你的名字和模型>
exported_at: <当前时间，ISO 8601 带时区>
language: <我们的工作语言>
files_mode: <local-paths | links | none>
---

然后是九个章节：
# Project Handoff: <项目名>
## 1. 项目概述 — 目标、成功标准、范围，不超过 10 行
## 2. 当前状态 — 当前阶段、大致完成度、正在进行中的事
## 3. 关键决策记录 — 编号列出：决定了什么、为什么、放弃了哪些方案
## 4. 技术栈与环境 — 语言、框架、版本、操作系统
## 5. 项目文件索引 — 表格：路径或链接 | 作用 | 状态（完成/进行中/过时）
## 6. 已完成工作 — 已完成里程碑列表
## 7. 待办与下一步 — 有序、可独立执行的任务列表，第一条是马上要做的事
## 8. 未决问题与风险 — 阻塞点、不确定项
## 9. 交接指令 — 给接手 AI 的要求：代码风格、约束、不要改动的地方
## 10. 附录：对话摘录 — 可选，关键对话的原文节选
## 11. 项目历程 — 推荐。用时间线讲这个项目怎么走到今天：怎么开始的、经历了哪些阶段和里程碑（带大致日期）、在哪些节点改变过方向、为什么是现在这个样子。这是给"人"看的故事，帮助用户在新 AI 上重新熟悉项目；对话里找不到的细节标"待确认"，不要编造。

要求：只写对话中真实发生过的内容，不确定的放进第 8 节并标注"待确认"；每个决策都要带上理由；总长控制在 200 行以内。不要写对话之外的内容。
```

Then the user saves the output as `PROJECT-HANDOFF.md` and brings it to the receiving AI.

## Per-AI quirks

- **Gemini**: long conversations may be truncated by the model's summary; ask it to double-check §3 and §6 against the earliest parts of the chat. Gemini can export to Google Docs — the user can also share that doc instead.
- **ChatGPT**: custom instructions/memory may hold relevant context not visible in the chat; add "也请参考你的记忆和自定义指令中与本项目相关的内容" to the prompt.
- **Claude**: Projects feature keeps files/instructions outside the chat; remind the user to mention Project knowledge explicitly in the prompt.
- **Kimi**: k1/k2 long context usually retains the whole thread; no special handling. Files in the workspace are already local → prefer `files_mode: local-paths`.

## Complement: official one-way import features

When migrating INTO Claude or Gemini, their official import flows can run alongside the handoff file:

- **Claude** (claude.com/import-memory): paste-ready prompt that makes the old AI summarize what it remembers about the *user*; result goes into Claude's memory settings. Covers preferences/facts, not project state — the handoff file still carries the project.
- **Gemini**: imports chat history (ZIP ≤5 GB, personal accounts only, unavailable in EEA/UK/CH) and memory-like context from other assistants. One-directional pull-in; does not recreate projects or files.
- **ChatGPT**: has memory export but no import; use the handoff file + paste prompt only.

Rule of thumb: official import = who the user is; PROJECT-HANDOFF = what the project is. Offer both when the target supports it.

## Auto-fetch notes

Browser bridges operate the user's own logged-in browser. Typical flow for Gemini/ChatGPT/Claude web UIs:

1. Open the conversation URL the user provides (or navigate from the site's chat list).
2. Scroll to the very top first, then page down to force lazy-loading of all messages.
3. Extract message texts (user + assistant), preserving order; save raw text to the workspace as `raw-conversation-<date>.md`.
4. Distill the raw text into the handoff format per `format.md` — never ship the raw transcript as the handoff.

Pitfalls: virtualized lists drop off-screen messages (must scroll incrementally); code blocks and canvases may live outside the main message DOM; rate limits on long pages. If extraction is incomplete, say so and fall back to the paste prompt.
