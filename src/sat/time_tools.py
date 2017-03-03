'Functions for working with time series'
from datetime import timedelta
from math import pi, exp
from cmath import rect
from numpy import array, angle, absolute, log, zeros_like
from numpy.fft import rfft, irfft, rfftfreq
from scipy.interpolate import splrep, splev
from scipy import polyfit

def make_plot(x_vals, y_vals):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x_vals, y_vals)
    show()

def make_plot_window(x_vals, y_vals, ind_from, ind_to):
    'QC plot of two time series'
    from matplotlib.pyplot import plot, show
    plot(x_vals[ind_from:ind_to], y_vals[ind_from:ind_to])
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

def make_residual_func(t_max, slope, n_harm, samples, indices):
    'closure for residual func'
    freqs = rfftfreq(indices[-1], 5)
    ind_from = int(round(1/(t_max*freqs[1])))
    ind_to = ind_from+n_harm
    def residual_func(x):
        'calculates sum of squared residuals'
        nonlocal freqs, ind_from, ind_to
        spectrum = zeros_like(freqs, 'complex')
        spectrum[0] = rect(10000.0 * x[0], 0)
        for i in range(ind_from, ind_to):
            spectrum[i] = rect(exp(x[1]+slope*log(freqs[i])), 2*pi*x[2+i])
        series = irfft(spectrum)
        sum_err = 0
        for position, ind in enumerate(indices):
            sum_err += (series[ind]-samples[position])**2
        return sum_err
    return residual_func

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
    #make_plot(all_indices, detrended)
    dense_samples = detrended[:split_time]
    sparse_samples = detrended[split_time:]
    sparse_indices = (all_indices[split_time:]-split_time).astype(int)
    #print(list(zip(sparse_indices,sparse_samples)))
    amp, _ = time_to_spectrum(dense_samples)
    dense_freq = rfftfreq(dense_samples.size, 5)
    periods = (3000.0, 300.0)
    ind_from = int(round(1/(periods[0]*dense_freq[1])))
    ind_to = int(round(1/(periods[1]*dense_freq[1])))
    loglog_a, _ = polyfit(log(dense_freq[ind_from:ind_to]), amp[ind_from:ind_to], 1)
    #print(loglog_a, loglog_b)
    #make_plot_window(log(dense_freq[1:]), amp[1:], ind_from, ind_to)
    n_harm = 5
    residual_func = make_residual_func(periods[0], loglog_a, n_harm, sparse_samples, sparse_indices)
    interp_times = []
    interp_values = []
    return zip(interp_times, interp_values)

