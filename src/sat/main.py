'Runner for calculations'
from datetime import timedelta
import inmarsat
import trajectory
import radial

def compare_r(radial_1, radial_2):
    'QC for radial distance computation'
    dict_1 = dict(radial_1.data)
    dict_2 = dict(radial_2.data)
    same_times = set(dict_1.keys()) & set(dict_2.keys())
    time_diff = [(t, dict_1[t]-dict_2[t]) for t in same_times]
    return sum([x[1] for x in time_diff])/len(time_diff)

def make_radial_plot(x1, y1, x2, y2):
    'Creates plot of radial distance vs time for QC'
    from matplotlib.pyplot import plot, show
    plot(x1, y1)
    plot(x2, y2)
    show()

def main():
    'Runs calculation chain'
    inm_log = inmarsat.InmarsatLog.from_csv(
        'data', 'inmarsat-su-log-redacted.csv')
    time_step = timedelta(seconds=10)
    bin_log = inm_log.bin_data(time_step)
    traj_time_step = time_step / 2
    traj = trajectory.Trajectory.from_csv('data',
                                          acars='acars.csv',
                                          adsb='all-combined.csv',
                                          radar='route.csv')
    int_traj = traj.int_data(
        bin_log.data[0].time - traj_time_step, traj_time_step)
    radial_btos = radial.RadialDistance.from_bto(bin_log.data)
    radial_known = radial.RadialDistance.from_traj(int_traj.data)
    #print compare_r(radial_btos, radial_known)
    radial_merged = radial_known.extend(radial_btos)
    spline = radial_merged.interpolate()
    x1, y1 = radial_merged.as_array()
    from numpy import arange
    x2 = arange(x1[0], x1[-1], 5)
    from scipy.interpolate import splev
    y2 = splev(x2, spline)
    make_radial_plot(x1, y1, x2, y2)

if __name__ == '__main__':
    main()

