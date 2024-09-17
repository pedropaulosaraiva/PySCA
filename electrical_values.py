from abc import ABC, abstractmethod
from math import sqrt, pi, cos, sin

# ! Review docstrings in all classes


class PuBase:
    """
    Represents a per-unit base for electrical quantities.

    Attributes:
        v_base (float): The base voltage value.
        s_base (float): The base power value.
        z_base (float): The base impedance value.
        i_base (float): The base current value.
        id_bus (int): The id of the bus holding the per-unit base.
        _electrical_variables (list): A list to store electrical variables that observes the per-unit base.
    """

    def __init__(self, v_base: float, s_base: float, id_bus: int):
        """
        Initializes a new instance of the PuBase class.

        Args:
            v_base (float): The base voltage value.
            s_base (float): The base power value.

        Initializes the following instance variables:
             - v_base (float): The base voltage value.
             - s_base (float): The base power value.
             - z_base (float): The base impedance value.
             - i_base (float): The base current value.
             - _electrical_variables (list): A list to store electrical variables.
        """
        self.v_base = v_base
        self.s_base = s_base
        self.id_bus = id_bus

        # Calculate the base impedance value
        self.z_base = v_base ** 2 / s_base

        # Calculate the base current value
        self.i_base = v_base / (sqrt(3) * self.z_base)

        # Initialize a list to store electrical variables
        self._electrical_variables = []
        
    @classmethod
    def default(cls):
        """
        Returns an instance of the class with default values for v_base and s_base.

        Returns:
            cls: An instance of the class with default values for v_base and s_base.
        """
        v_base = 100*10**3
        s_base = 100*10**6

        return cls(v_base, s_base)
        
    def add_electrical_variable(self, electrical_variable):
        """
        Appends the given electrical variable to the list of stored electrical variables.
        Args:
            electrical_variable: The electrical variable to be added.
        Returns:
            None
        """
        self._electrical_variables.append(electrical_variable)
        
    def update_base(self, v_base: complex, s_base: complex):
        """
        Update the base values of the object.

        Args:
            v_base (complex): The new base voltage value.
            s_base (complex): The new base power value.

        This function updates the base values of the object. It then iterates over all electrical variables stored in
        the object and calls the "change_base" method on each variable.
        """
        self.v_base = v_base
        self.s_base = s_base
        self.z_base = self.v_base**2 / self.s_base.conjugate()
        self.i_base = self.v_base / (sqrt(3)*self.z_base)
        
        for electrical_variable in self._electrical_variables:
            electrical_variable.change_base


class PuBaseManager:

    pu_bases: list[PuBase] = []

    @classmethod
    def create_pu_base(cls, v_base: float, s_base: float, id_bus: int):

        for pu_base in cls.pu_bases:
            id_bus_base = pu_base.id_bus
            if id_bus == id_bus_base:
                return pu_base

        pu_base = PuBase(v_base, s_base, id_bus)
        cls.pu_bases.append(pu_base)
        return pu_base



class ImmittanceConstant:

    def __init__(self, y_pu: complex, base_m: PuBase, id_bus_m: int, id_bus_n: int):
        self.y_pu = y_pu

        self.z_baseM = base_m.z_base
        base_m.add_electrical_variable(self)

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n

    @classmethod
    def defined_by_impedance(cls, z_pu: complex, base_m: PuBase, id_bus_m: int, id_bus_n: int):
        y_pu = z_pu**(-1)

        return cls(y_pu, base_m, id_bus_m, id_bus_n)

    def change_base(self, pu_base: PuBase):
        self.y_pu = (self.y_pu * pu_base.z_base) / self.z_baseM
        self.z_baseM = pu_base.z_base
            

class VIVariable(ABC):
    """
    Abstract base class for electrical variables.

    This class represents a base class for electrical variables, such as voltage and current.
    """
    
    def __init__(self, pu_base: PuBase):
        """
        Initializes the object with the given PuBase object.

        Args:
            pu_base (PuBase): The PuBase object used to set the voltage and power bases.
        """
        self.v_base = pu_base.v_base
        self.s_base = pu_base.s_base
        pu_base.add_electrical_variable(self)
        
        self.value_base = None
        
        self.value_pre_fault_pu = None
        self.value_seq0_pos_fault_pu = None
        self.value_seq1_pos_fault_pu = None
        self.value_seq2_pos_fault_pu = None
        
        self.request_seq_values = None
        self.request_value_pu = None
        self.request_value = None
        
    @abstractmethod
    def change_base(self, pu_base: PuBase):
        """
        Update the base values of the object.

        Args:
            pu_base (PuBase): The new PuBase object used to update the base values.
        """
        pass
    
    def update_base_values(self, old_value_base, new_value_base):
        """
        Update the base values of the object.

        Args:
            old_value_base (complex): The old base value.
            new_value_base (complex): The new base value.
        """
        try:
            self.value_pre_fault_pu = (self.value_pre_fault_pu * old_value_base)/new_value_base
        except TypeError:
            pass
        
        try:
            self.value_seq0_pos_fault_pu = (self.value_seq0_pos_fault_pu * old_value_base)/new_value_base
            self.value_seq1_pos_fault_pu = (self.value_seq1_pos_fault_pu * old_value_base)/new_value_base
            self.value_seq2_pos_fault_pu = (self.value_seq2_pos_fault_pu * old_value_base)/new_value_base
        except TypeError:
            pass
    
    def define_value_pre_fault_si(self, value):
        """
        Define the value before fault in SI units.

        Args:
            value (complex): The value in SI units.
        """
        self.value_pre_fault_pu = value / self.value_base
        
    def define_values_pos_fault_si(self, value_seq0, value_seq1, value_seq2):
        """
        Define the values after fault in SI units.

        Args:
            value_seq0 (complex): The value in sequence 0 in SI units.
            value_seq1 (complex): The value in sequence 1 in SI units.
            value_seq2 (complex): The value in sequence 2 in SI units.
        """
        self.value_seq0_pos_fault_pu = value_seq0 / self.value_base
        self.value_seq1_pos_fault_pu = value_seq1 / self.value_base
        self.value_seq2_pos_fault_pu = value_seq2 / self.value_base
        
    def define_value_pre_fault_pu(self, value):
        """
        Define the value before fault in pu units.

        Args:
            value (complex): The value in pu units.
        """
        self.value_pre_fault_pu = value
        
    def define_values_pos_fault_pu(self, value_seq0, value_seq1, value_seq2):
        """
        Define the values after fault in pu units.

        Args:
            value_seq0 (complex): The value in sequence 0 in pu units.
            value_seq1 (complex): The value in sequence 1 in pu units.
            value_seq2 (complex): The value in sequence 2 in pu units.
        """
        self.value_seq0_pos_fault_pu = value_seq0
        self.value_seq1_pos_fault_pu = value_seq1 
        self.value_seq2_pos_fault_pu = value_seq2 
    
    def request_value(self, time, phase_seq, pu_si, notation):
        """
        Request the value of the object.

        Args:
            time (str): The time of the request.
            phase_seq (str): The phase sequence of the request.
            pu_si (str): The unit of the requested value.
            notation (str): The notation of the requested value.

        Returns:
            The requested value.
        """
        if time == 'pre':
            self.pre()
        elif time == 'pos':
            self.pos()
        else:
            pass
            
        if phase_seq == 'a':
            self.a()
        elif phase_seq == 'b':
            self.b()
        elif phase_seq == 'c':
            self.c()
        elif phase_seq == 'seq0':
            self.seq0()
        elif phase_seq == 'seq1':
            self.seq1()
        elif phase_seq == 'seq2':
            self.seq2()
        else:
            pass
            
        if pu_si == 'pu':
            self.pu()
        elif pu_si == 'si':
            self.si()
        else:
            pass
        
        if notation == 'rec':
            value = self.rec()
        elif notation == 'mag':
            value = self.mag()
        elif notation == 'ang':
            value = self.ang()
        else:
            pass
        
        return value

    # * Request functions
    def pre(self):
        """
        Request the value before fault.
        """
        self.request_seq_values = (0, self.value_pre_fault_pu, 0)

        return self
    
    def pos(self):
        """
        Request the values after fault.
        """
        self.request_seq_values = (self.value_seq0_pos_fault_pu, self.value_seq1_pos_fault_pu,
                                   self.value_seq2_pos_fault_pu)

        return self

    def a(self):
        """
        Request the value in phase A.
        """
        self.request_value_pu = (self.request_seq_values[0] + self.request_seq_values[1] * cpolar(1, 0) +
                                 self.request_seq_values[2] * cpolar(1, 0))

        return self

    def b(self):
        """
        Request the value in phase B.
        """
        self.request_value_pu = (self.request_seq_values[0] + self.request_seq_values[1] * cpolar(1, -120) +
                                 self.request_seq_values[2] * cpolar(1, 120))

        return self
    
    def c(self):
        """
        Request the value in phase C.
        """
        self.request_value_pu = (self.request_seq_values[0] + self.request_seq_values[1] * cpolar(1, 120) +
                                 self.request_seq_values[2] * cpolar(1, -120))

        return self
    
    def seq0(self):
        """
        Request the value in phase A and B.
        """
        self.request_value_pu = self.request_seq_values[0]

        return self
    
    def seq1(self):
        """
        Request the value in phase B and C.
        """
        self.request_value_pu = self.request_seq_values[1]

        return self
    
    def seq2(self):
        """
        Request the value in phase A and C.
        """
        self.request_value_pu = self.request_seq_values[2]

        return self
    
    def pu(self):
        """
        Request the value in pu.
        """
        self.request_value = self.request_value_pu

        return self
    
    def si(self):
        """
        Request the value in SI units.
        """
        self.request_value = self.request_value_pu * self.value_base

        return self
    
    def rec(self):
        """
        Request the real part of the value.
        """
        return self.request_value
    
    def mag(self):
        """
        Request the magnitude of the value.
        """
        return abs(self.request_value)
    
    def ang(self):
        """
        Request the angle of the value.
        """
        if self.request_value == 0:
            return 0
        else:
            return self.request_value.angle()   
        
        
class VoltageVariable(VIVariable):
    
    def __init__(self, pu_base: PuBase):
        super().__init__(pu_base)
        
    def change_base(self, pubase: PuBase):
        self.update_base_values(self.value_base, pubase.v_base)
        self.value_base = pubase.v_base
        

class CurrentVariable(VIVariable):
    
    def __init__(self, pu_base: PuBase):
        super().__init__(pu_base)
        
    def change_base(self, pubase: PuBase):
        self.update_base_values(self.value_base, pubase.i_base)
        self.value_base = pubase.i_base


# * Auxiliary functions
def cpolar(r, theta):
    theta = theta * pi / 180
    return r * complex(cos(theta), sin(theta))
