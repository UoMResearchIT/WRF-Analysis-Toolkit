# SPDX-FileCopyrightText: 2026 University of Manchester
#4
# SPDX-License-Identifier: apache-2.0

from matplotlib.pyplot import get_cmap
from matplotlib.colors import ListedColormap
import cmasher as cmr


class svariable:
    def __init__(
        self,
        dim=3,
        wrfname=None,
        ptitle=None,
        outfile=None,
        range_min=None,
        range_max=None,
        interpvar="pressure",
        interpvalue=None,
        windbarbs=0,
        windbarb_gap=25,
        isdif=0,
        colormap=get_cmap("jet"),
        under_color=None,
        over_color=None,
        contour_color=None,
        contour_c_labels=True,
        scale="linear",
        nticks=5,
        nlevs=9,
        logbase=10,
        bounds=None,
        hide_edge_ticks=True,
        overlap_sv=None,
        overlap_gap=None,
        overlap_cmap=None,
        lat=None,
        lon=None,
        vcross=False,
        along_traj=None,
        start_latlon=None,
        end_latlon=None,
        plim_bottom=1000,
        plim_top=100,
        plevs=10,
    ):
        self.dim = dim
        self.wrfname = wrfname
        self.ptitle = ptitle
        self.outfile = outfile
        self.range_min = range_min
        self.range_max = range_max
        self.interpvar = interpvar
        self.interpvalue = interpvalue
        self.windbarbs = windbarbs
        self.windbarb_gap = windbarb_gap
        self.isdif = isdif
        self.colormap = colormap
        if under_color is not None:
            self.colormap.set_under(under_color)
        if over_color is not None:
            self.colormap.set_over(over_color)
        self.contour_color = contour_color
        self.contour_c_labels = contour_c_labels
        self.scale = scale
        self.nticks = nticks
        self.nlevs = nlevs
        self.logbase = logbase
        self.bounds = bounds
        self.hide_edge_ticks = hide_edge_ticks
        self.overlap_sv = overlap_sv
        self.overlap_gap = overlap_gap
        self.overlap_cmap = overlap_cmap
        self.lat = lat
        self.lon = lon
        self.along_traj = along_traj
        self.vcross=vcross,
        self.start_latlon=start_latlon
        self.end_latlon=end_latlon
        self.plim_bottom=plim_bottom
        self.plim_top=plim_top
        self.plevs=plevs

def get_sv_names():
    """Return names of declared sensible variables in this module."""
    names = [name for name, value in globals().items() if isinstance(value, svariable)]
    return sorted(names)


def get_sv_places():
    """Return names of declared locations (SkewT) in this module."""
    names = get_sv_names()
    places = [name.replace("SkewT_", "") for name in names if name.startswith("SkewT_")]
    places = [place for place in places if place not in ["Trajectory"]]
    return sorted(places)


# 2D + Field
TerrainElevation = svariable(
    wrfname="ter",
    ptitle="Terrain elevation [m]",
    outfile="TerrainElevation",
    range_min=0,
    range_max=2000,
    colormap=ListedColormap(
        [
            "mediumblue",
            "darkgreen",
            "green",
            "limegreen",
            "lawngreen",
            "yellow",
            "gold",
            "sienna",
            "burlywood",
            "linen",
            "white",
        ]
    ),
    scale="bounds",
    bounds=[
        -0.05,
        1,
        200,
        400,
        600,
        800,
        1000,
        1200,
        1400,
        1600,
        1800,
        2000,
    ],
)
TerrainElevation1000 = svariable(
    wrfname="ter",
    ptitle="Terrain elevation [m]",
    outfile="TerrainElevation",
    range_min=0,
    range_max=1000,
    colormap=ListedColormap(
        [
            "mediumblue",
            "darkgreen",
            "green",
            "limegreen",
            "lawngreen",
            "yellow",
            "gold",
            "sienna",
            "burlywood",
            "linen",
            "white",
        ]
    ),
    scale="bounds",
    bounds=[
        -0.05,
        1,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
    ],
)
SeaLevelPressure = svariable(
    wrfname="slp",
    ptitle="Sea level pressure [hPa]",
    outfile="SeaLevelPressure",
    nticks=12,
    nlevs=12,
    range_min=986,
    range_max=1030,
    windbarbs=1,
    colormap=get_cmap("Purples"),
)
SeaLevelPressure1hPa = svariable(
    wrfname="slp",
    ptitle="Sea level pressure [hPa]",
    outfile="SeaLevelPressure1hPa",
    range_min=986,
    range_max=1030,
    nticks=12,
    nlevs=45,
    windbarbs=1,
    colormap=get_cmap("Purples"),
    contour_color="navy",
)
SeaLevelPressure2hPa = svariable(
    wrfname="slp",
    ptitle="Sea level pressure [hPa]",
    outfile="SeaLevelPressure2hPa",
    range_min=986,
    range_max=1030,
    nticks=12,
    nlevs=23,
    windbarbs=1,
    colormap=get_cmap("Purples"),
    contour_color="navy",
)
AirTemp2m = svariable(
    wrfname="T2",
    ptitle="Temperature at 2m [K]",
    outfile="AirTemp2m",
    nticks=11,
    nlevs=61,
    range_min=270,
    range_max=330,
    colormap=get_cmap("Reds"),
    contour_color="maroon",
)
DewpointTemp2m = svariable(
    wrfname="td2",
    ptitle="Dewpoint Temperature at 2m [C]",
    outfile="DewpointTemp2m",
    nticks=12,
    nlevs=56,
    range_min=-20,
    range_max=35,
    colormap=get_cmap("BuPu"),
    contour_color="indigo",
)
RelativeHumidity2m = svariable(
    wrfname="rh2",
    ptitle="Relative Humidity at 2m [%]",
    outfile="RelHum2m",
    range_min=0,
    range_max=100,
    colormap=get_cmap("YlGnBu"),
)
PotentialTemp2m = svariable(
    wrfname="TH2",
    ptitle="Potential temperature at 2m [K]",
    outfile="PotTemp2m",
    nticks=11,
    nlevs=21,
    range_min=280,
    range_max=320,
    colormap=get_cmap("Reds"),
)
CAPE = svariable(
    wrfname="cape_2d",
    ptitle="Max CAPE (Convective Available Potential Energy) [J/kg]",
    outfile="CAPE",
    #    range_min=0,
    #    range_max=6000,
    #    colormap=get_cmap("BuGn"))
    scale="bounds",
    colormap=ListedColormap(
        [
            "#ffffff",
            "#ffffcc",
            "#ffeda0",
            "#fed976",
            "#feb24c",
            "#fd8d3c",
            "#fc4e2a",
            "#e31a1c",
            "#bd0026",
            "#800026",
        ]
    ),
    bounds=[
        -0.1,
        0,
        10,
        50,
        100,
        250,
        500,
        1000,
        1500,
        2000,
        4000,
    ],
    range_min=0,
    range_max=6000,
)
CIN = svariable(
    wrfname="cape_2d",
    ptitle="Max CIN (Convective Inhibition) [J/kg]",
    outfile="CIN",
    #    range_min=0,
    #    range_max=1600,
    #    colormap=get_cmap("BuGn"))
    scale="bounds",
    colormap=ListedColormap(
        [
            "#ffffff",
            "#ffffd9",
            "#edf8b1",
            "#c7e9b4",
            "#7fcdbb",
            "#41b6c4",
            "#1d91c0",
            "#225ea8",
            "#253494",
            "#081d58",
        ]
    ),
    bounds=[-0.1, 0, 10, 25, 50, 100, 200, 400, 600, 800, 1000],
    range_min=0,
    range_max=3000,
)
CIN_YlGnBu = svariable(
    wrfname="cape_2d",
    ptitle="Max CIN (Convective Inhibition) [J/kg]",
    outfile="CIN_YlGnBu",
    range_min=0,
    range_max=1800,
    colormap=get_cmap("YlGnBu"),
)
CIN_YlGn = svariable(
    wrfname="cape_2d",
    ptitle="Max CIN (Convective Inhibition) [J/kg]",
    outfile="CIN_YlGn",
    scale="bounds",
    colormap=cmr.get_sub_cmap("YlGnBu", 0.0, 0.5, N=5),
    contour_color="darkgreen",
    contour_c_labels=False,
    bounds=[0, 10, 50, 100, 500, 1000],
    hide_edge_ticks=False,
    range_min=0,
    range_max=3000,
)
Rain = svariable(
    wrfname="RAINC",
    ptitle="Total Hourly Precipitation [mm]",
    outfile="Rain",
    windbarbs=1,
    isdif=1,
    ##################### Blues
    scale="linear",
    colormap=get_cmap("Blues"),
    range_min=0,
    range_max=60,
    nlevs=7,
    nticks=7,
    #####################
    ##################### Log
    # scale="log",
    # colormap=ListedColormap(
    #     [
    #         "white",
    #         "cyan",
    #         # "cornflowerblue",
    #         "blue",
    #         "darkgreen",
    #         "gold",
    #         "darkorange",
    #         "red",
    #         "magenta",
    #         "purple",
    #     ]
    # ),
    # nlevs=10,
    # logbase=2,
    # range_min=-3,
    # range_max=6,
    #####################
    ##################### Manunicast
    # scale="bounds",
    # colormap=ListedColormap(
    #     [
    #         "white",
    #         "cyan",
    #         "cornflowerblue",
    #         "blue",
    #         "lawngreen",
    #         "limegreen",
    #         "green",
    #         "darkgreen",
    #         "yellow",
    #         "gold",
    #         "darkorange",
    #         "red",
    #         "firebrick",
    #         "darkred",
    #         "magenta",
    #         "darkviolet",
    #         "bisque",
    #     ]
    # ),
    # bounds=[-0.1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    # range_min=0,
    # range_max=16,
    #####################
    ##################### Manuni-Log
    # scale="bounds",
    # colormap=ListedColormap(
    #     [
    #         "white",
    #         "cyan",
    #         "cornflowerblue",
    #         "blue",
    #         "lawngreen",
    #         "limegreen",
    #         # "green",
    #         "darkgreen",
    #         "yellow",
    #         "gold",
    #         "darkorange",
    #         "red",
    #         # "firebrick",
    #         "darkred",
    #         "magenta",
    #         "darkviolet",
    #         # "bisque",
    #     ]
    # ),
    # bounds=[-0.1, 0.5, 1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 60],
    # range_min=0,
    # range_max=60,
    #####################
)
SimRadarReflectivityMax = svariable(
    wrfname="mdbz",
    ptitle="Maximum simulated radar reflectivity[dBZ]",
    outfile="SimRadarReflMax",
    windbarbs=1,
    scale="bounds",
    colormap=ListedColormap(
        [
            "white",
            "cyan",
            "deepskyblue",
            "blue",
            "steelblue",
            "lawngreen",
            "green",
            "gold",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
            "indigo",
            "rebeccapurple",
            "mediumpurple",
            "lavender",
        ]
    ),
    bounds=[-0.1, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
    range_min=0,
    range_max=64,
)

# 3D + Field
AirTemp = svariable(
    dim=4,
    wrfname="temp",
    ptitle=f"Air Temperature [K]",
    outfile=f"AirTemp",
    colormap=get_cmap("Reds"),
    nticks=15,
    nlevs=15,
    range_min=240,
    range_max=310,
)
AirTemp925 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature at 925 hPa [K]",
    outfile="AirTemp925",
    nticks=12,
    nlevs=23,
    range_min=270,
    range_max=314,
    interpvar="pressure",
    interpvalue=925,
    colormap=get_cmap("Reds"),
)
AirTemp850 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature at 850 hPa [K]",
    outfile="AirTemp850",
    nticks=12,
    nlevs=23,
    range_min=270,
    range_max=314,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("Reds"),
)
AirTemp700 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature at 700 hPa [K]",
    outfile="AirTemp700",
    nticks=12,
    nlevs=23,
    range_min=270,
    range_max=314,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("Reds"),
)
AirTemp500 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature at 500 hPa [K]",
    outfile="AirTemp500",
    nticks=9,
    nlevs=41,
    range_min=240,
    range_max=280,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("Reds"),
    contour_color="maroon",
)
AirTemp300 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature at 300 hPa [K]",
    outfile="AirTemp300",
    nticks=9,
    nlevs=41,
    range_min=240,
    range_max=280,
    interpvar="pressure",
    interpvalue=300,
    colormap=get_cmap("Reds"),
    contour_color="maroon",
)
AirTempDif6h850 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 6h at 850 hPa [K]",
    outfile="AirTempDif6h850",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("seismic"),
)
AirTempDif6h700 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 6h at 700 hPa [K]",
    outfile="AirTempDif6h700",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("seismic"),
)
AirTempDif6h500 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 6h at 500 hPa [K]",
    outfile="AirTempDif6h500",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("seismic"),
)
AirTempDif12h850 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 12h at 850 hPa [K]",
    outfile="AirTempDif12h850",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("seismic"),
)
AirTempDif12h700 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 12h at 700 hPa [K]",
    outfile="AirTempDif12h700",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("seismic"),
)
AirTempDif12h500 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Temperature change in 12h at 500 hPa [K]",
    outfile="AirTempDif12h500",
    range_min=-12,
    range_max=12,
    nticks=9,
    nlevs=9,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("seismic"),
)

DewpointTemp = svariable(
    dim=4,
    wrfname="td",
    ptitle=f"Dewpoint Temperature [C]",
    outfile=f"DewpointTemp",
    colormap=get_cmap("BuPu"),
    range_min=-75,
    range_max=25,
)
DewpointTemp925 = svariable(
    dim=4,
    wrfname="td",
    ptitle="Dewpoint Temperature at 925hPa [C]",
    outfile="DewpointTemp925",
    range_min=-75,
    range_max=25,
    interpvar="pressure",
    interpvalue=925,
    colormap=get_cmap("BuPu"),
)
DewpointTemp850 = svariable(
    dim=4,
    wrfname="td",
    ptitle="Dewpoint Temperature at 850hPa [C]",
    outfile="DewpointTemp850",
    range_min=-75,
    range_max=25,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("BuPu"),
)
DewpointTemp700 = svariable(
    dim=4,
    wrfname="td",
    ptitle="Dewpoint Temperature at 700hPa [C]",
    outfile="DewpointTemp700",
    range_min=-75,
    range_max=25,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("BuPu"),
)
DewpointTemp500 = svariable(
    dim=4,
    wrfname="td",
    ptitle="Dewpoint Temperature at 500hPa [C]",
    outfile="DewpointTemp500",
    range_min=-75,
    range_max=25,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("BuPu"),
)
DewpointTemp300 = svariable(
    dim=4,
    wrfname="td",
    ptitle="Dewpoint Temperature at 300hPa [C]",
    outfile="DewpointTemp300",
    range_min=-75,
    range_max=25,
    interpvar="pressure",
    interpvalue=300,
    colormap=get_cmap("BuPu"),
)

RelativeHumidity = svariable(
    dim=4,
    wrfname="rh",
    ptitle=f"Relative Humidity [%]",
    outfile=f"RelativeHumidity",
    colormap=get_cmap("YlGnBu"),
    range_min=0,
    range_max=100,
    nticks=11,
    nlevs=21,
)
RelativeHumidity925 = svariable(
    dim=4,
    wrfname="rh",
    ptitle="Relative Humidity at 925hPa [%]",
    outfile="RelHum925",
    range_min=0,
    range_max=100,
    interpvar="pressure",
    interpvalue=925,
    colormap=get_cmap("YlGnBu"),
)
RelativeHumidity850 = svariable(
    dim=4,
    wrfname="rh",
    ptitle="Relative Humidity at 850hPa [%]",
    outfile="RelHum850",
    range_min=0,
    range_max=100,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("YlGnBu"),
)
RelativeHumidity700 = svariable(
    dim=4,
    wrfname="rh",
    ptitle="Relative Humidity at 700hPa [%]",
    outfile="RelHum700",
    range_min=0,
    range_max=100,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("YlGnBu"),
)
RelativeHumidity500 = svariable(
    dim=4,
    wrfname="rh",
    ptitle="Relative Humidity at 500hPa [%]",
    outfile="RelHum500",
    range_min=0,
    range_max=100,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("YlGnBu"),
)
RelativeHumidity300 = svariable(
    dim=4,
    wrfname="rh",
    ptitle="Relative Humidity at 300hPa [%]",
    outfile="RelHum300",
    range_min=0,
    range_max=100,
    interpvar="pressure",
    interpvalue=300,
    colormap=get_cmap("YlGnBu"),
)

PotentialTemp = svariable(
    dim=4,
    wrfname="theta",
    ptitle=f"Potential temperature [K]",
    outfile=f"PotTemp",
    colormap=get_cmap("Reds"),
    range_min=270,
    range_max=335,
    nticks=13,
    nlevs=25,
)
PotentialTemp925 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 925hPa [K]",
    outfile="PotTemp925",
    nticks=13,
    nlevs=25,
    range_min=270,
    range_max=330,
    interpvar="pressure",
    interpvalue=925,
    colormap=get_cmap("Reds"),
)
PotentialTemp850 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 850hPa [K]",
    outfile="PotTemp850",
    nticks=11,
    nlevs=21,
    range_min=280,
    range_max=330,
    interpvar="pressure",
    interpvalue=850,
    colormap=get_cmap("Reds"),
)
PotentialTemp800 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 800hPa [K]",
    outfile="PotTemp800",
    nticks=11,
    nlevs=21,
    range_min=280,
    range_max=330,
    interpvar="pressure",
    interpvalue=800,
    colormap=get_cmap("Reds"),
)
PotentialTemp700 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 700hPa [K]",
    outfile="PotTemp700",
    nticks=11,
    nlevs=21,
    range_min=285,
    range_max=335,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("Reds"),
)
PotentialTemp600 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 600hPa [K]",
    outfile="PotTemp600",
    nticks=11,
    nlevs=21,
    range_min=285,
    range_max=335,
    interpvar="pressure",
    interpvalue=600,
    colormap=get_cmap("Reds"),
)
PotentialTemp500 = svariable(
    dim=4,
    wrfname="theta",
    ptitle="Potential temperature at 500hPa [K]",
    outfile="PotTemp500",
    nticks=11,
    nlevs=21,
    range_min=285,
    range_max=335,
    interpvar="pressure",
    interpvalue=500,
    colormap=get_cmap("Reds"),
)


def create_GeoPotHeight_at(
    interpvalue, range_min=5340, range_max=6060, nticks=13, nlevs=13
):
    return svariable(
        dim=4,
        ptitle=f"Geopotential Height at {interpvalue}hPa [m]",
        outfile=f"GeoPotHeight{interpvalue}",
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
        windbarbs=1,
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=get_cmap("Greens"),
        contour_color="darkslategray",
        contour_c_labels=False,
    )


GeoPotHeight925 = create_GeoPotHeight_at(
    925,
    range_min=480,
    range_max=1020,
    nticks=10,
    nlevs=10,
)
GeoPotHeight850 = create_GeoPotHeight_at(
    850,
    range_min=1080,
    range_max=1800,
    nticks=7,
    nlevs=13,
)
GeoPotHeight700 = create_GeoPotHeight_at(
    700,
    range_min=2700,
    range_max=3420,
    nticks=7,
    nlevs=13,
)
GeoPotHeight500 = create_GeoPotHeight_at(
    500,
    range_min=5280,
    range_max=6120,
    nticks=8,
    nlevs=15,
)
GeoPotHeight300 = create_GeoPotHeight_at(
    300,
    range_min=8700,
    range_max=10020,
    nticks=12,
    nlevs=12,
)

StaticStability700500 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Static stability at 700-500 hPa [C]",
    outfile="StaticStability700500",
    nticks=13,
    nlevs=25,
    range_min=6,
    range_max=30,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("Oranges"),
)
StaticStability850700 = svariable(
    dim=4,
    wrfname="temp",
    ptitle="Static stability at 850-700 hPa [C]",
    outfile="StaticStability850700",
    nticks=14,
    nlevs=27,
    range_min=-4,
    range_max=22,
    interpvar="pressure",
    interpvalue=700,
    colormap=get_cmap("Oranges"),
    contour_color="maroon",
)
SimRadarReflectivity1km = svariable(
    dim=4,
    wrfname="dbz",
    ptitle="Simulated radar reflectivity at 1km [dBZ]",
    outfile="SimRadarRefl1km",
    interpvar="z",
    interpvalue=1000,
    windbarbs=1,
    scale="bounds",
    colormap=ListedColormap(
        [
            "white",
            "cyan",
            "deepskyblue",
            "blue",
            "steelblue",
            "lawngreen",
            "green",
            "gold",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
            "indigo",
            "rebeccapurple",
            "mediumpurple",
            "lavender",
        ]
    ),
    bounds=[-0.1, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
    range_min=0,
    range_max=64,
)
InstRain = svariable(
    # Uses simulated radar reflectivity at 1km (Z) to calculate
    # instantaneous precipitation rate (R) from:   Z=200R^1.6
    dim=4,
    wrfname="dbz",
    ptitle="Instantaneous Precipitation Rate [mm/h]",
    outfile="InstRain",
    interpvar="z",
    interpvalue=1000,
    scale="bounds",
    colormap=ListedColormap(
        [
            "indigo",
            "royalblue",
            "teal",
            "lime",
            "yellow",
            "darkorange",
            "red",
            "deeppink",
            "gainsboro",
            "darkgray",
            "dimgray",
        ]
    ),
    under_color="white",
    bounds=[0.1, 0.2, 0.5, 1, 2, 4, 8, 16, 32, 64, 96, 128],
    hide_edge_ticks=False,
    range_min=0,
    range_max=128,
)

Frontogenesis925 = svariable(
    dim=4,
    ptitle="Petterssen Frontogenesis at 925 hPa [K/(100km 3h)]",
    outfile="Frontogenesis925",
    overlap_sv="PotentialTemp925",
    overlap_gap=1,
    overlap_cmap=get_cmap("coolwarm"),
    windbarbs=1,
    interpvar="pressure",
    interpvalue=925,
    scale="bounds",
    bounds=[-16, -8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8, 16],
    colormap=ListedColormap(
        [
            "midnightblue",
            "darkblue",
            "blue",
            "deepskyblue",
            "cyan",
            "white",
            "yellow",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
        ]
    ),
    range_min=-8,
    range_max=8,
)
Frontogenesis850 = svariable(
    dim=4,
    ptitle="Petterssen Frontogenesis at 850 hPa [K/(100km 3h)]",
    outfile="Frontogenesis850",
    overlap_sv="PotentialTemp850",
    overlap_gap=1,
    overlap_cmap=get_cmap("coolwarm"),
    windbarbs=1,
    interpvar="pressure",
    interpvalue=850,
    scale="bounds",
    bounds=[-16, -8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8, 16],
    colormap=ListedColormap(
        [
            "midnightblue",
            "darkblue",
            "blue",
            "deepskyblue",
            "cyan",
            "white",
            "yellow",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
        ]
    ),
    range_min=-8,
    range_max=8,
)
Frontogenesis700 = svariable(
    dim=4,
    ptitle="Petterssen Frontogenesis at 700 hPa [K/(100km 3h)]",
    outfile="Frontogenesis700",
    overlap_sv="PotentialTemp700",
    overlap_gap=1,
    overlap_cmap=get_cmap("coolwarm"),
    windbarbs=1,
    interpvar="pressure",
    interpvalue=700,
    scale="bounds",
    bounds=[-16, -8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8, 16],
    colormap=ListedColormap(
        [
            "midnightblue",
            "darkblue",
            "blue",
            "deepskyblue",
            "cyan",
            "white",
            "yellow",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
        ]
    ),
    range_min=-8,
    range_max=8,
)
Frontogenesis500 = svariable(
    dim=4,
    ptitle="Petterssen Frontogenesis at 500 hPa [K/(100km 3h)]",
    outfile="Frontogenesis500",
    overlap_sv="PotentialTemp500",
    overlap_gap=1,
    overlap_cmap=get_cmap("coolwarm"),
    windbarbs=1,
    interpvar="pressure",
    interpvalue=500,
    scale="bounds",
    bounds=[-16, -8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8, 16],
    colormap=ListedColormap(
        [
            "midnightblue",
            "darkblue",
            "blue",
            "deepskyblue",
            "cyan",
            "white",
            "yellow",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
        ]
    ),
    range_min=-8,
    range_max=8,
)
Frontogenesis = svariable(
    dim=4,
    ptitle="Petterssen Frontogenesis [K/(100km 3h)]",
    outfile="Frontogenesis",
    overlap_sv="PotentialTemp",
    overlap_gap=1,
    overlap_cmap=get_cmap("coolwarm"),
    scale="bounds",
    bounds=[-16, -8, -4, -2, -1, -0.5, 0.5, 1, 2, 4, 8, 16],
    colormap=ListedColormap(
        [
            "midnightblue",
            "darkblue",
            "blue",
            "deepskyblue",
            "cyan",
            "white",
            "yellow",
            "darkorange",
            "red",
            "firebrick",
            "darkred",
        ]
    ),
    range_min=-8,
    range_max=8,
)


# Absolute Vorticity
av_range_min = -150
av_range_max = 200
av_max_frac = 0.55 + min(0.45, (av_range_max / (av_range_max - av_range_min)))
av_min_frac = 0.55 + min(0, (av_range_min / (av_range_max - av_range_min)))
av_nticks = 8
av_nlevs = 15
AbsoluteVorticity = svariable(
    dim=4,
    wrfname="avo",
    ptitle=f"Absolute Vorticity [10-5/s]",
    outfile=f"AbsVorticity",
    colormap=cmr.get_sub_cmap("PuOr", av_min_frac, av_max_frac, N=av_nlevs),
    range_min=av_range_min,
    range_max=av_range_max,
    nticks=av_nticks,
    nlevs=av_nlevs
)

def create_AbsoluteVorticity_at(
    interpvalue, overlap_gap=30, range_min=av_range_min, range_max=av_range_max, nticks=av_nticks, nlevs=av_nticks
):
    max_frac = 0.55 + min(0.45, (range_max / (range_max - range_min)))
    min_frac = 0.55 + min(0, (range_min / (range_max - range_min)))
    return svariable(
        dim=4,
        wrfname="avo",
        ptitle=f"Absolute Vorticity at {interpvalue} hPa [10-5/s]",
        outfile=f"AbsVorticity{interpvalue}",
        overlap_sv=f"GeoPotHeight{interpvalue}",
        overlap_gap=overlap_gap,
        overlap_cmap=get_cmap("coolwarm"),
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=cmr.get_sub_cmap("PuOr", min_frac, max_frac, N=nlevs),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
    )


AbsoluteVorticity925 = create_AbsoluteVorticity_at(925)
AbsoluteVorticity850 = create_AbsoluteVorticity_at(850)
AbsoluteVorticity700 = create_AbsoluteVorticity_at(700)
AbsoluteVorticity500 = create_AbsoluteVorticity_at(500, overlap_gap=60)
AbsoluteVorticity300 = create_AbsoluteVorticity_at(300, overlap_gap=120)


# Wetbulb Temperature
Wetbulb = svariable(
    dim=4,
    wrfname="twb",
    ptitle=f"Wetbulb Temperature [K]",
    outfile=f"Wetbulb",
    colormap=cmr.get_sub_cmap("Reds", 0.0, 0.8),
    range_min=214,
    range_max=304,
    nticks=11,
    nlevs=21
)

def create_Wetbulb_at(
    interpvalue, overlap_gap=30, range_min=264, range_max=304, nticks=11, nlevs=21
):
    return svariable(
        dim=4,
        wrfname="twb",
        ptitle=f"Wetbulb Temperature at {interpvalue} hPa [K]",
        outfile=f"Wetbulb{interpvalue}",
        overlap_sv=f"GeoPotHeight{interpvalue}",
        overlap_gap=overlap_gap,
        overlap_cmap=cmr.get_sub_cmap("bone", 0.0, 0.5),
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=cmr.get_sub_cmap("Reds", 0.0, 0.8),
        contour_color="chocolate",
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
    )

Wetbulb925 = create_Wetbulb_at(925)
Wetbulb850 = create_Wetbulb_at(850)
Wetbulb700 = create_Wetbulb_at(700, range_min=254, range_max=294)
Wetbulb500 = create_Wetbulb_at(500, range_min=240, range_max=280, overlap_gap=60)
Wetbulb300 = create_Wetbulb_at(300, range_min=216, range_max=256, overlap_gap=120)


# WindSpeed
WindSpeed = svariable(
    dim=4,
    wrfname="wspd",
    ptitle=f"Wind Speed [m/s]",
    outfile=f"WindSpeed",
    colormap=get_cmap("YlGnBu"),
    nticks=13,
    nlevs=13,
    range_min=0,
    range_max=60,
)

def create_WindSpeed_at(interpvalue, range_min=0, range_max=60, nticks=12, nlevs=12):
    return svariable(
        dim=4,
        wrfname="wspd",
        ptitle=f"Wind Speed at {interpvalue} hPa [m/s]",
        outfile=f"WindSpeed{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=get_cmap("YlGnBu"),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
        windbarbs=True,
    )


WindSpeed925 = create_WindSpeed_at(925)
WindSpeed850 = create_WindSpeed_at(850)
WindSpeed700 = create_WindSpeed_at(700)
WindSpeed500 = create_WindSpeed_at(500)
WindSpeed300 = create_WindSpeed_at(300, range_min=0, range_max=80)

def create_U_at(interpvalue, range_min=0, range_max=60, nticks=12, nlevs=12):
    return svariable(
        dim=4,
        wrfname="U",
        ptitle=f"Wind Speed in West-East direction at {interpvalue} hPa [m/s]",
        outfile=f"U{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=get_cmap("YlGnBu"),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
        windbarbs=True,
    )

U925 = create_U_at(925)
U850 = create_U_at(850)
U700 = create_U_at(700)
U500 = create_U_at(500)
U300 = create_U_at(300, range_min=0, range_max=80)


# Potential Vorticity
pv_range_min = -10
pv_range_max = 10
pv_max_frac = 0.55 + min(0.45, (pv_range_max / (pv_range_max - pv_range_min)))
pv_min_frac = 0.55 + min(0, (pv_range_min / (pv_range_max - pv_range_min)))
pv_nticks = 11
pv_nlevs = 11

PotVorticity = svariable(
    dim=4,
    wrfname="pvo",
    ptitle=f"Potential Vorticity [PVU]",
    outfile=f"PotVorticity",
    colormap=cmr.get_sub_cmap("PuOr", pv_min_frac, pv_max_frac, N=pv_nlevs),
    range_min=pv_range_min,
    range_max=pv_range_max,
    nticks=pv_nticks,
    nlevs=pv_nlevs
)
def create_PotentialVorticity_at(
    interpvalue,
    overlap_gap=30,
    range_min=pv_range_min,
    range_max=pv_range_max,
    nticks=pv_nticks,
    nlevs=pv_nlevs
):
    max_frac = 0.55 + min(0.45, (range_max / (range_max - range_min)))
    min_frac = 0.55 + min(0, (range_min / (range_max - range_min)))
    return svariable(
        dim=4,
        wrfname="pvo",
        ptitle=f"Potential Vorticity at {interpvalue} hPa [PVU]",
        outfile=f"PotVorticity{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=cmr.get_sub_cmap("PuOr", min_frac, max_frac, N=nlevs),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
    )

PotVorticity925 = create_PotentialVorticity_at(925, range_min=-5, range_max=5)
PotVorticity850 = create_PotentialVorticity_at(850, range_min=-5, range_max=5)
PotVorticity700 = create_PotentialVorticity_at(700, range_min=-5, range_max=5)
PotVorticity500 = create_PotentialVorticity_at(500, range_min=-5, range_max=5)
PotVorticity300 = create_PotentialVorticity_at(300, range_min=-10, range_max=10)

# SkewT
# https://www.umr-cnrm.fr/dbfastex/datasets/rsc_data.html
SkewT = svariable(
    ptitle="SkewT at 53.3638,-2.2764",  # WMO_code  Alt[m]
    outfile="SkewT",
    windbarbs=1,
    lat=53.3638,
    lon=-2.2764,
    range_min=-60,
    range_max=40,
)
SkewT_Trajectory = svariable(
    ptitle="SkewT along trajectory",
    outfile="SkewT_Traj",
    along_traj="/traj/csv/path",
    windbarbs=1,
    lat=53.3638,
    lon=-2.2764,
    range_min=-60,
    range_max=40,
)
SkewT_Casablanca = svariable(
    ptitle="SkewT at 33.57,-7.67 (MOROCCO Casablanca)",  # 60155    56
    outfile="SkewT_Gibraltar",
    windbarbs=1,
    lat=33.57,
    lon=-7.67,
    range_min=-60,
    range_max=40,
)
SkewT_Algeria = svariable(
    ptitle="SkewT at 31.62,-2.23 (ALGERIA Bechar)",  # 60571  81
    outfile="SkewT_Algeria",
    windbarbs=1,
    lat=31.62,
    lon=-2.23,
    range_min=-60,
    range_max=40,
)
SkewT_Lerwick = svariable(
    ptitle="SkewT at 60.13,-1.18 (UK Lerwick)",  # 03005  82
    outfile="SkewT_Lerwick",
    windbarbs=1,
    lat=60.13,
    lon=-1.18,
    range_min=-60,
    range_max=40,
)
SkewT_Stornoway = svariable(
    ptitle="SkewT at 58.22,-6.32 (UK Stornoway)",  # 03026  9
    outfile="SkewT_Stornoway",
    windbarbs=1,
    lat=58.22,
    lon=-6.32,
    range_min=-60,
    range_max=40,
)
SkewT_Nottingham = svariable(
    ptitle="SkewT at 53.00,-1.25 (UK Nottingham)",  # 03354  117
    outfile="SkewT_Nottingham",
    windbarbs=1,
    lat=53.00,
    lon=-1.25,
    range_min=-60,
    range_max=40,
)
SkewT_Aberporth = svariable(
    ptitle="SkewT at 52.13,-4.57 (UK Aberporth)",  # 03502  133
    outfile="SkewT_Aberporth",
    windbarbs=1,
    lat=52.13,
    lon=-4.57,
    range_min=-60,
    range_max=40,
)
SkewT_Larkhill = svariable(
    ptitle="SkewT at 51.20,-1.80 (UK Larkhill)",  # 03743  132
    outfile="SkewT_Larkhill",
    windbarbs=1,
    lat=51.20,
    lon=-1.80,
    range_min=-60,
    range_max=40,
)
SkewT_Camborne = svariable(
    ptitle="SkewT at 50.22,-5.32 (UK Camborne)",  # 03808  88
    outfile="SkewT_Camborne",
    windbarbs=1,
    lat=50.22,
    lon=-5.32,
    range_min=-60,
    range_max=40,
)
SkewT_Herstmonceux = svariable(
    ptitle="SkewT at 50.90,0.32 (UK Herstmonceux)",  # 03882  52
    outfile="SkewT_Herstmonceux",
    windbarbs=1,
    lat=50.90,
    lon=0.32,
    range_min=-60,
    range_max=40,
)
SkewT_Bath = svariable(
    ptitle="SkewT at 51.38,-2.36 (UK Bath)",
    outfile="SkewT_Bath",
    windbarbs=1,
    lat=51.38,
    lon=-2.36,
    range_min=-60,
    range_max=40,
)
SkewT_Caerphilly = svariable(
    ptitle="SkewT at 51.64,-3.30 (UK Caerphilly)",
    outfile="SkewT_Caerphilly",
    windbarbs=1,
    lat=51.64,
    lon=-3.30,
    range_min=-60,
    range_max=40,
)
SkewT_BristolChannel = svariable(
    ptitle="SkewT at 51.02,-5.23 (UK Bristol Channel)",
    outfile="SkewT_BristolChannel",
    windbarbs=1,
    lat=51.02,
    lon=-5.23,
    range_min=-60,
    range_max=40,
)
SkewT_Trappes = svariable(
    ptitle="SkewT at 48.77,2.02 (FRANCE Trappes)",  # 07145  168
    outfile="SkewT_Trappes",
    windbarbs=1,
    lat=48.77,
    lon=2.02,
    range_min=-60,
    range_max=40,
)
SkewT_Bordeaux = svariable(
    ptitle="SkewT at 44.82,-0.68 (FRANCE Bordeaux)",  # 07510 48
    outfile="SkewT_Bordeaux",
    windbarbs=1,
    lat=44.82,
    lon=-0.68,
    range_min=-60,
    range_max=40,
)
SkewT_Nimes = svariable(
    ptitle="SkewT at 43.87,4.40 (FRANCE Nimes)",  # 07645  60
    outfile="SkewT_Nimes",
    windbarbs=1,
    lat=43.87,
    lon=4.40,
    range_min=-60,
    range_max=40,
)
SkewT_LaCoruna = svariable(
    ptitle="SkewT at 43.37,-8.42 (SPAIN La Coruna)",  # 08001  58
    outfile="SkewT_LaCoruna",
    windbarbs=1,
    lat=43.37,
    lon=-8.42,
    range_min=-60,
    range_max=40,
)
SkewT_Santander = svariable(
    ptitle="SkewT at 43.47,-3.82 (SPAIN Santander)",  # 08023  64
    outfile="SkewT_Santander",
    windbarbs=1,
    lat=43.47,
    lon=-3.82,
    range_min=-60,
    range_max=40,
)
SkewT_Madrid = svariable(
    ptitle="SkewT at 40.45,-3.55 (SPAIN Madrid)",  # 08221  633
    outfile="SkewT_Madrid",
    windbarbs=1,
    lat=40.45,
    lon=-3.55,
    range_min=-60,
    range_max=40,
)
SkewT_Murcia = svariable(
    ptitle="SkewT at 38.00,-1.17 (SPAIN Murcia)",  # 08430  62
    outfile="SkewT_Murcia",
    windbarbs=1,
    lat=38.00,
    lon=-1.17,
    range_min=-60,
    range_max=40,
)
SkewT_Gibraltar = svariable(
    ptitle="SkewT at 36.15,-5.35 (GIBRALTAR Gibraltar)",  # 08495  3
    outfile="SkewT_Gibraltar",
    windbarbs=1,
    lat=36.15,
    lon=-5.35,
    range_min=-60,
    range_max=40,
)

# QVapor
def create_QVapor_at(interpvalue, range_min=0, range_max=0.01, nticks=11, nlevs=11):
    return svariable(
        dim=4,
        wrfname="QVAPOR",
        ptitle=f"Water Vapour Mixing Ratio at {interpvalue} hPa [kg kg-1]",
        outfile=f"QVapor{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=get_cmap("YlGnBu"),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
        windbarbs=True,
    )
QVapor925 = create_QVapor_at(925)
QVapor850 = create_QVapor_at(850)
QVapor700 = create_QVapor_at(700)
QVapor500 = create_QVapor_at(500)
QVapor300 = create_QVapor_at(300)

# Sensible variables for analysing momentum tendency terms
# Raw variables, in x- or y-direction, not projected onto unit vector of wind
# Mass Tendency 2D, U direction
mu_range_min = -100
mu_range_max = 100
mu_max_frac = 0.55 + min(0.45, (pv_range_max / (pv_range_max - pv_range_min)))
mu_min_frac = 0.55 + min(0, (pv_range_min / (pv_range_max - pv_range_min)))
mu_nticks = 21
mu_nlevs = 21
UHorizAdvMomentum = svariable(
    dim=4,
    wrfname="RU_TEND_HADV",
    ptitle=f"Horizontal advection of zonal coupled momentum term in X [Pa m s-2]",
    outfile=f"UHorizAdvMomentum",
    colormap=get_cmap("YlGnBu"),
)

def create_UHorizAdvMomentum_at(
    interpvalue,
    range_min=mu_range_min,
    range_max=mu_range_max,
    nticks=mu_nticks,
    nlevs=mu_nlevs
):
    min_frac = 0.55 + min(0, (range_min / (range_max - range_min)))
    max_frac = 0.55 + min(0.45, (range_max / (range_max - range_min)))
    return svariable(
        dim=4,
        wrfname="RU_TEND_HADV",
        ptitle=f"Horizontal advection of zonal coupled momentum term in X at {interpvalue} hPa [Pa m s-2]",
        outfile=f"UHorizAdvMomentum{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        colormap=cmr.get_sub_cmap("PuOr", min_frac, max_frac, N=nlevs),
        nticks=nticks,
        nlevs=nlevs,
        range_min=range_min,
        range_max=range_max,
    )
UMassTendency925 = create_UHorizAdvMomentum_at(925) #, range_min=-5, range_max=5)
UMassTendency850 = create_UHorizAdvMomentum_at(850) #, range_min=-5, range_max=5)
UMassTendency700 = create_UHorizAdvMomentum_at(700) #, range_min=-5, range_max=5)
UMassTendency500 = create_UHorizAdvMomentum_at(500) #, range_min=-5, range_max=5)
UMassTendency300 = create_UHorizAdvMomentum_at(300) #, range_min=-10, range_max=10)

# Combined terms projected onto unit vector of wind
# MOMENTUM_TEND_DICT = {
#     "tend_hadv": {"var_u": "ru_tend_hadv", "var_v": "rv_tend_hadv"},
#     "tend_vadv": {"var_u": "ru_tend_vadv", "var_v": "ru_tend_vadv"},
#     "tend_pgf": {"var_u": "ru_tend_pgf", "var_v": "rv_tend_pgf"},
#     "tend_cor": {"var_u": "ru_tend_cor", "var_v": "rv_tend_cor"},
#     "tend_curv": {"var_u": "ru_tend_curv", "var_v": "rv_tend_curv"},
#     "tendf_pbl": {"var_u": "ru_tendf_pbl", "var_v": "rv_tendf_pbl"},
#     "tendf_cu": {"var_u": "ru_tendf_cu", "var_v": "rv_tendf_cu"},
#     "tendf_diff": {"var_u": "ru_tendf_diff", "var_v": "rv_tendf_diff"}
# }
tend_scale="bounds",
tend_bounds=[-100, -50, -20, -10, -5, 5, 10, 20, 50, 100]
tend_colormap=ListedColormap(
    [
        "darkgreen",
        "forestgreen",
        "limegreen",
        "greenyellow",
        "white",
        "gold",
        "darkorange",
        "red",
        "darkred",
    ]
)
tend_range_min=-100
tend_range_max=100

def create_TendHADV_at(
    interpvalue,
    scale=tend_scale,
    bounds=tend_bounds,
    colormap=tend_colormap,
    range_min=tend_range_min,
    range_max=tend_range_max
):
    """
    Calculates:
    (ru_tend_hadv * U + rv_tend_hadv * V) / |wind_spd|

    GetSensVar works out how to calculate based on outname rather than wrfname
    """
    return svariable(
        dim=4,
        wrfname=None,
        ptitle=f"Horizontal advection of zonal coupled momentum term projected onto unit vector at {interpvalue} hPa [Pa m s-2]",
        outfile=f"TendHADV{interpvalue}",
        interpvar="pressure",
        interpvalue=interpvalue,
        scale=scale,
        bounds=bounds,
        colormap=colormap,
        range_min=range_min,
        range_max=range_max,
    )

TendHADV925 = create_TendHADV_at(925) #, range_min=-5, range_max=5)
TendHADV850 = create_TendHADV_at(850) #, range_min=-5, range_max=5)
TendHADV700 = create_TendHADV_at(700) #, range_min=-5, range_max=5)
TendHADV500 = create_TendHADV_at(500) #, range_min=-5, range_max=5)
TendHADV300 = create_TendHADV_at(300) #, range_min=-10, range_max=10)

