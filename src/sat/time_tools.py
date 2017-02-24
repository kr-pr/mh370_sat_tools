'Functions for working with time series'
from datetime import timedelta
from numpy import array, arange, angle, absolute, log
from numpy.fft import rfft, irfft, rfftfreq
from scipy.interpolate import splrep, splev

def make_plot(x_vals, y_vals):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x_vals, y_vals)
    show()

def make_plot_first(x_vals, y_vals, num):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x_vals[:num], y_vals[:num])
    show()

def make_plot_2(x_vals, y_vals, x2_vals, y2_vals):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x_vals, y_vals)
    plot(x2_vals, y2_vals)
    show()

def time_to_index(dtime, time_ref, delta=5):
    'Computes array index from datetime'
    return (dtime-time_ref).total_seconds()//delta

def index_to_time(ind, time_ref, delta=5):
    'Computes datetime from array index'
    return time_ref+timedelta(seconds=ind*delta)

def time_to_spectrum(t_series):
    'computes power spectral density of time series'
    spectrum = rfft(t_series)
    return log(absolute(spectrum)), angle(spectrum)

def resample_spectrum(f_spec):
    'resamples and smoothes Fourier spectrum representation'

def generate_time_series(f_spec):
    'creates a random time series for given Fourier spectrum'

def interp_helper(all_data, trend_data, time_from):
    'performs lf spline + hf fft interpolation of radial distance'
    all_times, all_values = zip(*all_data)
    trend_times, trend_values = zip(*trend_data)

    split_time = int(time_to_index(time_from, all_times[0]))

    trend_indices = array([time_to_index(item, all_times[0]) for item in trend_times])
    spline = splrep(trend_indices, array(trend_values))

    all_indices = array([time_to_index(item, all_times[0]) for item in all_times])
    trend = splev(all_indices, spline)
    detrended = array(all_values) - trend

    #make_plot_2(all_indices, trend, all_indices, array(all_values))
    make_plot(all_indices, detrended)
    dense_samples = detrended[:split_time]
    sparse_samples = detrended[split_time:]
    sparse_indices = all_indices[split_time:]
    amp, phase = time_to_spectrum(dense_samples)

    make_plot_first(rfftfreq(dense_samples.size,5), amp,20)
    make_plot_first(rfftfreq(dense_samples.size,5), phase,20)

    interp_times = []
    interp_values = []
    return zip(interp_times, interp_values)