'Contains time grid'

class TimeGrid:
    'Creates time grid from R(t) curve and interpolates'
    def __init__(self, data):
        self.data = data

    def interpolate(self):
        'Interpolates time on grid from values on arcs'
        int_data = None
        return TimeGrid(int_data)

    @classmethod
    def from_r_t(cls, radial):
        'Calculates time grid from radial distance function'
        data = None
        return cls(data)


