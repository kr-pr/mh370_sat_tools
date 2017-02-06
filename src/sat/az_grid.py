'Aircraft azimuth on a grid'

class AzimuthGrid:
    'Creates azimuth grid from BFO and interpolates'
    bnds = ((15, -40, 0.1), (85, 105, 0.1))
    def __init__(self, data):
        self.data = data

    def interpolate(self):
        'Performs 2D interpolation over azimuth values on arc'
        int_data = None
        return AzimuthGrid(int_data)

    @classmethod
    def from_bfo(cls, time_grid, inmarsat_log):
        'Creates azimuth grid from time grid and BFO values'
        data = None
        return cls(data)

