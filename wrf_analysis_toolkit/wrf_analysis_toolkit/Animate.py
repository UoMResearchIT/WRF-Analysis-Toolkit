from netCDF4 import Dataset
import imageio
import os

from wrf_analysis_toolkit.utils import select_wrfout_files, latlon_check
from wrf_analysis_toolkit.Plot2DField import *
from wrf_analysis_toolkit.SkewT import *
from wrf_analysis_toolkit.GetSensVar import *
from wrf_analysis_toolkit.VerticalCrossSection import VerticalCrossSection
import wrf_analysis_toolkit.SensibleVariables as sv


def Animate(
    dir_path,
    svariable,
    time_from=None,
    time_to=None,
    time_step=None,
    windbarbs=0,
    outfile="MyMP4",
    outdir="./",
    smooth=1,
    region="full",
    region_ticks=False,
    us_states=False,
    cleanpng=1,
    save_pdf=0,
    make_mp4=True
):
    ##Input check
    # Directories
    if dir_path[-1] != "/":
        dir_path = dir_path + "/"
    if outdir[-1] != "/":
        outdir = outdir + "/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # Need to implement input check here!

    if cleanpng and not save_pdf and not make_mp4:
        raise ValueError("save_pdf_frames and/or make_mp4 must be True if clean_png_frames is True, or Animate will save no output")

    #
    print("Generating diagnostic for", svariable.outfile)
    WRFfiles = select_wrfout_files(dir_path, time_from, time_to, time_step)
    print("Source wrfout files:", dir_path)
    for f in WRFfiles:
        print("  ", f)
    print(
        "Using:\n\twindbarbs =",
        windbarbs,
        "\n\tvcross    =",
        svariable.vcross,
        "\n\tsmooth    =",
        smooth,
        "\n\tcleanpng  =",
        cleanpng,
        "\n\tsave_pdf  =",
        save_pdf,
        "\n\tmake_mp4  =",
        make_mp4,
    )
    print("Output will be saved as ", outdir + outfile, "\n")

    # Initialization
    PNGfiles = []
    vpv = None
    overlapsv = None
    overlap = None
    tmp_dir = outdir + "__" + outfile
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    tmp_dir = tmp_dir + "/"

    if svariable.along_traj:
        # Load trajectory CSV file
        with open(svariable.along_traj, "r") as f:
            print(f"Loading {svariable.along_traj}")
            lines = f.readlines()
            assert lines[0].startswith(
                "Time [h],Latitude [deg],Longitude [deg],Elevation [m],Pressure [mb],"
            ), "Invalid CSV format"
            lines = lines[1:]
            trajectory = []
            for x in lines:
                try:
                    t, lat, lon, z, p, *_ = x.split(",")
                    trajectory.append(
                        {
                            "t": float(t),
                            "lat": float(lat),
                            "lon": float(lon),
                            "p": float(p),
                        }
                    )
                except ValueError as e:
                    # Skip line if there is an error reading the line and converting to right type
                    print(f"WARNING: Skipping line with invalid data:")
                    print(f"  {x}")
                    print(f"  {e}")
                    continue

    # Plot each time frame in each file
    sim_ti = 0
    traj_ti = 0
    for wrf_fn in WRFfiles:
        # Open the NetCDF file
        print("Loading ", wrf_fn)
        ncfile = Dataset(dir_path + wrf_fn)

        # If using start/end_latlon, confirm both are in the domain
        if svariable.start_latlon and svariable.end_latlon:
            latlon_check(ncfile, svariable.start_latlon)
            latlon_check(ncfile, svariable.end_latlon)

        # Get number of time frames and plot them
        timerange = ncfile.variables["Times"].shape[0]
        for ti in range(timerange):
            print("Processing:", ti + 1, "/", timerange, end="\r")
            if "SkewT" in svariable.outfile:
                outfname = tmp_dir + outfile + wrf_fn + "_t_" + str(ti) + ".png"
                skip = 0
                if svariable.along_traj:

                    if sim_ti >= trajectory[0]["t"] and sim_ti <= trajectory[-1]["t"]:
                        assert sim_ti == trajectory[traj_ti]["t"], "Invalid time index"
                        svariable.lat = trajectory[traj_ti]["lat"]
                        svariable.lon = trajectory[traj_ti]["lon"]
                        svariable.interpvalue = trajectory[traj_ti]["p"]
                        svariable.ptitle = (
                            f"SkewT along trajectory  ({svariable.lat},{svariable.lon})"
                        )
                        traj_ti += 1
                    else:
                        skip = 1
                if not skip:
                    Plot_SkewT(
                        ncfile,
                        ti,
                        svariable,
                        outfname,
                        save_pdf=save_pdf,
                    )
                    PNGfiles.append(outfname)
                sim_ti = sim_ti + 1

            elif svariable.vcross:
                outfname = tmp_dir + outfile + wrf_fn + "_t_" + str(ti) + ".png"
                VerticalCrossSection(
                    ncfile,
                    svariable,
                    outfname=outfname,
                    save_pdf=save_pdf,
                )
                PNGfiles.append(outfname)

            else:
                var, u, v, vpv = GetSensVar(ncfile, svariable, windbarbs, ti, vpv)
                if svariable.overlap_sv is not None:
                    overlapsv = eval("sv." + svariable.overlap_sv)
                    overlap, _, _, _ = GetSensVar(ncfile, overlapsv, 0, ti, None)
                if var is not None:
                    outfname = tmp_dir + outfile + wrf_fn + "_t_" + str(ti) + ".png"
                    Plot2DField(
                        var,
                        svariable,
                        windbarbs,
                        outfname,
                        overlap,
                        u,
                        v,
                        smooth,
                        region=region,
                        region_ticks=region_ticks,
                        us_states=us_states,
                        save_pdf=save_pdf,
                    )
                    PNGfiles.append(outfname)

        print("Processed successfully.")

    # Build GIF
    # with imageio.get_writer(outfile+".gif", mode='I') as writer:
    #    for filename in PNGfiles:
    #        image = imageio.imread(filename)
    #        writer.append_data(image)
    # Build mp4
    if make_mp4:
        print("Building MP4 from png files...")
        with imageio.get_writer(outdir + outfile + ".mp4", mode="I") as writer:
            for filename in PNGfiles:
                image = imageio.imread(filename)
                writer.append_data(image)

    # Remove individual frame files
    if cleanpng:
        print("Deleting png files...")
        for file in PNGfiles:
            os.remove(file)
        # clean up temp output directory if it is now empty
        if not any(os.scandir(tmp_dir)):
            os.removedirs(tmp_dir)
        print("All done.")
