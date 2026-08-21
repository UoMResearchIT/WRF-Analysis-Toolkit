# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

from netCDF4 import Dataset
from wrf import to_np, getvar
import numpy as np


def main():
    frontogenesis3D()


# Input netcdf - [bottom_top, north_south, west_east]
def frontogenesis3D(ncfile, time):
    if type(ncfile) is Dataset:
        ncFile = ncfile
    elif type(ncfile) is str:
        ncFile = Dataset(ncfile)
    else:
        print(
            f"ncfile should be a netCDF4.Dataset or a string with a path to a dataset. {type(ncfile)} is not valid."
        )
        return 1
    # Fetch the fields we need
    p = to_np(
        getvar(ncFile, "pressure", timeidx=time) * 100
    )  # The 100 converts hPa to Pa
    z = to_np(getvar(ncFile, "z"))
    ua = to_np(getvar(ncFile, "ua", timeidx=time))
    va = to_np(getvar(ncFile, "va", timeidx=time))
    theta = to_np(getvar(ncFile, "theta", timeidx=time))
    omega = to_np(getvar(ncFile, "omega", timeidx=time))

    dx = ncFile.DX
    dy = ncFile.DY
    dz = calc_center_difference(z, 0)
    dp = calc_center_difference(p, 0)

    theta_gradient = np.sqrt(
        (np.gradient(theta, dx, axis=2)) ** 2
        + (np.gradient(theta, dy, axis=1)) ** 2
        + (calc_center_difference(theta, 0) / dp) ** 2
    )
    zonal_gradient = (-1 * np.gradient(theta, dx, axis=2)) * (
        (np.gradient(ua, dx, axis=2) * np.gradient(theta, dx, axis=2))
        + (np.gradient(va, dx, axis=2) * np.gradient(theta, dy, axis=1))
    )
    meridional_gradient = (-1 * np.gradient(theta, dy, axis=1)) * (
        (np.gradient(ua, dy, axis=1) * np.gradient(theta, dx, axis=2))
        + (np.gradient(va, dy, axis=1) * np.gradient(theta, dy, axis=1))
    )
    vertical_gradient = (-1 * (calc_center_difference(theta, 0) / dp)) * (
        (np.gradient(omega, dx, axis=2) * np.gradient(theta, dx, axis=2))
        + (np.gradient(omega, dy, axis=1) * np.gradient(theta, dy, axis=1))
    )

    F3D = (
        1.08e9
        * (1 / theta_gradient)
        * (zonal_gradient + meridional_gradient + vertical_gradient)
    )  # The 1.08e9 converts from [K/m/s] to [K/100km/3h]
    return F3D


def calc_center_difference(A, ax):
    gradient = np.gradient(A, axis=ax)
    gradient *= 2.0
    if ax == 0:
        gradient[0, :, :] /= 2.0
        gradient[-1, :, :] /= 2.0
    elif ax == 1:
        gradient[:, 0, :] /= 2.0
        gradient[:, -1, :] /= 2.0
    elif ax == 2:
        gradient[:, :, 0] /= 2.0
        gradient[:, :, -1] /= 2.0
    else:
        return ValueError("Invalid axis passed to calc_center_difference")
    return gradient


if __name__ == "__main__":
    main()
