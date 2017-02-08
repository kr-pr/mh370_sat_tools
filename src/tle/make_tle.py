'Fits TLE orbit elements to known satellite positions in ECEF'
from re import findall
from math import pi
from numpy import array, multiply, zeros
from scipy.optimize import minimize
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

import astro

def elem_from_tle(tle):
    'Extracts orbital elements from TLE'
    lines = tle.split('\n')
    elements = (lines[2][8:16], lines[2][17:25], lines[2][26:33],
                lines[2][34:42], lines[2][43:51], lines[2][52:63])
    return array([float(x) for x in elements])

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
    return x_pm, y_pm, dut, lod

def ecef_state_from_csv(file_name):
    'Loads Inmarsat satellite state vectors'
    with open('data/'+file_name, 'rt') as fin:
        data = []
        for line in fin:
            items = line.split(' ')
            time = [int(item) for item in items[0].split(':')]
            day = 8 if time[0] == 0 else 7
            date = [2014, 3, day]+time
            state = array([float(item) for item in items[1:]])
            data.append((date, state))
    return data

def make_teme_ecef_conv_func(*constants):
    'Closure for ECEF conversion function'
    def teme_ecef_conv(r_t, v_t, *time_utc):
        'Converts from TEME to ECEF'
        nonlocal constants
        x_pm, y_pm, dut, lod = constants
        time_ut1 = list(time_utc)
        time_ut1[-1] += dut
        jul_day = astro.jd(*time_ut1)
        theta, omega = astro.gmst(lod, jul_day)
        r_e, v_e = astro.teme_to_ecef(r_t, v_t, x_pm, y_pm, theta, omega)
        return r_e, v_e
    return teme_ecef_conv

def tle_from_factors(tle, factors, orig_elems):
    weights = array([1.0,1.0,10000.0,1.0,1.0,1e-4])
    new_state = orig_elems+multiply(factors, weights)
    new_tle = elem_to_tle(tle, *list(new_state))
    return new_tle

def make_residual_func(tle, ecef_state, orig_elems, conv_func):
    'Closure for least squares residual function'
    def residual_func(factors):
        'Calculates sum of squared residuals over all known state vectors'
        nonlocal tle, ecef_state, orig_elems, conv_func
        new_tle = tle_from_factors(tle, factors, orig_elems)
        res = 0
        for time, state in ecef_state:
            r_t, v_t = predict(new_tle, *time)
            r_e, v_e = conv_func(array(r_t), array(v_t), *time)
            res_r = r_e - state[:3]
            res_v = (v_e - state[3:])*1e3
            res += res_r.dot(res_r) + res_v.dot(res_v)
        print(factors)
        return res
    return residual_func

def predict(tle, *time):
    'Calculates state vector using SGP4 routines'
    lines = tle.split('\n')
    satellite = twoline2rv(lines[1], lines[2], wgs72)
    position, velocity = satellite.propagate(*time)
    return position, velocity

def main():
    'Runs calculation chain'
    constants = earth_constants_from_text('finals2000A.data')
    ecef_conv_func = make_teme_ecef_conv_func(*constants)

    tle = '''0 INMARSAT 3-F1
1 23839U 96020A   14066.96754476 -.00000012  00000-0  10000-3 0  9995
2 23839 001.6371 073.1994 0005326 270.3614 234.8362 01.00274124 65669'''
    orig_elements = elem_from_tle(tle)
    sat_state_ecef = ecef_state_from_csv('ecef.txt')
    resid_func = make_residual_func(tle, sat_state_ecef, orig_elements, ecef_conv_func)
    opt_factors = minimize(resid_func, zeros(6), method='BFGS', options={'maxiter':11, 'eps':1e-4})
    opt_tle = tle_from_factors(tle, opt_factors.x, orig_elements)
    with open('data/opt.tle', 'wt') as fout:
        for line in opt_tle:
            fout.write(line)

if __name__ == '__main__':
    main()
