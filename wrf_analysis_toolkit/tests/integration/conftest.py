# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
import subprocess
import sys
from pathlib import Path

import pytest
from netCDF4 import Dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_PY = REPO_ROOT / "wrf_analysis_toolkit" / "cli.py"


def has_wrfout_files(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    return any(p.name.startswith("wrfout") for p in path.iterdir() if p.is_file())


def resolve_wrf_control_dir() -> Path | None:
    env_path = os.environ.get("WRF_DATA_PATH")
    candidates: list[Path] = []

    if env_path:
        base = Path(env_path)
        candidates.extend([base / "control", base])

    candidates.extend(
        [
            Path("/wrfdata/control"),
            Path("/wrfdata"),
            Path("/home/ubuntu/SpanishPlume/tests/wrfdata/control"),
        ]
    )

    for candidate in candidates:
        if has_wrfout_files(candidate):
            return candidate
    return None


def resolve_wrf_input_dirs() -> tuple[Path, Path] | None:
    env_path = os.environ.get("WRF_DATA_PATH")
    candidates: list[Path] = []

    if env_path:
        env_base = Path(env_path)
        if env_base.name in {"control", "zero"}:
            candidates.append(env_base.parent)
        else:
            candidates.append(env_base)

    candidates.extend(
        [
            Path("/wrfdata"),
            Path("/home/ubuntu/SpanishPlume/tests/wrfdata"),
        ]
    )

    for base in candidates:
        control = base / "control"
        zero = base / "zero"
        if has_wrfout_files(control) and has_wrfout_files(zero):
            return control, zero

    return None


def count_total_timesteps(wrf_dir: Path) -> int:
    total = 0
    for file in sorted(wrf_dir.glob("wrfout*")):
        with Dataset(file) as ncfile:
            total += ncfile.variables["Times"].shape[0]
    return total


def diagnostic_variables() -> list[str]:
    from wrf_analysis_toolkit import SensibleVariables as sv

    sens_vars = sv.get_sv_names()
    diagnostics = [var for var in sens_vars if not var.startswith("SkewT")]
    diagnostics.append("SkewT")
    return diagnostics


def non_terrain_diagnostic_variables() -> list[str]:
    return [d for d in diagnostic_variables() if not d.startswith("Terrain")]


def terrain_diagnostic_variables() -> list[str]:
    return [d for d in diagnostic_variables() if d.startswith("Terrain")]


def assert_valid_pdf(pdf_file: Path) -> None:
    assert pdf_file.exists(), f"Expected PDF file was not created: {pdf_file}"
    assert pdf_file.stat().st_size > 0, f"PDF file is empty: {pdf_file}"
    with pdf_file.open("rb") as f:
        assert f.read(4) == b"%PDF", f"PDF header is invalid: {pdf_file}"


def assert_valid_mp4(mp4_file: Path) -> None:
    assert mp4_file.exists(), f"Expected MP4 file was not created: {mp4_file}"
    assert mp4_file.stat().st_size > 0, f"MP4 file is empty: {mp4_file}"


@pytest.fixture(scope="session")
def wrf_control_dir() -> Path:
    wrf_dir = resolve_wrf_control_dir()
    if wrf_dir is None:
        pytest.skip(
            "No WRF input data found. Set WRF_DATA_PATH to a directory containing "
            "wrfout files (or a parent directory with a control/ subdirectory)."
        )
    return wrf_dir


@pytest.fixture(scope="session")
def wrf_input_dirs() -> tuple[Path, Path]:
    dirs = resolve_wrf_input_dirs()
    if dirs is None:
        pytest.skip(
            "Could not find both control and zero WRF input directories. Set "
            "WRF_DATA_PATH to a directory containing control/ and zero/ with wrfout files."
        )
    return dirs


@pytest.fixture(scope="session")
def total_timesteps(wrf_control_dir: Path) -> int:
    return count_total_timesteps(wrf_control_dir)


def run_diagnostic(var_name, wrf_dir, out_dir):
    import wrf_analysis_toolkit as wat

    outfile = wat.diagnostic(
        variable_name=var_name,
        wrfout_dir=str(wrf_dir),
        output_dir=str(out_dir),
    )
    assert_valid_mp4(out_dir / f"{outfile}.mp4")


@pytest.fixture()
def prepared_compare_inputs(tmp_path, wrf_input_dirs):
    control_wrf_dir, zero_wrf_dir = wrf_input_dirs
    control_out = tmp_path / "control"
    zero_out = tmp_path / "zero"
    control_out.mkdir(parents=True, exist_ok=True)
    zero_out.mkdir(parents=True, exist_ok=True)

    for var_name in ("DewpointTemp925", "CAPE"):
        run_diagnostic(var_name, control_wrf_dir, control_out)
        run_diagnostic(var_name, zero_wrf_dir, zero_out)

    return control_out, zero_out
