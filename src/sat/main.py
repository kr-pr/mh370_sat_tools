'Runner for calculations'
from datetime import timedelta
import inmarsat
import trajectory
import radial

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
if __name__ == '__main__':
    main()

