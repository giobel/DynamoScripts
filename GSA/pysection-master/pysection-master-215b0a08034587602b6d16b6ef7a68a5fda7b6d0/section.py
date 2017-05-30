import math
import bisect

import shape
import material

class Bar:
    """A circular reinforcement bar"""

    #metric diameters sizes
    diam_10M = 11.3
    diam_12M = 12.7
    diam_15M = 16.0
    diam_20M = 19.5
    diam_25M = 25.2
    diam_30M = 29.9
    diam_35M = 35.7
    diam_45M = 43.7
    diam_55M = 56.4

    def __init__(self,steel,diameter,depth):
        self.steel = steel
        self.diameter = diameter #[mm]
        self.depth = depth #[mm]

        self.shape = shape.Circle(diameter,depth-diameter/2)

class Section:
    """A section of reinforced concrete"""

    def __init__(self,concrete,profile,bars):
        self.concrete = concrete
        self.profile = shape.Compound([profile])
        self.bars = bars

        self.concrete_factor = 1
        self.steel_factor = 1

        #add holes to profile for the bars
        for bar in bars:
            self.profile.holes.append(bar.shape)

        #get material areas
        self.concrete_area = self.profile.area()

        self.steel_area = 0
        for bar in bars:
            self.steel_area += bar.shape.area()

        #top of the section is considered 0 depth
        assert self.profile.limits()[0] == 0
        assert self.profile.limits()[1] > 0

        self.height = self.profile.limits()[1]
        self.middle = self.profile.centroid()

        #create mirrored profile and bars
        self.mirrored_profile = self.profile.reflect()
        self.mirrored_profile.shift(self.height)

        self.mirrored_bars = []
        for bar in self.bars:
            mirrored_bar = Bar(bar.steel,bar.diameter,-bar.depth+self.height)
            self.mirrored_bars.append(mirrored_bar)

        self.mirrored_middle = self.height - self.middle

    def calc_peak_axial_strength(self):
        #calculate P_ro, Reinforced Concrete 1 pg 173, Clause 10.10.4
        result = 0

        for bar in self.bars:
            bar_area = bar.shape.area()

            result += self.steel_factor * bar.steel.strength * bar_area / 1000

            #print(str(self.steel_factor) + " * " + str(bar.steel.strength) + " * " + str(bar_area) + " / 1000 = " + str(self.steel_factor * bar.steel.strength * bar_area / 1000))

        #use self.profile to calculate area, bar areas already removed
        result += self.concrete.alpha_1 * self.concrete_factor * self.concrete.strength * self.concrete_area / 1000

        #print(str(self.concrete.alpha_1) + " * " + str(self.concrete_factor) + " * " + str(self.concrete.strength) + " * " + str(self.concrete_area) + " / 1000 = " + str(self.concrete.alpha_1 * self.concrete_factor * self.concrete.strength * self.concrete_area / 1000))

        return result

    def calc_M_N(self):
        count = 100

        positive_bending = []
        negative_bending = []
        for i in range(0,count*2):
            positive_bending.append(self.calc_M_N_for_axis(self.height*(i+0.5)/count,False))
            negative_bending.append(self.calc_M_N_for_axis(self.height*(i+0.5)/count,True))

        #remove the overlap
        i_pos = 1
        i_neg = 1

        while i_pos < count*2 and i_neg < count*2:
            m_pos = positive_bending[i_pos][0]
            m_neg = negative_bending[i_neg][0]

            f_pos = positive_bending[i_pos][1]
            f_neg = negative_bending[i_neg][1]

            if m_pos < m_neg:
                positive_bending = positive_bending[0:i_pos]
                negative_bending = negative_bending[0:i_neg]
                break

            if f_pos > f_neg:
                i_pos += 1
            else:
                i_neg += 1

        #combine result
        result = []

        result.extend(positive_bending)

        negative_bending.reverse()
        result.extend(negative_bending)

        result.append(result[0])

        return MNChart(result)

    def calc_M_N_for_axis(self,neutral_axis,flip):
        #calculate total compressive force of concrete
        concrete_force = 0
        concrete_moment = 0

        if flip:
            profile = self.mirrored_profile
            bars = self.mirrored_bars
            middle = self.mirrored_middle
        else:
            profile = self.profile
            bars = self.bars
            middle = self.middle

        if True:
            #treat the profile like a series of rectangular blocks
            dx = 10 #[mm]
            x = neutral_axis

            #sum the forces of concrete areas in compression
            while x > 0:
                slice_area = profile.area_slice(x-dx,x) #[mm^2 = e-6 m^2]
                slice_middle = profile.centroid_slice(x-dx,x) #[mm]

                strain = self.concrete.strain_ultimate * (1 - slice_middle / neutral_axis) #[]
                stress = self.concrete.calc_stress(strain) #[MPa]

                force = self.concrete_factor * stress * slice_area / 1000 #[kN]
                moment = force * (slice_middle-middle) / 1000 #[kNm]
                #print("Area: " + str(slice_area) + ", Middle: " + str(slice_middle))
                #print("Strain: " + str(strain) + ", Stress: " + str(stress))
                #print("Force:" + str(force) + ", Moment:" + str(moment))

                concrete_force += force
                concrete_moment += moment

                x -= dx
        else:
            #use rectangular block
            concrete_force = self.concrete_factor * -self.concrete.alpha_1 * self.concrete.beta_1 * profile.area_slice(0,neutral_axis) * self.concrete.strength / 1e3
            concrete_moment = concrete_force * (self.concrete.beta_1*neutral_axis/2 - middle) / 1e3

        #calculate total force of steel
        steel_force = 0
        steel_moment = 0

        for bar in bars:
            bar_area = bar.shape.area()
            bar_middle = bar.shape.centroid()

            strain = self.concrete.strain_ultimate * (1 - bar_middle / neutral_axis) #[]
            stress = bar.steel.calc_stress(strain) #[MPa]

            force = self.steel_factor * stress * bar_area / 1000 #[kN]
            moment = force * (bar_middle-middle) / 1000 #[kNm]
            #print("Area: " + str(bar_area) + ", Middle: " + str(bar_middle))
            #print("Strain: " + str(strain) + ", Stress: " + str(stress))
            #print("Force:" + str(force) + ", Moment:" + str(moment))

            steel_force += force
            steel_moment += moment

        total_force = concrete_force + steel_force
        total_moment = concrete_moment + steel_moment

        #print(neutral_axis)
        #print("F: " + str(total_force) + " = " + str(concrete_force) + " + " + str(steel_force))
        #print("M: " + str(total_moment) + " = " + str(concrete_moment) + " + " + str(steel_moment))

        if flip:
            total_moment = -total_moment

        return total_moment, total_force

class MNChart:
    """A moment axial load chart"""

    def __init__(self,entries):
        self.entries = entries

        self.points_in_M = sorted(range(len(self.entries)), key = lambda i: entries[i][0])
        self.points_in_N = sorted(range(len(self.entries)), key = lambda i: entries[i][1])

        #cache DC ranges
        self.max_M_index = max(range(len(self.entries)), key=lambda i: self.entries[i][0])
        self.min_M_index = min(range(len(self.entries)), key=lambda i: self.entries[i][0])
        self.max_N_index = 0
        self.min_N_index = min(range(len(self.entries)), key=lambda i: self.entries[i][1])

        self.low_M_indexes = list(range(self.min_N_index,len(self.entries)-1)) + [0]
        self.high_M_indexes = list(reversed(range(0,self.min_N_index+1)))
        self.low_N_indexes = list(reversed(range(self.max_M_index,self.min_M_index+1)))
        self.high_N_indexes = list(range(self.min_M_index,len(self.entries)-1)) + list(range(0,self.max_M_index+1))

        self.low_M_lookup = [self.entries[i][1] for i in self.low_M_indexes]
        self.high_M_lookup = [self.entries[i][1] for i in self.high_M_indexes]
        self.low_N_lookup = [self.entries[i][0] for i in self.low_N_indexes]
        self.high_N_lookup = [self.entries[i][0] for i in self.high_N_indexes]

        self.angles = [math.atan2(self.entries[i][1],self.entries[i][0]) for i in range(0,len(self.entries))]

    def calc_DC_moment(self,value):
        #takes an M,N tuple and returns the DC for moment load
        if value[0] > 0:
            lookup = self.high_M_lookup
            indexes = self.high_M_indexes
        else:
            lookup = self.low_M_lookup
            indexes = self.low_M_indexes

        iindex = bisect.bisect_left(lookup,value[1])
        if iindex == 0 or iindex == len(lookup):
            return None

        index_a = indexes[iindex]
        index_b = indexes[iindex+1]
        param = (value[1] - self.entries[index_a][1]) / (self.entries[index_b][1] - self.entries[index_a][1])

        capacity = self.entries[index_a][0] + param * (self.entries[index_b][0] - self.entries[index_a][0])

        return value[0] / capacity

    def calc_DC_axial(self,value):
        #takes an M,N tuple and returns the DC for axial load
        if value[1] > 0:
            lookup = self.high_N_lookup
            indexes = self.high_N_indexes
        else:
            lookup = self.low_N_lookup
            indexes = self.low_N_indexes

        iindex = bisect.bisect_left(lookup,value[0])
        if iindex == 0 or iindex == len(lookup):
            return None

        index_a = indexes[iindex]
        index_b = indexes[iindex+1]
        param = (value[0] - self.entries[index_a][0]) / (self.entries[index_b][0] - self.entries[index_a][0])

        capacity = self.entries[index_a][1] + param * (self.entries[index_b][1] - self.entries[index_a][1])

        return value[1] / capacity

    def calc_DC_radial(self,value):
        #takes an M,N tuple and returns the DC for combined radial load
        
        #todo
        return 1