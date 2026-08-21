# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import metpy as mp
from metpy.units import units
from metpy.plots import SkewT
from wrf import ll_to_xy, getvar
import matplotlib.pyplot as plt
import numpy as np

import wrf_analysis_toolkit.SensibleVariables as sv


def Plot_SkewT(ncfile, ti, svariable, outfname="MyPlot.png", save_pdf=0):

    # Load wrf variables
    x_y = ll_to_xy(ncfile, svariable.lat, svariable.lon)
    height = getvar(ncfile, "ter", timeidx=ti)
    p1 = getvar(ncfile, "pressure", timeidx=ti)
    T1 = getvar(ncfile, "tc", timeidx=ti)
    Td1 = getvar(ncfile, "td", timeidx=ti)
    u1 = getvar(ncfile, "ua", timeidx=ti)
    v1 = getvar(ncfile, "va", timeidx=ti)
    # Extract date time for label
    dtime = str(p1.Time.values)[0:19]
    # Prepare variables for metpy
    h = height[x_y[1], x_y[0]].data * units.m
    p = p1[:, x_y[1], x_y[0]].data * units.hPa
    T = T1[:, x_y[1], x_y[0]].data * units.degC
    Td = Td1[:, x_y[1], x_y[0]].data * units.degC
    u = u1[:, x_y[1], x_y[0]].data * units("m/s")
    v = v1[:, x_y[1], x_y[0]].data * units("m/s")

    # Create figure
    fig = plt.figure(figsize=(10.88, 8.16), dpi=100)
    skew = SkewT(fig=fig)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(svariable.range_min, svariable.range_max)
    skew.ax.set_xlabel(r"Temperature [$^\circ$C]")
    skew.ax.set_ylabel("Pressure [hPa]")

    # Shade every other isotherm
    isothermal_values = np.arange(-100, 1001, 10)
    for i in range(len(isothermal_values) - 1)[::2]:
        skew.ax.fill_betweenx(
            p, isothermal_values[i], isothermal_values[i + 1], color="gray", alpha=0.1
        )
    # skew.ax.axvline(0, color='c', linestyle='-', linewidth=1.5)         # Zero degree isotherm

    # Plot only some windbarbs
    my_interval = np.arange(100, 1000, 50) * units("mbar")
    ix = mp.calc.resample_nn_1d(p, my_interval)
    skew.plot_barbs(p[ix], u[ix], v[ix], plot_units=units("knots"))

    # Plot LCL temperature as black dot
    lcl_pressure, lcl_temperature = mp.calc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, "ko", markerfacecolor="black")
    # Calculate the parcel profile and plot as black line
    parcel_prof = mp.calc.parcel_profile(p, T[0], Td[0]).to("degC")
    skew.plot(p, parcel_prof, "k", linewidth=2)
    # Adds CAPE and CIN
    skew.shade_cape(p, T, parcel_prof)
    skew.shade_cin(p, T, parcel_prof, Td)
    cape_cin = mp.calc.cape_cin(p, T, Td, parcel_prof)
    plt.annotate(
        f"CAPE: {round(cape_cin[0].magnitude,1)}",
        xy=(0.84, 0.97),
        xycoords="axes fraction",
        bbox=dict(boxstyle="round", facecolor="red", alpha=0.3),
    )
    plt.annotate(
        f"  CIN: {round(cape_cin[1].magnitude,1)}",
        xy=(0.84, 0.93),
        xycoords="axes fraction",
        bbox=dict(boxstyle="round", facecolor="cornflowerblue", alpha=0.3),
    )

    # Add background lines
    skew.plot_dry_adiabats(
        color="red", linestyle="-", linewidth=1
    )  # Dry adiabats (default to red)
    skew.plot_moist_adiabats(
        color="blue", linestyle="-", linewidth=1
    )  # Moist adiabats (default to blue)
    skew.plot_mixing_lines(
        color="green", linestyle="--", linewidth=1
    )  # Mixing lines (default to green)

    # Plot Temperature and Dew Point Temperature
    skew.plot(p, T, color="red")
    skew.plot(p, Td, color="green")

    # Add title, frame time, save and close
    plt.title(f"{svariable.ptitle} ~ {int(h.magnitude)} m.a.s.l.")
    plt.annotate(dtime, xy=(0.01, 0.01), xycoords="figure fraction")
    if svariable.interpvalue:
        plt.annotate(
            f"Trajectory at ~ {int(svariable.interpvalue)}hPa",
            xy=(0.8, 0.01),
            xycoords="figure fraction",
        )
    plt.savefig(outfname)
    if save_pdf:
        plt.savefig(outfname.replace(".png", ".pdf"))
    plt.close(fig)
