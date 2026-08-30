# Usage

## Input sources

`tomlclean` accepts a file path or stdin. If no path is given, or if the path is `-`, the tool reads from stdin.

## Output sources

By default, formatted text goes to stdout. Use `--in-place` to rewrite the source file.

## Checking without rewriting

Use `--check` in editors or CI. The exit code is `0` when no formatting changes are needed, and `1` when the input would change.

```bash
tomlclean --check pyproject.toml
```

## Key sorting

Key sorting lowercases keys and sorts them alphabetically within sections. It does not rewrite comments or non-KV lines.

```bash
tomlclean --sort-keys pyproject.toml
```

## Blank line handling

Blank-line collapsing removes only *consecutive* blank lines, leaving one separator where present.

## Comment stripping

Comments are stripped after line trimming. Inline comments after values are left in place because they are part of the value text.
