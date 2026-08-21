<!--
SPDX-FileCopyrightText: 2026 University of Manchester

SPDX-License-Identifier: apache-2.0
-->

# RIP Toolkit

This toolkit contains a set of functions to generate trajectories from WRF outputs using RIP.

## Table of contents
- [RIP Toolkit](#rip-toolkit)
  - [Table of contents](#table-of-contents)
  - [Setup](#setup)
  - [Usage](#usage)
    - [As a module](#as-a-module)
    - [As a CLI](#as-a-cli)
    - [Parameters](#parameters)
    - [Notebook Example](#notebook-example)
  - [Conda environment](#conda-environment)

## Setup

This module needs apptainer (or singularity) to be installed on your system, and the `apptainer` command must be available in your path.
You also need to have the container image for rip. The image location is passed to functions as `image_path`.

<details>
<summary>Set up your conda environment to meet the requirements.</summary>

- See [conda environment](#conda-environment) for instructions on how to set up the conda environment.
- Make sure you have installed this package too, so that you can cleanly import the module from your own scripts.

</details>

## Usage
Once installed, this package can be imported as a [module](#as-a-module) in your python code.
The tasks that you will normally want to use are:
 - **preprocess**, which generates ripdp data from the WRF output files.
    - Requires: `wrfout_dir`, `output_dir` and `image_path`.
 - **point_trajectory**, which generates a trajectory for a single point.
   - Requires: `wrfout_dir`, `output_dir`, `ripdp_data` `image_path`, trajectory location (`traj_x`, `traj_y` in grid coordinates), elevation (`traj_z` in hPa) and times (`traj_t_0`, `traj_t_f`).
 - **swarm_trajectories**, which calls `point_trajectory` for multiple points.
   - Requires: the same as `point_trajectory`, but takes arrays for `traj_x`, `traj_y` and `traj_z`.
 - **plot_trajectories**, which generates a plot from the trajectories.
   - Requires: `output_dir`, `ripdp_data`, `image_path`, and `traj_tags_colors`.
 
### As a module
You can import the package and call the main tasks as members of `rip_toolkit`.

For example:

```python
import rip_toolkit as ript

image_path = "/path/to/rip_container.sif"
output_dir = "/path/to/my/output/dir"
wrfout_dir = "/path/to/my/wrfout/dir"

ripdp_data = ript.preprocess(wrfout_dir=wrfout_dir, output_dir=output_dir, image_path=image_path, file_tag="my_run")

ript.point_trajectory(wrfout_dir=wrfout_dir, output_dir=output_dir, image_path=image_path, ripdp_data=ripdp_data, traj_x=20, traj_y=30, traj_z=900, traj_t_0=0, traj_t_f=10, traj_tag="my_trajectory_t=0-10")

my_swarm_trajectories = ript.swarm_trajectories(wrfout_dir=wrfout_dir, output_dir=output_dir, image_path=image_path, ripdp_data=ripdp_data, traj_x=[20, 25], traj_y=[30, 35], traj_z=[900, 850], traj_t_0=0, traj_t_f=10, traj_tag="my_swarm_t=0-10")

ript.plot_trajectories(output_dir=output_dir, ripdp_data=ripdp_data, image_path=image_path, traj_tags_colors={"my_trajectory_t=0-10": "blue", **my_swarm_trajectories})
```

You may access the full documentation of each of these functions by calling, for example:
```
help(ript.point_trajectory)
```

you may also set environment variables for `image_path`, `wrfout_dir`, `output_dir`, and `ripdp_data`, which means you don;t need to pass them as arguments:

```python
import os
import rip_toolkit as ript

os.environ["IMAGE_PATH"] = "/path/to/rip_container.sif"
os.environ["OUTPUT_DIR"] = "/path/to/my/output/dir"
os.environ["WRFOUT_DIR"] = "/path/to/my/wrfout/dir"

ripdp_data = ript.preprocess(file_tag="my_run")

os.environ["RIPDP_DATA"] = ripdp_data

ript.point_trajectory(traj_x=20, traj_y=30, traj_z=900, traj_t_0=0, traj_t_f=10, traj_tag="my_trajectory_t=0-10")

my_swarm_trajectories = ript.swarm_trajectories(traj_x=[20, 25], traj_y=[30, 35], traj_z=[900, 850], traj_t_0=0, traj_t_f=10, traj_tag="my_swarm_t=0-10")

ript.plot_trajectories(traj_tags_colors={"my_trajectory_t=0-10": "blue", **my_swarm_trajectories})
```

### As a CLI

You can also use the package as a command line interface (CLI) tool. The CLI is called `rip_toolkit_cli` and has the same tasks as the module.

Once the package is installed, you can run the CLI from the command line. For example:

```
image_path="/path/to/rip_container.sif"
output_dir="/path/to/my/output/dir"
wrfout_dir="/path/to/my/wrfout/dir"

rip_toolkit_cli --task preprocess --wrfout_dir $wrfout_dir --output_dir $output_dir --tag "cli_sample" --image_path $image_path

ripdp_data=${output_dir}/RIPDP/rdp_cli_sample

rip_toolkit_cli --task point_trajectory --wrfout_dir $wrfout_dir --output_dir $output_dir --ripdp_data $ripdp_data --tag "my_traj_tag" --traj_x 50 --traj_y 30 --traj_z 900 --traj_t_0 0 --traj_t_f 12 --image_path $image_path

rip_toolkit_cli --task swarm_trajectories --wrfout_dir $wrfout_dir --output_dir $output_dir --ripdp_data $ripdp_data --tag "my_swarm_tag" --swarm_x 40,60 --swarm_y 30 --swarm_z 900 --traj_t_0 0 --traj_t_f 12 --image_path $image_path

traj_tags="my_traj_tag,my_swarm_tag_-_40_30_-_900_hPa,my_swarm_tag_-_60_30_-_900_hPa"
traj_cols=magenta,red,dark.green

rip_toolkit_cli --task plot_trajectories --output_dir $output_dir --ripdp_data $ripdp_data --traj_tags $traj_tags --traj_cols blue,$traj_cols --tag "cli_sample_plot" --image_path $image_path
```

you may also set environment variables for `image_path`, `wrfout_dir`, `output_dir`, and `ripdp_data`, which means you don;t need to pass them as arguments. Additionally, you may use short tags for the arguments. For example:

```
export IMAGE_PATH="/path/to/rip_container.sif"
export WRFOUT_DIR="/path/to/my/wrfout/dir"
export OUTPUT_DIR="/path/to/my/output/dir"


rip_toolkit_cli -t preprocess -T "cli_sample"

export RIPDP_DATA=${OUTPUT_DIR}/RIPDP/rdp_cli_sample

rip_toolkit_cli -t point_trajectory -T "my_traj_tag" -x 50 -y 30 -z 900 -t0 0 -tf 12

rip_toolkit_cli -t swarm_trajectories -T "my_swarm_tag" -x 40,60 -y 30 -z 900 -t0 0 -tf 12

traj_tags="my_traj_tag,my_swarm_tag_-_40_30_-_900_hPa,my_swarm_tag_-_60_30_-_900_hPa"
traj_cols=magenta,red,dark.green

rip_toolkit_cli -t plot_trajectories -T "cli_sample_plot" --traj_tags $traj_tags --traj_cols $traj_cols
```

### Parameters
The parameters for each of the tasks are described in each of the functions.

The cli simplifies some inputs so that dictionaries and lists can be passed in as comma-separated strings.
You may call the cli with the `--help` flag to see the flags that are available.

### Notebook Example

See the [notebook example](examples/rip.toolkit.ipynb) for a notebook demonstration of how to use this package.

## Conda environment

The virtual environment for wrf_analysis_toolkit covers all the dependencies for this package, so you may use that environment to run this package.

Finally, install this module in editable mode with
```
pip install -e .
```
You are now set up to use the code.
