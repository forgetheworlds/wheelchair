"""Restore the exact STEP and GLB exports from lossless .gz files in this repo."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path(__file__).with_name('artifacts_manifest.json')


def restore(output_root: Path) -> None:
    records = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for record in records:
        source = ROOT / record['stored_path']
        target = output_root / record['original_path']
        data = gzip.decompress(source.read_bytes())
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_sha != record['sha256']:
            raise ValueError(f"Checksum mismatch for {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"Restored {target.relative_to(output_root)} ({len(data):,} bytes)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    args = parser.parse_args()
    restore(args.output_root.resolve())
