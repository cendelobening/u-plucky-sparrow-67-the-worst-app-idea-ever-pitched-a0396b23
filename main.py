#!/usr/bin/env python3
"""Worst App Idea Ever Pitched — entry generator.

Writes a single pitch sentence (at most 240 characters) to
$MAKEFUN_OUTPUT_DIR/entry.txt, exactly one line, no trailing newline.
Pure Python standard library only.
"""

import os
import sys
import tempfile

LINE = (
    "Meet FridgeCourt: an AI app that subpoenas your own fridge, puts your "
    "midnight snacks on trial before a jury of twelve neighbours, and fines "
    "you in crypto for eating leftovers after 11pm."
)

MAX_CHARS = 240


def main():
    line = LINE.strip()

    if not line:
        print("error: pitch is empty", file=sys.stderr)
        return 1
    if "\n" in line or "\r" in line:
        print("error: pitch must be exactly one line", file=sys.stderr)
        return 1
    if len(line) > MAX_CHARS:
        print(
            "error: pitch is %d chars, over the %d limit" % (len(line), MAX_CHARS),
            file=sys.stderr,
        )
        return 1

    data = line.encode("utf-8")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify.
    with open(target, "rb") as f:
        actual = f.read()
    if actual != data:
        print("error: read-back bytes differ from pitch", file=sys.stderr)
        return 1
    if len(line) != len(data.decode("utf-8")):
        print("error: char count mismatch on read-back", file=sys.stderr)
        return 1
    mode = os.stat(target).st_mode & 0o777
    if mode != 0o644:
        print("error: entry.txt mode is %o, expected 0644" % mode, file=sys.stderr)
        return 1

    print("wrote %s (%d chars, %d bytes)" % (target, len(line), len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
