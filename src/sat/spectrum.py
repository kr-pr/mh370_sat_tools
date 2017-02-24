'Functions for working with time series'

from datetime import timedelta
from numpy import array, arange
from scipy.interpolate import splrep, splev
from main import T0
from radial import RadialDistance

def make_radial_plot(x1, y1, x2, y2):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x1, y1)
    plot(x2, y2)
    show()

def time_to_index(dtime, delta=5, t_ref='take-off'):
    'Computes array index from datetime'
    return (dtime-T0[t_ref]).total_seconds()//delta

def index_to_time(ind, delta=5, t_ref='take-off'):
    'Computes datetime from array index'
    delta = timedelta(seconds=ind*delta)
    return T0[t_ref]+delta

def trend_spline(series, spline_times):
    'Interpolates values with splines'
    spline = splrep(spline_times, series[spline_times])
    trend = splev(arange(series.size), spline)
    return trend

def psd_from_series(series):
    'computes power spectral density of time series'

def resample_psd(psd):
    'resamples and smoothes a PSD'

def series_from_psd(psd):
    'creates a random time series for given PSD'

def interpolate(r_list, trend_times):
    'performs lf spline + hf interpolation of radial distance'
    r_interp = None
    return RadialDistance(r_interp)