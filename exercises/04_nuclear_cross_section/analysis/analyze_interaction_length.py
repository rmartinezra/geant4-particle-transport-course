#!/usr/bin/env python3
"""Nombre pedagogico canonico; delega en analyze_hadronic.py."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("analyze_hadronic.py")), run_name="__main__")
