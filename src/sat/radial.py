'Calculation of radial distance and time derivative'
from collections import namedtuple
from time_conv import to_sec

Distance = namedtuple('Distance', 'time r')
class RadialDistance:
    'Compute and interpolate a/c to satellite radial distance function'

    def __init__(self, data):
        self.data = data

    def extend(self, other):
        'Adds values to the end of self.dataa'
        last_time = self.data[-1].time
        extended_data = self.data + list(filter(lambda t: t.time > last_time, other.data))
        return RadialDistance(extended_data)

    def as_array(self):
        'Returns self.data as tuple of Numpy arrays'
        from numpy import array
        combined = array([(to_sec(item.time), item.r) for item in self.data])
        return combined[:, 0, None], combined[:, 1, None]

    def interpolate(self):
        'Interpolates missing values with splines'
        from scipy.interpolate import splrep
        x, y = self.as_array()
        return splrep(x, y, s=len(self.data))

    @classmethod
    def from_traj(cls, traj):
        'Calculates radial distance from trajectory'
        import sat
        satellite = sat.Satellite()
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

        import sat
        satellite = sat.Satellite()

        data = [Distance(item.time, distance(item.time, item.bto)) for item in
                filter(lambda record: record.bto is not None, inm_log)]
        return cls(data)

