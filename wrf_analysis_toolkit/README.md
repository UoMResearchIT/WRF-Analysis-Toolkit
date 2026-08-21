<!--
SPDX-FileCopyrightText: 2026 University of Manchester

SPDX-License-Identifier: apache-2.0
-->

# WRF Analysis Toolkit

This repo contains a set of scripts to generate diagnostics from WRF outputs, and to compare them with other WRF outputs.

## Table of contents
- [WRF Analysis Toolkit](#wrf-analysis-toolkit)
  - [Table of contents](#table-of-contents)
  - [Setup](#setup)
  - [Usage](#usage)
    - [As a module](#as-a-module)
    - [As a CLI](#as-a-cli)
    - [Parameters](#parameters)
      - [Module only](#module-only)
      - [CLI only](#cli-only)
    - [Variables](#variables)
    - [Plotting Regions](#plotting-regions)
    - [Locations](#locations)
  - [About the source code](#about-the-source-code)
    - [Animate](#animate)
    - [Plot2DField](#plot2dfield)
    - [SensibleVariables](#sensiblevariables)
    - [GetSensVar](#getsensvar)
    - [Special diagnostics](#special-diagnostics)
      - [TerrainPlots](#terrainplots)
      - [Frontogenesis](#frontogenesis)
      - [SkewT](#skewt)
    - [Direct comparison of outputs](#direct-comparison-of-outputs)
      - [ConcatNDiff](#concatndiff)
      - [ConcatNxM](#concatnxm)
      - [WRFSmoothDiff](#wrfsmoothdiff)
  - [Tests](#tests)
  - [Conda environment](#conda-environment)

## Setup

<details>
<summary>Set up your conda environment to meet the requirements.</summary>

- See [conda environment](#conda-environment) for instructions on how to set up the conda environment.
- Make sure you have installed this package too, so that you can call the cli script from anywhere and cleanly import the modules from your own scripts.

</details>

## Usage
Once installed, this package can be imported as a [module](#as-a-module) in your python code, or called directly as as a [cli](#as-a-cli).
The tasks that you will normally want to use are:
 - **diagnostic**, which generates animated plots of a given variable.
    - Requires: `wrfout_dir`, `variable_name`, and `output_dir`.
 - **terrain**, which generates a terrain elevation plot.
   - Requires: `wrfout_dir`, and `output_dir`.
 - **csv**, which generates a csv file with the values of the given variables at a given location.
   - Requires: `wrfout_dir`, `output_dir`, and either `place` or both `lat` and `lon`.
 - **wrfdiff**, which generates a diagnostic of the difference of two WRF output files.
   - Requires: `wrfout_dir_A`, `wrfout_dir_B`, `variable_name`, and `output_dir`.
 - **mp4diff**, which generates a video of the pixel difference of two mp4 files.
   - Requires: `file_A`, `file_B`, and `output_dir`.
 - **mp4stitch**, which generates a video that stitches together a set of mp4 files in a grid.
   - Requires: `file_paths` and `output_dir`.

### As a module
You can import the package and call the main tasks as members of `wrf_analysis_toolkit`.

For example:

```python
import wrf_analysis_toolkit as wat

wat.diagnostic(variable_name="AirTemp2m", wrfout_dir="/my/data/", output_dir="/my/results/")
wat.terrain(wrfout_dir="/my/data/", output_dir="/my/results/")
wat.csv(variable_names=["AirTemp2m", "CAPE"], wrfout_dir="/my/data/", output_dir="/my/results/", lat=40.0, lon=-105.0)
wat.wrfdiff(variable_name="AirTemp2m", wrfout_dir_A="/my/data1/", wrfout_dir_B="/my/data2/", output_dir="/my/results/")
wat.mp4diff(file_A="/my/data1/diagnostic.mp4", file_B="/my/data2/diagnostic.mp4", output_dir="/my/results/")
wat.mp4stitch(file_paths=["/my/data1/diagnostic.mp4", "/my/data2/diagnostic.mp4"], output_dir="/my/results/", rows=1, cols=2)
```

You may access the full documentation of each of these functions by calling, for example:
```
help(wat.diagnostic)
```

### As a CLI
When being used as a cli, you *always* have to pass arguments as `--key=value` pairs, and a **task** key is always needed. This can be any of the listed above.

Example calls for this function are (to be run within the active conda environment):
```
wrf_analysis_toolkit_cli --task=diagnostic --var=AirTemp2m --wrfout_dir=/my/data/ --output_dir=/my/results/
wrf_analysis_toolkit_cli --task=diagnostic --var=WindSpeed --vcross=1 --wrfout_dir=/my/data/ --output_dir=/my/results/--start_latlon=55,-2.0 --end_latlon=50.0,2.0
wrf_analysis_toolkit_cli --task=terrain --var=TerrainElevation --wrfout_dir=/my/data/ --output_dir=/my/results/
wrf_analysis_toolkit_cli --task=csv --csv_vars=AirTemp2m,CAPE --wrfout_dir=/my/data/ --output_dir=/my/results/ --lat=40.0 --lon=-105.0
wrf_analysis_toolkit_cli --task=wrfdiff --var=AirTemp2m --dirs=/my/data1/,/my/data2/ --output_dir=/my/results/
wrf_analysis_toolkit_cli --task=mp4diff --files=/my/data1/diagnostic.mp4,/my/data2/diagnostic.mp4 --output_dir=/my/results/
wrf_analysis_toolkit_cli --task=mp4stitch --files=/my/data1/diagnostic.mp4,/my/data2/diagnostic.mp4 --output_dir=/my/results/ --rows=1 --cols=2
```

You may access the full cli documentation with the -h flag:
```
wrf_analysis_toolkit_cli -h
```

### Parameters
The parameters for each of the tasks are described in each of the functions.
This is a (hopefully) complete list of the parameters that can be passed, but not all of them are needed for each task:
- `output_dir`: Directory where the output file(s) will be saved.
- `wrfout_dir`: Directory containing WRF output files.
- `variable_name`: Name of the variable to analyze (see the list of available [variables](#variables)).
- `file_tag`: String to append to the output filename.
- `time_from`: Only use wrfout files from this time onward (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS".
- `time_to`: Only use wrfout files up to this time (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS".
- `range_min`: Minimum value for the variable range .
- `range_max`: Maximum value for the variable range .
- `windbarbs`: Boolean indicating whether to include wind barbs in the plots.
- `windbarb_gap`: Number of grid points between wind barbs (default is 25).
- `place`: Predefined location name (see the list of available [locations](#locations)).
- `lat`: Latitude for the variable. If provided, `lon` must also be provided.
- `lon`: Longitude for the variable. If provided, `lat` must also be provided.
- `trajectory`: Path to a trajectory file for SkewT plots animated along a trajectory.
- `region`: Area covered by the plots, set by a comma-separated string of projected bounding box coordinates as "min_x,max_x,min_y,max_y".
    (default is "full", which uses all the area covered by the wrf data). See [plotting regions](#plotting-regions) for details.
- `smooth`: Boolean indicating whether to apply smoothing to the plots (default is False).
- `clean_png_frames`: Boolean indicating whether to delete intermediate PNG frames after creating the animation (default is True).
- `save_pdf_frames`: Boolean indicating whether to save each frame as a PDF (default is False).
- `make_mp4`: Boolean indicating whether to combine PNG frames in to an MP4 file (default is True).
- `output_format`: (`terrain` task only) Format of the output file (default is "pdf"; can be "png").
- `variable_names`: (`csv` task only) List of variable names to include in the CSV file.
- `wrfout_dir_A`: (`wrfdiff` task only) Full path to the first WRF output directory.
- `wrfout_dir_B`: (`wrfdiff` task only) Full path to the second WRF output directory.
- `colormap`: (`wrfdiff` task only) Colormap to use for the plots.
- `label_diff`: (`wrfdiff` and `mp4diff` tasks only) Label to be added at the top left corner of the resulting diagnostic.
- `file_A`: (`mp4diff` task only) Full path to the first mp4 file.
- `file_B`: (`mp4diff` task only) Full path to the second mp4 file.
- `label_A`: (`mp4diff` task only) Label to be added at the top left corner of video A in the output.
- `label_B`: (`mp4diff` task only) Label to be added at the top left corner of video B in the output.
- `file_paths`: (`mp4stitch` task only) List of full paths to the mp4 files to be stitched together.
- `labels`: (`mp4stitch` task only) List of labels to be added at the top left corner of each video in the output.
- `rows`: (`mp4stitch` task only) Number of rows in the output video (defaults to 1).
- `cols`: (`mp4stitch` task only) Number of columns in the output video (will increase to fit all files, if necessary).

#### Module only
When used as a library, a full `svariable` object can be passed to the `diagnostic` and `wrfdiff` tasks, instead of a named variable from the available list. This allows for more control over the plotting of the variable, including the color scale, units, title, range, type of plot, annotations (like wind-barbs or contour-lines), and potentially overlapping variables. If it is something that you find yourself using a lot, please consider adding it to the list of [variables](#variables) in the code.

- `sens_var`: (`diagnostic` and `wrfdiff` tasks only) This must be an `svariable` object and it is recommended that it is only used if existing [variables](#variables) cannot be used.

#### CLI only
On top of the parameters listed above, the CLI has a few additional parameters or synonyms that are only used for the CLI interface:
- `task`: (required) The task to be performed.
- `var`: synonym of `variable_name`, for the cli.
- `csv_vars`: synonym of `variable_names`, for the cli.
- `clean`: synonym of `clean_png_frames`, for the cli.
- `files`: Comma-separated list of files. Synonym of `file_paths`, for the cli, and replaces `file_A` and `file_B` for the `mp4diff` task.
- `dirs`: Comma-separated list of directories. Replaces of `wrfout_dir_A` and `wrfout_dir_B`, for the cli.
- `labels`: Comma-separated list of labels. Replaces of `label_A` and `label_B`, for the cli. May include `label_diff` as the third label for the `mp4diff` task.
- `traj`: synonym of `trajectory`, for the cli.

### Variables

This is a list of the variables that are currently defined in the code, and can be used as `variable_name` parameters.

- AbsoluteVorticity
- AbsoluteVorticity300
- AbsoluteVorticity500
- AbsoluteVorticity700
- AbsoluteVorticity850
- AbsoluteVorticity925
- AirTemp
- AirTemp2m
- AirTemp300
- AirTemp500
- AirTemp700
- AirTemp850
- AirTemp925
- AirTempDif12h500
- AirTempDif12h700
- AirTempDif12h850
- AirTempDif6h500
- AirTempDif6h700
- AirTempDif6h850
- CAPE
- CIN
- CIN_YlGn
- CIN_YlGnBu
- DewpointTemp
- DewpointTemp2m
- DewpointTemp300
- DewpointTemp500
- DewpointTemp700
- DewpointTemp850
- DewpointTemp925
- Frontogenesis500
- Frontogenesis700
- Frontogenesis850
- Frontogenesis925
- GeoPotHeight300
- GeoPotHeight500
- GeoPotHeight700
- GeoPotHeight850
- GeoPotHeight925
- InstRain
- PotVorticity
- PotVorticity300
- PotVorticity500
- PotVorticity700
- PotVorticity850
- PotVorticity925
- PotentialTemp
- PotentialTemp2m
- PotentialTemp500
- PotentialTemp600
- PotentialTemp700
- PotentialTemp800
- PotentialTemp850
- PotentialTemp925
- Rain
- RelativeHumidity
- RelativeHumidity2m
- RelativeHumidity300
- RelativeHumidity500
- RelativeHumidity700
- RelativeHumidity850
- RelativeHumidity925
- SeaLevelPressure
- SeaLevelPressure1hPa
- SeaLevelPressure2hPa
- SimRadarReflectivity1km
- SimRadarReflectivityMax
- SkewT
- StaticStability700500
- StaticStability850700
- TerrainElevation
- TerrainElevation1000
- Wetbulb
- Wetbulb300
- Wetbulb500
- Wetbulb700
- Wetbulb850
- Wetbulb925
- WindSpeed
- WindSpeed300
- WindSpeed500
- WindSpeed700
- WindSpeed850
- WindSpeed925

### Plotting Regions

The plotting region can be specified as a bounding box of the projected coordinates with the `region` parameter as "min_x,max_x,min_y,max_y".
By default, the `full` area covered by the WRF data is plotted.

To be able to easily select a region, it is recommended that the terrain elevation is plotted first, with the `region_ticks` parameter set to True, i.e.:
```
wat.terrain(wrfout_dir="/my/data/", output_dir="/my/results/", region_ticks=True)
```
This will produce a plot with the projected coordinates on the right and bottom axes, which can be used to select the bounding box for the `region` parameter.

### Locations

This locations are currently defined in the code, and can be used as `place` parameters.

- Aberporth
- Algeria
- Bath
- Bordeaux
- BristolChannel
- Caerphilly
- Camborne
- Casablanca
- Gibraltar
- Herstmonceux
- LaCoruna
- Larkhill
- Lerwick
- Madrid
- Murcia
- Nimes
- Nottingham
- Santander
- Stornoway
- Trajectory
- Trappes

## About the source code

### Animate
This is the core of the diagnostic generation.
In this function all your wrfout files are loaded, the variables are extracted using **GetSensVar**, plotted using **Plot2DField**, and combined into an mp4.

*All* the files in ***wrfout_dir*** will be loaded and combined, so make sure you want that.

The information on the diagnostic being generated should be provided in an ***svariable*** object, as defined in **SensibleVariables**.

Should you wish to override the default windbarb overlapping defined for some **SensibleVariables**, the call to this function is the best place to do so.

By default, when the animation is processed and the mp4 is successfully generated all png files are deleted. This can be controled with the flag ***cleanpng***.

### Plot2DField
This function simply plots a given variable (***var***) with the metadata found in the ***svariable*** object.

A flag for ***windbarbs*** may be turned on, for which the wind components ***u*** and ***v*** must be given as inputs too.

### SensibleVariables
This defines a class for variables with more sensible names than the ones used in wrf, which makes it a bit more amicable.

The object is basically composed of metadata for the diagnostics that are of interest to this particular project, but the list can easily be expanded.

The information in each object is used as instructions in the extraction of the variable from netcdf files and during plotting.

Each of the variables has the attributes that describe the way the variable should be plotted, including the color scale, units, title, range, type of plot, annotations (like wind-barbs or contour-lines), and potentially overlapping variables.

See the description of each predefined **svariable** inside the file.

### GetSensVar
This function is an adaptation of wrf-python's *getvar*, but makes it simpler to obtain the diagnostics of interest, and uses the information in **svariable** objects

It deals with all the tecnical details on how to load the variables from the netcdf file so that they can be passed to the **Plot2DField** function.
This includes loading the wind velocity components when ***windbarbs*** is set to 1.

During this process, it also takes care of some variable computation, which is not universally implemented in *getvar*.

The outputs are the processed variable ***var***, the wind velocity components ***u*** and ***v*** (if windbarbs=0 these will be None), and the raw variable values ***varv*** (for use in *isdif* **svariable** computation).


### Special diagnostics

The following diagnostics have special functions to deal with them, but the diagnostic generation is still done through the wrf_analysis_toolkit_cli.py script.

#### TerrainPlots
These do not require animation nor the whole of the wrfout files, so they have a special function to deal with them.
They use the same **Plot2DField** function, and add annotations to the plot.

#### Frontogenesis
This is a special diagnostic that requires a bit of extra computation. The function is called from within GetSensVar, and passed to Animate as the other diagnostics.

#### SkewT
SkewTs are a completely different plotting style, and so they have a special function to deal with them,
which uses the [metpy](https://unidata.github.io/MetPy/latest/api/index.html) library.
They also combine a lot of wrf variables, so they are not generated in the same way as the other diagnostics.
The function is called from Animate, as an alternative to the standard Plot2DField for other diagnostics.


### Direct comparison of outputs

The `MP4Compare` and `WRFCompare` files contain functions to compare two sets of data directly.
They are not part of the standard workflow, but are useful for quick comparisons.

#### ConcatNDiff
This function is a very quick way to compare mp4 files. 

It  gets the absolute value pixel to pixel difference of each frame, and concatenates it to the two original videos side by side.

#### ConcatNxM
This function simply stitches videos on a grid with ***N*** rows and ***M*** columns.

#### WRFSmoothDiff
This is a slightly more advanced way of comparing two sets of data.

It gets the difference directly from the wrfout files, and then animates the result using a divergent color scale.
If the flag ***smooth*** is set to 1, it smooths the data before making the diff, so that slight positional changes are not as strongly reflected in the output.


## Tests
There are three ways in which the code can be currently tested, with slightly different objectives.

The tests inside the `tests/integration` folder are designed to run independently, and detect both coverage and code errors. They are run using pytest, and assert the existence of the output files, but do not check their content.

The tests inside the `tests/human_checks` folder are designed to produce outputs that can be visually checked by a human. These run by calling the cli.

The tests inside the `tests/library` folder are of the same spirit as the human checks, but are run directly calling the library, rather than the cli.

All sets of tests are only integration tests, and do not check the individual functions. They are designed to be run inside a container, which is built using the Dockerfile in the root of this repo.
A compose file is provided for convenience, which will build the container and run the tests inside it.
You may run the tests by first mounting into the test directory (`cd tests/`) and then running:
```
docker compose up --build pytest-coverage
```
or
```
docker compose up --build human-checks
```
or
```
docker compose up --build library-tests
```

You'll find further information in the compose file.


## Conda environment

If you are using this code directly on your machine (as opposed to using the container described in [tests](#tests)), make sure you have the conda environment set up and active before you call `wrf_analysis_toolkit_cli.py` or `test.py`.

If you do not have the environment, make sure you have anaconda/miniconda/micromamba installed.
This will install it with defaults:
```
echo | "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
source ~/.bashrc
```
Then you can create and activate the environment with
```
micromamba env create --name wrf-py-env --file environment.yml
micromamba activate wrf-py-env
```
Finally, install the package in editable mode with
```
pip install -e .
```
You are now set up to use the code.

### Install Instructions for MASC compute

These instructions are for installing a new version of the tool on our shared service. 

#### Notes:
- Replace `<version>` with your new version number (e.g. `2.2.1`) in the commands below. This version number should be taken from the `pyproject.toml` file, e.g.:
```
[project]
name = "wrf_analysis_toolkit"
version = "2.2.1"
```
- Start by copying a template environment directory (`wrf-py-env-template`) which has all the supporting libraries needed on this platform, rather than building the environment fresh each time. This ensures we don't accidentally change version. This copy process will take several minutes to perform.
- When installing the local package make sure to use `python -m pip` - otherwise pip will not get the environment setup correct, and will try to install the binary in `~/.local/bin/`.
- `/mnt/projects/wrf-python/wrf-py-env` is a soft symlink to our current environment, so we can delete this link safely before linking to the new environment.
- Don't delete the old environment until you've confirmed that the new one works!

#### Steps:
- `cp -a /mnt/projects/wrf-python/wrf-py-env-template /mnt/projects/wrf-python/wrf-py-env-<version>` **replace `<version>` in this code!**
- `module load micromamba`
- `micromamba activate /mnt/projects/wrf-python/wrf-py-env-<version>` **replace `<version>` in this code!**
- `python -m pip install .` **this must be run from this git repo, in `wrf_analysis_toolkit` directory**
- `rm /mnt/projects/wrf-python/wrf-py-env`
- `ln -s /mnt/projects/wrf-python/wrf-py-env-<version> /mnt/projects/wrf-python/wrf-py-env` **replace `<version>` in this code!**


