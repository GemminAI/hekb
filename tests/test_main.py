"""Coverage for hekb's public entry points: main(), `python -m hekb`, and
the `hekb` console script installed via [project.scripts].
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from hekb import main


def test_main_prints_demo_output(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    captured = capsys.readouterr()
    assert "HEKB Algebraic Core" in captured.out
    assert "EpistemicGraphSnapshot" in captured.out


def test_python_dash_m_hekb_runs_as_a_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hekb"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "HEKB Algebraic Core" in result.stdout
    assert "EpistemicGraphSnapshot" in result.stdout


def test_console_entry_point_runs() -> None:
    """The `hekb` console script installed via [project.scripts]."""
    script = Path(sys.executable).parent / "hekb"
    if not script.exists():
        pytest.skip(f"console script not found at {script} (package not installed?)")

    result = subprocess.run(
        [str(script)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "HEKB Algebraic Core" in result.stdout
    assert "EpistemicGraphSnapshot" in result.stdout
