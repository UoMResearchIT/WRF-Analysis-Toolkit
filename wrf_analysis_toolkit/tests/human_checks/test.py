# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

# This script runs main in a cli and passes the arguments in all_args.
# It is meant to generate sample outputs, for a human to check.
# Run this script with:
# ```
# export WRF_DATA_PATH=/path/to/wrfdata
# python ./test.py
# ```

import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(1, base_dir)
import subprocess
from datetime import datetime

wrfdata = os.getenv("WRF_DATA_PATH", "/wrfdata")
wrfdata = wrfdata[:-1] if wrfdata.endswith("/") else wrfdata
res_path = os.getenv("RESULTS_PATH", f"{base_dir}/tests/human_checks/results")

all_args = [
    f"--task=diagnostic   --var=DewpointTemp925              --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/control/",
    f"--task=diagnostic   --var=DewpointTemp925              --wrfout_dir={wrfdata}/zero/         --output_dir={res_path}/zero/",
    f"--task=diagnostic   --var=CAPE                         --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/control/ --region=-1.55e6,-0.45e6,2.1e6,3.3e6 --save_pdf_frames=1",
    f"--task=diagnostic   --var=CAPE                         --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/zero/  --region=-1550000,-450000,2000000,3300000 --region_ticks=1",
    f"--task=diagnostic   --var=CAPE                         --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/zero/  --region=-3542500,942500,-732500,3642500 --file_tag=_UE_SW+NA",
    f"--task=diagnostic   --var=TerrainElevation1000        --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/ --lat=51.38  --lon=-2.36 --file_tag=_Bath1000",
    f"--task=terrain      --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/ --place=Bath --file_tag=_Bath",
    f"--task=csv          --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/ --place=BristolChannel",
    f"--task=csv          --wrfout_dir={wrfdata}/control/      --output_dir={res_path}/ --place=Bath --csv_vars=CIN,CAPE,AirTemp500,AirTemp300",
    f"--task=wrfdiff   --var=DewpointTemp925  --dirs={wrfdata}/control/,{wrfdata}/zero/ --label_diff=Control-Zero --output_dir={res_path}/ --file_tag=_wrf_diff_control-zero",
    f"--task=mp4diff      --var=DewpointTemp925  --dirs={res_path}/control/,{res_path}/zero/ --labels=control,zero --label_diff=Control-Zero --output_dir={res_path}/ --file_tag=_mp4_diff_control-zero",
    f"--task=mp4diff      --files={res_path}/control/DewpointTemp925.mp4,{res_path}/zero/DewpointTemp925.mp4 --labels=control,zero,Control-Zero --output_dir={res_path}/ --file_tag=_mp4_diff_control-zero_2",
    f"--task=mp4stitch    --files={res_path}/control/DewpointTemp925.mp4,{res_path}/zero/DewpointTemp925.mp4,{res_path}/control/CAPE.mp4,{res_path}/zero/CAPE.mp4 --rows=2 --cols=2 --labels=control,zero,control,zero --output_dir={res_path}/ --file_tag=_mp4_stitch_control-zero",
]


big_div = "\n" + "=" * 80 + "\n"
print(big_div)

tasks = []
for arg in all_args:
    t = arg.split("--task=")[1].split(" ")[0]
    var = arg.split("--var=")[1].split(" ")[0] if "--var=" in arg else ""
    var = var[:30] + "..." if len(var) > 30 else var
    tag = arg.split("--file_tag=")[1].split(" ")[0] if "--file_tag=" in arg else ""
    task = f"{t}_{var}{tag}"
    task = task.replace(",", "-")
    tasks.append(task)
tasks.append("installed_script_call_help")
tasks.append("installed_script_call_diag")

task_status = {d: {"exit": "Not Run", "runtime": "---"} for d in tasks}
print(f"\nTasks:")
for task in tasks:
    print(f"  - {task}")

t0 = datetime.now()

for args, task in zip(all_args, tasks[:-2]):
    output_dir = args.split("--output_dir=")[1]
    if " " in output_dir:
        output_dir = output_dir.split(" ")[0]
    subprocess.run(f"mkdir -p {output_dir}", shell=True)
    ti = datetime.now()
    print(f"\n----- {task} ---------- Started at: {ti}")
    print(f"\npython {base_dir}/wrf_analysis_toolkit/cli.py {args}")
    result = subprocess.run(
        f"python {base_dir}/wrf_analysis_toolkit/cli.py {args}", shell=True
    )
    runtime = datetime.now() - ti
    print(f"\n----- {task} ---------- Finished after: {runtime}")
    task_status[task] = {
        "exit": "OK" if result.returncode == 0 else "ERROR",
        "runtime": runtime,
    }
for args, task in zip(
    [
        " -h",
        f" --task=diagnostic --var=AirTemp2m --wrfout_dir={wrfdata}/control/ --output_dir={res_path}/control/",
    ],
    tasks[-2:],
):
    ti = datetime.now()
    print(f"\n----- {task} ---------- Started at: {ti}")
    print(f"\nwrf_analysis_toolkit_cli {args}")
    result = subprocess.run(f"wrf_analysis_toolkit_cli {args}", shell=True)
    runtime = datetime.now() - ti
    print(f"\n----- {task} ---------- Finished after: {runtime}")
    task_status[task] = {
        "exit": "OK" if result.returncode == 0 else "ERROR",
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
