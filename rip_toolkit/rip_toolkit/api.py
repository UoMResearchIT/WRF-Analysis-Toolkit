# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
from pathlib import Path
import shutil
import shlex
import subprocess
from datetime import datetime
from .utils import (
    get_model_times,
    colors,
    chunks,
    generate_default_file_tag,
    setup_dir_structure,
    check_dir_exists,
    check_image_exists,
    generate_rdp_input,
    generate_run_script,
    merge_xtimes,
    diagnostic_groups,
    generate_point_traj_input,
    generate_tabdiag_format,
    tabdiag_to_csv,
    parse_point_traj_input,
    generate_traj_plot_input,
)


def run_rip_container(
    file_tag: str,
    run_script: str,
    wrfout_dir: str | None = None,
    output_dir: str | None = None,
    ripdp_dir: str | None = None,
    image_path: str | None = None,
    raise_on_error: bool = True,
    load_apptainer_module: bool = False,
    module_init_cmd: str = "source /etc/profile.d/modules.sh",
    module_load_cmd: str = "module load apptainer",
):
    """
    Calls apptainer to run the rip_toolkit commands.
    It bind mounts the output directory, the RIPDP directory, and the wrfout directory.
    Then it runs the run_script inside the container specified by the image.

    Streams output lines that contain 'forecast time=' in real time, to track preprocessing progress.

    Set the environment variable `LOAD_APPTAINER_MODULE=1` or pass `load_apptainer_module=True` to load the apptainer module before running the container (useful for HPC systems).

    Inputs:
    - file_tag (str): A tag to identify the run within the container.
    - run_script (str): Path to the script to be executed inside the container.
    - wrfout_dir (str | None): Path to the directory containing the wrfout files. Can also be set via the environment variable `WRFOUT_DIR`.
    - output_dir (str | None): Directory where the RIPDP directory will be created and populated. Can also be set via the environment variable `OUTPUT_DIR`.
    - ripdp_dir (str | None): Path to the RIPDP directory containing the preprocessing outputs. Can also be extracted from the environment variable `RIPDP_DATA`.
    - image_path (str | None): Path to the apptainer image. Can also be set via the environment variable `IMAGE_PATH`.
    - raise_on_error (bool): If True, raises a RuntimeError if the container exits with a non-zero exit code. If False, returns the exit code.
    - load_apptainer_module (bool): If True, loads the apptainer module before running the container. Can also be set via the environment variable `LOAD_APPTAINER_MODULE=1`.
    - module_init_cmd (str): Command to initialize the module system (default: "source /etc/profile.d/modules.sh").
    - module_load_cmd (str): Command to load the apptainer module (default: "module load apptainer").

    Outputs:
    - int: process exit code.
    """
    if wrfout_dir is None:
        wrfout_dir = os.environ["WRFOUT_DIR"]
    if output_dir is None:
        output_dir = os.environ["OUTPUT_DIR"]
    if ripdp_dir is None:
        ripdp_data = os.environ["RIPDP_DATA"]
        ripdp_dir = str(Path(ripdp_data).parent) if ripdp_data else None
    if image_path is None:
        image_path = os.environ["IMAGE_PATH"]
    print(f"Running RIP container with image {image_path}...")
    check_dir_exists(output_dir)
    check_image_exists(image_path)
    wrfout_dir = Path(wrfout_dir).resolve()
    output_dir = Path(output_dir).resolve()
    ripdp_dir = Path(ripdp_dir).resolve()
    image_path = Path(image_path).resolve()

    apptainer_command = [
        "apptainer",
        "exec",
        "--contain",
        "--cleanenv",
        f"--bind={output_dir}/:/{file_tag}/",
        f"--bind={wrfout_dir}/:/{file_tag}/WRFData/",
        f"--bind={ripdp_dir}/:/{file_tag}/RIPDP/",
        "--pwd",
        f"/{file_tag}",
        f"{image_path}",
        "/bin/bash",
        f"{run_script}",
    ]

    if load_apptainer_module or os.getenv("LOAD_APPTAINER_MODULE", "0") == "1":
        # Build a safe shell command for bash -lc
        apptainer_cmd_str = " ".join(shlex.quote(arg) for arg in apptainer_command)
        shell_cmd = (
            f"{module_init_cmd} >/dev/null 2>&1 || true; "
            f"{module_load_cmd} && {apptainer_cmd_str}"
        )
        popen_cmd = ["bash", "-lc", shell_cmd]
    else:
        popen_cmd = apptainer_command

    print(f"Starting rip container...")
    proc = subprocess.Popen(
        popen_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert proc.stdout is not None
    os.makedirs(os.path.join(output_dir, "Logs"), exist_ok=True)
    run_name = Path(run_script).stem
    logs_path = os.path.join(output_dir, "Logs", f"{file_tag}.combined_out")
    with open(logs_path, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{'='*80}\n{ts} {'-'*10} Started: {run_name} {'-'*10}\n")
        for line in proc.stdout:
            if (
                "forecast time=" in line
            ):  # ripdp preprocessing streams processing time live
                print(line, end="")
            f.write(line)  # everything is written to the logs
        te = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{te} {'-'*10} Completed: {run_name} {'-'*10}\n")
        f.write(f"{'='*80}\n")

    proc.wait()

    if proc.returncode != 0 and raise_on_error:
        msg = (
            "Container failed.\n"
            f"  --  Command  --\n    {' '.join(apptainer_command)}\n"
            f"  -- Exit code --\n    {proc.returncode}\n"
            f"  -- Log file  --\n    {logs_path}\n"
        )
        raise RuntimeError(msg) from None

    return proc.returncode


def preprocess(
    file_tag: str | None = None,
    time_from: float | None = None,
    time_to: float | None = None,
    time_step: float | None = None,
    wrfout_dir: str | None = None,
    output_dir: str | None = None,
    image_path: str | None = None,
    batch_size: int = 50,
):
    """
    This step only needs to be performed once per set of wrf data, and can be reused to compute many trajectories a posteriori.
    It creates the output directory and, inside it, a `RIPDP` directory, where it saves all the preprocessing outputs.

    Inputs:
    - file_tag (str | None): A tag to identify the run of the preprocessing.
    - time_from (float): Start model time for preprocessing, in hours since simulation start (inclusive).
    - time_to (float | None): End model time for preprocessing, in hours since simulation start (inclusive).
    - time_step (float): Requested RIPDP output interval in hours for ptimes. RIPDP can only emit times that exist in the provided WRF history data.
    - wrfout_dir (str | None): Path to the directory containing the wrfout files. Can also be set via the environment variable `WRFOUT_DIR`.
    - output_dir (str | None): Directory where the RIPDP directory will be created and populated. Can also be set via the environment variable `OUTPUT_DIR`.
    - image_path (str | None): Path to apptainer image. Can also be set via the environment variable `IMAGE_PATH`.
    - batch_size (int): The number of wrfout files to process in each batch (progress is saved at the end of each batch).

    *Note: model times can be obtained from the wrfout files using the `get_model_times` function in `rip_toolkit.utils`.

    Outputs:
    - The path to the RIPDP directory containing the preprocessing outputs.
    """
    if wrfout_dir is None:
        wrfout_dir = os.environ["WRFOUT_DIR"]
    if output_dir is None:
        output_dir = os.environ["OUTPUT_DIR"]
    if image_path is None:
        image_path = os.environ["IMAGE_PATH"]
    print(f"Starting preprocessing of {wrfout_dir} data...")
    check_dir_exists(wrfout_dir)
    check_image_exists(image_path)
    if file_tag is None:
        file_tag = generate_default_file_tag(wrfout_dir, time_step)

    mt = get_model_times(wrfout_dir)
    if len(mt) < 2:
        raise ValueError(
            f"Not enough model times found in wrfout_dir ({wrfout_dir}) to perform preprocessing. Found: {mt}"
        )
    if time_from is None:
        time_from = min(mt.keys())
    if time_to is None:
        time_to = max(mt.keys())
    if time_from < min(mt.keys()):
        raise ValueError(
            f"time_from ({time_from}) is less than the minimum model time ({min(mt.keys())})"
        )
    if time_to > max(mt.keys()):
        raise ValueError(
            f"time_to ({time_to}) is greater than the maximum model time ({max(mt.keys())})"
        )
    mt_time_step = sorted(mt.keys())[1] - sorted(mt.keys())[0]

    if time_step is None:
        time_step = mt_time_step
    if time_step < mt_time_step:
        raise ValueError(
            f"time_step ({time_step}) is less than the minimum time step in the model data ({mt_time_step})"
        )

    setup_dir_structure(output_dir)

    rdp_in = generate_rdp_input(
        output_dir,
        file_tag=file_tag,
        time_from=time_from,
        time_to=time_to,
        time_step=time_step,
    )

    all_xtimes = []
    xtimes_file = os.path.join(output_dir, "RIPDP", f"rdp_{file_tag}.xtimes")
    batches = list(chunks(wrfout_dir, batch_size))
    nbatches = len(batches)

    for batch_id, batch in batches:
        print(f"Processing batch {batch_id}/{nbatches} ({len(batch)} wrfout files)...")
        # Command for this chunk only
        rel_files = " ".join(f"WRFData/{name}" for name in batch)
        cmd = f"ripdp_wrfarw -n {rdp_in} {rdp_in} all {rel_files}"
        run_script = generate_run_script(
            output_dir=output_dir,
            script_name=f"run_{Path(rdp_in).name}_{batch_id:03d}.sh",
            commands=[cmd],
        )

        run_rip_container(
            wrfout_dir=wrfout_dir,
            output_dir=output_dir,
            ripdp_dir=os.path.join(output_dir, "RIPDP"),
            file_tag=file_tag,
            image_path=image_path,
            run_script=run_script,
        )

        if os.path.isfile(xtimes_file):
            batch_xtimes = os.path.join(
                output_dir, "RIPDP", f"rdp_{file_tag}.xtimes.batch_{batch_id:03d}"
            )
            shutil.copy2(xtimes_file, batch_xtimes)
            all_xtimes.append(batch_xtimes)
        else:
            raise RuntimeError(f"Missing xtimes after batch {batch_id}: {xtimes_file}")

    # final merged xtimes
    merge_xtimes(all_xtimes)

    if not os.path.isfile(xtimes_file):
        print(
            f"ERROR: Preprocessing container is done, but the expected xtimes file was not found: {xtimes_file}"
        )
    print(f"\nPreprocessing done.")
    with open(xtimes_file, "r") as f:
        xt = f.read().splitlines()
        print(f"Preprocessed a total of {xt[0].replace(' ', '')} times:")
        for line in xt[1:]:
            print(f"  {line}")
    print(f"Outputs saved to: {output_dir}/RIPDP/\n")

    return os.path.join(output_dir, rdp_in)


def point_trajectory(
    traj_tag: str,
    traj_t_0: float,
    traj_t_f: float,
    traj_x: int,
    traj_y: int,
    traj_z: float,
    traj_dt: int = 600,
    file_dt: int | None = None,
    hydrometeor: int = 0,
    traj_diagnostics: dict = diagnostic_groups("base"),
    wrfout_dir: str | None = None,
    output_dir: str | None = None,
    ripdp_data: str | None = None,
    image_path: str | None = None,
):
    """
    Computes a single trajectory using existing RIPDP preprocessed data.

    Inputs:
    - traj_tag (str): A tag to identify the trajectory. It is recommended for it to include trajectory times and release coordinates, e.g. `my_traj_t=0-12_900hPa`.
    - traj_t_0 (float): Particle release time (model time) in hours.
    - traj_t_f (float): Time until which the trajectory will be computed (model time) in hours.
    - traj_x (int): Grid x position from which the particle is released.
    - traj_y (int): Grid y position from which the particle is released.
    - traj_z (float): Pressure level (hPa).
    - traj_dt (int): Trajectory numerical timestep (seconds).
    - file_dt (int): Time interval in RIPDP data (seconds).
    - hydrometeor (int): Set to 0 for Air Parcel trajectories, or 1 for Hydrometeor trajectories.
    - traj_diagnostics (dict): Diagnostics to be computed along trajectory, as returned by `diagnostic_groups(group_name)`.
    - wrfout_dir (str | None): Path to the directory containing wrfout files. Can also be set via the environment variable `WRFOUT_DIR`.
    - output_dir (str | None): Directory where trajectory files will be saved. Can also be set via the environment variable `OUTPUT_DIR`.
    - ripdp_data (str | None): Full path to the RIPDP prefix file (e.g. RIPDP/rdp_test) generated by the preprocess function. Can also be set via the environment variable `RIPDP_DATA`.
    - image_path (str | None): Path to apptainer image. Can also be set via the environment variable `IMAGE_PATH`.

    Outputs:
    - Path to generated trajectory file.
    """
    if wrfout_dir is None:
        wrfout_dir = os.environ["WRFOUT_DIR"]
    if output_dir is None:
        output_dir = os.environ["OUTPUT_DIR"]
    if ripdp_data is None:
        ripdp_data = os.environ["RIPDP_DATA"]
    if image_path is None:
        image_path = os.environ["IMAGE_PATH"]
    check_dir_exists(wrfout_dir)
    check_dir_exists(ripdp_data)
    check_image_exists(image_path)

    print(f"Computing trajectory '{traj_tag}'...")

    setup_dir_structure(output_dir)

    ripdp_data = str(Path(ripdp_data).resolve())
    ripdp_dir = str(Path(ripdp_data).parent)
    rdp_in = f"RIPDP/{Path(ripdp_data).name}"

    if file_dt is None:
        xtimes_file = os.path.join(ripdp_dir, f"{Path(rdp_in).name}.xtimes")
        if not os.path.isfile(xtimes_file):
            raise ValueError(
                "file_dt was not provided and could not be inferred because "
                f"xtimes file does not exist: {xtimes_file}. "
                "Please pass file_dt explicitly in seconds."
            )

        with open(xtimes_file, "r") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

        # ripdp xtimes starts with a count line followed by model times.
        times = []
        for ln in lines[1:]:
            try:
                times.append(float(ln))
            except ValueError:
                continue

        if len(times) < 2:
            raise ValueError(
                "file_dt was not provided and xtimes does not contain enough "
                f"time entries to infer it: {xtimes_file}. "
                "Please pass file_dt explicitly in seconds."
            )

        file_dt = int(round((times[1] - times[0]) * 3600))

    if file_dt <= 0:
        raise ValueError(f"Invalid file_dt: {file_dt}. It must be > 0 seconds.")

    traj_name = f"{traj_tag}_traj_point"
    traj_in = generate_point_traj_input(
        output_dir=output_dir,
        traj_name=traj_name,
        traj_t_0=traj_t_0,
        traj_t_f=traj_t_f,
        traj_dt=traj_dt,
        file_dt=file_dt,
        traj_x=traj_x,
        traj_y=traj_y,
        traj_z=traj_z,
        hydrometeor=hydrometeor,
        traj_diagnostics=traj_diagnostics,
    )
    tabdiag_format = generate_tabdiag_format(
        output_dir=output_dir,
        traj_tag=traj_tag,
        traj_diagnostics=traj_diagnostics,
    )

    commands = [f"rip -f {rdp_in} {traj_in}"]
    if tabdiag_format is not None:
        traj_prefix = os.path.splitext(traj_in)[0]
        commands.extend(
            [
                f"if [ -f '{traj_prefix}.diag' ]; then",
                f"  tabdiag {traj_prefix}.diag {tabdiag_format}",
                "fi",
            ]
        )
    run_script = generate_run_script(
        output_dir=output_dir,
        script_name=f"run_{Path(traj_in).stem}.sh",
        commands=commands,
    )

    run_rip_container(
        wrfout_dir=wrfout_dir,
        output_dir=output_dir,
        ripdp_dir=ripdp_dir,
        file_tag=traj_tag,
        image_path=image_path,
        run_script=run_script,
    )

    traj_file = os.path.join(output_dir, "BTrajectories", traj_name)

    if not os.path.isfile(traj_file + ".traj"):
        print(
            f"ERROR: Plot container run completed but expected output file was not found: {traj_file+".traj"}"
        )
        trajout = f"    {traj_file}.out:\n"
        if os.path.isfile(traj_file + ".out"):
            with open(traj_file + ".out", "r") as f:
                for line in f:
                    trajout += f"     {line}"
                print(trajout)
        raise RuntimeError(f"Trajectory file could not be generated.")

    if traj_diagnostics != {}:
        tabdiag_to_csv(
            traj_file=traj_file,
            tabdiag_file=traj_file + ".tabdiag",
            traj_diagnostics=traj_diagnostics,
        )

    print(f"\nTrajectory computation done.")
    print(f"Outputs saved to: {traj_file}*\n")

    return f"{traj_file}.traj"


def swarm_trajectories(
    traj_tag: str,
    traj_t_0: float,
    traj_t_f: float,
    traj_x: list[int],
    traj_y: list[int],
    traj_z: list[float] = [950, 900, 850, 800, 750, 700, 650, 600, 500, 400, 300, 200],
    traj_dt: int = 600,
    file_dt: int | None = None,
    hydrometeor: int = 0,
    traj_diagnostics: dict = diagnostic_groups("base"),
    colors: list[str] = colors(),
    wrfout_dir: str | None = None,
    output_dir: str | None = None,
    ripdp_data: str | None = None,
    image_path: str | None = None,
):
    """
    Computes the trajectory of a swarm of points.

    All combinations of the provided x, y, z coordinates will be computed.

    Inputs:
    - traj_tag (str): A tag to identify the trajectory.
    - traj_t_0 (float): Particle release time (model time) in hours.
    - traj_t_f (float): Time until which the trajectory will be computed (model time) in hours.
    - traj_x (list[int]): List of grid x positions from which the particles are released.
    - traj_y (list[int]): List of grid y positions from which the particles are released.
    - traj_z (list[float]): List of pressure levels (hPa) from which the particles are released.
    - traj_dt (int): Trajectory numerical timestep (seconds).
    - file_dt (int): Time interval in RIPDP data (seconds).
    - hydrometeor (int): Set to 0 for Air Parcel trajectories, or 1 for Hydrometeor trajectories.
    - traj_diagnostics (dict): Diagnostics to be computed along trajectory, as returned by `diagnostic_groups(group_name)`.
    - colors (list[str]): List of colors to be used for the trajectories. If there are more trajectories than colors, colors will be reused.
    - wrfout_dir (str | None): Path to the directory containing wrfout files. Can also be set via the environment variable `WRFOUT_DIR`.
    - output_dir (str | None): Directory where trajectory files will be saved. Can also be set via the environment variable `OUTPUT_DIR`.
    - ripdp_data (str | None): Full path to the RIPDP prefix file (e.g. RIPDP/rdp_test) generated by the preprocess function. Can also be set via the environment variable `RIPDP_DATA`.
    - image_path (str | None): Path to apptainer image. Can also be set via the environment variable `IMAGE_PATH`.

    Outputs:
    - Dictionary with trajectory tags as keys and colors as values (`{traj_tag: rip_color}`), as required by `plot_trajectories`.
    """
    if wrfout_dir is None:
        wrfout_dir = os.environ["WRFOUT_DIR"]
    if output_dir is None:
        output_dir = os.environ["OUTPUT_DIR"]
    if ripdp_data is None:
        ripdp_data = os.environ["RIPDP_DATA"]
    if image_path is None:
        image_path = os.environ["IMAGE_PATH"]
    i = 0
    tags = {}
    for z in traj_z:
        for y in traj_y:
            for x in traj_x:
                t_tag = f"{traj_tag}_-_{int(x)}_{int(y)}_-_{int(z)}_hPa"
                point_trajectory(
                    wrfout_dir=wrfout_dir,
                    output_dir=output_dir,
                    ripdp_data=ripdp_data,
                    traj_tag=t_tag,
                    traj_x=x,
                    traj_y=y,
                    traj_z=z,
                    traj_t_0=traj_t_0,
                    traj_t_f=traj_t_f,
                    traj_dt=traj_dt,
                    file_dt=file_dt,
                    hydrometeor=hydrometeor,
                    traj_diagnostics=traj_diagnostics,
                    image_path=image_path,
                )
                tags[t_tag] = colors[i % len(colors)]
                i += 1

    print(f"\nSwarm trajectory computation done. {len(tags)} trajectories computed.")

    return tags


def plot_trajectories(
    traj_tags_colors: dict[str, str],
    plot_tag: str,
    format: str = "pdf",
    output_dir: str | None = None,
    ripdp_data: str | None = None,
    image_path: str | None = None,
):
    """
    Generate trajectory plot from the trajectory(ies) specified.

    Inputs:
    - traj_tags_colors (dict[str, str]): A dictionary with trajectory tags as keys and colors as values (`{traj_tag: rip_color}`).
        For each key `traj_tag`, a `BTrajectories/{traj_tag}.traj` or `BTrajectories/{traj_tag}_traj_point.traj` is expected.
    - file_tag (str | None): A tag to identify the plot.
    - output_dir (str | None): Output directory used by the RIP workflow (must contain `BTrajectories` directory). Can also be set via the environment variable `OUTPUT_DIR`.
    - ripdp_data (str | None): Full path to the RIPDP prefix file (e.g. RIPDP/rdp_test) generated by the preprocess function. Can also be set via the environment variable `RIPDP_DATA`.
    - image_path (str | None): Path to apptainer image. Can also be set via the environment variable `IMAGE_PATH`.

    Outputs:
    - Path to generated plot file (`.pdf`).
    """
    if output_dir is None:
        output_dir = os.environ["OUTPUT_DIR"]
    if ripdp_data is None:
        ripdp_data = os.environ["RIPDP_DATA"]
    if image_path is None:
        image_path = os.environ["IMAGE_PATH"]
    print(f"Generating trajectory plot...")
    if not traj_tags_colors:
        raise ValueError(
            "traj_tags_colors must contain at least one traj_tag -> color pair"
        )

    setup_dir_structure(output_dir)

    output_abs = Path(output_dir).resolve()
    rdp_in_abs = Path(ripdp_data).resolve()
    ripdp_dir = rdp_in_abs.parent
    rdp_in_rel = f"RIPDP/{rdp_in_abs.name}"
    btraj_dir = output_abs / "BTrajectories"
    if not btraj_dir.is_dir():
        raise FileNotFoundError(f"BTrajectories directory not found: {btraj_dir}")

    trajectories = []
    for traj_tag, traj_color in traj_tags_colors.items():
        direct = btraj_dir / f"{traj_tag}.traj"
        point = btraj_dir / f"{traj_tag}_traj_point.traj"
        if direct.is_file():
            traj_abs = direct
        elif point.is_file():
            traj_abs = point
        else:
            raise FileNotFoundError(
                "Could not find trajectory file for tag "
                f"'{traj_tag}'. Looked for: {direct.name}, {point.name}"
            )

        traj_in_file = str(traj_abs.with_suffix(".in"))
        parsed = parse_point_traj_input(traj_in_file)

        trajectories.append(
            {
                "traj_file_rel": str(traj_abs.relative_to(output_abs)),
                "traj_t_0": parsed["traj_t_0"],
                "traj_t_f": parsed["traj_t_f"],
                "traj_title": traj_tag,
                "traj_color": traj_color,
            }
        )

    plot_in = generate_traj_plot_input(
        output_dir=output_dir,
        plot_tag=plot_tag,
        trajectories=trajectories,
        min_t0=min(t["traj_t_0"] for t in trajectories),
        format=format,
    )

    run_script = generate_run_script(
        output_dir=output_dir,
        script_name=f"run_{Path(plot_in).stem}.sh",
        commands=[f"rip -f {rdp_in_rel} {plot_in}"],
    )

    run_rip_container(
        wrfout_dir=os.path.join(output_dir, "WRFData"),
        output_dir=output_dir,
        ripdp_dir=str(ripdp_dir),
        file_tag=plot_tag,
        image_path=image_path,
        run_script=run_script,
    )

    plot_file = os.path.join(output_dir, f"{plot_tag}.{format}")
    if not os.path.isfile(plot_file):
        print(
            f"ERROR: Plot container run completed but expected output file was not found: {plot_file}"
        )
        plotout = f"    {plot_file.replace(format, 'out')}:\n"
        if os.path.isfile(plot_file.replace(format, "out")):
            with open(plot_file.replace(format, "out"), "r") as f:
                for line in f:
                    plotout += f"     {line}"
                print(plotout)
        raise RuntimeError(f"Plot file could not be generated.")
    else:
        print(f"\nTrajectory plot done.")
        print(f"Output saved to: {plot_file}\n")

    return plot_file
