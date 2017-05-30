import math

class Material:
    """A type of material"""

    def calc_stress(self,strain):
        return 0

class Concrete(Material):
    """A type of concrete"""

    def __init__(self,strength):
        self.strength = strength #f'_c peak compressive stress [MPa]
        self.strain_ultimate = -0.0035 #eps_cu crushing strain [] Clause 10.1.3
        self.update()

    def update(self):
        self.alpha_1 = 0.85 - 0.0015 * self.strength #a_1 [] Reinforced Concrete 1 pg 61
        self.beta_1 = 0.97 - 0.0025 * self.strength #b_1 [] Reinforced Concrete 1 pg 61

        self.curve_factor = 0.8 + self.strength / 17 #n [] Prestressed Concrete Structures pg 63
        self.decay_factor = max(1, 0.67 + self.strength / 62) #k [] Prestressed Concrete Structures pg 63
        self.tangent_stiffness = 3320 * math.sqrt(self.strength) + 6900 #E_c Young's modulus [MPa] Prestressed Concrete Structures pg 63
        #self.tangent_stiffness = 4730 * math.sqrt(self.strength) #E_c Young's modulus [MPa] Prestressed Concrete Structures pg 63
        self.strain_peak = -(self.strength / self.tangent_stiffness) * (self.curve_factor / (self.curve_factor - 1)) #eps'_c [] Prestressed Concrete Structures pg 63

        #self.secant_stiffness = 4500 * math.sqrt(self.strength) #E_cs [MPa] Clause 8.6.2.3 - Reinforced Concrete 1 pg 12
        #self.tangent_stiffness = -2 * self.strength / self.strain_peak #E_ct [MPa] Reinforced Concrete 1 pg 13, hognestad parabola
        #self.tangent_stiffness = 5000 * math.sqrt(self.strength) #E_ct [MPa] Reinforced Concrete 1 pg 13
        self.strength_tensile = 0.33 * math.sqrt(self.strength) #f'_t tensile cracking stress [MPa] Reinforced Concrete 1 pg 14
        self.strength_rupture = 0.6 * math.sqrt(self.strength) #f_r [MPa] Reinforced Concrete 1 pg 14
        self.strength_spliting = 0.5 * math.sqrt(self.strength) #f_sp [MPa] Reinforced Concrete 1 pg 15
        self.strength_double_punch = 0.45 * math.sqrt(self.strength) #f_dp [MPa] Reinforced Concrete 1 pg 16

    def calc_stress(self,strain):
        return self.calc_stress_popovics_hsc(strain)

    def calc_stress_hognestad(self,strain): #hognestad parabola [MPa] Reinforced Concrete 1 pg 30
        if strain > 0:
            return 0

        #adequate for normal strength concrete

        strain_ratio = strain / self.strain_peak

        return -self.strength * (2*strain_ratio - strain_ratio*strain_ratio)

    def calc_stress_popovics_nsc(self,strain): #[MPa] Mechanics of Reinforced Concrete pg 141
        if strain > 0:
            return 0

        #adequate for normal strength concrete, f'_c <= 50 MPa

        #NOTE: Uses same tangent stiffness and strain peak as high strength concrete, see below

        strain_ratio = strain / self.strain_peak
        peak_stiffness = -self.strength / self.strain_peak

        factor = self.tangent_stiffness / (self.tangent_stiffness - peak_stiffness)

        return -self.strength * strain_ratio * factor / (factor - 1 + math.pow(strain_ratio,factor))

    def calc_stress_popovics_hsc(self,strain): #[MPa] Prestressed Concrete Structures pg 61
        if strain > 0:
            return 0

        #adequate for high strength concrete, f'_c > 50 MPa

        strain_ratio = strain / self.strain_peak
        decay_factor = max(1,self.decay_factor)

        return -self.strength * strain_ratio * self.curve_factor / (self.curve_factor - 1 + math.pow(strain_ratio, self.curve_factor*decay_factor))

    def calc_stress_hoshikuma(self,strain): #[MPa] Mechanics of Reinforced Concrete pg 142
        if strain > 0:
            return 0

        #adequate for concrete up to f'_c ~= 80 MPa

        strain_ratio = strain / self.strain_peak
        peak_stiffness = -self.strength / self.strain_peak

        factor = self.tangent_stiffness / (self.tangent_stiffness - peak_stiffness)

        return self.tangent_stiffness * strain * (1 - 1 / factor * math.pow(strain_ratio, factor-1))

class Steel(Material):
    """A type of steel"""

    def __init__(self,strength,stiffness):
        self.strength = strength #f_y yield strength [MPa]
        self.stiffness = stiffness #E Young's modulus [MPa]
        self.update()

    def update(self):
        self.strain_yield = self.strength / self.stiffness #eps_y []

    def calc_stress(self,strain):
        return max(-self.strength, min(self.strength, self.stiffness*strain))
