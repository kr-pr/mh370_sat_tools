'Runner for calculations'
from datetime import datetime, timedelta
from inmarsat import InmarsatLog
from trajectory import Trajectory
from radial import RadialDistance

T0 = {'take-off': datetime(2014, 3, 7, 16, 42, 0, 0),
      'off-radar': datetime(2014, 3, 7, 18, 22, 10, 0)}

def compare_r(radial_1, radial_2):
    'QC for radial distance computation'
    dict_1 = dict(radial_1.data)
    dict_2 = dict(radial_2.data)
    same_times = set(dict_1.keys()) & set(dict_2.keys())
    time_diff = [(t, dict_1[t]-dict_2[t]) for t in same_times]
    return sum([x[1] for x in time_diff])/len(time_diff)

def main():
    'Runs calculation chain'
    inm_log = InmarsatLog.from_csv(
        'data', 'inmarsat-su-log-redacted.csv')

    time_step = timedelta(seconds=10)
    bin_log = inm_log.bin_data(time_step)
    traj_time_step = time_step / 2

    traj = Trajectory.from_csv('data',
                                          acars='acars.csv',
                                          adsb='all-combined.csv',
                                          radar='route.csv')
    int_traj = traj.int_data(
        bin_log.data[0].time - traj_time_step, traj_time_step)

    r_btos = RadialDistance.from_bto(bin_log.data)
    r_known = RadialDistance.from_traj(int_traj.data)
    r_flight = r_known.append(r_btos).take_after(T0['take-off'])

    trend_times = [(2014, 3, 7, 16, 42, 0), (2014, 3, 7, 17, 23, 0), (2014, 3, 7, 18, 28, 15),
                   (2014, 3, 7, 19, 41, 5), (2014, 3, 7, 20, 41, 5), (2014, 3, 7, 21, 41, 25),
                   (2014, 3, 7, 22, 41, 25), (2014, 3, 8, 0, 19, 35)]

    r_trend = r_flight.filter_by_list([datetime(*item) for item in trend_times])
    r_interp = r_flight.interpolate(r_trend, T0['off-radar'])

if __name__ == '__main__':
    main()

