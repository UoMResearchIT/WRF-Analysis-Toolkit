# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
import re
from copy import deepcopy
from datetime import datetime, timedelta
from wrf import CoordPair, ll_to_xy, destagger
import numpy as np
from xarray import Dataset, DataArray

import wrf_analysis_toolkit.SensibleVariables as sv


def str2bool(s):
    if isinstance(s, bool):
        return s

    if not isinstance(s, str):
        str_in = str(s)
    else:
        str_in = s

    if str_in.lower() in ("yes", "true", "t", "y", "1"):
        return 1
    elif str_in.lower() in ("no", "false", "f", "n", "0"):
        return 0
    else:
        raise Exception("Boolean value expected.")


def set_variable(
    variable_name: str,
    range_min=None,
    range_max=None,
    windbarbs=None,
    windbarb_gap=None,
    place=None,
    lat=None,
    lon=None,
    trajectory=None,
    vcross=None,
    start_latlon=None,
    end_latlon=None,
    plim_bottom=None,
    plim_top=None,
    plevs=None,
    sens_var=None,
):
    """
    Returns a SensibleVariable with the specified properties.
    """
    if sens_var is None:
        try:
            svar = deepcopy(getattr(sv, variable_name))
        except AttributeError:
            raise ValueError(
                f"Variable '{variable_name}' is not defined in SensibleVariables."
                f"Options are: {', '.join(sv.get_sv_names())}"
            )
    else:
        svar = deepcopy(sens_var)

    if range_min is not None:
        svar.range_min = float(range_min)
    if range_max is not None:
        svar.range_max = float(range_max)

    if windbarbs is not None:
        svar.windbarbs = str2bool(windbarbs)

    if windbarb_gap is not None:
        svar.windbarb_gap = int(windbarb_gap)

    if place is not None:
        try:
            point = getattr(sv, f"SkewT_{place}")
        except AttributeError:
            raise ValueError(
                f"Place '{place}' is not defined in SensibleVariables."
                f"Options are: {', '.join(sv.get_sv_places())}"
            )
        svar.lat = point.lat
        svar.lon = point.lon

    if (lat is not None and lon is None) or (lat is None and lon is not None):
        raise ValueError("Both 'lat' and 'lon' must be provided together.")
    if lat is not None:
        svar.lat = float(lat)
    if lon is not None:
        svar.lon = float(lon)

    if trajectory is not None:
        svar.along_traj = trajectory
        trajname = os.path.splitext(os.path.basename(trajectory))[0]
        svar.outfile = f"SkewT_Traj_{trajname}"

    if "SkewT" in svar.outfile and (lat is not None or lon is not None):
        svar.outfile = f"SkewT_at_{svar.lat}_{svar.lon}"
        svar.ptitle = f"SkewT at {svar.lat},{svar.lon}"

    # Settings for making vertical cross sections
    if vcross is not None:
        svar.vcross = str2bool(vcross)
    if (start_latlon is not None and end_latlon is None) \
        or (start_latlon is None and end_latlon is not None):
        raise ValueError("Both 'start_latlon' and 'end_latlon' must be provided together.")

    if start_latlon is not None:
        svar.start_latlon = tuple(start_latlon)
    if end_latlon is not None:
        svar.end_latlon = tuple(end_latlon)
    if plim_bottom is not None:
        svar.plim_bottom = float(plim_bottom)
    if plim_top is not None:
        svar.plim_top = float(plim_top)
    if plevs is not None:
        svar.plevs = int(plevs)

    return svar

def check_timestamp(timestamp: str):
    """
    Checks if the timestamp is in the format YYYY-MM-DD_HH:MM:SS.
    Raises a ValueError if the format is invalid.

    Returns a datetime object of the timestamp
    """
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d_%H:%M:%S")
    except:
        raise ValueError(
            f"Invalid timestamp format: {timestamp}. Expected format is YYYY-MM-DD_HH:MM:SS."
        )

def parse_timestep(time_step: str):
    """
    Checks if the time_step is in the format HH:MM:SS.
    Raises a ValueError if the format is invalid.

    Returns a timedelta object version of the time_step
    """
    pattern_time = r"\d{2}:\d{2}:\d{2}$"
    if re.match(pattern_time, time_step):
        h, m, s = map(int, time_step.split(":"))
    else:
        raise ValueError(
            f"Invalid timestamp format: {time_step}. Expected format is 'DD_HH:MM:SS' or 'HH:MM:SS'."
        )
    return timedelta(hours=h, minutes=m, seconds=s)

def select_wrfout_files(
        wrfout_dir: str,
        time_from: str = None,
        time_to: str = None,
        time_step: str = None,
    ):
    """
    Returns a list of WRF output files in the specified directory, optionally filtered by time range.
    Expect the files to be named in the format "wrfout_*_YYYY-MM-DD_HH:MM:SS", where * is a wildcard.

    By default, all files starting with "wrfout_" are included.

    If time_from is provided, only files with timestamps >= time_from are included.
    If time_to is provided, only files with timestamps <= time_to are included.
    If time_step is provided, only files that are time_step apart from each other are included
    """
    WRFfiles = sorted(f for f in os.listdir(wrfout_dir) if f.startswith("wrfout_"))

    if time_from is not None:
        datetime_from = check_timestamp(time_from)
        WRFfiles = [f for f in WRFfiles if check_timestamp(f[-19:]) >= datetime_from]
    if time_to is not None:
        datetime_to = check_timestamp(time_to)
        WRFfiles = [f for f in WRFfiles if check_timestamp(f[-19:]) <= datetime_to]
    if time_step is not None:
        time_delta = parse_timestep(time_step)
        datetimes = [check_timestamp(f[-19:]) for f in WRFfiles]
        t0 = datetimes[0]
        WRFfiles = [
            f for f, t in zip(WRFfiles, datetimes)
            if (t - t0) % time_delta == timedelta(0)
        ]

    return WRFfiles

def latlon_check(ncfile: Dataset, latlon: tuple):
    """
    Checks whether a latlon pair of form (lat, lon) is
    inside a WRF domain, defined by the ncfile

    Raises a ValueError if the point is outside of the domain
    """
    coord_pair = CoordPair(lat=latlon[0], lon=latlon[1])
    lat = coord_pair.lat
    lon = coord_pair.lon
    x_y = ll_to_xy(ncfile, lat, lon)
    nx = len(ncfile.dimensions["west_east"])
    ny = len(ncfile.dimensions["south_north"])
    if not (0 <= x_y[0] < nx) or not (0 <= x_y[1] < ny):
        raise ValueError(
            f"Point ({lat}, {lon}) is outside the WRF domain"
        )

def destagger_var(
    var: DataArray,
    meta_var: DataArray | None=None,
    meta: bool=False
):
    stagger_dim = None
    for i, dim in enumerate(var.dims):
        if dim.endswith("_stag"):
            stagger_dim = i
            break

    # Destagger the variable if it is staggered
    if stagger_dim:
        try:
            var_out = destagger(var, stagger_dim, meta=meta)
            if meta:
                if meta_var is None:
                    raise ValueError("Need a sample meta_var to attatch coordinate fields to destaggared array")
                # Manually assign coordinates from meta_var because these aren't done automatically
                var_out = var_out.assign_coords(coords=meta_var.coords)
                var_out.attrs.update(stagger=meta_var.attrs['stagger'], coordinates=meta_var.attrs['coordinates'])
                meta_var["Time"] = meta_var.Time
        except:
            raise ValueError("Unable to destagger variable")

    # Otherwise return the original variable unchanged
    else:
        return var

def project_vector(
    var_u: np.ndarray,
    var_v: np.ndarray,
    wind_u: np.ndarray,
    wind_v: np.ndarray,
    wind_spd = None,
):
    """
    Function to project a given vector (with terms in the X and Y directions)
    onto the unit vectors of wind in the X and Y directions (U and V),
    in order to calculate the along-flow values of the vector

    Inputs:
    - var_u: values of variable of in interest in the x direction, must be destaggered
    - var_v: values of variable of in interest in the y direction, must be destaggered
    - wind_u: values of wind speed in the x direction, must be destaggered
    - wind_v: values of wind speed in the y direction, must be destaggered
    - wind_spd: (optional) magnitude of wind spped, will be calculated from vectors if not given
    """
    if any([
        var_u.shape() != var_v.shape(),
        var_u.shape() != wind_u.shape(),
        var_u.shape() != wind_v.shape()
    ]):
        raise ValueError("project_vector: Shape of vectors do not match, do they need destaggering?")

    if wind_spd is None:
        wind_mag = np.sqrt(np.square(wind_u) + np.square(wind_v))
    else:
        wind_mag = wind_spd

    return (var_u*wind_u + var_v*wind_v) / wind_mag
