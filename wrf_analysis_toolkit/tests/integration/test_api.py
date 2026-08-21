# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import shutil
import csv
from pathlib import Path

import pytest
from tests.integration.conftest import (
    assert_valid_mp4,
    assert_valid_pdf,
    non_terrain_diagnostic_variables,
    prepared_compare_inputs,
)

import wrf_analysis_toolkit as wat


class TestDiagnostics:
    # Optional manual curation template.
    # Leave empty to test all available diagnostics discovered from SensibleVariables.
    # Example:
    # EXPECTED_DIAGNOSTICS = ["DewpointTemp925", "CAPE", "SkewT"]
    EXPECTED_DIAGNOSTICS = []

    @classmethod
    def selected_diagnostics(cls):
        diagnostics = non_terrain_diagnostic_variables()
        if not cls.EXPECTED_DIAGNOSTICS:
            return diagnostics

        missing = [d for d in cls.EXPECTED_DIAGNOSTICS if d not in diagnostics]
        assert (
            not missing
        ), "EXPECTED_DIAGNOSTICS contains unknown variables: " + ", ".join(missing)
        return cls.EXPECTED_DIAGNOSTICS

    @classmethod
    def diag_needs_timesteps(cls, diag):
        if "AirTempDif12h" in diag:
            return 13
        if "AirTempDif6h" in diag:
            return 7
        return 1

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "diag", non_terrain_diagnostic_variables(), ids=lambda d: f"{d}"
    )
    def test_diagnostic(
        self, diag: str, tmp_path: Path, wrf_control_dir: Path, total_timesteps: int
    ):
        if diag not in self.selected_diagnostics():
            pytest.skip("Skipping not selected diagnostic: " + diag)
        min_timesteps = self.diag_needs_timesteps(diag)
        if total_timesteps < min_timesteps:
            pytest.skip(
                f"{diag} needs at least {min_timesteps} timesteps; dataset has {total_timesteps}."
            )

        print(f"...", flush=True)
        print(f"    ", end="")

        produced_name = wat.diagnostic(
            variable_name=diag,
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
            save_pdf_frames=True,
        )

        from wrf_analysis_toolkit import SensibleVariables as sv

        outfile_stem = getattr(sv, diag).outfile
        assert produced_name == outfile_stem

        mp4_file = tmp_path / f"{outfile_stem}.mp4"
        assert_valid_mp4(mp4_file)

        pdf_dir = tmp_path / f"__{outfile_stem}"
        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        assert (
            pdf_files
        ), f"No PDF frames generated for {diag}. Expected files in {pdf_dir}."
        assert_valid_pdf(pdf_files[0])

        # Keep resource usage bounded across many parametrized diagnostics.
        mp4_file.unlink(missing_ok=True)
        shutil.rmtree(pdf_dir, ignore_errors=True)

    def test_terrain_diagnostic_redirects(self, wrf_control_dir: Path, tmp_path: Path):
        diag = "TerrainElevation"
        produced_name = wat.diagnostic(
            variable_name=diag,
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
        )

        from wrf_analysis_toolkit import SensibleVariables as sv

        outfile_stem = getattr(sv, diag).outfile
        assert produced_name == outfile_stem

        assert_valid_pdf(tmp_path / f"{outfile_stem}.pdf")

        # Terrain diagnostics should be redirected and not produce mp4/pdf frame dir artifacts.
        assert not (tmp_path / f"{outfile_stem}.mp4").exists()
        assert not (tmp_path / f"__{outfile_stem}").exists()


class TestTerrain:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_terrain(self, tmp_path, wrf_control_dir):
        produced_name = wat.terrain(
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
            region="full",
        )

        assert f"{produced_name}" == "TerrainElevation"
        assert_valid_pdf(tmp_path / f"{produced_name}.pdf")

    def test_terrain_with_point(self, tmp_path, wrf_control_dir):
        produced_name = wat.terrain(
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
            region="-1.55e6,-0.45e6,2.1e6,3.3e6",
            place="Bath",
            file_tag="_Bath",
        )

        assert f"{produced_name}" == "TerrainElevation_Bath"
        assert_valid_pdf(tmp_path / f"{produced_name}.pdf")


class TestCSV:

    def _csv_data_svars(self):
        CSV_DATA_V = ["AirTemp", "DewpointTemp", "RelativeHumidity"]
        CSV_DATA_P = [925, 850, 700, 500, 300]
        CSV_DATA_SVARS = ["CIN", "CAPE"] + [
            f"{var}{height}" for var in CSV_DATA_V for height in CSV_DATA_P
        ]
        return CSV_DATA_SVARS

    def _expected_csv_columns(self):
        CSV_DATA_SVARS = self._csv_data_svars()

        # CSV columns are based on each sensible variable's outfile name.
        return ["Timestamp"] + [
            getattr(wat.SensibleVariables, var_name).outfile
            for var_name in CSV_DATA_SVARS
        ]

    def _assert_valid_csv(self, csv_file: Path, expected_columns: list[str]):
        assert csv_file.exists(), f"Expected CSV file was not created: {csv_file}"
        assert csv_file.stat().st_size > 0, f"CSV file is empty: {csv_file}"

        with csv_file.open("r", newline="") as f:
            metadata = f.readline().strip()
            assert metadata.startswith(
                "# lat:"
            ), f"CSV metadata header is missing/invalid in {csv_file}: {metadata}"

            reader = csv.reader(f)
            header = next(reader)
            assert header == expected_columns, (
                f"CSV columns mismatch in {csv_file}.\n"
                f"Expected: {expected_columns}\n"
                f"Got: {header}"
            )

            first_data_row = next(reader, None)
            assert first_data_row is not None, f"CSV has no data rows: {csv_file}"
            assert len(first_data_row) == len(expected_columns), (
                f"CSV first data row has wrong width in {csv_file}.\n"
                f"Expected {len(expected_columns)} fields, got {len(first_data_row)}"
            )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_csv_task_from_csv_place_shortcut(self, tmp_path, wrf_control_dir):
        produced_name = wat.csv(
            place="BristolChannel",
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
        )
        assert produced_name == "CSV_Data_BristolChannel"

        expected_columns = self._expected_csv_columns()
        self._assert_valid_csv(
            tmp_path / "CSV_Data_BristolChannel.csv", expected_columns
        )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_csv_task_from_explicit_variable_list(self, tmp_path, wrf_control_dir):
        CSV_DATA_SVARS = self._csv_data_svars()
        produced_name = wat.csv(
            variable_names=CSV_DATA_SVARS,
            wrfout_dir=str(wrf_control_dir),
            output_dir=str(tmp_path),
            place="Bath",
        )
        assert produced_name == "CSV_Data_Bath"

        expected_columns = self._expected_csv_columns()
        self._assert_valid_csv(tmp_path / "CSV_Data_Bath.csv", expected_columns)


class TestWRFDiff:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_wrfdiff_generates_diff_mp4(self, tmp_path, wrf_input_dirs):
        control_wrf_dir, zero_wrf_dir = wrf_input_dirs
        out_dir = tmp_path / "wrfcompare"
        out_dir.mkdir(parents=True, exist_ok=True)

        outfile = wat.wrfdiff(
            variable_name="DewpointTemp925",
            wrfout_dir_A=str(control_wrf_dir),
            wrfout_dir_B=str(zero_wrf_dir),
            label_diff="Control-Zero",
            output_dir=str(out_dir),
            file_tag="_wrf_diff_control-zero",
        )
        assert_valid_mp4(out_dir / f"{outfile}.mp4")


class TestMP4Diff:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_mp4diff_generates_diffed_mp4(self, tmp_path, prepared_compare_inputs):
        control_out, zero_out = prepared_compare_inputs
        out_dir = tmp_path / "mp4diff"
        out_dir.mkdir(parents=True, exist_ok=True)

        outfile = wat.mp4diff(
            file_A=str(control_out / "DewpointTemp925.mp4"),
            file_B=str(zero_out / "DewpointTemp925.mp4"),
            label_A="control",
            label_B="zero",
            label_diff="Control-Zero",
            output_dir=str(out_dir),
            file_tag="_control-zero",
        )
        assert_valid_mp4(out_dir / f"{outfile}.mp4")


class TestMP4Stitch:
    @pytest.mark.integration
    @pytest.mark.slow
    def test_mp4stitch_generates_stitched_mp4(self, tmp_path, prepared_compare_inputs):
        control_out, zero_out = prepared_compare_inputs
        out_dir = tmp_path / "mp4stitch"
        out_dir.mkdir(parents=True, exist_ok=True)

        outfile = wat.mp4stitch(
            file_paths=[
                str(control_out / "DewpointTemp925.mp4"),
                str(zero_out / "DewpointTemp925.mp4"),
                str(control_out / "CAPE.mp4"),
                str(zero_out / "CAPE.mp4"),
            ],
            rows=2,
            cols=2,
            labels=["control", "zero", "control", "zero"],
            output_dir=str(out_dir),
            file_tag="_mp4_stitch_control-zero",
        )
        stitched = out_dir / outfile
        assert stitched.name.endswith("_mp4_stitch_control-zero.mp4")
        assert_valid_mp4(stitched)
