import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

class Channel:
    """
    Calculates parameters for a prismatic rectangular or trapezoidal channel. 
    Pass the bottom width b in feet, the side slopes zleft and zright (z is the
    horizontal distance corresponding to a vertical rise of 1), Manning's n, 
    the longitudinal slope of the channel as a decimal (e.g. 6% as 0.06), and 
    the flowrate q in cfs to be conveyed. For a rectangular channel, pass 
    zleft = zright = 0, otherwise pass values for the sideslopes of a 
    trapezoidal channel. Capable of computing top width, water  area, wetted
    perimeter, hydraulic radius, normal depth, critical depth, determining if
    channel slope is mild or steep. There is also the option to pass the depth 
    of the channel y1 and y2 at two points, which cannot be equal, and the
    velocity correction factor alpha, which by default is equal to 1. 
    If y1 and y2 are passed, the class can determine which point is downstream
    and use the direct step method to determine the distance along the channel
    between the two points, as well as displaying a graph of the water surface
    and channel bottom if 'tograph = True' is passed.
    
    Methods are top(y), area(y), wet_perim(y), hyd_rad(y), norm_depth(), 
    crit_depth(), slope_cat(), downstream(), and direct_step(tograph)
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

    
    def top(self, y):
        """ 
        Calculates the top width T of a channel when the water depth y is passed
        """
        return self.b + y * (self.zleft + self.zright)

    def area(self, y):
        """
        Calculates the water area A using area of trapezoid formula when the
        water depth y is passed
        """
        return ((self.b+self.top(y))/2) * y

    def wet_perim(self, y):
        """ 
        Calculates the wetted perimeter P (the length of the wet portion of
        the channel) when the water depth y is passed
        """
        return np.sqrt(y**2 + (y*self.zleft)**2) + self.b + np.sqrt(y**2 + (y*self.zright)**2)

    def hyd_rad(self, y):
        """
        Calculates the hydraulic radius R (defined as R = A/P) when the water 
        depth y is passed
        """
        return self.area(y)/self.wet_perim(y)

    def norm_depth(self):
        """
        Takes no inputs. Calculates and returns the normal depth for an
        object of the 'Channel' class when the bottom width width b (ft), side
        slopes zleft & zright, Manning's n, the longitudinal slope of the channel
        (as a decimal), and the flowrate q (cfs) have been passed to the
        constructor. Assumes US units so k=1.49 in Manning equation
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
        Takes no inputs. Calculates and returns the critical depth for an object
        of the 'Channel' class when the bottom width b (ft), side slopes zleft 
        and zright, and the flowrate q (cfs) have been passed to the constructor.
        Assumes US units so g=32.2 ft/s^2
        """
        # Crit depth, based on specific energy
        # Q^2/g = A^3/T -> A^3/T - Q^2/g = 0
        def crit(y):
            return (self.area(y)**3 / self.top(y)) - (self.q**2 / 32.2)

        return fsolve(crit, x0=1)[0]

    def slope_cat(self):
        """
        Takes no inputs. Determines whether a profile is mild or steep depending
        on whether yn < yc (steep) or yn > yc (mild)
        """
        if self.norm_depth() < self.crit_depth():
            mild_steep = 'steep'
        elif self.norm_depth() > self.crit_depth():
            mild_steep = 'mild'
        # ignore case if yn = yc
        return 'Channel slope is {}'.format(mild_steep)


    def downstream(self):
        """
        Takes no inputs. Determines whether Point 1 or Point 2 is downstream 
        based on the type of channel profile from slope_cat. 
        """
        # skip further calculations if depths are not passed or both same
        if (self.y1 == None or self.y2 == None) or (self.y1 - self.y2 == 0 ):
            return                          

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

    def direct_step(self, tograph = None):
        """ 
        Uses the direct step method to calculate the distance between two
        depths y1 and y2 which should have been passed to the class constructor.
        Takes no inputs other than an optional value of tograph, which can
        is set to None by default. If you would like a graph of the water
        surface and channel bottom, pass a value for tograph that is NOT None. 
        """
        # Arbitrary decision: make distance of each step equal to 1/1000
        # of the vertical distance between the two points
        # small step size ensures accurate results
        step = abs(self.y1-self.y2)/1000

        ystart = min(self.y1, self.y2)      # start from smallest depth
        ystop = max(self.y1, self.y2)       # end at largest depths

        a_list = []         # list of areas
        r_list = []         # list of hydraulic radii
        v_list = []         # list of velocities
        vhead_list = []     # list of velocity heads
        e_list = []         # list of specific energies
        delta_e_list = []   # list of changes in specific energy
        sf_list = []        # list of water surface slopes, using Manning eq
        sf_avg_list = []    # list of averaged water surface slopes
        delta_x_list = []   # list of distances so far
        cum_x_list = []     # list of cumulative distance traveled

        two_g = 64.4 # 2*32.2

        y = ystart  # start iterating at the smallest step

        i = 0       # keep count of index as append to lists
        
        while y < ystop:
            a_list.append(self.area(y)) # calculate properties and add to list
            r_list.append(self.hyd_rad(y)) 
            v_list.append(self.q/a_list[i])
            
            # velocity head = alpha * v^2 / 2g
            vhead_list.append((self.alpha * v_list[i]**2) / two_g)
            
            # E = y + velocity head
            e_list.append(y + vhead_list[i]) # specific energy
            if i == 0:
                delta_e_list.append(0)  # change in specific energy, not 
                                        # defined for first element 
            else:
                delta_e_list.append(e_list[i] - e_list[i-1])
            
            # long calculation so calculate first then append
            # based on rearranging Manning equation for slope
            # Q = 1.49/n A R^2/3 S^1/2 -> S = ((Qn)/(1.49*A*R^2/3))^2
            sf = ((self.q * self.n) / (1.49 * a_list[i] * r_list[i]**(2/3)))**2
            sf_list.append(sf)
            if i == 0:
                sf_avg_list.append(0)
            else:
                sf_avg_list.append((sf_list[i] + sf_list[i-1])/2)    
            
            # change in distance
            # defined as delta E / (channel slope - averge water slope)
            if i == 0:
                delta_x_list.append(0) # no change yet for first element 
            else:
                delta_x_list.append((delta_e_list[i] / (self.slope - sf_avg_list[i])))
            
            if i == 0:
                cum_x_list.append(0)
            else:
                cum_x_list.append(delta_x_list[i] + cum_x_list[i-1])
                # cumulative distance is distance for this iteration plus
                # the cumulative distance so far
            
            i += 1
            y += step
        
        # pull last cumulative distance
        print('Points 1 and 2 are ', abs(cum_x_list[-1]), ' ft apart')
        
        if tograph == None:
            return
        else:
            # creating names for variables for convenience
            x =  [abs(ele) for ele in cum_x_list]   # take abs value just in 
                                                    # case distances negative
            
            # determine which point to start from
            # making sure to start from upstream point
            if self.downstream() == 'Point 1 is downstream of Point 2':
                y = np.linspace(self.y2, self.y1, 1001)
            elif self.downstream() == 'Point 2 is downstream of Point 1':
                y = np.linspace(self.y1, self.y2, 1001)
            else: 
                return 'Upstream point could not be determined'
            
            # the channel bottom can be modeled with a function starting from
            # the initial depth and continuing with m = -slope
            def slopefun(x):
                slope_y = []
                for i in range(len(x)):
                    slope_y.append(-self.slope * x[i])
                
                return slope_y
                
            plt.plot(x, y, color='blue', label='Water Surface')
            plt.plot(x, slopefun(x) ,color='black', label='Channel Bottom')
            plt.title('Graph of Water Surface Between Points 1 and 2', fontweight='black', fontfamily='monospace')
            plt.xlabel('Distance Along Channel', fontweight='bold')
            plt.ylabel('Depth')
            plt.legend(bbox_to_anchor=(0.5, -0.3), loc="center")
            plt.show()