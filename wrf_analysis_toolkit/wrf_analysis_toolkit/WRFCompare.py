# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
from netCDF4 import Dataset
from wrf import smooth2d
import imageio
from PIL import Image, ImageDraw

from wrf_analysis_toolkit.utils import select_wrfout_files
from wrf_analysis_toolkit.GetSensVar import *
from wrf_analysis_toolkit.Plot2DField import *


def WRFSmoothDiff(
    dir1,
    dir2,
    svariable,
    time_from=None,
    time_to=None,
    windbarbs=0,
    smooth=1,
    difflabel="",
    colormap="seismic",
    outfile="MyMP4",
    outdir="./",
    region="full",
    region_ticks=False,
    cleanpng=1,
    save_pdf=0,
):
    # Input check
    # Directories
    if dir1[-1] != "/":
        dir1 = dir1 + "/"
    if dir2[-1] != "/":
        dir2 = dir2 + "/"
    if outdir[-1] != "/":
        outdir = outdir + "/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # Need to implement input check here!

    #
    print("Comparing WRF files for.", svariable.outfile)
    print("Source wrfout files:", dir1, " & ", dir2)
    WRFfiles1 = select_wrfout_files(dir1, time_from, time_to)
    WRFfiles2 = select_wrfout_files(dir2, time_from, time_to)
    print("Source wrfout files:\n  ", dir1)
    for f in WRFfiles1:
        print("    ", f)
    print("Source wrfout files:\n  ", dir2)
    for f in WRFfiles2:
        print("    ", f)
    print(
        "Using:\n\tdifflabel=",
        difflabel,
        "\n\twindbarbs=",
        windbarbs,
        "\n\tsmooth=",
        smooth,
        "\n\tcleanpng=",
        cleanpng,
    )
    print("Output will be saved as ", outdir + outfile, "\n")

    # Modifies plotting range and colormap
    match svariable.scale:
        case "linear":
            svariable.range_max = (svariable.range_max - svariable.range_min) / 2
        case "log":
            svariable.range_max = svariable.logbase ** (
                (svariable.range_max + svariable.range_min) * 2 / 3
            )
            svariable.scale = "linear"
        case "bounds":
            svariable.range_max = svariable.bounds[len(svariable.bounds) // 2]
            svariable.scale = "linear"
    svariable.range_min = -1 * svariable.range_max
    if colormap is None:
        svariable.colormap = "seismic"
    else:
        svariable.colormap = colormap

    # Initialization
    PNGfiles = []
    vpv1 = vpv2 = u = v = None
    tmp_dir = outdir + "__" + outfile
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    tmp_dir = tmp_dir + "/"

    # Compares list of files
    nfiles = min(len(WRFfiles1), len(WRFfiles2))
    for i in range(nfiles):
        if WRFfiles1[i] != WRFfiles2[i]:
            print("WARNING!: Files in the two directories may not be compatible.")
            print(
                "The name of these files differs, so they may be simulating different days:"
            )
            print("\t", WRFfiles1[i], "-", WRFfiles2[i])
            print(
                "I will carry on labelling with",
                WRFfiles1[i],
                "\b, but make sure you want me to...",
            )

    # Plot each time frame in each file
    for i in range(nfiles):
        # Open the NetCDF files
        wrf_fn_1 = WRFfiles1[i]
        wrf_fn_2 = WRFfiles2[i]
        wrf_fn = wrf_fn_1
        print("Loading ", wrf_fn_1, "and", wrf_fn_2)
        ncfile1 = Dataset(dir1 + wrf_fn_1)
        ncfile2 = Dataset(dir2 + wrf_fn_2)
        # Get number of time frames and plot them
        timerange1 = ncfile1.variables["Times"].shape[0]
        timerange2 = ncfile2.variables["Times"].shape[0]
        if timerange1 != timerange2:
            print("WARNING!: Files in the two directories may not be compatible.")
            print("The number of time slices differs in the following files:")
            print("\t", WRFfiles1[i], "-", WRFfiles2[i])
            print("This is probably a good time to stop... quitting...")
        else:
            timerange = timerange1
            # for ti in range(0,timerange,4):                              ## For tests only
            for ti in range(timerange):
                of = tmp_dir + outfile + wrf_fn + "_t_" + str(ti) + ".png"
                PNGfiles.append(of)
                print("Processing:", ti + 1, "/", timerange, end="\r")
                var1, u1, v1, vpv1 = GetSensVar(ncfile1, svariable, windbarbs, ti, vpv1)
                var2, u2, v2, vpv2 = GetSensVar(ncfile2, svariable, windbarbs, ti, vpv2)
                if smooth:
                    # Smoothing variables
                    smovar1 = smooth2d(var1, 3, cenweight=4)
                    smovar2 = smooth2d(var2, 3, cenweight=4)
                else:
                    smovar1 = var1
                    smovar2 = var2
                # Making diff
                smooth_var = smooth2d(var1, 3, cenweight=4)
                smooth_var.values = smovar2.values - smovar1.values
                if windbarbs:
                    u = u2 - u1
                    v = v2 - v1
                # Plotting
                Plot2DField(
                    smooth_var,
                    svariable,
                    windbarbs,
                    of,
                    u,
                    v,
                    smooth=0,
                    region=region,
                    region_ticks=region_ticks,
                    nlevs=20,
                    save_pdf=save_pdf,
                )
            print("Processed", timerange, "/", timerange, "successfully.")

    if difflabel != "":
        # Adds difflabels to frames
        for i in range(len(PNGfiles)):
            with Image.open(PNGfiles[i]) as im:
                draw = ImageDraw.Draw(im)
                draw.text((10, 10), difflabel, fill=(0, 0, 0))
                im.save(PNGfiles[i])

    # Build mp4
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
        if not save_pdf:
            os.removedirs(tmp_dir)
        print("All done.")
