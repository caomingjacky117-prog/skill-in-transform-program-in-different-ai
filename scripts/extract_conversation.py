#!/usr/bin/env python3
"""Extract a conversation from an official AI data export into raw markdown,
ready to be distilled into a PROJECT-HANDOFF file.

Supported sources (auto-detected):
  - ChatGPT data export: conversations.json (Settings -> Data Controls -> Export)
  - Claude data export:  conversations.json or conversations.jsonl
  - Gemini Google Takeout: a directory of per-conversation .html files

Usage:
  extract_conversation.py <export-path> --list
  extract_conversation.py <export-path> [--index N | --title TEXT] [-o OUT.md]

Output: raw-conversation markdown (NOT a handoff file). Distill it per
references/format.md afterwards. Stdlib only.
"""
import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


# ---------- loaders: each returns list of {title, created, messages:[(role, text)]} ----------

def load_chatgpt(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    convs = []
    for conv in data:
        mapping = conv.get("mapping") or {}
        msgs = []
        for node in mapping.values():
            msg = node.get("message")
            if not msg:
                continue
            role = (msg.get("author") or {}).get("role", "")
            if role not in ("user", "assistant"):
                continue
            content = msg.get("content") or {}
            parts = content.get("parts") or []
            text = "\n".join(p for p in parts if isinstance(p, str)).strip()
            if text:
                msgs.append((msg.get("create_time") or 0, role, text))
        msgs.sort(key=lambda m: m[0])
        convs.append({
            "title": conv.get("title") or "(untitled)",
            "created": conv.get("create_time"),
            "messages": [(r, t) for _, r, t in msgs],
        })
    return "ChatGPT", convs


def load_claude(path: Path):
    raw = path.read_text(encoding="utf-8").strip()
    if path.suffix == ".jsonl":
        data = [json.loads(line) for line in raw.splitlines() if line.strip()]
    else:
        data = json.loads(raw)
        if isinstance(data, dict):
            data = [data]
    convs = []
    for conv in data:
        msgs = []
        for m in conv.get("chat_messages") or []:
            role = {"human": "user", "assistant": "assistant"}.get(m.get("sender"), m.get("sender", ""))
            text = (m.get("text") or "").strip()
            if not text:
                blocks = m.get("content") or []
                text = "\n".join(b.get("text", "") for b in blocks
                                 if isinstance(b, dict) and b.get("type") == "text").strip()
            if text:
                msgs.append((m.get("created_at") or "", role, text))
        msgs.sort(key=lambda m: m[0])
        convs.append({
            "title": conv.get("name") or "(untitled)",
            "created": conv.get("created_at"),
            "messages": [(r, t) for _, r, t in msgs],
        })
    return "Claude", convs


class _TextHTMLParser(HTMLParser):
    """Collect visible text blocks from Gemini Takeout HTML."""
    SKIP = {"script", "style", "head"}

    def __init__(self):
        super().__init__()
        self.blocks = []
        self._buf = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._depth += 1
        elif tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._depth:
            self._depth -= 1
        elif tag in ("p", "div", "li", "tr", "h1", "h2", "h3"):
            self._flush()

    def handle_data(self, data):
        if not self._depth:
            self._buf.append(data)

    def _flush(self):
        text = "".join(self._buf).strip()
        if text:
            self.blocks.append(text)
        self._buf = []


# Takeout labels vary by locale; extend as needed.
_SPEAKER_RE = re.compile(r"^(You|Gemini|你|你说| Gemini 说)[:：]?\s*(.*)$", re.DOTALL)


def load_gemini(path: Path):
    files = sorted(path.glob("*.html")) if path.is_dir() else [path]
    convs = []
    for f in files:
        parser = _TextHTMLParser()
        parser.feed(f.read_text(encoding="utf-8", errors="replace"))
        parser._flush()
        msgs = []
        role = None
        for block in parser.blocks:
            m = _SPEAKER_RE.match(block)
            if m and ("gemini" in m.group(1).lower() or m.group(1) in ("You", "你", "你说")):
                role = "assistant" if "gemini" in m.group(1).lower() else "user"
                rest = m.group(2).strip()
                if rest:
                    msgs.append((role, rest))
            elif role:
                msgs.append((role, block))
        if msgs:
            convs.append({"title": f.stem, "created": None, "messages": msgs})
    return "Gemini (Takeout)", convs


# ---------- dispatch ----------

def detect_and_load(path: Path):
    if path.is_dir():
        htmls = list(path.glob("**/*.html"))
        if htmls:
            return load_gemini(path)
        raise SystemExit(f"ERROR: 目录中找不到可解析的导出文件: {path}")
    if path.suffix == ".jsonl":
        return load_claude(path)
    if path.suffix == ".html":
        return load_gemini(path)
    if path.suffix == ".json":
        head = path.read_text(encoding="utf-8", errors="replace")[:4096]
        data = json.loads(path.read_text(encoding="utf-8"))
        sample = data[0] if isinstance(data, list) and data else {}
        if "mapping" in sample or "\"mapping\"" in head:
            return load_chatgpt(path)
        if "chat_messages" in sample or "\"chat_messages\"" in head:
            return load_claude(path)
        raise SystemExit("ERROR: 无法识别的 JSON 导出格式（既非 ChatGPT 也非 Claude）")
    raise SystemExit(f"ERROR: 不支持的文件类型: {path.suffix}")


def to_markdown(source: str, conv: dict) -> str:
    # merge consecutive same-role blocks (e.g. Gemini Takeout splits on <br>)
    merged = []
    for role, text in conv["messages"]:
        if merged and merged[-1][0] == role:
            merged[-1][1] += "\n" + text
        else:
            merged.append([role, text])
    lines = [f"# Raw conversation: {conv['title']}",
             f"<!-- source: {source} export | messages: {len(merged)} -->", ""]
    for role, text in merged:
        lines.append(f"**[{role}]**")
        lines.append("")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export_path", type=Path)
    ap.add_argument("--list", action="store_true", help="列出导出中的所有对话")
    ap.add_argument("--index", type=int, help="选择第 N 个对话（--list 显示的序号）")
    ap.add_argument("--title", help="按标题子串选择对话（不区分大小写）")
    ap.add_argument("-o", "--output", type=Path, help="输出 markdown 路径（默认 stdout）")
    args = ap.parse_args()

    if not args.export_path.exists():
        raise SystemExit(f"ERROR: 路径不存在: {args.export_path}")

    source, convs = detect_and_load(args.export_path)
    if not convs:
        raise SystemExit("ERROR: 未解析到任何对话")

    if args.list or (args.index is None and not args.title):
        print(f"来源: {source} | 共 {len(convs)} 个对话\n")
        for i, c in enumerate(convs):
            print(f"[{i}] {c['title']}  ({len(c['messages'])} 条消息)")
        if not args.list:
            print("\n用 --index N 或 --title 关键词 选择一个对话导出")
        return 0

    if args.index is not None:
        if not (0 <= args.index < len(convs)):
            raise SystemExit(f"ERROR: index 超出范围 0..{len(convs) - 1}")
        conv = convs[args.index]
    else:
        needle = args.title.lower()
        hits = [c for c in convs if needle in c["title"].lower()]
        if len(hits) != 1:
            raise SystemExit(f"ERROR: 标题匹配到 {len(hits)} 个对话，请换用 --index 精确指定")
        conv = hits[0]

    md = to_markdown(source, conv)
    if args.output:
        args.output.write_text(md, encoding="utf-8")
        print(f"已写出: {args.output}（{len(conv['messages'])} 条消息）")
        print("下一步：按 references/format.md 将原文提炼为 PROJECT-HANDOFF.md，切勿直接搬运全文")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
