'Runner for calculations'
from sys import argv
from json import load
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

def frange(a, b, step):
    c = a
    if b > a:
        while not c > b:
            yield c
            c += step
    else:
        while not c < b:
            yield c
            c += step

def main(args):
    'Runs calculation chain'
    try:
        action = args[1]
        config = args[2]
    except IndexError:
        action = config = None

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

    if action == 'polygon':
        with open(config, 'rt') as cfg_file:
            cfg = load(cfg_file)
        from shapefile import Writer, POLYGON
        shp_file = Writer(POLYGON)
        shp_file.field('TIME','C','20')
        for contour in cfg['times']:
            contour_pts = []
            ind_a = 0
            ind_b = 1
            contour_time = datetime(*contour['time'])
            if contour_time > r_interp.data[-1][0]:
                contour_time = r_interp.data[-1][0]
            for offset in cfg['time_delta']:
                time_offset = timedelta(minutes=offset)
                cur_time = contour_time+time_offset
                contour_pts += [
                    r_interp.find_loc(cur_time, lat) for lat in frange(
                        contour['lat_bounds'][ind_a],
                        contour['lat_bounds'][ind_b],
                        cfg['lat_step']*(ind_b-ind_a)
                    )
                ]
                ind_a, ind_b = ind_b, ind_a
            shp_file.poly(parts=[contour_pts])
            poly_name = '{}_{}_{}'.format(*contour['time'][2:5])
            shp_file.record(poly_name)
        shp_file.save(cfg['save_to_file'])


if __name__ == '__main__':
    main(argv)

