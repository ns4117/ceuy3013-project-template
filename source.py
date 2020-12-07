import numpy as np
from scipy.optimize import fsolve

class Channel:
    """
    Calculates parameters for an open channel. Pass the bottom width b in feet,
    the side slopes zleft and zright (z is the horizontal distance corresponding
    to a vertical rise of 1), Manning's n, the longitudinal slope of the channel
    as a decimal (e.g. 6% slope is passed as 0.06), and the flowrate q in ft3/s
    to be conveyed. Capable of computing top width, water area, wetted perimeter,
    hydraulic radius, normal depth, critical depth, determining if channel slope
    is mild or steep. There is also the option to pass the depth of the channel
    y1 and y2 at two points, which cannot be equal, and the velocity correction
    factor alpha, which by default is equal to 1. If y1 and y2 are passed,
    the class can determine which point is downstream and use the direct step
    method to determine the distance along the channel between the two points.
    """
    def __init__(self, b, zleft, zright, n, slope, q, y1=None, y2=None, alpha=1):
        """
        Constructor
        """
        self.b = b
        self.zleft = zleft
        self.zright = zright
        self.n = n
        self.slope = slope
        self.q = q
        self.y1 = y1
        self.y2 = y2
        self.alpha = alpha

    def __str__(self):
        return 'This is a channel with various parameters'

    # Top width T
    def top(self, y):
        return self.b + y * (self.zleft + self.zright)

    # Water Area A using area of trapezoid formula
    def area(self, y):
        return ((self.b+self.top(y))/2) * y

    # wetted perimeter P
    def wet_perim(self, y):
        return np.sqrt(y**2 + (y*self.zleft)**2) + self.b + np.sqrt(y**2 + (y*self.zright)**2)

    # Hydraulic radius R = A/P
    def hyd_rad(self, y):
        return self.area(y)/self.wet_perim(y)

    def norm_depth(self):
        """
        Calculates and returns the normal depth for a channel given the bottom
        width b (ft), side slopes zleft & zright, Manning's n, the longitudinal
        slope of the channel inputted as a decimal, and the flowrate q (cfs) to
        convey. For a rectangular channel, input zleft=zright=0, otherwise give
        side slope values for trapezoidal channels. z is the horizontal distance
        corresponding to a vertical rise of 1. Assumes US units so k=1.49 in
        Manning equation
        """
        # Based on manning equation
        # Q = k/n AR^2/3 S^1/2 -> ((k/n) * S^1/2) * A * R^2/3 - Q = 0
        def norm(y):
            return (1.49/self.n) * np.sqrt(self.slope) * self.area(y) * self.hyd_rad(y)**(2/3) - self.q

        return fsolve(norm, x0=1)[0]    # use initial guesss of 1
                                        # will return 1-D array by default,
                                        # so pull first value

    def crit_depth(self):
        """
        Calculates and returns the critical depth for a channel given
        the bottom width b (ft), side slopes zleft and zright, and the flowrate
        q (cfs) to convey. For a rectangular channel, input zleft=zright=0,
        otherwise give side slope values for trapezoidal channels. z is the
        horizontal distance corresponding to a vertical rise of 1. Assumes US
        units so g=32.2 ft/s^2
        """
        # Crit depth, based on specific energy
        # Q^2/g = A^3/T -> A^3/T - Q^2/g = 0
        def crit(y):
            return (self.area(y)**3 / self.top(y)) - (self.q**2 / 32.2)

        return fsolve(crit, x0=1)[0]

    def slope_cat(self):
        """
        Determines whether a profile is mild or steep depending on whether
        yn < yc (steep) or yn > yc (mild)
        """
        if self.norm_depth() < self.crit_depth():
            mild_steep = 'steep'
        elif self.norm_depth() > self.crit_depth():
            mild_steep = 'mild'
        # ignore case if yn = yc
        return 'Channel slope is {}'.format(mild_steep)


    def downstream(self):
        """
        Determines whether Point 1 or Point 2 is downstream based on the
        type of channel profile.
        """

        if (self.y1 == None or self.y2 == None) or (self.y1 - self.y2 == 0 ):
            return                          # skip further calculations
                                            # if depths are not passed
                                            # or if both depths are same

        # Mild slopes
        if self.norm_depth() > self.crit_depth():
            # M1 slope, deeper downstream
            if self.y1 > self.norm_depth():
                if self.y1 > self.y2:
                    return 'Point 1 is downstream of Point 2'
                else:
                    return 'Point 2 is downstream of Point 1'
            # M3 slope, deeper downstream
            if self.y1 < self.crit_depth():
                if self.y1 > self.y2:
                    return 'Point 1 is downstream of Point 2'
                else:
                    return 'Point 2 is downstream of Point 1'
            # M2 slope, deeper upstream
            else:
                if self.y1 > self.y2:
                    return 'Point 2 is downstream of Point 1'
                else:
                    return 'Point 1 is downstream of Point 2'
        # Steep slopes
        else:
            # S1 slope, deeper downstream
            if self.y1 > self.crit_depth():
                if self.y1 > self.y2:
                    return 'Point 1 is downstream of Point 2'
                else:
                    return 'Point 2 is downstream of Point 1'
            # S3 slope, deeper downstream
            if self.y1 < self.norm_depth():
                if self.y1 > self.y2:
                    return 'Point 1 is downstream of Point 2'
                else:
                    return 'Point 2 is downstream of Point 1'
            # S2 slope, deeper upstream
            else:
                if self.y1 > self.y2:
                    return 'Point 2 is downstream of Point 1'
                else:
                    return 'Point 1 is downstream of Point 2'

    def direct_step(self):
        step = abs(self.y1-self.y2)/1000    # make distance of each step
                                            # equal to 1/1000 of the vertical
                                            # distance between the two points

        ystart = min(self.y1, self.y2)      # start from smallest depth
        ystop = max(self.y1, self.y2)       # end at largest depths

        a_list = []         # list of areas
        p_list = []         # list of wetted perimeters
        r_list = []         # list of hydraulic radii
        v_list = []         # list of velocities
        vhead_list = []     # list of velocity heads
        e_list []           # list of specific energies
        delta_e_list = []   # list of changes in specific energy
        sf_list = []        # list of water surface slopes
        sf_avg_list = []    # list of averaged water surface slopes

        g = 32.2

        y = ystart # start iterating at the smallest step
        while y < ystop:
            a_list.append(area(y))
            p_list.append(wet_perim(y))
            r_list.append(hyd_rad(y))
            v_list.append(self.q/area(y))
            vhead_list.append(self.alpha * v_list[y]**2 / 2*g)

            y += step
