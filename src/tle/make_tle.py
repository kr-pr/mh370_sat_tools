'Fits TLE to known satellite position'
from scipy import optimize

def parse_tle(tle):
    return {}

def position_from_csv(file_name):
    return []

def make_residual_func(data):
    def residual_func():
        nonlocal data
        res = None
        return res
    return residual_func

def fit_tle():

def save_tle():

def main():
    'Runs calculation chain'
    tle = '''0 INMARSAT 3-F1
1 23839U 96020A   14066.96754476 -.00000012  00000-0  10000-3 0  9995
2 23839 001.6371 073.1994 0005326 270.3614 234.8362 01.00274124 65669'''
    elements = parse_tle(tle)


if __name__ == '__main__':
    main()