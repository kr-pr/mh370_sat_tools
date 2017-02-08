'Time-related shared functions'
from datetime import datetime, timedelta

T0 = datetime(2014, 3, 7, 16, 0, 0, 0)

def to_sec(dtime):
    'Computes offset seconds from datetime'
    return (dtime-T0).total_seconds()

def to_dt(sec):
    'Computes datetime from offset seconds'
    delta = timedelta(seconds=sec)
    return T0+delta

