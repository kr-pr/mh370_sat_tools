'Contains satellite state'
import ephem

def to_eph_date(time):
    'Converts from datetime to Pyephem Date'
    return ephem.Date((time.year, time.month, time.day, time.hour, time.minute,
                       time.second+time.microsecond*1e-6))

class Satellite:
    'Calculates distances from satellite to ground station and a/c'
    def __init__(self):
        tle = '''0 INMARSAT 3-F1
1 23839U 96020A   14066.96754476 -.00000012  00000-0  10000-3 0  9995
2 23839 001.6371 073.1994 0005326 270.3614 234.8362 01.00274124 65669'''
        self.sat = ephem.readtle(*[line for line in tle.split('\n')])
        perth_ll = ('-31.80463888', '115.8874444', 46.0)
        self.perth = ephem.Observer()
        self.perth.lat = perth_ll[0]
        self.perth.lon = perth_ll[1]
        self.perth.elevation = perth_ll[2]
        self.aircraft = ephem.Observer()

    def distance_to_ac(self, time, lat, lon, alt):
        'Computes distance from satellite to known aircraft position'
        self.aircraft.lat = str(lat)
        self.aircraft.lon = str(lon)
        self.aircraft.elevation = alt*0.3048
        self.aircraft.date = to_eph_date(time)
        self.sat.compute(self.aircraft)
        return self.sat.range

    def distance_to_gs(self, time):
        'Computes distance from satellite to Perth ground station'
        self.perth.date = to_eph_date(time)
        self.sat.compute(self.perth)
        return self.sat.range
