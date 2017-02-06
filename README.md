This is a Python class collection used for computing time and direction grids for flight MH370 based on Inmarsat data. The grids are used to define target time contours and linear feature azimuths on available IR imagery.

Grids are obtained via following process:
1. Radial distance from a/c to satellite is calculated for all BTO values.
2. Radial distance is interpolated with a suitable smooth function.
3. Time derivative of radial distance is computed.
4. R(t) and dR/dt are used together with BFO model to obtain possible track azimuth versus position on an arc.
5. Time grid is calculated from interpolated R(t) function
6. Azimuth grid is calculated by 2-D interpolation of values derived from BFO
