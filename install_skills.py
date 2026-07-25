#!/usr/bin/env python3
"""Install SDD boost skills into the layout Claude Code actually discovers.

Claude Code loads personal skills from ~/.claude/skills/<skill-name>/SKILL.md
with YAML frontmatter. Flat .yaml files are never discovered, so every source
skill is rewritten into that layout.

Usage:
  python3 install_skills.py          # dry-run
  python3 install_skills.py --apply  # write to ~/.claude/skills/
"""
from __future__ import annotations

import os
import re
import sys
import textwrap
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "skills"
DEST = Path.home() / ".claude" / "skills"
DRY = "--apply" not in sys.argv

DROP = {"version", "created", "updated", "objectId", "metadata", "type"}
DESC_CAP = 1400

MANUAL_DESC = {
    "java-record-breaking-changes": (
        "Managing Java record constructor breaking changes. Strategies for adding "
        "fields to records without breaking existing callers, including the Builder "
        "pattern migration path. Use when adding fields to an existing Java record "
        "or fixing compilation errors after a record change."
    ),
}


def flow(text: str) -> str:
    s = " ".join(str(text).split())
    if len(s) > DESC_CAP:
        s = s[:DESC_CAP].rsplit(" ", 1)[0] + " ..."
    return s


def split_frontmatter(raw: str):
    if not raw.startswith("---"):
        return None
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.DOTALL)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(fm, dict):
        return None
    return fm, m.group(2)


def emit(name: str, fm: dict, body: str) -> str:
    fm_out = {"name": name, "description": flow(fm["description"])}
    for k, v in fm.items():
        if k in ("name", "description") or k in DROP:
            continue
        fm_out[k] = v
    dumped = yaml.dump(
        fm_out,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=4096,
    ).strip()
    return f"---\n{dumped}\n---\n\n{body.strip()}\n"


def convert(path: Path, name: str):
    raw = path.read_text(encoding="utf-8")

    fmsplit = split_frontmatter(raw)
    if fmsplit and "description" in fmsplit[0]:
        fm, body = fmsplit
        return "A", emit(name, fm, body)

    try:
        data = yaml.safe_load(raw)
        parsed = isinstance(data, dict)
    except yaml.YAMLError:
        parsed = False

    if parsed:
        if "description" not in data:
            raise ValueError("parsed YAML has no description")
        parts = []
        instructions = data.get("instructions")
        if instructions:
            parts.append(textwrap.dedent(str(instructions)).strip())
        extra = {
            k: v
            for k, v in data.items()
            if k not in ("name", "description", "instructions") and k not in DROP
        }
        if extra:
            dumped = yaml.dump(
                extra,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
                width=100,
            ).strip()
            heading = "## Reference" if instructions else f"# {name}"
            parts.append(f"{heading}\n\n```yaml\n{dumped}\n```")
        if not parts:
            parts.append(f"# {name}\n\n{data['description']}")
        return "B", emit(name, {"description": data["description"]}, "\n\n".join(parts))

    dm = re.search(r"^description:[ \t]*(.+)$", raw, re.MULTILINE)
    if dm:
        desc = dm.group(1).strip().strip('"').strip("'")
        body = (
            f"# {name}\n\n{desc}\n\n"
            "The full skill definition follows, preserved verbatim from the "
            "source package.\n\n"
            f"```yaml\n{raw.strip()}\n```"
        )
        return "C", emit(name, {"description": desc}, body)

    if name in MANUAL_DESC:
        return "D", emit(name, {"description": MANUAL_DESC[name]}, raw)

    raise ValueError("no description found and no manual fallback")


def main() -> int:
    if not SRC.is_dir():
        print(f"Skills directory not found: {SRC}", file=sys.stderr)
        return 1

    jobs = [
        (SRC / f, Path(f).stem)
        for f in sorted(os.listdir(SRC))
        if f.endswith(".yaml")
    ]
    nav = SRC / "sdd-navigator" / "SKILL.md"
    if nav.exists():
        jobs.append((nav, "sdd-navigator"))

    ok, failed = [], []
    for path, name in jobs:
        try:
            cls, content = convert(path, name)
        except Exception as exc:  # noqa: BLE001
            failed.append((name, repr(exc)))
            continue
        rt = split_frontmatter(content)
        if not rt or rt[0].get("name") != name or not rt[0].get("description"):
            failed.append((name, "emitted file failed frontmatter round-trip"))
            continue
        ok.append((name, cls, len(content), len(rt[0]["description"])))
        if not DRY:
            dest_dir = DEST / name
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "SKILL.md").write_text(content, encoding="utf-8")

    print(f"{'DRY RUN' if DRY else 'APPLIED'}: {len(ok)} ok, {len(failed)} failed")
    print(f"Destination: {DEST}\n")
    for name, cls, size, dlen in sorted(ok):
        print(f"  [{cls}] {name:38s} {size:6d}B  desc={dlen}")
    for name, err in failed:
        print(f"  FAIL {name}: {err}")
    print()
    print("by class:", dict(Counter(c for _, c, _, _ in ok)))
    if DRY:
        print("\nRe-run with --apply to write files.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
