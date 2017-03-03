'Functions for working with time series'
from datetime import timedelta
from math import pi, exp
from cmath import rect
from numpy import array, angle, absolute, log, zeros_like, arange
from numpy.fft import rfft, irfft, rfftfreq
from scipy.interpolate import splrep, splev
from scipy.optimize import minimize
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
    #print(spectrum[:5])
    return log(absolute(spectrum)), angle(spectrum)

def make_residual_func(samples, indices, **params):
    'closure for residual func'
    fft_size = 2
    while fft_size<indices[-1]:
        fft_size*=2
    freqs = rfftfreq(fft_size, 5)
    ind_from = int(round(1/(params['t_max']*freqs[1])))
    ind_to = ind_from+params['n_harm']
    def make_series(x):
        'Calculates time series from parameterized spectrum'
        nonlocal freqs, ind_from, ind_to, params
        spectrum = zeros_like(freqs, 'complex')
        sign_x0 = 0 if x[0] == 0.5 else abs(x[0]-0.5)/(x[0]-0.5)
        spectrum[0] = rect(sign_x0*exp(params['scale'][0]*abs(x[0]-0.5)), 0)
        for i in range(ind_from, ind_to):
            spectrum[i] = rect(
                exp(params['scale'][1]*x[1]+params['slope']*log(freqs[i])),
                params['scale'][2]*x[2+i-ind_from]
            )
        #print(x)
        #print(spectrum[0], spectrum[ind_from:ind_to])
        return irfft(spectrum)
    def residual_func(x):
        'calculates sum of squared residuals'
        nonlocal samples, indices
        series = make_series(x)
        sum_err = 0
        for position, ind in enumerate(indices):
            sum_err += (series[ind]-samples[position])**2
        print(series[:5])
        return sum_err
    return make_series, residual_func

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
    #print(min(detrended), max(detrended))
    sparse_samples = detrended[split_time:]
    sparse_indices = (all_indices[split_time:]-split_time).astype(int)
    #print(list(zip(sparse_indices,sparse_samples)))
    amp, _ = time_to_spectrum(dense_samples)
    #print(amp[:5])
    dense_freq = rfftfreq(dense_samples.size, 5) 
    periods = (3000.0, 300.0)
    ind_from = int(round(1/(periods[0]*dense_freq[1])))
    ind_to = int(round(1/(periods[1]*dense_freq[1])))
    slope, _ = polyfit(log(dense_freq[ind_from:ind_to]), amp[ind_from:ind_to], 1)
    #print(loglog_a, loglog_b)
    #make_plot_window(log(dense_freq[1:]), amp[1:], ind_from, ind_to)
    params = {
        't_max': periods[0],
        'slope': slope,
        'n_harm': 21,
        'scale': [20, 4, 2*pi]
    }
    series_func, residual_func = make_residual_func(sparse_samples, sparse_indices, **params)
    x0 = array([0.5]*(params["n_harm"]+2))
    bounds = [(0, 1)]*(params["n_harm"]+2)
    result = minimize(residual_func, x0, method="L-BFGS-B", bounds=bounds, options={'eps':1e-3})
    print(result.x)
    make_plot_2(sparse_indices, sparse_samples, arange(sparse_indices[-1]), series_func(result.x)[:sparse_indices[-1]])
    interp_times = []
    interp_values = []
    return zip(interp_times, interp_values)

