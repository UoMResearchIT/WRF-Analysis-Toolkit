# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

from wrf import to_np, getvar, g_geoht, interplevel, destagger
import numpy as np
from copy import deepcopy

import wrf_analysis_toolkit.SensibleVariables as sv
import wrf_analysis_toolkit.Frontogenesis as Frontogenesis

from wrf_analysis_toolkit.utils import destagger_var, project_vector

MOMENTUM_TEND_DICT = {
    "tendhadv": {"var_u": "RU_TEND_HADV", "var_v": "RV_TEND_HADV"},
    "tendvadv": {"var_u": "RU_TEND_VADV", "var_v": "RU_TEND_VADV"},
    "tendpgf": {"var_u": "RU_TEND_PGF", "var_v": "RU_TEND_PGF"},
    "tendcor": {"var_u": "RU_TEND_COR", "var_v": "RU_TEND_COR"},
    "tendcurv": {"var_u": "RU_TEND_CURV", "var_v": "RU_TEND_CURV"},
    "tendfpbl": {"var_u": "RU_TENDF_PBL", "var_v": "RU_TENDF_PBL"},
    "tendfcu": {"var_u": "RU_TENDF_CU", "var_v": "RU_TENDF_CU"},
    "tendfdiff": {"var_u": "RU_TENDF_DIFF", "var_v": "RU_TENDF_DIFF"}
}

def GetSensVar(ncfile, svariable, windbarbs=0, time=0, varprevv=None):
    u = v = varv = None
    # For simple 2D +value variables
    if svariable.dim == 3:
        var = getvar(ncfile, svariable.wrfname, timeidx=time)
        if windbarbs:
            # Get wind speed components at 10m
            u, v = to_np(getvar(ncfile, "uvmet10", timeidx=time))
        # Special variable acquisition
        if svariable.outfile in ["CAPE"]:
            var = var[0]
        elif svariable.outfile in ["CIN", "CIN_YlGnBu", "CIN_YlGn"]:
            var = var[1]
        # Special variable computation
        if svariable.outfile in ["Rain"]:
            # Adds RAINC and RAINNC to get total accumulated precipitation
            rnc = getvar(ncfile, "RAINNC", timeidx=time)
            var.values = var.values + rnc.values
            # Saves current accumulated total rain to output and use in next time index
            varv = var.values
            # Converts accumulated rain to "hourly" rain (given hourly time indices)
            if varprevv is not None:
                var.values = var.values - varprevv
    
    # For 3D +value variables, interpolated at interpvalue of interpvar
    elif svariable.dim == 4:

        interpvar = getvar(ncfile, svariable.interpvar, timeidx=time)
        if svariable.wrfname is not None:
            d4var = getvar(ncfile, svariable.wrfname, timeidx=time)
        # Special variable acquisition
        elif svariable.outfile.startswith("GeoPotHeight"):
            d4var = g_geoht.get_height(ncfile, timeidx=time)
        elif "Frontogenesis" in svariable.outfile:
            F3D = Frontogenesis.frontogenesis3D(ncfile, time)
            d4var = getvar(ncfile, svariable.interpvar, timeidx=time)
            d4var.values = F3D
        elif any([k in svariable.outfile.lower() for k in MOMENTUM_TEND_DICT]):
            for k in MOMENTUM_TEND_DICT:
                if k in svariable.outfile.lower():
                    tend_name = k
                    break
            print(f"Extracting variables to calculate {tend_name}")
            var_u = getvar(ncfile, MOMENTUM_TEND_DICT[tend_name]["var_u"], timeidx=time)
            attrs = var_u.attrs
            var_u = destagger_var(var_u, meta=False)
            var_v = getvar(ncfile, MOMENTUM_TEND_DICT[tend_name]["var_v"], timeidx=time)
            var_v = destagger_var(var_v, meta=False)
            ua = getvar(ncfile, "ua", timeidx=time)
            va = getvar(ncfile, "va", timeidx=time)
            wspd = getvar(ncfile, "wspd", timeidx=time)

            # Calculate the variable projected onto the unit vector of
            # horizontal winds, to calculate the along-flow values
            # This is quickest if calculated using arrays without metadata,
            # and the metadata are copied from the interpvar afterwards
            d4var = deepcopy(interpvar)
            print(f"Projecting {tend_name} onto unit wind vector")
            d4var.values = project_vector(var_u, var_v, ua, va, wspd)
            d4var.attrs.update(attrs)
            print(d4var.attrs)

        else:
            if svariable.wrfname is not None:
                raise ValueError(f"Failed to extract variable {svariable.wrfname}")
            else:
                raise ValueError(f"Failed to extract variable for {svariable.outfile}")

        # Destagger the variable if it is staggered
        d4var = destagger_var(d4var, meta_var=interpvar, meta=True)

        # interpolate variable
        var = interplevel(d4var, interpvar, svariable.interpvalue)

        # Special variable computation
        if "AirTempDif6h" in svariable.outfile:
            # Temperature difference in 6h
            if varprevv is None:
                varv = [var.values]
                var = None
            else:
                if len(varprevv) < 6:
                    varv = np.append(varprevv, [var.values], axis=0)
                    var = None
                else:
                    varv = np.append(varprevv[1:], [var.values], axis=0)
                    var.values = var.values - varprevv[0]

        elif "AirTempDif12h" in svariable.outfile:
            # Temperature difference in 12h
            if varprevv is None:
                varv = [var.values]
                var = None
            else:
                if len(varprevv) < 12:
                    varv = np.append(varprevv, [var.values], axis=0)
                    var = None
                else:
                    varv = np.append(varprevv[1:], [var.values], axis=0)
                    var.values = var.values - varprevv[0]
        elif svariable.outfile in ["StaticStability700500"]:
            # Static stability computed as air temperature difference
            var2 = interplevel(d4var, interpvar, 500)
            var.values = var.values - var2.values
        elif svariable.outfile in ["StaticStability850700"]:
            # Static stability computed as air temperature difference
            var2 = interplevel(d4var, interpvar, 850)
            var.values = var2.values - var.values
        elif svariable.outfile in ["InstRain"]:
            # InstRain (R) from SimRadarReflectivity1km (dBZ) using Marshall-Palmer: Z = 10^(dBZ/10) = 200*R^1.6
            var.values = (0.005 * 10 ** (0.1 * var.values)) ** (0.625)

        if windbarbs:
            # Get wind speed components at interpvalue
            ua = getvar(ncfile, "ua", timeidx=time)
            va = getvar(ncfile, "va", timeidx=time)
            u = to_np(interplevel(ua, interpvar, svariable.interpvalue))
            v = to_np(interplevel(va, interpvar, svariable.interpvalue))

    return var, u, v, varv
