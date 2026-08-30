from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence

TOML_KV_RE = re.compile(r"^(?P<key>[^=]+?)\s*=\s*(?P<value>.*)$")


def _quote_value(value: str) -> str:
    value = value.strip()
    if not value:
        return '""'
    if value.startswith(("'")) and value.endswith("'"):
        return f'"{value[1:-1]}"'
    if value.startswith(('"', "[", "{")):
        return value
    if value.lower() in {"true", "false"}:
        return value.lower()
    if re.fullmatch(r"-?\d+", value):
        return value
    if re.fullmatch(r"-?\d+\.\d+", value):
        return value
    return f'"{value}"'


def normalize_key_value(line: str, lower_key: bool = False) -> str:
    match = TOML_KV_RE.match(line)
    if not match:
        return line
    key = match.group("key").strip()
    value = _quote_value(match.group("value"))
    if lower_key:
        key = key.lower()
    return f"{key} = {value}"


def _is_key_value_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped and not stripped.startswith(("#", "[")) and "=" in stripped)


def _clean_lines(text: str, *, strip_comments: bool, drop_blank_lines: bool, lower_keys: bool) -> list[str]:
    lines = text.splitlines()
    output = []
    blank_run = 0

    for raw in lines:
        stripped = raw.strip()
        is_blank = stripped == ""
        is_comment = stripped.startswith("#")

        if is_comment and strip_comments:
            continue
        if is_blank and drop_blank_lines:
            blank_run += 1
            if blank_run > 1:
                continue
        blank_run = 0 if not is_blank else blank_run

        if _is_key_value_line(stripped):
            output.append(normalize_key_value(stripped, lower_key=lower_keys))
        else:
            output.append(stripped)

    return output


def _sort_items(items: list[str]) -> list[str]:
    parsed = []
    for line in items:
        match = TOML_KV_RE.match(line)
        if match:
            parsed.append((match.group("key").strip().lower(), line))
        else:
            parsed.append((line.lower(), line))
    return [item[1] for item in sorted(parsed, key=lambda item: item[0])]


def _sort_sections(text: str) -> str:
    lines = text.splitlines()
    result = []
    section_items = []
    top_items = []
    current_heading: str | None = None

    def flush_section() -> None:
        nonlocal section_items
        if section_items:
            result.extend(_sort_items(section_items))
        section_items = []

    def flush_top() -> None:
        nonlocal top_items
        if top_items:
            result.extend(_sort_items(top_items))
        top_items = []

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            flush_top()
            flush_section()
            current_heading = stripped
            result.append(current_heading)
        elif current_heading is not None and _is_key_value_line(stripped):
            section_items.append(stripped)
        else:
            flush_section()
            if current_heading is None and _is_key_value_line(stripped):
                top_items.append(stripped)
            else:
                flush_top()
                current_heading = None
                result.append(stripped)

    flush_section()
    flush_top()
    return "\n".join(result)


def format_toml(text: str, *, sort_keys: bool = False, strip_comments: bool = False, drop_blank_lines: bool = False) -> str:
    lines = _clean_lines(text, strip_comments=strip_comments, drop_blank_lines=drop_blank_lines, lower_keys=sort_keys)
    formatted = "\n".join(lines)
    if formatted:
        formatted += "\n"
    if sort_keys:
        formatted = _sort_sections(formatted)
    if formatted and not formatted.endswith("\n"):
        formatted += "\n"
    return formatted


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize TOML formatting.")
    parser.add_argument("path", nargs="?", default="-", help="TOML file path or '-' for stdin")
    parser.add_argument("--sort-keys", action="store_true", help="lowercase and sort keys")
    parser.add_argument("--strip-comments", action="store_true", help="remove comment lines")
    parser.add_argument("--drop-blank-lines", action="store_true", help="collapse multiple blank lines")
    parser.add_argument("--in-place", action="store_true", help="rewrite the target file")
    parser.add_argument("--check", action="store_true", help="exit 1 if formatting would change")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace | None:
    parser = build_parser()
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return None
        raise


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _write_input(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args is None:
        return 0
    original = _read_input(args.path)
    normalized = format_toml(
        original,
        sort_keys=args.sort_keys,
        strip_comments=args.strip_comments,
        drop_blank_lines=args.drop_blank_lines,
    )
    if args.check:
        return 0 if normalized == original else 1
    if args.in_place and args.path != "-":
        _write_input(args.path, normalized)
        return 0
    sys.stdout.write(normalized)
    return 0
