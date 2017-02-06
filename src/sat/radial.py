'Calculation of radial distance and time derivative'
from collections import namedtuple

Distance = namedtuple('Distance', 'time r')
class RadialDistance:
    'Compute and interpolate a/c to satellite radial distance function'

    def __init__(self, data):
        self.data = data

    def __add__(self, other):
        return RadialDistance(self.data + other.data)

    def interpolate(self):
        'Interpolates missing values with splines'
        int_data = None
        return RadialDistance(int_data)

    @classmethod
    def from_traj(cls, traj):
        'Calculates radial distance from trajectory'
        import sat
        satellite = sat.Satellite()
        data = [(item.time, satellite.distance_to_ac(*item)) for item in traj]
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

        data = [(item.time, distance(item.time, item.bto)) for item in
                filter(lambda record: record.bto is not None, inm_log)]
        return cls(data)

