# PROJECT-HANDOFF Format Spec (v1.0)

A single markdown file carrying everything a receiving AI needs to continue a project. Required: frontmatter + sections 1–9. Optional: section 10 appendix.

## Frontmatter

| Field | Required | Values / notes |
|---|---|---|
| `handoff_version` | yes | `"1.0"` |
| `project_name` | yes | short human name |
| `source_ai` | yes | e.g. `Gemini`, `ChatGPT`, `Claude`, `Kimi`; add model if known |
| `exported_at` | yes | ISO 8601 with timezone |
| `language` | yes | working language of the project, e.g. `zh`, `en` |
| `files_mode` | yes | `local-paths` \| `links` \| `none` |
| `repo` | no | main repository URL if any |
| `conversation_ref` | no | provenance of the source material, e.g. `ChatGPT export 2026-11-10, conv "记账小助手开发"` — helps later re-extraction |

## Sections

1. **项目概述 (Goal)** — what the project is, success criteria, scope/non-scope. ≤10 lines.
2. **当前状态 (Status)** — current phase, rough % done, what is mid-flight right now.
3. **关键决策记录 (Decisions)** — numbered list: decision + rationale + rejected alternatives. This is the highest-value section; never leave it empty if any choice was made.
4. **技术栈与环境 (Stack & Environment)** — languages, frameworks, versions, OS, credentials locations (never secrets themselves).
5. **项目文件索引 (Files)** — table: path/URL | role | state (complete/WIP/stale). Honor `files_mode`.
6. **已完成工作 (Done)** — bullet list of finished milestones, so the receiving AI never redoes them.
7. **待办与下一步 (Next steps)** — ordered, actionable, each with enough context to execute alone. First item = immediate next action.
8. **未决问题与风险 (Open questions & risks)** — blockers, unknowns, items marked 待确认.
9. **交接指令 (Instructions to the receiving AI)** — tone, conventions, constraints, what NOT to change, how the user likes to work.
10. **附录：对话摘录 (Appendix, optional)** — verbatim excerpts of key exchanges; distill, don't dump the whole log.
11. **项目历程 (Journey, optional but recommended)** — chronological narrative of how the project got here: origin → phases/milestones (with rough dates) → turning points where direction changed → how the current state came to be. Sections 2/6 answer *where the project is*; this section answers *how it got here*, so the user (not just the receiving AI) can re-familiarize themselves after the switch. Write it as a readable timeline, not a task list. If the source conversation lacks this detail, mark gaps as 待确认 rather than inventing history.

## Authoring rules

- Target length: 60–200 lines. Long enough to resume, short enough to fit any context window.
- Every claim must trace to the actual conversation or files; uncertain → put in §8, not stated as fact.
- Paths must be absolute or repo-relative; links must be full URLs.
- Write in the project's working language (`language` field), section headers stay as defined above.
