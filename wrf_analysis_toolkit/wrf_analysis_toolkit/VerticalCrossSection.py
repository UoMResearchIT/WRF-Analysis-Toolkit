from netCDF4 import Dataset

import matplotlib.pyplot as plt
from matplotlib.pyplot import get_cmap
from matplotlib.ticker import ScalarFormatter

from wrf import to_np, getvar, CoordPair, vertcross

from wrf_analysis_toolkit.utils import set_variable
from wrf_analysis_toolkit.GetSensVar import *
import wrf_analysis_toolkit.SensibleVariables as sv

def VerticalCrossSection(
    ncfile: Dataset,
    svariable: sv.svariable,
    outfname="VCrossSec.png",
    time_tag=1,
    return_fig=0,
    dpi=100,
    save_pdf=0,
):
    # Confirm valid start/end lat-lon points
    start_latlon = svariable.start_latlon
    end_latlon = svariable.end_latlon
    if start_latlon is None or end_latlon is None:
        raise ValueError("start_latlon and end_latlon must both be defined to make a vertical cross-section")
    start_point = CoordPair(lat=start_latlon[0], lon=start_latlon[1])
    end_point = CoordPair(lat=end_latlon[0], lon=end_latlon[1])

    levs = np.linspace(svariable.range_min, svariable.range_max, svariable.nlevs)
    ticklevs = np.linspace(svariable.range_min, svariable.range_max, svariable.nlevs)

    # Extract variable along pressure coordinates
    var =  getvar(ncfile, svariable.wrfname)
    dtime = str(var.Time.values)[0:19]
    p = getvar(ncfile, "pressure")
    var_cross = vertcross(
        var,
        p,
        wrfin=ncfile,
        start_point=start_point,
        end_point=end_point,
        latlon=True,
        meta=True
    )

    # Create a figure
    fig = plt.figure(figsize=(10.88, 8.16), dpi=dpi)
    ax = plt.axes()
    coord_pairs = to_np(var_cross.coords["xy_loc"])
    var_contours = ax.contourf(
        np.arange(coord_pairs.shape[0]),
        to_np(var_cross["vertical"]),
        to_np(var_cross),
        levels=levs,
        cmap=get_cmap(svariable.colormap)
    )
    col_bar = plt.colorbar(
        var_contours,
        extendfrac=[0.01, 0.01],
        ticks=ticklevs
    )

    # Make overlay line-plot
    if svariable.overlap_sv is not None:
        ov_svar = set_variable(svariable.overlap_sv)
        ov_var =  getvar(ncfile, ov_svar.wrfname)
        ov_cross = vertcross(
            ov_var,
            p,
            wrfin=ncfile,
            start_point=start_point,
            end_point=end_point,
            latlon=True,
            meta=True
        )
        min_ov = np.nanmin(ov_cross)
        max_ov = np.nanmax(ov_cross)
        gap = svariable.overlap_gap
        # Adjusts to the nearest multiple of overlap_gap
        adjusted_min_ov = int(min_ov - (min_ov % gap))
        adjusted_max_ov = int(max_ov + (gap - (max_ov % gap)) % gap)
        olevs = list(range(adjusted_min_ov, adjusted_max_ov, gap))
        ov_contour = ax.contour(
            np.arange(coord_pairs.shape[0]),
            to_np(ov_cross["vertical"]),
            to_np(ov_cross),
            levels=olevs,
            linewidths=0.4,
            cmap=svariable.overlap_cmap,
            linestyles='dashed'
        )
        plt.clabel(ov_contour, inline=True, fontsize=10, levels=olevs[0::2])

    # Arrange x-axis labels - latlon pairs
    x_ticks = np.arange(coord_pairs.shape[0])
    x_labels = [
        pair.latlon_str(fmt="{:.2f}, {:.2f}") for pair in to_np(coord_pairs)
    ]
    ax.set_xticks(x_ticks[::20])
    ax.set_xticklabels(x_labels[::20], rotation=45, fontsize=10)
    ax.set_xlabel("Latitude/Longitude", fontsize=12)

    # Arrange y-axis labels - pressure
    ax.set_yscale('symlog')
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks(
        np.linspace(svariable.plim_top, svariable.plim_bottom, svariable.plevs)
    )
    ax.set_ylim(svariable.plim_bottom, svariable.plim_top)
    ax.set_ylabel("Pressure (hPa)", fontsize=12)

    if time_tag:
        plt.title(f"{svariable.ptitle} at {dtime}")
    else:
        plt.title(f"{svariable.ptitle}")

    plt.tight_layout()

    if return_fig:
        return fig
    else:
        plt.savefig(outfname)
        if save_pdf:
            plt.savefig(outfname.replace(".png", ".pdf"))
        plt.close(fig)

