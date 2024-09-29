from base_elements import Element3Terminals, CompositeElement
from electrical_values import VoltageVariable, CurrentVariable, PuBase, PuBaseManager, ImmittanceConstant
from abc import ABC, abstractmethod
from electrical_relations import calculate_central_v_star, calculate_current, delta2star


class PassiveElement3Terminals(Element3Terminals):
    def __init__(self, y_series_mn_seq0_pu: complex, y_series_mn_seq1_pu: complex, y_series_mn_seq2_pu: complex,
                 y_series_np_seq0_pu: complex, y_series_np_seq1_pu: complex, y_series_np_seq2_pu: complex,
                 y_series_mp_seq0_pu: complex, y_series_mp_seq1_pu: complex, y_series_mp_seq2_pu: complex,
                 id_bus_m: int, id_bus_n: int, id_bus_p: int, v_base_m: float, v_base_n: float, v_base_p: float,
                 s_base: float):

        super().__init__(y_series_mn_seq0_pu, y_series_mn_seq1_pu, y_series_mn_seq2_pu,
                         y_series_np_seq0_pu, y_series_np_seq1_pu, y_series_np_seq2_pu,
                         y_series_mp_seq0_pu, y_series_mp_seq1_pu, y_series_mp_seq2_pu,
                         id_bus_m, id_bus_n, id_bus_p, v_base_m, v_base_n, v_base_p, s_base)

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


class PassiveElement2Terminals(PassiveElement3Terminals):
    
    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, v_base_m: float, v_base_n: float, s_base: float):

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, 0,
                         0, 0, 0, 0,
                         0, id_bus_m, id_bus_n, 0, v_base_m, v_base_n,
                         PuBase.default().v_base, s_base)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass


class PassiveElement1Terminal(PassiveElement2Terminals):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, 0,
                         v_base_m, PuBase.default().v_base, s_base)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass


# Maybe PassiveCompositeElement will be useful for the design of the double line class or something that models the
# couple inductances phenomenon
class PassiveCompositeElement(CompositeElement):

    def __init__(self, elements: list[PassiveElement3Terminals]):

        super().__init__(elements)
