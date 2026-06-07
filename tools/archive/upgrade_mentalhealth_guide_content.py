#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""後方互換ラッパー。新規は upgrade_guide_content.py を使用。"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "upgrade_guide_content.py"
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name="__main__")
