import os
import sys

# Adds folder to python path search
sys.path.insert(1, "/".join(__file__.split("/")[:-2]))

import argparse
from wrf_analysis_toolkit.utils import str2bool
import wrf_analysis_toolkit as wat


def latlon(value):
    try:
        lat, lon = map(float, [x.strip() for x in value.split(",")])
        return (lat, lon)
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            "Expected lat,lon, e.g. 52.5,-2.0"
        ) from err

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task",
        type=str,
        default="diagnostic",
        choices=wat.__all__,
    )
    parser.add_argument(
        "--var",
        "--variable_name",
        dest="var",
        type=str,
        default="DewpointTemp2m",
        help="Sensible variable to work with.",
        choices=wat.SensibleVariables.get_sv_names(),
    )
    parser.add_argument(
        "--csv_vars",
        "--variable_names",
        dest="csv_vars",
        type=str,
        default="",
        help="Comma separated variables to include in csv.",
    )
    parser.add_argument(
        "--windbarbs",
        type=str2bool,
        default=None,
        help="Default behaviour is set by sensible variable.",
    )
    parser.add_argument(
        "--windbarb_gap",
        type=int,
        default=None,
        help="Number of grid points between wind barbs (optional).",
    )
    parser.add_argument(
        "--smooth",
        type=str2bool,
        default=0,
        help="Set to 1 for conical smoothing of wrf variables.",
    )
    parser.add_argument(
        "--clean",
        "--clean_png_frames",
        dest="clean",
        type=str2bool,
        default=1,
        help="Set to 0 to conserve png or mp4 temp files generated during the task",
    )
    parser.add_argument(
        "--save_pdf_frames",
        type=str2bool,
        default=0,
        help="Set to 1 to save pdf files of each frame generated during the task",
    )
    parser.add_argument(
        "--make_mp4",
        type=str2bool,
        default=0,
        help="Set to 1 to combine PNG frames into an MP4 file (only for task=diagnostic)",
    )
    parser.add_argument(
        "--region",
        type=str,
        default="full",
        help="Area to plot, can be the 'full' area in the WRF simulation, or comma separated projected bounding box coordinates: 'min_x,max_x,min_y,max_y'.",
    )
    parser.add_argument(
        "--region_ticks",
        type=str2bool,
        default=0,
        help="Show lat/lon labels on the top and left and projected coordinate labels on the bottom and right.",
    )
    parser.add_argument(
        "--us_states",
        type=str2bool,
        default=0,
        help="Show US state boundaries on plot.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=1,
        help="Number of rows in the grid used for mp4stitch.",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=1,
        help="Number of columns in the grid used for mp4stitch.",
    )
    parser.add_argument(
        "--files",
        "--file_paths",
        dest="files",
        type=str,
        default="",
        help="List of file names used for mp4stitch. Provide a list in quotes separated by commas.",
    )
    parser.add_argument(
        "--dirs",
        type=str,
        default="",
        help="List of file directories used for mp4stitch. Provide a list in quotes separated by commas.",
    )
    parser.add_argument(
        "--labels",
        type=str,
        default="",
        help="List of labels used for mp4stitch. Provide a list in quotes separated by commas.",
    )
    parser.add_argument(
        "--colormap",
        type=str,
        default=None,
        help="Default colormaps are defined in sensible variables or the chosen task. You can override them by choosing a different one here.",
    )
    parser.add_argument(
        "--range_min",
        type=str,
        default=None,
        help="Minimum value used in the colormap. Default value is defined in sensible variables. You can override them by choosing a different one here.",
    )
    parser.add_argument(
        "--range_max",
        type=str,
        default=None,
        help="Maximum value used in the colormap. Default value is defined in sensible variables. You can override them by choosing a different one here.",
    )
    parser.add_argument(
        "--label_diff",
        type=str,
        default="",
        help="Label added in top corner of diff image",
    )
    parser.add_argument(
        "--wrfout_dir",
        type=str,
        help="Path to the directory with your wrfout files.",
    )
    parser.add_argument(
        "--time_from",
        type=str,
        default=None,
        help="Only use wrfout files from this time onward (inclusive). Expects format 'YYYY-MM-DD_HH:MM:SS' (optional).",
    )
    parser.add_argument(
        "--time_to",
        type=str,
        default=None,
        help="Only use wrfout files up to this time (inclusive). Expects format 'YYYY-MM-DD_HH:MM:SS' (optional).",
    )
    parser.add_argument(
        "--time_step",
        type=str,
        default=None,
        help="Only use wrfout files seperated by this time step. Expects format 'HH:MM:SS' (optional, only useable with diagnostic).",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./",
        help="Path to the directory in which outputs will be saved.",
    )
    parser.add_argument(
        "--file_tag",
        type=str,
        default="",
        help="Tag appended at the end of the output file name to prevent replacement.",
    )
    parser.add_argument(
        "--lat",
        type=str,
        default=None,
        help="Latitude of point of interest (used for SkewT plots).",
    )
    parser.add_argument(
        "--lon",
        type=str,
        default=None,
        help="Longitude of point of interest (used for SkewT plots).",
    )
    parser.add_argument(
        "--place",
        type=str,
        default=None,
        help="Name of place for point location on map).",
        choices=[
            attr.split("_")[1]
            for attr in wat.SensibleVariables.get_sv_names()
            if attr.startswith("SkewT_")
        ],
    )
    parser.add_argument(
        "--traj",
        "--trajectory",
        dest="traj",
        type=str,
        default=None,
        help="Path to the trajectory CSV file.",
    )
    parser.add_argument(
        "--vcross",
        type=str2bool,
        default=0,
        help="Set to 1 to make a vertical cross section plot.",
    )
    parser.add_argument(
        "--start_latlon",
        type=latlon,
        default=None,
        help="Start latlon coordinate for making vertical cross section, or start point to draw a line on a 2D map plot."
    )
    parser.add_argument(
        "--end_latlon",
        type=latlon,
        default=None,
        help="End latlon coordinate for making vertical cross section, or end point to draw a line on a 2D map plot.",
    )
    parser.add_argument(
        "--plim_bottom",
        type=float,
        default=None,
        help="Pressure level at bottom of y-axis for vertical cross section plots.",
    )
    parser.add_argument(
        "--plim_top",
        type=float,
        default=None,
        help="Pressure level at top of y-axis for vertical cross section plots.",
    )
    parser.add_argument(
        "--plevs",
        type=int,
        default=None,
        help="Number of pressure values on y-axis for vertical cross section plots.",
    )

    args = parser.parse_args()

    if args.task not in wat.__all__:
        print(
            f"Task '{args.task}' is not defined in wrf_analysis_toolkit."
            f"Options are: {', '.join(wat.__all__)}"
        )
        exit(1)

    files = args.files.split(",")
    dirs = args.dirs.split(",") if args.dirs else [args.wrfout_dir]
    labels = args.labels.split(",")

    match args.task:
        case "terrain":
            wat.terrain(
                wrfout_dir=dirs[0],
                output_dir=args.output_dir,
                variable_name=args.var,
                file_tag=args.file_tag,
                range_min=args.range_min,
                range_max=args.range_max,
                place=args.place,
                lat=args.lat,
                lon=args.lon,
                region=args.region,
                region_ticks=args.region_ticks,
                smooth=args.smooth,
            )

        case "diagnostic":
            wat.diagnostic(
                wrfout_dir=dirs[0],
                output_dir=args.output_dir,
                variable_name=args.var,
                file_tag=args.file_tag,
                time_from=args.time_from,
                time_to=args.time_to,
                time_step=args.time_step,
                range_min=args.range_min,
                range_max=args.range_max,
                windbarbs=args.windbarbs,
                windbarb_gap=args.windbarb_gap,
                place=args.place,
                lat=args.lat,
                lon=args.lon,
                trajectory=args.traj,
                region=args.region,
                region_ticks=args.region_ticks,
                us_states=args.us_states,
                vcross=args.vcross,
                start_latlon=args.start_latlon,
                end_latlon=args.end_latlon,
                plim_bottom=args.plim_bottom,
                plim_top=args.plim_top,
                plevs=args.plevs,
                smooth=args.smooth,
                clean_png_frames=args.clean,
                save_pdf_frames=args.save_pdf_frames,
                make_mp4=args.make_mp4
            )
        case "csv":
            wat.csv(
                wrfout_dir=dirs[0],
                output_dir=args.output_dir,
                variable_names=args.csv_vars.split(",") if args.csv_vars else None,
                place=args.place,
                lat=args.lat,
                lon=args.lon,
                file_tag=args.file_tag,
                time_from=args.time_from,
                time_to=args.time_to,
            )
        case "wrfdiff":
            wat.wrfdiff(
                wrfout_dir_A=dirs[0],
                wrfout_dir_B=dirs[1],
                variable_name=args.var,
                output_dir=args.output_dir,
                file_tag=args.file_tag,
                time_from=args.time_from,
                time_to=args.time_to,
                label_diff=args.label_diff or (labels[0] or None),
                range_min=args.range_min,
                range_max=args.range_max,
                windbarbs=args.windbarbs,
                windbarb_gap=args.windbarb_gap,
                colormap=args.colormap,
                region=args.region,
                region_ticks=args.region_ticks,
                smooth=args.smooth,
                clean_png_frames=args.clean,
                save_pdf_frames=args.save_pdf_frames,
            )
        case "mp4diff":
            if len(files) != 2:
                if args.var and len(dirs) == 2:
                    files = [f"{dirs[0]}/{args.var}.mp4", f"{dirs[1]}/{args.var}.mp4"]
                else:
                    raise ValueError(
                        "mp4diff requires exactly 2 files or a variable name with 2 directories."
                    )
            wat.mp4diff(
                file_A=files[0],
                file_B=files[1],
                output_dir=args.output_dir,
                file_tag=args.file_tag,
                label_A=labels[0],
                label_B=labels[1],
                label_diff=args.label_diff or (labels[2] or None),
                clean_png_frames=args.clean,
            )
        case "mp4stitch":
            wat.mp4stitch(
                file_paths=files,
                output_dir=args.output_dir,
                file_tag=args.file_tag,
                labels=labels,
                rows=args.rows,
                cols=args.cols,
            )

if __name__ == "__main__":
    cli()
