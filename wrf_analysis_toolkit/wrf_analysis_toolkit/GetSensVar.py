from wrf import to_np, getvar, g_geoht, interplevel, destagger
import numpy as np

import wrf_analysis_toolkit.SensibleVariables as sv
import wrf_analysis_toolkit.Frontogenesis as Frontogenesis


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

        # Destagger the variable if it is staggered
        print("d4var cords coords before:")
        print(str(d4var.coords))
        stagger_dim = None
        for i, dim in enumerate(d4var.dims):
            if dim.endswith("_stag"):
                stagger_dim = i
                print(f"Destaggering {svariable.outfile} along dim {i}")
                break
        if stagger_dim:
            try:
                d4var = destagger(d4var, stagger_dim, meta=True)
                # Manually assign coordinates from interpvar because these aren't done automatically
                d4var.assign_coords(coords=interpvar.coords)
                d4var.assign_coords({
                    'XLONG': (('south_north', 'west_east'), interpvar.coords['XLONG'].values),
                    'XLAT': (('south_north', 'west_east'), interpvar.coords['XLAT'].values)
                })
                d4var["Time"] = interpvar.Time
            except:
                raise ValueError(f"Unable to destagger {svariable.outfile}")
        print("d4var cords coords after:")
        print(str(d4var.coords))

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
