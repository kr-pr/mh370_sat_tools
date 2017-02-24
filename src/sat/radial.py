'Calculation of radial distance and time derivative'
from collections import namedtuple

Distance = namedtuple('Distance', 'time r')
class RadialDistance:
    'Compute and interpolate a/c to satellite radial distance function'

    def __init__(self, data):
        self.data = data

    def append(self, other):
        'Adds values to the end of self.data'
        last_time = self.data[-1].time
        extended_data = self.data + list(filter(lambda t: t.time > last_time, other.data))
        return RadialDistance(extended_data)

    def take_after(self, time_from):
        'Makes a new container with different starting time'
        cut_data = list(filter(lambda t: t.time >= time_from, self.data))
        return RadialDistance(cut_data)

    def filter_by_list(self, times):
        'Downsamples acc to list of timestamps'
        filtered_data = list(filter(lambda x: x.time in times, self.data))
        return RadialDistance(filtered_data)

    def interpolate(self, trend, time_from):
        'Interpolates with spline + Fourier spectrum of residual after substracting spline'
        from time_tools import interp_helper
        int_data = interp_helper(self.data, trend.data, time_from)
        return RadialDistance(int_data)

    @classmethod
    def from_traj(cls, traj):
        'Calculates radial distance from trajectory'
        from sat_tools import Satellite
        satellite = Satellite()
        data = [Distance(item.time, satellite.distance_to_ac(*item)) for item in traj]
        return cls(data)

    @classmethod
    def from_bto(cls, inm_log):
        'Calculates radial distance from BTO'
        def distance(time, bto):
            'Computes distance from satellite to aircraft from BTO'
            nonlocal satellite
            bias = 495680.0
            c = 299792458*1e-6
            return c*(bto+bias)/2 - satellite.distance_to_gs(time)

        from sat_tools import Satellite
        satellite = Satellite()

        data = [Distance(item.time, distance(item.time, item.bto)) for item in
                filter(lambda record: record.bto is not None, inm_log)]
        return cls(data)

