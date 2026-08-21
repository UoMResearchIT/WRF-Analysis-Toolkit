# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wrf_analysis_toolkit.cli", *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
    )


@pytest.mark.integration
def test_cli_help() -> None:
    result = _run_cli(["-h"])
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "--task" in result.stdout


@pytest.mark.integration
@pytest.mark.slow
def test_cli_csv_task(tmp_path: Path, wrf_control_dir: Path) -> None:
    result = _run_cli(
        [
            "--task=csv",
            f"--wrfout_dir={wrf_control_dir}",
            f"--output_dir={tmp_path}",
            "--place=Bath",
            "--region=full",
        ]
    )

    assert result.returncode == 0, (
        "CLI csv task failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    csv_file = tmp_path / "CSV_Data_Bath.csv"
    assert csv_file.exists(), f"Expected CSV file was not created: {csv_file}"
    assert csv_file.stat().st_size > 0, f"CSV file is empty: {csv_file}"
