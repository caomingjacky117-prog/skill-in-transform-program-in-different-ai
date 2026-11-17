#!/usr/bin/env python3
"""Validate a PROJECT-HANDOFF markdown file (format v1.0).

Usage: validate_handoff.py <path-to-handoff.md>
Exit 0 = valid; exit 1 = missing required items (details on stdout).
No third-party dependencies.
"""
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = [
    "handoff_version", "project_name", "source_ai",
    "exported_at", "language", "files_mode",
]
FILES_MODES = {"local-paths", "links", "none"}
REQUIRED_SECTIONS = [
    "项目概述", "当前状态", "关键决策记录", "技术栈与环境",
    "项目文件索引", "已完成工作", "待办与下一步", "未决问题与风险", "交接指令",
]


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML-frontmatter reader: flat `key: value` pairs only."""
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    data = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if kv:
            data[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return data


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: file not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    errors, warnings = [], []

    fm = parse_frontmatter(text)
    if not fm:
        errors.append("缺少 YAML frontmatter（文件须以 --- 开头）")
    else:
        for key in REQUIRED_FRONTMATTER:
            if not fm.get(key):
                errors.append(f"frontmatter 缺字段或为空: {key}")
        mode = fm.get("files_mode", "")
        if mode and mode not in FILES_MODES:
            errors.append(f"files_mode 非法: {mode!r}（应为 {sorted(FILES_MODES)} 之一）")
        ver = fm.get("handoff_version", "")
        if ver and ver != "1.0":
            warnings.append(f"handoff_version={ver!r}，本校验器按 v1.0 校验")

    headings = set(re.findall(r"^#{1,3}\s*\d*\.*\s*([^\n#]+?)\s*$", text, re.MULTILINE))
    for sec in REQUIRED_SECTIONS:
        if not any(sec in h for h in headings):
            errors.append(f"缺少必需章节: {sec}")
    if not any("附录" in h for h in headings):
        warnings.append("无附录章节（可选，但长项目建议附关键对话摘录）")

    # Section body non-empty check for required sections
    body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)
    parts = re.split(r"^(#{1,3}\s*[^\n]+)$", body, flags=re.MULTILINE)
    for i in range(1, len(parts) - 1, 2):
        title, content = parts[i], parts[i + 1]
        for sec in REQUIRED_SECTIONS:
            if sec in title:
                stripped = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
                stripped = re.sub(r"[\s|:-]", "", stripped)
                if not stripped:
                    warnings.append(f"章节为空（或只有注释/空表）: {sec}")

    print(f"== PROJECT-HANDOFF 校验: {path.name} ==")
    if fm:
        print(f"项目: {fm.get('project_name', '?')} | 来源: {fm.get('source_ai', '?')} "
              f"| files_mode: {fm.get('files_mode', '?')} | 语言: {fm.get('language', '?')}")
    for w in warnings:
        print(f"WARN : {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\n校验未通过（{len(errors)} 个错误，{len(warnings)} 个警告）")
        return 1
    print(f"\n校验通过（{len(warnings)} 个警告）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
