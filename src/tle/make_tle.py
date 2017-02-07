'Fits TLE orbit elements to known satellite positions in ECEF'
from re import findall
from math import pi
#from numpy import array
#from scipy import optimize

def elem_from_tle(tle):
    'Extracts orbital elements from TLE'
    lines = tle.split('\n')
    elements = (lines[2][8:16], lines[2][17:25], lines[2][26:33],
                lines[2][34:42], lines[2][43:51], lines[2][52:63])
    return [float(x) for x in elements]

def elem_to_tle(tle, *elems):
    'Saves elements into TLE string'
    if len(elems) == 6:
        lines = tle.split('\n')
        elem_list = list(elems)
        elem_list[2] = int(elems[2])
        newline = lines[2][:8]+'{:08.4f} {:08.4f} {:07d} {:08.4f} {:08.4f} {:011.8f}'.format(
            *elem_list)+lines[2][63:-1]
        checksum = str(sum([int(x) for x in findall(r'\d', newline)]) % 10)
        lines[2] = newline+checksum
    else:
        raise ValueError
    new_tle = '\n'.join(lines)
    return new_tle

def earth_constants_from_text(file_name):
    'Loads earth movement constants from IERF file'
    with open('data/'+file_name, 'rt') as fin:
        line = next(fin)
        while not line[:6] == '14 3 7':
            line = next(fin)
        x_pm = float(line[18:27])*pi/648000.0
        y_pm = float(line[37:46])*pi/648000.0
        dut = float(line[58:68])
        lod = float(line[79:86])*1e-3
    return (dut, x_pm, y_pm, dut, lod)

def ecef_state_from_csv(file_name):
    'Loads Inmarsat satellite state vectors'
    with open('data/'+file_name, 'rt') as fin:
        data = []
        for line in fin:
            items = line.split(' ')
            time = [int(item) for item in items[0].split(':')]
            day = 8 if time[0] == 0 else 7
            date = [2014, 3, day]+time
            state = [float(item) for item in items[1:]]
            data.append((date, state))
    return data

def make_residual_func(ecef_state, orig_elems):
    def residual_func(*factors):
        nonlocal ecef_state, orig_elems
        new_state = [factors[i]*orig_elems[i] for i in range(6)]
        res = 0
        for date, state in ecef_state:
            teme_state = predict(tle)
            res += 0 
        return res
    return residual_func


def predict(tle):

    return None

def TEME_to_IERF(teme_r, teme_v)
    return None

def main():
    'Runs calculation chain'
    tle = '''0 INMARSAT 3-F1
1 23839U 96020A   14066.96754476 -.00000012  00000-0  10000-3 0  9995
2 23839 001.6371 073.1994 0005326 270.3614 234.8362 01.00274124 65669'''
    orig_elems = elem_from_tle(tle)

    sat_state_ecef = ecef_state_from_csv('ecef.txt')


if __name__ == '__main__':
    main()