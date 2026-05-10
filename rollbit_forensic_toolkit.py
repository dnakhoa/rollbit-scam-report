#!/usr/bin/env python3
"""
Compatibility wrapper for the superseded monolithic toolkit.

The repository now uses modular, evidence-first scripts under `scripts/`.
This file is kept only so old commands fail with a clear migration path instead
of regenerating stale narrative artifacts.
"""

from __future__ import annotations

import sys


MESSAGE = """\
rollbit_forensic_toolkit.py has been superseded.

Use the current evidence-first workflow instead:

  python3 scripts/build_case_corpus.py
  python3 scripts/run_investigation.py --quick
  python3 scripts/technical_deep_dive.py
  python3 scripts/web_surface_capture.py
  python3 scripts/public_record_capture.py

Current reports separate observed facts, reported claims, analytical limits,
and next collection steps. The old monolithic toolkit is intentionally disabled
so it cannot regenerate stale argumentative artifacts.
"""


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
