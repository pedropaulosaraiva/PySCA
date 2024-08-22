from electrical_values import VoltageVariable, CurrentVariable, PuBase, ImmittanceConstant
from abc import ABC, abstractmethod
from electrical_relations import calculate_central_v_star, calculate_current, delta2star


class Element3Terminals(ABC):
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

        self.i_mn = CurrentVariable(self.base_m)
        self.i_np = CurrentVariable(self.base_n)
        self.i_mp = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = []
        self.branches_seq1: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq1_pu, self.base_m, id_bus_m,
                                                                           id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq1_pu, self.base_m, id_bus_n,
                                                                           id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq1_pu, self.base_m, id_bus_p,
                                                                           id_bus_m)]
        self.branches_seq2: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq2_pu, self.base_m, id_bus_m,
                                                                           id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq2_pu, self.base_m, id_bus_n,
                                                                           id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq2_pu, self.base_m, id_bus_m,
                                                                           id_bus_p)]

        self._define_seq0_topology(y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_bus_n = self.v_bus_n.pre().a().pu().rec()
        v_bus_p = self.v_bus_p.pre().a().pu().rec()

        y_mn_pu = self.branches_seq1[0].y_pu
        y_np_pu = self.branches_seq1[1].y_pu
        y_mp_pu = self.branches_seq1[2].y_pu

        i_mn_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        self.i_mn.define_value_pre_fault_pu(i_mn_pu)
        self.i_np.define_value_pre_fault_pu(i_np_pu)
        self.i_mp.define_value_pre_fault_pu(i_mp_pu)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_pu = calculate_current(y_n, v_bus_n, v_central_star)
        i_bus_p_pu = calculate_current(y_p, v_bus_p, v_central_star)

        self.i_bus_m.define_value_pre_fault_pu(i_bus_m_pu)
        self.i_bus_n.define_value_pre_fault_pu(i_bus_n_pu)
        self.i_bus_p.define_value_pre_fault_pu(i_bus_p_pu)

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


class Element2Terminals(Element3Terminals, ABC):
    
    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, v_base_m: float, v_base_n: float, s_base: float):
        
        Element3Terminals.__init__(self,  y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, 0,
                                   0, 0, 0, 0,
                                   0, id_bus_m, id_bus_n, 0, v_base_m, v_base_n,
                                   PuBase.default().v_base, s_base)

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_bus_n = self.v_bus_n.pre().a().pu().rec()
        y_pu = self.branches_seq1[0].y_pu
        i_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        self.i_bus_m.define_value_pre_fault_pu(i_pu)
        self.i_bus_n.define_value_pre_fault_pu(-i_pu)


class Element1Terminal(Element2Terminals, ABC):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        Element2Terminals.__init__(self, y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, 0,
                                   v_base_m, PuBase.default().v_base, s_base)

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()

        y_pu = self.branches_seq1[0].y_pu
        i_pu = calculate_current(y_pu, v_bus_m, 0)

        self.i_bus_m.define_value_pre_fault_pu(i_pu)
