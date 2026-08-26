# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm, BoundaryNorm
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path
import cartopy
from wrf import to_np, smooth2d, get_cartopy, cartopy_xlim, cartopy_ylim, latlon_coords

_pkg_data_dir = Path(__file__).resolve().parent / "cartopy_data"
if _pkg_data_dir.exists():
    cartopy.config["data_dir"] = str(_pkg_data_dir)

import wrf_analysis_toolkit.SensibleVariables as sv

# from datetime import datetime      ###############################################
# print(datetime.now())              ###############################################


def Plot2DField(
    var,
    svariable,
    windbarbs=0,
    outfname="MyPlot.png",
    overlap=None,
    u=None,
    v=None,
    smooth=1,
    region="full",
    region_ticks=False,
    us_states=False,
    nlevs=10,
    time_tag=1,
    return_fig=0,
    dpi=100,
    save_pdf=0,
):
    # Input check

    # Need to implement input check here!

    # Gets timestamp
    dtime = str(var.Time.values)[0:19]

    # Smooth the variable
    if smooth:
        smooth_var = smooth2d(var, 3, cenweight=4)
    else:
        smooth_var = var
    thismin = np.nanmin((smooth_var.values))
    thismax = np.nanmax((smooth_var.values))
    # print("min=",thismin," max=",thismax)

    # Get the latitude and longitude points
    lats, lons = latlon_coords(var)
    x = to_np(lons)
    y = to_np(lats)

    # Get the cartopy mapping object
    cart_proj = get_cartopy(var)

    # Create a figure
    fig = plt.figure(figsize=(10.88, 8.16), dpi=dpi)

    # Set the GeoAxes to the projection used by WRF
    ax = plt.axes(projection=cart_proj)

    # Download and add the borders and coastlines	####Takes ~2s
    borders = cartopy.feature.BORDERS.with_scale("50m")
    ax.add_feature(borders, linewidth=0.4, edgecolor="black")
    ax.coastlines("50m", linewidth=0.8)

    # Add U.S. state borders
    if us_states:
        states_feature = cartopy.feature.STATES.with_scale("50m")
        ax.add_feature(states_feature, linestyle=':', linewidth=0.3, edgecolor='black')

    # Filled contours
    z = to_np(smooth_var)
    match svariable.scale:
        case "linear":
            nticks = svariable.nticks
            nlevs = svariable.nlevs
            levs = np.linspace(svariable.range_min, svariable.range_max, nlevs)
            norm = Normalize(svariable.range_min, svariable.range_max)
            ticklevs = np.linspace(svariable.range_min, svariable.range_max, nticks)
        case "log":
            levs = np.logspace(
                svariable.range_min,
                svariable.range_max,
                num=svariable.nlevs,
                base=svariable.logbase,
            )
            norm = LogNorm(
                svariable.logbase**svariable.range_min,
                svariable.logbase**svariable.range_max,
            )
            z = np.ma.masked_where(z <= 0, z)
            ticklevs = np.logspace(
                svariable.range_min,
                svariable.range_max,
                num=svariable.nlevs,
                base=svariable.logbase,
            )
        case "bounds":
            levs = svariable.bounds
            norm = BoundaryNorm(levs, len(levs))
            if svariable.hide_edge_ticks:
                ticklevs = levs[1:-1]
            else:
                ticklevs = levs
    contour_fills = plt.contourf(
        x,
        y,
        z,
        levels=levs,
        norm=norm,
        transform=cartopy.crs.PlateCarree(),
        cmap=svariable.colormap,
        alpha=0.8,
        extend="both",
        zorder=1,
    )
    if svariable.contour_color is not None:
        contour_lines = plt.contour(
            x,
            y,
            z,
            levels=levs,
            colors=svariable.contour_color,
            linewidths=0.4,
            transform=cartopy.crs.PlateCarree(),
            extend="both",
            zorder=2,
        )
        if svariable.contour_c_labels:
            plt.clabel(contour_lines, inline=True, fontsize=8, levels=ticklevs)
    # Add a color bar
    col_bar = plt.colorbar(contour_fills, extendfrac=[0.01, 0.01], ticks=ticklevs)
    if svariable.contour_color is not None:
        col_bar.add_lines(contour_lines)
    plt.annotate(
        "v",
        xy=(
            1.11,
            (
                (thismin - svariable.range_min)
                / (svariable.range_max - svariable.range_min)
            )
            + 0.00,
        ),
        xycoords="axes fraction",
        fontsize=10,
    )
    plt.annotate(
        "ʌ",
        xy=(
            1.11,
            (
                (thismax - svariable.range_min)
                / (svariable.range_max - svariable.range_min)
            )
            - 0.015,
        ),
        xycoords="axes fraction",
        fontsize=10,
    )

    # Overlap empty contours
    if overlap is not None:
        # Smooth the overlap variable
        if smooth:
            smooth_overlap = smooth2d(overlap, 3, cenweight=4)
        else:
            smooth_overlap = overlap

        z = to_np(smooth_overlap)

        min_z = np.nanmin(z)
        max_z = np.nanmax(z)
        gap = svariable.overlap_gap
        # Adjusts to the nearest multiple of overlap_gap
        adjusted_min_z = int(min_z - (min_z % gap))
        adjusted_max_z = int(max_z + (gap - (max_z % gap)) % gap)
        olevs = list(range(adjusted_min_z, adjusted_max_z, gap))
        ov = plt.contour(
            x,
            y,
            z,
            levels=olevs,
            linewidths=0.4,
            cmap=svariable.overlap_cmap,
            transform=cartopy.crs.PlateCarree(),
        )
        plt.clabel(ov, inline=True, fontsize=10, levels=olevs[0::2])

    if windbarbs:
        # Convert u and v components to knots
        u = to_np(u)
        v = to_np(v)
        u = u * 1.94384
        v = v * 1.94384
        # Add wind barbs, only plotting every nbarbs
        nbarbs = svariable.windbarb_gap
        ax.barbs(
            x[::nbarbs, ::nbarbs],
            y[::nbarbs, ::nbarbs],
            u[::nbarbs, ::nbarbs],
            v[::nbarbs, ::nbarbs],
            transform=cartopy.crs.PlateCarree(),
            length=7,
            linewidth=1.0,
        )

    # Set the map bounds
    if region == "full":  # Get limits from the WRF data
        ax.set_xlim(cartopy_xlim(smooth_var))
        ax.set_ylim(cartopy_ylim(smooth_var))
    else:  # expect string of 4 comma-separated floats: "min_x,max_x,min_y,max_y"
        reg_split = [float(x) for x in region.split(",")]
        if len(reg_split) == 4:
            ax.set_xlim([reg_split[0], reg_split[1]])
            ax.set_ylim([reg_split[2], reg_split[3]])
        else:
            raise ValueError(
                f"Invalid region specification: {region}."
                " Expected 'full' or 'min_x,max_x,min_y,max_y'"
            )

    if svariable.start_latlon and svariable.end_latlon:
        se_lons = np.array([svariable.start_latlon[1], svariable.end_latlon[1]])
        se_lats = np.array([svariable.start_latlon[0], svariable.end_latlon[0]])
        print(f"Drawing line between {svariable.start_latlon} and {svariable.end_latlon}")
        xy_pts = cart_proj.transform_points(
            cartopy.crs.PlateCarree(),
            se_lons,
            se_lats,
        )
        plt.plot(
            xy_pts[:, 0],
            xy_pts[:, 1],
            color='black', linestyle='-', linewidth=2,
            zorder=3,
        )

    # Add the gridlines
    add_lat_lon_ticks(ax, region_ticks)
    if region_ticks:
        add_projected_ticks(ax)
        add_grid_ticks(ax, lats, lons, cart_proj)

    # Add title and frame time
    plt.title(svariable.ptitle)
    if time_tag:
        plt.annotate(dtime, xy=(0.02, -0.03), xycoords="axes fraction")

    if return_fig:
        return fig
    else:
        plt.savefig(outfname)
        if save_pdf:
            plt.savefig(outfname.replace(".png", ".pdf"))
        plt.close(fig)


def add_lat_lon_ticks(ax, draw_labels, nbins=6):
    gl = ax.gridlines(color="black", linestyle="dotted")
    gl.xlocator = mticker.MaxNLocator(nbins=nbins)
    gl.ylocator = mticker.MaxNLocator(nbins=nbins)

    gl.draw_labels = draw_labels
    gl.x_inline = False
    gl.top_labels = draw_labels
    gl.bottom_labels = False
    gl.xformatter = cartopy.mpl.gridliner.LONGITUDE_FORMATTER
    gl.y_inline = False
    gl.right_labels = False
    gl.left_labels = draw_labels
    gl.yformatter = cartopy.mpl.gridliner.LATITUDE_FORMATTER


def add_projected_ticks(ax, nbins=10):

    x_locator = mticker.MaxNLocator(nbins=nbins)
    y_locator = mticker.MaxNLocator(nbins=nbins)
    x_limits = ax.get_xlim()
    y_limits = ax.get_ylim()
    x_min, x_max = sorted(x_limits)
    y_min, y_max = sorted(y_limits)

    # Keep only ticks inside current limits to avoid expanding the plotted area.
    x_ticks = x_locator.tick_values(x_min, x_max)
    y_ticks = y_locator.tick_values(y_min, y_max)
    x_ticks = x_ticks[(x_ticks >= x_min) & (x_ticks <= x_max)]
    y_ticks = y_ticks[(y_ticks >= y_min) & (y_ticks <= y_max)]

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_xlim(x_limits)
    ax.set_ylim(y_limits)
    ax.tick_params(
        axis="x",
        bottom=True,
        top=False,
        labelbottom=True,
        labeltop=False,
        labelsize=5,
    )
    ax.tick_params(
        axis="y",
        left=False,
        right=True,
        labelleft=False,
        labelright=True,
        labelsize=5,
    )
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_format_projected_tick))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_format_projected_tick))

    ax.set_axisbelow(True)
    ax.grid(True, which="major", linestyle="--", linewidth=0.4, color="black")

    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
        label.set_rotation_mode("anchor")

    for label in ax.get_yticklabels():
        label.set_rotation(45)
        label.set_ha("left")
        label.set_va("center")
        label.set_rotation_mode("anchor")


def add_grid_ticks(ax, lats, lons, cart_proj, nbins=11, color="0.65"):
    """
    Add approximate WRF grid-index ticks (i,j) to projected map axes.
    lats/lons are 2D arrays for the displayed field.
    """
    ny, nx = lats.shape
    locator = mticker.MaxNLocator(nbins=10, integer=True)

    i_vals = locator.tick_values(0, nx - 1)
    j_vals = locator.tick_values(0, ny - 1)

    i_vals = i_vals[(i_vals >= 0) & (i_vals <= nx - 1)].astype(int)
    j_vals = j_vals[(j_vals >= 0) & (j_vals <= ny - 1)].astype(int)

    # Use middle row/column as representative transects
    j_mid = ny // 2
    i_mid = nx // 2

    # Convert selected lon/lat points to projected map coordinates
    pc = cartopy.crs.PlateCarree()

    x_pts = cart_proj.transform_points(
        pc,
        lons[j_mid, i_vals],
        lats[j_mid, i_vals],
    )[:, 0]

    y_pts = cart_proj.transform_points(
        pc,
        lons[j_vals, i_mid],
        lats[j_vals, i_mid],
    )[:, 1]

    # Keep only ticks inside current visible bounds
    x0, x1 = sorted(ax.get_xlim())
    y0, y1 = sorted(ax.get_ylim())
    x_mask = (x_pts >= x0) & (x_pts <= x1)
    y_mask = (y_pts >= y0) & (y_pts <= y1)

    ax_x = ax.secondary_xaxis("bottom")
    ax_y = ax.secondary_yaxis("right")

    ax_x.set_xticks(x_pts[x_mask])
    ax_x.set_xticklabels([str(i) for i in i_vals[x_mask]], color=color)
    ax_x.tick_params(axis="x", colors=color, labelsize=5, pad=2)

    ax_y.set_yticks(y_pts[y_mask])
    ax_y.set_yticklabels([str(j) for j in j_vals[y_mask]], color=color)
    ax_y.tick_params(axis="y", colors=color, labelsize=5, pad=2)

    for spine in ax_x.spines.values():
        spine.set_edgecolor(color)
    for spine in ax_y.spines.values():
        spine.set_edgecolor(color)


def _format_projected_tick(value, _position):
    return f"{value:.1e}"
