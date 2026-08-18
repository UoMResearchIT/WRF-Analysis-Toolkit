import os
from copy import deepcopy
from typing import List

from wrf_analysis_toolkit.utils import set_variable

import wrf_analysis_toolkit.SensibleVariables as sv
from wrf_analysis_toolkit.Animate import Animate
from wrf_analysis_toolkit.TerrainPlots import Terrain
from wrf_analysis_toolkit.CSV_Data import CSV_Data
from wrf_analysis_toolkit.MP4Compare import ConcatNDiff, ConcatNxM
from wrf_analysis_toolkit.WRFCompare import WRFSmoothDiff
from wrf_analysis_toolkit.VerticalCrossSection import VerticalCrossSection


def diagnostic(
    wrfout_dir: str,
    output_dir: str,
    variable_name: str,
    sens_var: sv.svariable | None = None,
    file_tag: str = "",
    time_from: str | None = None,
    time_to: str | None = None,
    time_step: str | None = None,
    range_min: float | None = None,
    range_max: float | None = None,
    windbarbs: bool | None = None,
    windbarb_gap: int | None = None,
    place: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    trajectory: str | None = None,
    region: str = "full",
    region_ticks: bool = False,
    us_states: bool = False,
    vcross: bool = False,
    start_latlon: tuple | None = None,
    end_latlon: tuple | None = None,
    plim_bottom: float | None = None,
    plim_top: float | None = None,
    plevs: int | None = None,
    smooth: bool = False,
    clean_png_frames: bool = True,
    save_pdf_frames: bool = False,
    make_mp4: bool = True,
):
    """
    Generates a diagnostic animation for the specified variable and saves it to the output directory.

    Inputs marked as '(optional)' take default values as defined in SensibleVariables.

    Inputs:
    - wrfout_dir: Directory containing WRF output files.
    - output_dir: Directory where the output file(s) will be saved.
    - variable_name: Name of the variable to analyze (must be defined in SensibleVariables).
    - sens_var: Sensible variable object (optional, only use if existing SensibleVariables cannot be used).
    - file_tag: String to append to the output filename (optional).
    - time_from: Only use wrfout files from this time onward (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).
    - time_to: Only use wrfout files up to this time (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).
    - time_step: Only use wrfout files seperated by this time step. Expects format "HH:MM:SS" (optional).
    - range_min: Minimum value for the variable range (optional).
    - range_max: Maximum value for the variable range (optional).
    - windbarbs: Boolean indicating whether to include wind barbs in the plots (optional).
    - windbarb_gap: Number of grid points between wind barbs (optional).
    - region: Area covered by the plots, set by a comma-separated string of projected bounding box coordinates as "min_x,max_x,min_y,max_y".
                (default is "full", which uses all the area covered by the wrf data). See pre-defined regions in the readme.
    - region_ticks: If True, plots show lat/lon labels on the top and left, and projected coordinate labels on the bottom and right.
    - us_states: Boolean, if True add US state boundaries to plot (default is False)
    - start_latlon: latitude-longitude coordinate pair for start point of cross-section, or start point to draw a line on a 2D map plot.
        (optional), required if vcross==True.
    - end_latlon: latitude-longitude coordinate pair for end point of cross-section, or end point to draw a line on a 2D map plot.
        (optional), required if vcross==True.
    - smooth: Boolean indicating whether to apply smoothing to the plots (default is False).
    - clean_png_frames: Boolean indicating whether to delete intermediate PNG frames after creating the animation (default is True).
    - save_pdf_frames: Boolean indicating whether to save each frame as a PDF (default is False).
    - make_mp4: Boolean whether to combine frames into an animated mpeg file

    For SkewT plots, the following additional inputs are available:
        - place: Predefined location name for SkewT plots (optional).
        - lat: Latitude for the variable (optional). If provided, lon must also be provided.
        - lon: Longitude for the variable (optional). If provided, lat must also be provided.
        - trajectory: Path to a trajectory file for SkewT plots animated along a trajectory (optional).

    For Vertical Cross-Section plots, the following additional inputs are available:
        - vcross: Set to True to make a vertical cross section plot (optional)
        - plim_bottom: pressure value for bottom of y-axis of vertical-cross section plots (optional)
        - plim_bottom: pressure value for top of y-axis of vertical-cross section plots (optional)
        - plevs: Number of pressure values of y-axis of vertical-cross section plots (optional)

    Returns: The name of the output file saved in the output directory.
    """
    if "Terrain" in variable_name:
        return terrain(
            wrfout_dir=wrfout_dir,
            output_dir=output_dir,
            variable_name=variable_name,
            file_tag=file_tag,
            range_min=range_min,
            range_max=range_max,
            place=place,
            lat=lat,
            lon=lon,
            region=region,
            region_ticks=region_ticks,
            smooth=smooth,
        )

    svar = set_variable(
        variable_name=variable_name,
        range_min=range_min,
        range_max=range_max,
        windbarbs=windbarbs,
        windbarb_gap=windbarb_gap,
        place=place,
        lat=lat,
        lon=lon,
        trajectory=trajectory,
        vcross=vcross,
        start_latlon=start_latlon,
        end_latlon=end_latlon,
        plim_bottom=plim_bottom,
        plim_top=plim_top,
        plevs=plevs,
        sens_var=sens_var,
    )

    outfile = svar.outfile + file_tag

    Animate(
        dir_path=wrfout_dir,
        svariable=svar,
        time_from=time_from,
        time_to=time_to,
        time_step=time_step,
        windbarbs=svar.windbarbs,
        outfile=outfile,
        outdir=output_dir,
        smooth=smooth,
        region=region,
        region_ticks=region_ticks,
        us_states=us_states,
        cleanpng=clean_png_frames,
        save_pdf=save_pdf_frames,
        make_mp4=make_mp4,
    )

    return outfile


def terrain(
    wrfout_dir: str,
    output_dir: str,
    output_format: str = "pdf",
    variable_name: str = "TerrainElevation",
    file_tag: str = "",
    range_min: float | None = None,
    range_max: float | None = None,
    place: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    region: str = "full",
    region_ticks: bool = False,
    smooth: bool = False,
):
    """
    Generates static image of the terrain elevation in the wrf data and saves it to the output directory.

    Inputs:
    - wrfout_dir: Directory containing WRF output files.
    - output_dir: Directory where the output file(s) will be saved.
    - output_format: Format of the output file (default is "pdf"; can be "png").
    - variable_name: Name of the variable to analyze (must be a TerrainElevation).
    - file_tag: String to append to the output filename (optional).
    - range_min: Minimum value for the elevation range (default is 0). Must be >= 0.
    - range_max: Maximum value for the elevation range (default is 2000). Must be >= 10.
    - region: Area covered by the plots, set by a comma-separated string of projected bounding box coordinates as "min_x,max_x,min_y,max_y".
                (default is "full", which uses all the area covered by the wrf data). See pre-defined regions in the readme.
    - region_ticks: If True, plots show lat/lon labels on the top and left, and projected coordinate labels on the bottom and right.
    - smooth: Boolean indicating whether to apply smoothing to the plot (default is False).

    A marker* can also be added to the plot if lat and lon are provided, or a place if place is provided.
        - place: Predefined location name (optional).
        - lat: Latitude for the variable (optional). If provided, lon must also be provided.
        - lon: Longitude for the variable (optional). If provided, lat must also be provided.

    * Two markers are added to the plot: a circle centred on the nearest grid point, and a cross at the specified location.

    Returns: The name of the output file saved in the output directory.
    """
    svar = set_variable(
        variable_name=variable_name,
        place=place,
        lat=lat,
        lon=lon,
    )
    # Set elevation range if specified (negative values are not allowed)
    if range_min is not None and range_max is not None:
        range_min = max(float(range_min), 0.0)
        range_max = max(float(range_max), 10.0)

        interval = (range_max - range_min) / 10
        bounds = [range_min - 0.05] + [range_min + i * interval for i in range(0, 11)]
        if range_min == 0:
            bounds[1] = 1

        svar.range_min = range_min
        svar.range_max = range_max
        svar.bounds = bounds

    outfile = svar.outfile + file_tag

    Terrain(
        dir_path=wrfout_dir,
        svariable=svar,
        outfile=outfile,
        outdir=output_dir,
        out_format=output_format,
        smooth=smooth,
        region=region,
        region_ticks=region_ticks,
    )

    return outfile


def csv(
    wrfout_dir: str,
    output_dir: str,
    variable_names: List[str] | None = None,
    place: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    file_tag: str = "",
    time_from: str | None = None,
    time_to: str | None = None,
):
    """
    Generates a CSV file with the values of the specified variables at a given location and saves it to the output directory.
    The variables default to AirTemp, DewpointTemp, and RelativeHumidity at 925, 850, 700, 500, and 300 hPa, as well as CIN, CAPE, if not specified.

    Inputs:
    - wrfout_dir: Directory containing WRF output files.
    - output_dir: Directory where the CSV file will be saved.
    - variable_names: List of variable names to include in the CSV file (optional).
    - place: Predefined location name (optional -- lat and lon may be provided instead).
    - lat: Latitude for the location (optional -- place may be provided instead).
    - lon: Longitude for the location (optional -- place may be provided instead).
    - file_tag: String to append to the output filename (optional).
    - time_from: Only use wrfout files from this time onward (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).
    - time_to: Only use wrfout files up to this time (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).

    Returns: The name of the output file saved in the output directory.
    """
    if all(v is None for v in [place, lat, lon]):
        raise ValueError(
            "Either 'place' or both 'lat' and 'lon' must be provided to specify the location for the CSV output."
        )

    if variable_names is None:
        csv_data_v = ["AirTemp", "DewpointTemp", "RelativeHumidity"]
        csv_data_p = [925, 850, 700, 500, 300]
        variable_names = ["CIN", "CAPE"] + [
            f"{var}{height}" for var in csv_data_v for height in csv_data_p
        ]

    defined_variables = sv.get_sv_names()
    undefined_variables = [
        var for var in variable_names if var not in defined_variables
    ]
    if undefined_variables:
        raise ValueError(
            f"Variable(s) '{', '.join(undefined_variables)}' are not defined in SensibleVariables."
            f"Options are: {', '.join(defined_variables)}"
        )
    csv_vars = [set_variable(variable_name=var) for var in variable_names]

    svar = set_variable(
        variable_name="SkewT",  # Placeholder SV for CSV output
        place=place,
        lat=lat,
        lon=lon,
    )
    if place is not None:
        svar.outfile = f"CSV_Data_{place}"
    else:
        svar.outfile = f"CSV_Data_{svar.lat},{svar.lon}"

    outfile = svar.outfile + file_tag

    CSV_Data(
        dir_path=wrfout_dir,
        svariables=csv_vars,
        location=svar,
        outfile=outfile,
        outdir=output_dir,
        time_from=time_from,
        time_to=time_to,
    )

    return outfile


def wrfdiff(
    wrfout_dir_A: str,
    wrfout_dir_B: str,
    variable_name: str,
    output_dir: str,
    sens_var: sv.svariable | None = None,
    file_tag: str = "",
    time_from: str | None = None,
    time_to: str | None = None,
    label_diff: str = "",
    range_min: float | None = None,
    range_max: float | None = None,
    windbarbs: bool | None = None,
    windbarb_gap: int | None = None,
    colormap: str | None = None,
    region: str = "full",
    region_ticks: bool = False,
    smooth: bool = False,
    clean_png_frames: bool = True,
    save_pdf_frames: bool = False,
):
    """
    Performs a difference of the WRF output files (A-B), and generates a diagnostic from the resulting difference.
    Both wrf output directories must have the same number of time steps.

    Inputs:
    - wrfout_dir_A: Full path to the first WRF output directory.
    - wrfout_dir_B: Full path to the second WRF output directory.
    - variable_name: Name of the variable to analyze (must be defined in SensibleVariables).
    - sens_var: Sensible variable object (optional, only use if existing SensibleVariables cannot be used).
    - output_dir: Directory where the output file(s) will be saved.
    - file_tag: String to append to the output filename (optional).
    - time_from: Only use wrfout files from this time onward (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).
    - time_to: Only use wrfout files up to this time (inclusive). Expects format "YYYY-MM-DD_HH:MM:SS" (optional).
    - label_diff: Label to be added at the top left corner of the resulting diagnostic (optional).
    - range_min: Minimum value for the variable range (optional).
    - range_max: Maximum value for the variable range (optional).
    - windbarbs: Boolean indicating whether to include wind barbs in the plots (optional).
    - windbarb_gap: Number of grid points between wind barbs (optional).
    - colormap: Colormap to use for the plots (optional).
    - region: Area covered by the plots, set by a comma-separated string of projected bounding box coordinates as "min_x,max_x,min_y,max_y".
                (default is "full", which uses all the area covered by the wrf data). See pre-defined regions in the readme.
    - region_ticks: If True, plots show lat/lon labels on the top and left, and projected coordinate labels on the bottom and right.
    - smooth: Boolean indicating whether to apply smoothing to the plots (default is False).
    - clean_png_frames: Boolean indicating whether to delete intermediate PNG frames after creating the animation (default is True).
    - save_pdf_frames: Boolean indicating whether to save each frame as a PDF (default is False).

    Returns: The name of the output file saved in the output directory.
    """
    svar = set_variable(
        variable_name=variable_name,
        range_min=range_min,
        range_max=range_max,
        sens_var=sens_var,
        windbarbs=windbarbs,
        windbarb_gap=windbarb_gap,
    )

    outfile = f"wrf_diff_{svar.outfile}{file_tag}"

    WRFSmoothDiff(
        wrfout_dir_A,
        wrfout_dir_B,
        svar,
        time_from=time_from,
        time_to=time_to,
        windbarbs=svar.windbarbs,
        difflabel=label_diff,
        colormap=colormap,
        outfile=outfile,
        outdir=output_dir,
        smooth=smooth,
        region=region,
        region_ticks=region_ticks,
        cleanpng=clean_png_frames,
        save_pdf=save_pdf_frames,
    )

    return outfile


def mp4diff(
    file_A: str,
    file_B: str,
    output_dir: str,
    file_tag: str = "",
    label_A: str = "",
    label_B: str = "",
    label_diff: str = "",
    clean_png_frames=True,
):
    """
    Performs a pixel-wise difference between two mp4 files.
    The output is a new mp4 file that shows three videos in 1 row and 3 columns: A, B and A-B.
    Both input files must have the same size and number of frames and be in mp4 format.

    Inputs:
    - file_A: Full path to the first mp4 file.
    - file_B: Full path to the second mp4 file.
    - output_dir: Directory where the output file will be saved.
    - file_tag: String to append to the output filename (optional).
    - label_A: Label to be added at the top left corner of video A in the output (optional).
    - label_B: Label to be added at the top left corner of video B in the output (optional).
    - label_diff: Label to be added at the top left corner of the difference video in the output (optional).
    - clean: Whether to clean up temporary files after processing (optional).

    Returns: The name of the output file saved in the output directory.
    """
    # Check if the input files exist and are mp4 files
    if not file_A.endswith(".mp4") or not file_B.endswith(".mp4"):
        raise ValueError(
            f"Both files need to be mp4 files."
            f" Make sure to include the .mp4 extension in the file name."
        )
    if not os.path.isfile(file_A):
        raise FileNotFoundError(f"File '{file_A}' does not exist.")
    if not os.path.isfile(file_B):
        raise FileNotFoundError(f"File '{file_B}' does not exist.")
    # separate the directories and file names
    dir1, file1 = os.path.split(file_A)
    dir2, file2 = os.path.split(file_B)

    outfile = f"mp4_diff_{file1.replace('.mp4', '')}"
    if file1 != file2:
        outfile = outfile + f"_{file2.replace('.mp4', '')}"
    outfile = outfile + file_tag

    ConcatNDiff(
        file1=file1,
        file2=file2,
        dir1=dir1,
        dir2=dir2,
        label1=label_A,
        label2=label_B,
        difflabel=label_diff,
        outfile=outfile,
        outdir=output_dir,
        cleandiff=clean_png_frames,
    )

    return outfile


def mp4stitch(
    file_paths: List[str],
    output_dir: str,
    file_tag: str = "",
    labels: List[str] | None = None,
    rows: int = 1,
    cols: int = 1,
):
    """
    Stitches multiple mp4 files into a single mp4 file arranged in the specified rows and columns.

    Inputs:
    - file_paths: List of full paths to the mp4 files to be stitched.
    - output_dir: Directory where the output file will be saved.
    - file_tag: String to append to the output filename (optional).
    - labels: List of labels to be added at the top left corner of each video in the output (optional).
    - rows: Number of rows in the output video (optional, defaults to 1).
    - cols: Number of columns in the output video (optional, will increase to fit all files, if necessary).
    """
    # Check if the input files exist and are mp4 files
    for file_path in file_paths:
        if not file_path.endswith(".mp4"):
            raise ValueError(
                f"File '{file_path}' is not an mp4 file."
                f" Make sure to include the .mp4 extension in the file names."
            )
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
    # Separate the directories and file names
    dirs = [os.path.dirname(file_path) for file_path in file_paths]
    files = [os.path.basename(file_path) for file_path in file_paths]

    outfile = f"mp4stitch_{rows}x{cols}{file_tag}.mp4"
    ConcatNxM(
        files,
        dirs=dirs,
        labels=labels,
        M=cols,
        N=rows,
        outfile=outfile,
        outdir=output_dir,
    )

    return outfile

