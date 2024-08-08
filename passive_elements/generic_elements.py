from electrical_values import VoltageVariable, CurrentVariable, PuBase, ImpedanceConstant, ImmittanceConstant
from abc import ABC, abstractmethod


class Element3Terminals(ABC):
    def __init__(self, y_series_mn_seq0_pu: complex, y_series_mn_seq1_pu: complex, y_series_mn_seq2_pu: complex,
                 y_series_np_seq0_pu: complex, y_series_np_seq1_pu: complex, y_series_np_seq2_pu: complex,
                 y_series_mp_seq0_pu: complex, y_series_mp_seq1_pu: complex, y_series_mp_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, id_bus_p: int, v_base_m: float, v_base_n: float, v_base_p: float, s_base: float):

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n
        self.id_bus_p = id_bus_p

        self.base_m = PuBase(v_base_m, s_base)
        self.base_n = PuBase(v_base_n, s_base)
        self.base_p = PuBase(v_base_p, s_base)

        self.v_bus_m = VoltageVariable(self.base_m)
        self.v_bus_n = VoltageVariable(self.base_n)
        self.v_bus_p = VoltageVariable(self.base_p)

        self.i_bus_m = CurrentVariable(self.base_m)
        self.i_bus_n = CurrentVariable(self.base_n)
        self.i_bus_p = CurrentVariable(self.base_p)

        self.i_mn = CurrentVariable(self.base_m)
        self.i_np = CurrentVariable(self.base_n)
        self.i_mp = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = []
        self.branches_seq1: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq1_pu, self.base_m, id_bus_m,
                                                                         id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq1_pu, self.base_n, id_bus_n,
                                                                         id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq1_pu, self.base_p, id_bus_p,
                                                                         id_bus_m)]
        self.branches_seq2: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq2_pu, self.base_m, id_bus_m,
                                                                         id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq2_pu, self.base_n, id_bus_n,
                                                                         id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq2_pu, self.base_p, id_bus_p,
                                                                         id_bus_m)]

        self._define_seq0_topology(y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    @abstractmethod
    def calculate_internal_currents_pre_fault_pu(self):
        pass

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass

    def admittance_representation(self, seq: str) -> list[ImmittanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex, voltage_bus_n_pu: complex,
                                     voltage_bus_p_pu: complex):

        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)
        self.v_bus_n.define_value_pre_fault_pu(voltage_bus_n_pu)
        self.v_bus_p.define_value_pre_fault_pu(voltage_bus_p_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex, voltage_bus_n_seq0_pu: complex,
                                     voltage_bus_n_seq1_pu: complex, voltage_bus_n_seq2_pu: complex,
                                     voltage_bus_p_seq0_pu: complex, voltage_bus_p_seq1_pu: complex,
                                     voltage_bus_p_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
        self.v_bus_n.define_values_pos_fault_pu(voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu)
        self.v_bus_p.define_values_pos_fault_pu(voltage_bus_p_seq0_pu, voltage_bus_p_seq1_pu, voltage_bus_p_seq2_pu)


class Element2Terminals(Element3Terminals):
    
    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, v_base_m: float, v_base_n: float, s_base: float):
        
        Element3Terminals.__init__(self,  y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, 0,
                                   0, 0, 0, 0,
                                   0, id_bus_m, id_bus_n, 0, v_base_m, v_base_n,
                                   PuBase.default(), s_base)


class Element2TerminalsDefinedByPU(ABC):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, v_base_m: float, v_base_n: float, s_base: float):

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n

        self.base_m = PuBase(v_base_m, s_base)
        self.base_n = PuBase(v_base_n, s_base)

        self.v_bus_m = VoltageVariable(self.base_m)
        self.v_bus_n = VoltageVariable(self.base_n)

        self.i_bus_m = CurrentVariable(self.base_m)
        self.i_bus_n = CurrentVariable(self.base_n)

        self.branches_seq0: list[ImpedanceConstant] = []
        self.branches_seq1: list[ImpedanceConstant] = [ImpedanceConstant(y_series_seq1_pu, self.base_m, id_bus_m,
                                                                         id_bus_n)]
        self.branches_seq2: list[ImpedanceConstant] = [ImpedanceConstant(y_series_seq2_pu, self.base_m, id_bus_m,
                                                                         id_bus_n)]

        self._define_seq0_topology(y_series_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_seq0_pu: complex):
        pass

    @abstractmethod
    def calculate_internal_currents_pre_fault_pu(self):
        pass

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass

    def admittance_representation(self, seq: str) -> list[ImpedanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex, voltage_bus_n_pu: complex):
        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)
        self.v_bus_n.define_value_pre_fault_pu(voltage_bus_n_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex, voltage_bus_n_seq0_pu: complex,
                                     voltage_bus_n_seq1_pu: complex, voltage_bus_n_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
        self.v_bus_n.define_values_pos_fault_pu(voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu)


class Element3TerminalsDefinedByPU(ABC):

    def __init__(self, y_series_mn_seq0_pu: complex, y_series_mn_seq1_pu: complex, y_series_mn_seq2_pu: complex,
                 y_series_np_seq0_pu: complex, y_series_np_seq1_pu: complex, y_series_np_seq2_pu: complex,
                 y_series_mp_seq0_pu: complex, y_series_mp_seq1_pu: complex, y_series_mp_seq2_pu: complex,
                 id_bus_m: int, id_bus_n: int, id_bus_p: int, v_base_m: float, v_base_n: float, v_base_p: float,
                 s_base: float):

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n
        self.id_bus_p = id_bus_p

        self.base_m = PuBase(v_base_m, s_base)
        self.base_n = PuBase(v_base_n, s_base)
        self.base_p = PuBase(v_base_p, s_base)

        self.v_bus_m = VoltageVariable(self.base_m)
        self.v_bus_n = VoltageVariable(self.base_n)
        self.v_bus_p = VoltageVariable(self.base_p)

        self.i_bus_m = CurrentVariable(self.base_m)
        self.i_bus_n = CurrentVariable(self.base_n)
        self.i_bus_p = CurrentVariable(self.base_p)

        self.I_mn = CurrentVariable(self.base_m)
        self.I_np = CurrentVariable(self.base_n)


        self.branches_seq0: list[ImpedanceConstant] = []
        self.branches_seq1: list[ImpedanceConstant] = [ImpedanceConstant(y_series_mn_seq1_pu, self.base_m, id_bus_m,
                                                                         id_bus_n),
                                                       ImpedanceConstant(y_series_np_seq1_pu, self.base_n, id_bus_n,
                                                                         id_bus_p),
                                                       ImpedanceConstant(y_series_mp_seq1_pu, self.base_p, id_bus_p,
                                                                         id_bus_m)]
        self.branches_seq2: list[ImpedanceConstant] = [ImpedanceConstant(y_series_mn_seq2_pu, self.base_m, id_bus_m,
                                                                         id_bus_n),
                                                       ImpedanceConstant(y_series_np_seq2_pu, self.base_n, id_bus_n,
                                                                         id_bus_p),
                                                       ImpedanceConstant(y_series_mp_seq2_pu, self.base_p, id_bus_p,
                                                                         id_bus_m)]

        self._define_seq0_topology(y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    @abstractmethod
    def calculate_internal_currents_pre_fault_pu(self):
        pass

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass

    def admittance_representation(self, seq: str) -> list[ImpedanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex, voltage_bus_n_pu: complex,
                                     voltage_bus_p_pu: complex):

        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)
        self.v_bus_n.define_value_pre_fault_pu(voltage_bus_n_pu)
        self.v_bus_p.define_value_pre_fault_pu(voltage_bus_p_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex, voltage_bus_n_seq0_pu: complex,
                                     voltage_bus_n_seq1_pu: complex, voltage_bus_n_seq2_pu: complex,
                                     voltage_bus_p_seq0_pu: complex, voltage_bus_p_seq1_pu: complex,
                                     voltage_bus_p_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
        self.v_bus_n.define_values_pos_fault_pu(voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu)
        self.v_bus_p.define_values_pos_fault_pu(voltage_bus_p_seq0_pu, voltage_bus_p_seq1_pu, voltage_bus_p_seq2_pu)


class Element2TerminalsDefinedBySI(Element2TerminalsDefinedByPU, ABC):

    def __init__(self, y_series_seq0_SI: complex, y_series_seq1_SI: complex, y_series_seq2_SI: complex, id_bus_m: int,
                 id_bus_n: int):

        default_base: PuBase = PuBase.default()
        v_base_m = default_base.v_base
        v_base_n = default_base.v_base
        s_base = default_base.s_base

        y_base = default_base.y_base

        y_series_seq0_pu = y_series_seq0_SI / y_base
        y_series_seq1_pu = y_series_seq1_SI / y_base
        y_series_seq2_pu = y_series_seq2_SI / y_base

        Element2TerminalsDefinedByPU.__init__(self, y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m,
                                              id_bus_n, v_base_m, v_base_n, s_base)


class Element3TerminalsDefinedBySI(Element3TerminalsDefinedByPU, ABC):

    def __init__(self, y_series_mn_seq0_SI: complex, y_series_mn_seq1_SI: complex, y_series_mn_seq2_SI: complex,
                 y_series_np_seq0_SI: complex, y_series_np_seq1_SI: complex, y_series_np_seq2_SI: complex,
                 y_series_mp_seq0_SI: complex, y_series_mp_seq1_SI: complex, y_series_mp_seq2_SI: complex, id_bus_m: int,
                 id_bus_n: int, id_bus_p: int):
        default_base: PuBase = PuBase.default()
        v_base_m = default_base.v_base
        v_base_n = default_base.v_base
        v_base_p = default_base.v_base

        s_base = default_base.s_base

        y_base = default_base.y_base

        y_series_mn_seq0_pu, y_series_mn_seq1_pu, y_series_mn_seq2_pu = (y_series_mn_seq0_SI / y_base,
                                                                         y_series_mn_seq1_SI / y_base,
                                                                         y_series_mn_seq2_SI / y_base)
        y_series_np_seq0_pu, y_series_np_seq1_pu, y_series_np_seq2_pu = (y_series_np_seq0_SI / y_base,
                                                                         y_series_np_seq1_SI / y_base,
                                                                         y_series_np_seq2_SI / y_base)
        y_series_mp_seq0_pu, y_series_mp_seq1_pu, y_series_mp_seq2_pu = (y_series_mp_seq0_SI / y_base,
                                                                         y_series_mp_seq1_SI / y_base,
                                                                         y_series_mp_seq2_SI / y_base)

        Element3TerminalsDefinedByPU.__init__(self, y_series_mn_seq0_pu, y_series_mn_seq1_pu, y_series_mn_seq2_pu,
                                              y_series_np_seq0_pu, y_series_np_seq1_pu, y_series_np_seq2_pu,
                                              y_series_mp_seq0_pu, y_series_mp_seq1_pu, y_series_mp_seq2_pu, id_bus_m,
                                              id_bus_n, id_bus_p, v_base_m, v_base_n, v_base_p, s_base)
