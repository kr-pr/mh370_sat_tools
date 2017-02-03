import inmarsat
import trajectory
from datetime import timedelta

inm_log = inmarsat.InmarsatLog.from_csv('data', 'inmarsat-su-log-redacted.csv')
bin_log = inm_log.bin_data()
time_step = bin_log.data[1].time - bin_log.data[0].time
traj_time_step = time_step/2
traj = trajectory.Trajectory.from_csv(
    bin_log.data[0].time-traj_time_step, traj_time_step,
    'data', acars='acars.csv', adsb='all-combined.csv', radar='route.csv')
int_traj = traj.int_data()
