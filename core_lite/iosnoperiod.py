#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

SEGMENT_MAP = {"github": ".github", "stegverse": ".stegverse"}

def utc_now() -> str: return datetime.now(timezone.utc).isoformat()

def safe_destination(repo_root: Path, parts: List[str]) -> Path:
    dest = (repo_root / Path(*parts)).resolve()
    root = repo_root.resolve()
    if root != dest and root not in dest.parents:
        raise ValueError(f"destination escapes repo root: {'/'.join(parts)}")
    return dest

def restore_parts(relative_path: Path) -> List[str]:
    restored: List[str] = []
    for index, part in enumerate(relative_path.parts):
        if part.startswith("."): raise ValueError(f"iosnoperiod path contains leading period: {relative_path}")
        if index == 0 and part in SEGMENT_MAP: restored.append(SEGMENT_MAP[part])
        elif part == "gitkeep": restored.append(".gitkeep")
        else: restored.append(part)
    return restored

def restore(repo_root: Path, overwrite: bool) -> Dict[str, object]:
    ios_dir = repo_root / "iosnoperiod"
    restored, skipped = [], []
    if ios_dir.exists():
        for source in sorted(ios_dir.rglob("*")):
            if not source.is_file(): continue
            dest = safe_destination(repo_root, restore_parts(source.relative_to(ios_dir)))
            if dest.exists() and not overwrite:
                skipped.append({"from": source.relative_to(repo_root).as_posix(), "to": dest.relative_to(repo_root).as_posix(), "reason": "destination exists"})
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            restored.append({"from": source.relative_to(repo_root).as_posix(), "to": dest.relative_to(repo_root).as_posix()})
    report = {"schema": "stegverse_iosnoperiod_restore_report.v1", "generated_at": utc_now(), "success": True, "overwrite": overwrite, "restored_count": len(restored), "skipped_count": len(skipped), "restored": restored, "skipped": skipped}
    (repo_root / "iosnoperiod_restore_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    report = restore(Path(args.repo_root).resolve(), args.overwrite)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
