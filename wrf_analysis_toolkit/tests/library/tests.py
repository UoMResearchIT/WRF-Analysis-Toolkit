# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

# This script calls the wrf_analysis_toolkit as a library, which must be previously installed from the base directory with `pip install .`.
# It is meant to replicate tests/human_checks/test.py, so it generate sample outputs, for a human to check.
# Run this script with:
# ```
# export WRF_DATA_PATH=/path/to/wrfdata
# python ./test.py
# ```

import sys
import os

import wrf_analysis_toolkit as wat

from matplotlib.pyplot import get_cmap

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(1, base_dir)
import subprocess
from datetime import datetime

wrfdata = os.getenv("WRF_DATA_PATH", "/wrfdata")
wrfdata = wrfdata[:-1] if wrfdata.endswith("/") else wrfdata
res_path = os.getenv("RESULTS_PATH", f"{base_dir}/tests/library/results")

big_div = "\n" + "=" * 80 + "\n"
print(big_div)

diagnostic_args = [
    {
        "variable_name": "DewpointTemp925",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/control/",
    },
    {
        "variable_name": "DewpointTemp925",
        "wrfout_dir": f"{wrfdata}/zero/",
        "output_dir": f"{res_path}/zero/",
    },
    {
        "variable_name": "CAPE",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/control/",
        "save_pdf_frames": True,
    },
    {
        "variable_name": "CAPE",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/zero/",
    },
    {
        "variable_name": "SkewT",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/control/",
        "place": "Bath",
    },
    {
        "variable_name": "TerrainElevation1000",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "region": "full",
        "lat": 51.38,
        "lon": -2.36,
        "file_tag": "_Bath1000",
    },
    {
        "variable_name": "TerrainElevation",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "region": "full",
        "place": "Bath",
        "range_min": 0,
        "range_max": 1000,
        "file_tag": "_Bath_range_0-1000",
    },
    {
        "variable_name": "AirTemp950",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "sens_var": wat.SensibleVariables.svariable(
            dim=4,
            wrfname="temp",
            ptitle="Temperature at 950 hPa [K]",
            outfile="AirTemp950",
            nticks=12,
            nlevs=23,
            range_min=270,
            range_max=314,
            interpvar="pressure",
            interpvalue=950,
            colormap=get_cmap("Reds"),
        ),
        "range_min": 290,
        "range_max": 310,
    },
    {
        "variable_name": "SeaLevelPressure",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/control/",
        "windbarb_gap": 50,
    },
    {
        "variable_name": "WindSpeed925",
        "wrfout_dir": f"{wrfdata}/arwen/",
        "output_dir": f"{res_path}/",
        "windbarb_gap": 50,
    },
    {
        "variable_name": "PotVorticity925",
        "wrfout_dir": f"{wrfdata}/arwen/",
        "output_dir": f"{res_path}/",
    },
]
terrain_args = [
    {
        "variable_name": "TerrainElevation",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "region_ticks": True,
    },
    {
        "variable_name": "TerrainElevation",
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "place": "Bath",
        "range_min": 0,
        "range_max": 750,
        "file_tag": "_Bath_range_0-750",
        "region": "-1.55e6,-0.45e6,2.1e6,3.3e6",
    },
]
csv_args = [
    {
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "lat": 51.38,
        "lon": -2.36,
    },
    {
        "wrfout_dir": f"{wrfdata}/control/",
        "output_dir": f"{res_path}/",
        "variable_names": ["CIN", "CAPE", "AirTemp500", "AirTemp300"],
        "place": "Bath",
    },
]
mp4diff_args = [
    {
        "file_A": f"{res_path}/control/DewpointTemp925.mp4",
        "file_B": f"{res_path}/zero/DewpointTemp925.mp4",
        "output_dir": f"{res_path}/",
        "label_A": "Control",
        "label_B": "Zero",
        "label_diff": "Control-Zero",
        "file_tag": "_Control-Zero",
    },
]
wrfdiff_args = [
    {
        "wrfout_dir_A": f"{wrfdata}/control/",
        "wrfout_dir_B": f"{wrfdata}/zero/",
        "variable_name": "DewpointTemp925",
        "output_dir": f"{res_path}/",
        "label_diff": "Control-Zero",
        "file_tag": "_Control-Zero",
    },
    {
        "wrfout_dir_A": f"{wrfdata}/control/",
        "wrfout_dir_B": f"{wrfdata}/zero/",
        "variable_name": "AirTemp950",
        "output_dir": f"{res_path}/",
        "sens_var": wat.SensibleVariables.svariable(
            dim=4,
            wrfname="temp",
            ptitle="Temperature at 950 hPa [K]",
            outfile="AirTemp950",
            nticks=12,
            nlevs=23,
            range_min=270,
            range_max=314,
            interpvar="pressure",
            interpvalue=950,
            contour_color="navy",
            colormap=get_cmap("Reds"),
        ),
    },
]
mp4stitch_args = [
    {
        "file_paths": [
            f"{res_path}/control/DewpointTemp925.mp4",
            f"{res_path}/zero/DewpointTemp925.mp4",
            f"{res_path}/control/CAPE.mp4",
            f"{res_path}/zero/CAPE.mp4",
        ],
        "labels": ["control", "zero", "control", "zero"],
        "output_dir": f"{res_path}/",
        "rows": 2,
        "cols": 2,
        "file_tag": "_control-zero",
    },
    {
        "file_paths": [
            f"{res_path}/control/DewpointTemp925.mp4",
            f"{res_path}/zero/DewpointTemp925.mp4",
            f"{res_path}/control/CAPE.mp4",
            f"{res_path}/zero/CAPE.mp4",
        ],
        "output_dir": f"{res_path}/",
        "rows": 3,
        "file_tag": "_control-zero",
    },
]

all_args = (
    diagnostic_args
    + terrain_args
    + csv_args
    + wrfdiff_args
    + mp4diff_args
    + mp4stitch_args
)

tasks = []
for arg in all_args:
    var = arg.get("variable_name")
    if var is None:
        if arg in csv_args:
            var = "CSV"
        elif arg in wrfdiff_args:
            var = "WRFCompare"
        elif arg in mp4diff_args:
            var = "MP4Diff"
        elif arg in mp4stitch_args:
            var = "MP4Stitch"
    var = var[:30] + "..." if len(var) > 30 else var
    tag = arg.get("file_tag", "")
    task = f"{var}{tag}"
    task = task.replace(",", "-")
    if task in tasks:
        task += f"_{len([t for t in tasks if t.startswith(task)])+1}"
    tasks.append(task)

task_status = {task: {"exit": "Not Run", "runtime": "---"} for task in tasks}
print(f"\nTasks:")
for task in tasks:
    print(f"  - {task}")

t0 = datetime.now()

for args, task in zip(all_args, tasks):
    ti = datetime.now()
    print(f"\n----- {task} ---------- Started at: {ti}")
    args_str = ",".join([f"{k}={v}" for k, v in args.items()])
    try:
        if args in diagnostic_args:
            print(f"\nwat.diagnostic({args_str})")
            result = wat.diagnostic(**args)
        elif args in terrain_args:
            print(f"\nwat.terrain({args_str})")
            result = wat.terrain(**args)
        elif args in csv_args:
            print(f"\nwat.csv({args_str})")
            result = wat.csv(**args)
        elif args in wrfdiff_args:
            print(f"\nwat.wrfdiff({args_str})")
            result = wat.wrfdiff(**args)
        elif args in mp4diff_args:
            print(f"\nwat.mp4diff({args_str})")
            result = wat.mp4diff(**args)
        elif args in mp4stitch_args:
            print(f"\nwat.mp4stitch({args_str})")
            result = wat.mp4stitch(**args)
        else:
            raise ValueError(f"Unknown task type for args: {args}")
    except Exception as e:
        print(f"Error occurred while running diagnostic: {e}")
        result = None
    runtime = datetime.now() - ti
    print(f"\n----- {task} ---------- Finished after: {runtime}")
    task_status[task] = {
        "exit": "OK" if result is not None else "ERROR",
        "runtime": runtime,
    }

print(big_div)
print("\n\nDiagnostic generation done. Status summary:")
task_label_width = max(len(task) for task in tasks) + 4
exit_label_width = max(len(status["exit"]) for status in task_status.values()) + 2
for task, status in task_status.items():
    print(
        f"  - {task.ljust(task_label_width)}{status['exit'].ljust(exit_label_width)} finished in   {status['runtime']}"
    )
print(f"\n\n  Total run time: {datetime.now()-t0}")

print(big_div)
