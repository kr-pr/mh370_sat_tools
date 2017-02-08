'Helper functions for time and coordinate conversion from Vallado matlab codes'
from math import floor, fmod, pi, cos, sin
from numpy import array, cross

def jd(*time_ut1):
    'Computes Julian Date'
    year, month, day, hour, minute, second = time_ut1
    jday = 367.0 * year - floor((7 * (year + floor((month + 9) / 12.0)))* 0.25) + \
        floor(275 * month / 9.0) + day + 1721013.5 + \
        (second + minute * 60.0 + hour * 3600.0) / 86400.0
    return jday


def gmst(lod, jul_day):
    '''Computes smoothed Greenwich siderial time:
    http://articles.adsabs.harvard.edu//full/1982A%26A...105..359A/0000360.000.html'''
    tut1 = (jul_day - 2451545.0) / 36525.0
    seconds = -6.2e-6 * tut1 * tut1 * tut1 + 0.093104 * tut1 * tut1 + \
        (876600.0 * 3600.0 + 8640184.812866) * tut1 + 67310.54841
    _theta = 2 * pi * fmod(seconds / 86400.0, 1.0)
    theta = _theta if _theta > 0 else _theta + 2*pi
    omega = 7.29211514670698e-5 * (1.0 - lod / 86400.0)

    return theta, omega


def teme_to_ecef(r_teme, v_teme, x_p, y_p, theta, omega):
    'Rotates coordinates to ECEF'
    s_x = sin(x_p)
    c_x = cos(x_p)
    s_y = sin(y_p)
    c_y = cos(y_p)
    s_z = sin(theta)
    c_z = cos(theta)
    rot_x = array(([1.0, 0, 0], [0, c_y, -s_y], [0, s_y, c_y]))
    rot_y = array(([c_x, 0, s_x], [0, 1.0, 0], [-s_x, 0, c_x]))
    rot_z = array(([c_z, -s_z, 0], [s_z, c_z, 0], [0, 0, 1.0]))

    rot_xyz = rot_z.dot(rot_x.T).dot(rot_y.T)
    r_ecef = r_teme.dot(rot_xyz)
    v_ecef = (v_teme - cross(array([0, 0, omega]), r_teme)).dot(rot_xyz)

    return r_ecef, v_ecef
