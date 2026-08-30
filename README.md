# tomlclean

<p align="left">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/status-stable-green" alt="Status" />
</p>

`tomlclean` is a tiny CLI that normalizes TOML formatting without changing values or structure. It removes trailing whitespace, normalizes spacing around `=`, quotes bare values, and can sort keys, drop blank lines, or strip comments. The goal is cleaner diffs and consistent formatting for checked-in TOML files.

## About

TOML files in real repos accumulate small inconsistencies: extra spaces around assignments, unquoted bare values, trailing whitespace, and irregular blank lines. `tomlclean` rewrites them to a consistent, readable form.

It focuses on formatting, not linting. Semantic errors remain the job of `tomltoml`, `taplo`, or TOML parsers.

## Features

- Normalize `=` spacing and trailing whitespace
- Quote bare unquoted values
- Sort keys within sections with `--sort-keys`
- Strip comment lines with `--strip-comments`
- Collapse consecutive blank lines with `--drop-blank-lines`
- `--check` mode for CI/editors
- `--in-place` file rewrites
- Zero external dependencies

## Installation

```bash
python -m pip install tomlclean
```

Or clone the repo and use it directly:

```bash
python -m pip install -e .
```

## Usage

```bash
tomlclean [path]
```

If `path` is omitted, `tomlclean` reads from stdin. Pass `-` explicitly to force stdin.

### Flags

| Flag | Description |
| --- | --- |
| `--sort-keys` | Normalize keys and sort them alphabetically |
| `--strip-comments` | Remove lines starting with `#` |
| `--drop-blank-lines` | Collapse runs of blank lines to a single blank line |
| `--in-place` | Rewrite the target file instead of stdout |
| `--check` | Exit 1 if formatting would change the input |

### Examples

```bash
# Format and print
tomlclean pyproject.toml

# Check without changing
tomlclean --check pyproject.toml

# Sort keys and rewrite the file
tomlclean --sort-keys --in-place pyproject.toml

# Strip comments from stdin
echo '# a comment\nname = "demo"' | tomlclean --strip-comments -
```

## Project structure

```
tomlclean/
  pyproject.toml
  tomlclean.py
  tests/
    test_tomlclean.py
  docs/
    usage.md
```

## Tags / keywords

`toml`, `formatter`, `cleaner`, `cli`, `python`, `open-source`
