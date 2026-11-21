#!/usr/bin/env python3
"""CHRONOTOAST entrypoint: copy assets/entry.jpg to /output/entry.png.

Deterministic, stdlib-only. Verifies the source image's magic bytes and
size, and that the copy matches byte for byte. Exits non-zero on failure.
"""
import hashlib
import os
import shutil
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.jpg")
OUT_DIR = "/output"
OUT = os.path.join(OUT_DIR, "entry.png")
MAX_BYTES = 1_048_576


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isfile(SRC):
        print(f"missing source image: {SRC}", file=sys.stderr)
        return 1
    with open(SRC, "rb") as f:
        magic = f.read(3)
    if magic != b"\xff\xd8\xff":
        print("source image is not a JPEG", file=sys.stderr)
        return 1
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        print(f"source image too large: {size} > {MAX_BYTES}", file=sys.stderr)
        return 1
    # Clean only the contents of /output, never remove /output itself.
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in os.listdir(OUT_DIR):
        path = os.path.join(OUT_DIR, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
    shutil.copyfile(SRC, OUT)
    if os.path.getsize(OUT) != size or sha256(OUT) != sha256(SRC):
        print("output does not match source", file=sys.stderr)
        return 1
    print(f"wrote {OUT} ({size} bytes, sha256 {sha256(OUT)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
