from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from tomlclean import format_toml, main


EMPTY = ""
BLANK_LINE_INPUT = "\n\n\n"
COMMENT_INPUT = '# comment\nname = "alice"\n'
MULTI_BLANK_INPUT = 'name = "alice"\n\n\n\nage = 30\n'
HEADINGS_INPUT = '[project]\nname = "demo"\n\n[settings]\nverbose = true\n'


def _write_temp(text: str, suffix: str = ".toml") -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w", encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return Path(tmp.name)


@pytest.mark.parametrize(
    "source, expected",
    [
        (EMPTY, ""),
        ("name = 'alice' ", 'name = "alice"\n'),
        ("name =  alice ", 'name = "alice"\n'),
        ("age=30\n", "age = 30\n"),
    ],
)
def test_positive_formatting(source, expected):
    assert format_toml(source) == expected


def test_positive_formatting_sort_keys():
    assert format_toml("NAME = true ", sort_keys=True) == "name = true\n"
    assert format_toml("b = 2\na = 1\n", sort_keys=True) == "a = 1\nb = 2\n"


def test_positive_comments_and_blanks():
    assert format_toml(COMMENT_INPUT) == COMMENT_INPUT
    assert format_toml(MULTI_BLANK_INPUT) == 'name = "alice"\n\n\n\nage = 30\n'


def test_positive_drop_blank_lines():
    assert format_toml("a = 1\n\n\nb = 2\n", drop_blank_lines=True) == "a = 1\n\nb = 2\n"


def test_positive_strip_comments():
    assert format_toml("# hello\na = 1\n", strip_comments=True) == "a = 1\n"


def test_negative_check_detects_changes():
    dirty = _write_temp('b = 2\na = 1\n')
    clean = _write_temp('a = 1\nb = 2\n')
    try:
        assert main(["--sort-keys", "--check", str(dirty)]) == 1
        assert main(["--sort-keys", "--check", str(clean)]) == 0
    finally:
        dirty.unlink()
        clean.unlink()


def test_negative_in_place_returns_zero(tmp_path):
    target = tmp_path / "demo.toml"
    target.write_text("b = 2\na = 1\n", encoding="utf-8")
    assert main(["--sort-keys", "--in-place", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == "a = 1\nb = 2\n"


def test_edge_blank_input():
    assert format_toml(EMPTY) == ""
    assert format_toml("\n\n\n") == "\n\n\n"


def test_edge_mixed_heading_and_pairs():
    expected = '[project]\nname = "demo"\n\n[settings]\nverbose = true\n'
    assert format_toml(HEADINGS_INPUT, sort_keys=True) == expected
