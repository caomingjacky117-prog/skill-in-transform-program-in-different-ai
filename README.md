# ai-project-handoff

**English** | [中文](#中文)

A skill that migrates projects seamlessly between AI assistants — via a standardized `PROJECT-HANDOFF.md` file, project context flows freely between Gemini, ChatGPT, Claude, and Kimi. No more re-explaining everything on the new AI.

## The Problem

Three weeks of LeetCode planning on Gemini, a half-designed Excel template on ChatGPT, half-written code on Claude — switch AIs and it's all gone. Official "memory import" moves preferences, not project state; full conversation exports are too long and noisy to use.

This skill transfers **structured project state**: goals, progress, key decisions (with rationale), file index, next steps, risks — plus a human-readable project journey.

## How It Works

```
Source AI (e.g. Gemini)              PROJECT-HANDOFF.md               Target AI (e.g. Kimi)
┌──────────────┐   export prompt    ┌─────────────────┐  paste/upload  ┌──────────────┐
│ project chat  │ ────────────────▶ │ standardized    │ ─────────────▶ │ validate →    │
│               │ or official export │ handoff file    │                │ journey recap │
└──────────────┘                    │ (~60-200 lines) │                │ → continue    │
                                    └─────────────────┘                └──────────────┘
```

The receiving AI needs **zero installation** — the handoff file plus one import instruction just works. An AI with this skill installed additionally gets validation, journey recap, and a guided resume workflow.

## Quick Start

### Export (move a project out)

Paste the export prompt (full text in `references/source-guides.md`) into the project conversation on the source AI, and save its markdown output as `PROJECT-HANDOFF.md`. If the source AI generated files (e.g. .xlsx), download them separately — text can't carry files.

Already have an official data export (ChatGPT/Claude `conversations.json`, Gemini Takeout)? Use the extractor:

```bash
python scripts/extract_conversation.py conversations.json --list                  # list all conversations
python scripts/extract_conversation.py conversations.json --index 3 -o raw.md     # extract the target one
# then have an AI distill raw.md into a handoff file per references/format.md
```

### Import (pick a project up)

Paste or drop `PROJECT-HANDOFF.md` into the new AI with this instruction:

> Attached is a PROJECT-HANDOFF file from another AI. Read it fully, then: 1) walk me through the project's journey as a timeline; 2) restate your understanding of the goal, current status, and next step. After I confirm, continue from the "next steps" section — do not redo completed work.

An AI with this skill installed automatically runs: format validation → project journey recap → understanding check → file verification → up to 3 clarifying questions → resume from next steps.

## Installation

| Platform | Method |
|---|---|
| Kimi | Import `ai-project-handoff.skill`, or unzip into the skills directory `daimon/skills/` |
| Claude.ai / Claude Code | Natively compatible: Capabilities → Skills → upload, or place in `~/.claude/skills/` |
| ChatGPT | Create a custom GPT: paste SKILL.md body into Instructions, attach template + format.md as Knowledge |
| Gemini | Create a Gem: paste SKILL.md body + template into the instructions field |
| Any AI | No install — just use the handoff file + import instruction |

## Repository Layout

```
ai-project-handoff/
├── SKILL.md                        # Core workflows (import / export / extract / auto-fetch)
├── references/
│   ├── format.md                   # PROJECT-HANDOFF v1.0 format spec
│   └── source-guides.md            # Per-platform export prompts, official exports, fetch notes
├── assets/
│   └── PROJECT-HANDOFF-template.md # Blank handoff template
└── scripts/
    ├── validate_handoff.py         # Handoff file validator (stdlib, zero deps)
    └── extract_conversation.py     # Official-export conversation extractor (stdlib, zero deps)
```

## Format at a Glance

YAML frontmatter (project name, source AI, export time, language, `files_mode`) + 11 sections:

| # | Section | Required | Purpose |
|---|---|---|---|
| 1 | Goal | ✅ | Objectives, success criteria, scope |
| 2 | Status | ✅ | Phase, % done, in-flight items |
| 3 | Key decisions | ✅ | Decision + rationale + rejected alternatives |
| 4 | Stack & environment | ✅ | Languages, frameworks, versions |
| 5 | File index | ✅ | Path/URL + role + state |
| 6 | Done | ✅ | Prevents the receiving AI from redoing work |
| 7 | Next steps | ✅ | Ordered, independently actionable |
| 8 | Open questions & risks | ✅ | Blockers, "to be confirmed" items |
| 9 | Instructions | ✅ | Style, constraints, do-not-touch list |
| 10 | Appendix: excerpts | optional | Key verbatim exchanges |
| 11 | Project journey | recommended | A timeline narrative for the human |

## Scripts

**validate_handoff.py** — checks required frontmatter fields, the 9 required sections, and non-empty bodies; exit code 0/1:

```bash
python scripts/validate_handoff.py PROJECT-HANDOFF.md
```

**extract_conversation.py** — auto-detects ChatGPT / Claude / Gemini-Takeout export formats; lists and extracts a chosen conversation to raw markdown (input for distillation — never use it as the handoff file itself).

## Known Limitations

- Handoff quality depends on the source AI's diligence — it may be sloppy or fabricate; the validator checks structure, not truth. **Your confirmation is the last line of defense.**
- Browser auto-fetch depends on each platform's page structure and breaks with redesigns; fall back to the paste prompt when it fails.
- Platform export menus and file formats change over time — `source-guides.md` and the extractor need ongoing maintenance.
- Distilling a months-long conversation into ~200 lines inevitably loses information; early details may be forgotten by the source AI itself.

## Design Principles

1. **Summary over transcript** — the handoff file is a decision-and-state document, not a chat log.
2. **Never invent history** — anything not in the conversation is marked "to be confirmed" in section 8.
3. **Zero-install usable** — the protocol works even when neither end has the skill installed.
4. **For AI and human alike** — sections 1-9 restore context for the AI; section 11 rebuilds memory for the human.

---

Format version: PROJECT-HANDOFF v1.0 · License: [MIT](LICENSE)

---

## 中文

把一个 AI 上的项目无缝迁移到另一个 AI 的 Skill——通过一份标准化的 `PROJECT-HANDOFF.md` 交接文件，让 Gemini、ChatGPT、Claude、Kimi 之间的项目上下文自由流动，不用在新 AI 上从头解释一遍。

### 解决什么问题

在 Gemini 上聊了三周的刷题计划、在 ChatGPT 上做了一半的 Excel 模板、在 Claude 上写到一半的代码——换个 AI 就全没了。官方"记忆导入"只搬偏好不搬项目，完整对话导出又臭又长没法用。

这个 skill 搬的是**结构化的项目状态**：目标、进度、关键决策（含理由）、文件索引、待办、风险、以及一段给"人"看的项目历程。

### 工作原理

```
源 AI（如 Gemini）                PROJECT-HANDOFF.md                 目标 AI（如 Kimi）
┌──────────────┐   导出咒语      ┌─────────────────┐   粘贴/上传     ┌──────────────┐
│ 项目对话      │ ─────────────▶ │ 标准化交接文件    │ ─────────────▶ │ 校验→历程回顾 │
│              │ 或官方导出提取   │ （约 60-200 行）  │                │ →确认→继续干活│
└──────────────┘                └─────────────────┘                └──────────────┘
```

接收方 AI **零安装**——交接文件 + 一句导入指令即可工作；安装了本 skill 的 AI 则自动完成校验、历程回顾和续作流程。

### 快速开始

**导出（把项目迁出去）**：在源 AI 的项目对话里粘贴导出咒语（完整文本见 `references/source-guides.md`），把它输出的 markdown 保存为 `PROJECT-HANDOFF.md`。若源 AI 生成过文件（如 .xlsx），需单独下载带走。

已有官方数据导出（ChatGPT/Claude 的 `conversations.json`、Gemini Takeout）？用提取脚本：

```bash
python scripts/extract_conversation.py conversations.json --list        # 列出所有对话
python scripts/extract_conversation.py conversations.json --index 3 -o raw.md   # 提取目标对话
# 然后交给 AI 按 references/format.md 提炼成交接文件
```

**导入（把项目接进来）**：把 `PROJECT-HANDOFF.md` 粘贴或拖给新 AI，附上这句：

> 附件是一份 PROJECT-HANDOFF 项目交接文件，来自另一个 AI。请完整阅读，然后：1）用时间线的方式给我讲一遍这个项目的历程；2）用几句话复述你对项目目标、当前状态和下一步的理解。我确认后，从"待办与下一步"继续工作，不要重复已完成的工作。

安装了本 skill 的 AI 会自动执行：格式校验 → 项目历程回顾 → 理解确认 → 文件核对 → ≤3 个澄清问题 → 从待办继续。

### 安装

| 平台 | 方式 |
|---|---|
| Kimi | 导入 `ai-project-handoff.skill`，或解压到技能目录 `daimon/skills/` |
| Claude.ai / Claude Code | 原生兼容：Capabilities → Skills 上传，或放 `~/.claude/skills/` |
| ChatGPT | 创建自定义 GPT：SKILL.md 正文贴进 Instructions，模板和 format.md 作为 Knowledge |
| Gemini | 创建 Gem：SKILL.md 正文 + 模板贴进指令栏 |
| 任何 AI | 不安装，直接使用交接文件 + 导入指令 |

### 目录结构

```
ai-project-handoff/
├── SKILL.md                        # 核心工作流（导入/导出/提取/抓取）
├── references/
│   ├── format.md                   # PROJECT-HANDOFF v1.0 格式规范
│   └── source-guides.md            # 各平台导出咒语、官方导出说明、抓取要点
├── assets/
│   └── PROJECT-HANDOFF-template.md # 空白交接文件模板
└── scripts/
    ├── validate_handoff.py         # 校验交接文件完整性（stdlib，零依赖）
    └── extract_conversation.py     # 解析官方导出，提取指定对话（stdlib，零依赖）
```

### 交接文件格式速览

YAML frontmatter（项目名、来源 AI、导出时间、语言、`files_mode`）+ 11 个章节：

| # | 章节 | 必需 | 作用 |
|---|---|---|---|
| 1 | 项目概述 | ✅ | 目标、成功标准、范围 |
| 2 | 当前状态 | ✅ | 阶段、完成度、进行中事项 |
| 3 | 关键决策记录 | ✅ | 决策 + 理由 + 放弃的备选 |
| 4 | 技术栈与环境 | ✅ | 语言、框架、版本 |
| 5 | 项目文件索引 | ✅ | 路径/链接 + 作用 + 状态 |
| 6 | 已完成工作 | ✅ | 防止接手 AI 重做 |
| 7 | 待办与下一步 | ✅ | 有序、可独立执行 |
| 8 | 未决问题与风险 | ✅ | 阻塞点、"待确认"项 |
| 9 | 交接指令 | ✅ | 风格、约束、禁忌 |
| 10 | 附录：对话摘录 | 可选 | 关键原文节选 |
| 11 | 项目历程 | 推荐 | 给"人"看的时间线故事 |

### 脚本

**validate_handoff.py** — 校验 frontmatter 必需字段、9 个必需章节、章节非空，退出码 0/1：

```bash
python scripts/validate_handoff.py PROJECT-HANDOFF.md
```

**extract_conversation.py** — 自动识别 ChatGPT / Claude / Gemini Takeout 三种导出格式，列出并提取指定对话为原始 markdown（供提炼，不要直接当交接文件用）。

### 已知局限

- 交接质量依赖源 AI 的执行力——它可能敷衍或编造；校验脚本查结构不查真假，**你的确认才是最后一道关**
- 浏览器自动抓取依赖各家网页结构，易随改版失效，失败时回退到粘贴咒语
- 各平台的导出入口、导出格式会随时间变化，`source-guides.md` 和提取脚本需要跟进维护
- 超长对话（数月）提炼成 200 行必然有信息损失，早期细节可能被源 AI 遗忘

### 设计原则

1. **摘要优先**：交接文件是决策与状态文档，不是聊天记录
2. **不编造历史**：对话里没有的标"待确认"，放进第 8 节
3. **零安装可用**：协议本身不依赖任何一端的安装
4. **人机双读**：第 1-9 节给 AI 恢复上下文，第 11 节给人找回记忆

---

格式版本：PROJECT-HANDOFF v1.0 · 许可：[MIT](LICENSE)
