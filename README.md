# ai-project-handoff

**English** | [中文](#中文)

Move a project from one AI assistant to another — without losing anything and without starting over.

## The Problem

You spent three weeks on Gemini planning a project: decisions were made, dead ends were ruled out, the next step is clear. Now you want to continue in Kimi (or ChatGPT, or Claude) — maybe you hit a usage limit, maybe another model is simply better at the next task.

What are your options today?

| Approach | What actually happens |
|---|---|
| Copy the whole chat | Hundreds of lines of noise; the new AI drowns in it or it doesn't fit the context window |
| Official "memory import" | Moves *who you are* (preferences, facts) — not *where your project is* (decisions, progress, next steps) |
| Browser extensions / memory services | Upload your data to third parties, break when pages change, still dump transcripts rather than state |
| Start over | You re-explain everything, and the new AI re-litigates decisions you already made |

The root cause: **project context lives inside a chat log, and chat logs are locked inside platforms.** Nothing extracts what actually matters.

## How This Skill Solves It

The key insight: **you don't need to move the conversation — you need to move the state.**

A chat log is a *recording* of the journey. What the next AI needs is a *snapshot*: where the project stands, what was decided and why, what's left to do. This skill defines a standardized snapshot — one markdown file called `PROJECT-HANDOFF.md`:

```
┌─────────────────────────────────────────────────────────────┐
│ PROJECT-HANDOFF.md — a decision-and-state document, ~60-200  │
│ lines, readable by any AI and by you:                        │
│                                                              │
│  ① Goal & scope          ⑥ Done (don't redo this)            │
│  ② Current status        ⑦ Next steps (ordered, actionable)  │
│  ③ Key decisions + WHY   ⑧ Open questions & risks            │
│  ④ Stack & environment   ⑨ Rules for the receiving AI        │
│  ⑤ File index            ⑪ Project journey (for YOU,         │
│                            the human — how it got here)      │
└─────────────────────────────────────────────────────────────┘
```

Four design choices make it actually work:

1. **Structured, so nothing important is forgotten.** Fixed sections force the source AI to surface decisions, rationale, and risks — the things that live in its "head" and never make it into a copy-paste.
2. **Zero-install on both ends.** The handoff file plus one paste-ready instruction is fully self-contained. Any AI that can read markdown can receive a project. Installing this skill just adds automation: format validation, journey recap, file checks.
3. **Bidirectional, one format.** The same file format works for export and import between any pair of AIs — no per-platform translators.
4. **Verified by a human checkpoint.** On import, the new AI must first narrate the project journey back to *you* and restate its understanding. Fabricated or drifting content gets caught at this gate — by you, not by blind trust. A validator script checks the structure; you check the truth.

### What it looks like in practice

**Export** — paste one prompt (the "export spell") into the source AI's project chat:

```
我们之后要在另一个 AI 上继续这个项目。请基于我们的全部对话，
生成一份"项目交接文件"，纯 markdown 输出……（完整文本见 references/source-guides.md）
```

It answers with a complete `PROJECT-HANDOFF.md`. Save it. (Have an official data export ZIP instead? `scripts/extract_conversation.py` pulls the right conversation out of ChatGPT/Claude/Gemini-Takeout exports.)

**Import** — drop the file into the new AI with one instruction, and it narrates the journey, confirms understanding, checks your files, then picks up at the next step:

```
Before: "Uh, so I was working on this thing with another AI, let me explain
         from the beginning..." → 30 minutes of re-typing, lost decisions

After:  paste file → AI: "Here's how your project got here… Your next step is
        X. The three files indexed aren't on this machine — how do you want to
        share them? I have 2 questions about the open risks, then I'll start."
```

## Quick Start

1. **On the source AI**: paste the export prompt from `references/source-guides.md` into your project conversation. Save the output as `PROJECT-HANDOFF.md`. Download any generated files (e.g. .xlsx) separately — text can't carry files.
2. **On the target AI**: paste the file + this line:

   > Attached is a PROJECT-HANDOFF file from another AI. Read it fully, then: 1) walk me through the project's journey as a timeline; 2) restate the goal, current status, and next step. After I confirm, continue from the next steps — do not redo completed work.

3. Confirm the recap is accurate, answer the AI's clarifying questions, done.

## Installation (optional, adds automation)

| Platform | Method |
|---|---|
| Kimi | Import `ai-project-handoff.skill`, or unzip into `daimon/skills/` |
| Claude.ai / Claude Code | Natively compatible: Capabilities → Skills → upload, or place in `~/.claude/skills/` |
| ChatGPT | Custom GPT: paste SKILL.md body into Instructions, attach template + format.md as Knowledge |
| Gemini | Create a Gem: paste SKILL.md body + template into the instructions field |
| Any AI | No install — the file + import instruction is enough |

## Repository Layout

```
ai-project-handoff/
├── SKILL.md                        # Core workflows (import / export / extract / auto-fetch)
├── references/
│   ├── format.md                   # PROJECT-HANDOFF v1.0 format spec
│   └── source-guides.md            # Export prompt, per-platform quirks, official exports
├── assets/
│   └── PROJECT-HANDOFF-template.md # Blank handoff template
└── scripts/
    ├── validate_handoff.py         # Structure validator (stdlib, zero deps)
    └── extract_conversation.py     # ChatGPT/Claude/Gemini-Takeout export parser (stdlib, zero deps)
```

```bash
python scripts/validate_handoff.py PROJECT-HANDOFF.md     # exit 0 = valid
python scripts/extract_conversation.py conversations.json --list
python scripts/extract_conversation.py conversations.json --index 3 -o raw.md
```

## Honest Limitations

- **Quality depends on the source AI.** It may be sloppy or fabricate history. The validator checks structure, not truth — that's why the import flow forces a human confirmation checkpoint before any work resumes.
- **Very long conversations lose detail.** A months-long chat distilled to ~200 lines inevitably drops things; early details may already be forgotten by the source AI itself.
- **Browser auto-fetch is fragile** (page structures change) and always falls back to the paste prompt.
- **Platform specifics rot.** Export menus, file formats, and regional restrictions change; `source-guides.md` and the extractor need occasional maintenance.

## Design Principles

1. **Summary over transcript** — move the state, not the recording.
2. **Never invent history** — unknowns are marked "to be confirmed", not guessed.
3. **Zero-install usable** — the protocol works even when neither end has the skill.
4. **For AI and human alike** — sections 1-9 restore context for the AI; the project journey rebuilds memory for you.

---

Format version: PROJECT-HANDOFF v1.0 · License: [MIT](LICENSE)

---

## 中文

把一个项目从一个 AI 搬到另一个 AI——不丢东西，也不从头再来。

### 问题

你在 Gemini 上聊了三周的项目：方案定了、坑排除了、下一步也清楚了。现在你想换到 Kimi（或 ChatGPT、Claude）继续——也许是用量到限了，也许是另一个模型更擅长接下来的活。

今天你能怎么办？

| 办法 | 实际结果 |
|---|---|
| 复制整个对话 | 几百行噪音，新 AI 淹没在里面，或者根本塞不进上下文窗口 |
| 官方"记忆导入" | 搬的是"你是谁"（偏好、事实），不是"你的项目在哪"（决策、进度、下一步） |
| 浏览器扩展 / 记忆服务 | 数据要过第三方服务器，网页一改版就失效，而且搬的还是对话记录不是项目状态 |
| 从头再来 | 重新解释半小时，新 AI 还会把你早就否决的方案再提一遍 |

根源在于：**项目上下文锁在聊天记录里，聊天记录锁在平台里。** 没有东西把真正重要的部分提炼出来。

### 这个 Skill 怎么解决

核心洞察：**你不需要搬"对话"，你需要搬"状态"。**

聊天记录是过程的"录像"，而下一个 AI 需要的是一张"快照"：项目现在到哪了、定了什么、为什么这么定、接下来做什么。这个 skill 把这张快照标准化成一个 markdown 文件——`PROJECT-HANDOFF.md`：

```
┌─────────────────────────────────────────────────────────┐
│ PROJECT-HANDOFF.md —— 决策与状态文档，约 60-200 行，      │
│ 任何 AI 和你自己都能读：                                  │
│                                                          │
│  ① 目标与范围        ⑥ 已完成（防止重做）                  │
│  ② 当前状态          ⑦ 待办下一步（有序、可执行）           │
│  ③ 关键决策+理由     ⑧ 未决问题与风险                      │
│  ④ 技术栈与环境      ⑨ 给接手 AI 的规则                    │
│  ⑤ 文件索引          ⑪ 项目历程（给你看的——                │
│                        它是怎么走到今天的）                │
└─────────────────────────────────────────────────────────┘
```

四个设计选择让它真正管用：

1. **结构化，所以不会漏。** 固定章节逼着源 AI 把决策、理由、风险写出来——这些东西平时只存在于它的"脑子"里，复制对话时根本带不走。
2. **两端零安装。** 交接文件 + 一句现成的导入指令就是全部，任何能读 markdown 的 AI 都能接手项目。安装本 skill 只是多了自动化：格式校验、历程回顾、文件核对。
3. **双向、一种格式。** 同一份文件格式在任意两个 AI 之间导出和导入通用，不需要针对每个平台做翻译器。
4. **人来把最后一道关。** 导入时新 AI 必须先把项目历程讲给**你**听、复述它的理解——编造或跑偏的内容会在这一关被你抓住，而不是靠盲信。校验脚本查结构，你查真伪。

### 实际用起来什么样

**导出**——在源 AI 的项目对话里粘贴一段"导出咒语"：

```
我们之后要在另一个 AI 上继续这个项目。请基于我们的全部对话，
生成一份"项目交接文件"，纯 markdown 输出……（完整文本见 references/source-guides.md）
```

它会输出一份完整的 `PROJECT-HANDOFF.md`，保存即可。（手里是官方数据导出 ZIP？`scripts/extract_conversation.py` 能从 ChatGPT/Claude/Gemini Takeout 导出里提取指定对话。）

**导入**——把文件丢给新 AI 加一句指令，它会讲历程、确认理解、核对文件，然后从下一步直接开工：

```
以前： "呃，我之前在另一个 AI 上做了个东西，我从头给你讲一下……"
       → 重新打字半小时，决策还丢了几个

现在： 粘贴文件 → AI："你的项目是这么走到今天的……下一步是 X。
       索引里的 3 个文件这台机器上没有，你打算怎么给我？
       关于未决风险我有 2 个问题，问完就开工。"
```

### 快速开始

1. **在源 AI 上**：把 `references/source-guides.md` 里的导出咒语粘贴到你的项目对话里，把输出保存为 `PROJECT-HANDOFF.md`。如果生成过文件（如 .xlsx），单独下载——文字带不走文件。
2. **在目标 AI 上**：粘贴文件 + 这句话：

   > 附件是一份 PROJECT-HANDOFF 项目交接文件，来自另一个 AI。请完整阅读，然后：1）用时间线的方式给我讲一遍这个项目的历程；2）用几句话复述你对项目目标、当前状态和下一步的理解。我确认后，从"待办与下一步"继续工作，不要重复已完成的工作。

3. 确认回顾无误，回答 AI 的几个澄清问题，完成。

### 安装（可选，提供自动化）

| 平台 | 方式 |
|---|---|
| Kimi | 导入 `ai-project-handoff.skill`，或解压到技能目录 `daimon/skills/` |
| Claude.ai / Claude Code | 原生兼容：Capabilities → Skills 上传，或放 `~/.claude/skills/` |
| ChatGPT | 创建自定义 GPT：SKILL.md 正文贴进 Instructions，模板和 format.md 作为 Knowledge |
| Gemini | 创建 Gem：SKILL.md 正文 + 模板贴进指令栏 |
| 任何 AI | 不安装，交接文件 + 导入指令就够了 |

### 目录结构

```
ai-project-handoff/
├── SKILL.md                        # 核心工作流（导入/导出/提取/抓取）
├── references/
│   ├── format.md                   # PROJECT-HANDOFF v1.0 格式规范
│   └── source-guides.md            # 导出咒语、各平台注意事项、官方导出说明
├── assets/
│   └── PROJECT-HANDOFF-template.md # 空白交接文件模板
└── scripts/
    ├── validate_handoff.py         # 结构校验（stdlib，零依赖）
    └── extract_conversation.py     # ChatGPT/Claude/Gemini-Takeout 导出解析（stdlib，零依赖）
```

```bash
python scripts/validate_handoff.py PROJECT-HANDOFF.md     # 退出码 0 = 校验通过
python scripts/extract_conversation.py conversations.json --list
python scripts/extract_conversation.py conversations.json --index 3 -o raw.md
```

### 诚实说明局限

- **质量依赖源 AI。** 它可能敷衍，甚至编造历史。校验脚本查结构不查真伪——所以导入流程强制设置了"你来确认"这一关，确认通过才继续干活。
- **超长对话会丢细节。** 几个月的对话压缩到 200 行必然有损失，早期细节可能源 AI 自己都忘了。
- **浏览器自动抓取很脆弱**（网页改版就失效），失败时永远回退到粘贴咒语。
- **平台相关信息会过时。** 导出入口、文件格式、地区限制都在变，`source-guides.md` 和提取脚本需要偶尔维护。

### 设计原则

1. **摘要优先**——搬状态，不搬录像。
2. **不编造历史**——不知道的标"待确认"，不靠猜。
3. **零安装可用**——两端都不装 skill，协议照样工作。
4. **人机双读**——第 1-9 节给 AI 恢复上下文，项目历程给你找回记忆。

---

格式版本：PROJECT-HANDOFF v1.0 · 许可：[MIT](LICENSE)
