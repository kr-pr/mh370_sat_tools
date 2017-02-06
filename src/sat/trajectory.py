'Trajectory data import and cleaning'
from collections import namedtuple
from datetime import datetime

Position = namedtuple('Position', 'time lat lon alt')

class Trajectory:
    'Loads and interpolates available aircraft position data'

    def __init__(self, data):
        self.data = data

    def int_data(self, time_from, time_step):
        'Interpolates position data to half the BTO/BFO bin interval'
        def make_time_finder(items):
            'Closure for finding function'
            pos = 0
            def time_find_func(test_value):
                'Finding in sorted array with state tracking'
                nonlocal pos, items
                while items[pos].time < test_value and pos < len(items):
                    pos += 1
                return pos
            return time_find_func

        finder = make_time_finder(self.data)
        interpolated = []
        time = time_from
        while time < self.data[-1].time:
            ind = finder(time)
            if time == self.data[ind].time:
                int_item = self.data[ind]
            else:
                pair = list(zip(self.data[ind-1], self.data[ind]))
                time_diff = (time - self.data[ind-1].time,
                             self.data[ind].time - time)
                sec_diff = [item.total_seconds() for item in time_diff]
                int_item = Position(time, *[(sec_diff[0] * y + sec_diff[1] * x) / sum(sec_diff)
                                            for x, y in pair[1:]])
            interpolated.append(int_item)
            time += time_step

        return Trajectory(interpolated)

    @classmethod
    def from_csv(cls, folder, **files):
        'Loads position data from files'
        cols = {
            "adsb": (0, 4, 5, 3),
            "acars": (0, 6, 7, 1),
            "radar": (0, 2, 1, None)
        }

        def parse_time(time_string):
            'Parses time string'
            hms = [int(item) for item in time_string.split(':')]
            return datetime(2014, 3, 7, hms[0], hms[1], hms[2], 0)

        def load_airport():
            'Parses aircraft position in airport'
            at_klia = [('16:00:00', '2:44:48.1', '101:42:45.5', '21.15'),
                       ('16:32:42', '2:44:48.1', '101:42:45.5', '21.15'),
                       ('16:40:38', '2:44:51.8', '101:43:15.4', '21.15')]

            def parse_deg(dms_string):
                'Parses dms string'
                return sum([float(item) / (60**i)
                            for item, i in zip(dms_string.split(':'), range(0, 3))])
            return [
                Position(parse_time(item[0]), parse_deg(item[1]),
                         parse_deg(item[2]), float(item[3]) / 0.3048)
                for item in at_klia]

        def load_adsb(time_string, lat_string, lon_string, alt_string):
            'Loads Sladen ADS-B file'
            if (not lat_string) or (not lon_string):
                return None
            return Position(datetime.utcfromtimestamp(float(time_string)),
                            float(lat_string), float(lon_string), float(alt_string))

        def load_csv(time_string, lat_string, lon_string, alt_string):
            'Loads ACARS/engine and sk999 interpolated PSR data'
            if alt_string is None:
                alt = 35000
            else:
                alt = float(alt_string)
            return Position(parse_time(time_string),
                            float(lat_string), float(lon_string), alt)

        loaders = {
            "adsb": load_adsb,
            "acars": load_csv,
            "radar": load_csv
        }

        data = load_airport()
        for file_type, file_name in files.items():
            with open(folder + '/' + file_name, 'rt') as fin:
                next(fin)
                for line in fin:
                    items = line.split(',')
                    args = []
                    for i in range(4):
                        try:
                            args.append(items[cols[file_type][i]])
                        except TypeError:
                            args.append(None)
                    parsed = loaders[file_type](*args)
                    if parsed is not None:
                        data.append(parsed)
        return cls(sorted(data, key=lambda item: item.time))
