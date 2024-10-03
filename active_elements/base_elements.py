from electrical_values import VoltageVariable
from electrical_relations import calculate_current
from base_elements import Element1Terminal, CompositeElement

from abc import abstractmethod


class ActiveElement1Terminal(Element1Terminal):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, v_base_m, s_base)

        self.v_internal = VoltageVariable(self.base_m)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_internal = self.v_internal.pre().a().pu().rec()

        y_mn_pu = self.branches_seq1[0].y_pu

        i_mn_pu = calculate_current(y_mn_pu, v_bus_m, v_internal)

        self.i_mn.define_value_pre_fault_pu(i_mn_pu)
        self.i_np.define_value_pre_fault_pu(0)
        self.i_mp.define_value_pre_fault_pu(0)

        i_bus_m_pu = i_mn_pu
        i_bus_n_pu = -i_mn_pu

        self.i_bus_m.define_value_pre_fault_pu(i_bus_m_pu)
        self.i_bus_n.define_value_pre_fault_pu(i_bus_n_pu)
        self.i_bus_p.define_value_pre_fault_pu(0)

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m_seq0_pu, v_bus_m_seq1_pu, v_bus_m_seq2_pu = (self.v_bus_m.pos().seq0().pu().rec(),
                                                             self.v_bus_m.pos().seq1().pu().rec(),
                                                             self.v_bus_m.pos().seq2().pu().rec())
        v_internal_seq0_pu, v_internal_seq1_pu, v_internal_seq2_pu = 0, self.v_internal.pre().a().pu().rec(), 0

        y_mn_seq0_pu = self.branches_seq0[0].y_pu
        y_mn_seq1_pu = self.branches_seq1[0].y_pu
        y_mn_seq2_pu = self.branches_seq2[0].y_pu

        i_mn_seq0_pu = calculate_current(y_mn_seq0_pu, v_bus_m_seq0_pu, 0)
        i_mn_seq1_pu = calculate_current(y_mn_seq1_pu, v_bus_m_seq1_pu, v_internal_seq1_pu)
        i_mn_seq2_pu = calculate_current(y_mn_seq2_pu, v_bus_m_seq2_pu, 0)

        i_bus_m_seq0_pu = calculate_current(y_mn_seq0_pu, v_bus_m_seq0_pu, 0)
        i_bus_m_seq1_pu = calculate_current(y_mn_seq1_pu, v_bus_m_seq1_pu, v_internal_seq1_pu)
        i_bus_m_seq2_pu = calculate_current(y_mn_seq2_pu, v_bus_m_seq2_pu, 0)

        i_bus_n_seq0_pu = calculate_current(y_mn_seq0_pu, 0, v_bus_m_seq0_pu)
        i_bus_n_seq1_pu = calculate_current(y_mn_seq1_pu, v_internal_seq1_pu, v_bus_m_seq1_pu)
        i_bus_n_seq2_pu = calculate_current(y_mn_seq2_pu, 0, v_bus_m_seq2_pu)

        self.i_mn.define_values_pos_fault_pu(i_mn_seq0_pu, i_mn_seq1_pu, i_mn_seq2_pu)
        self.i_np.define_values_pos_fault_pu(0, 0, 0)
        self.i_mp.define_values_pos_fault_pu(0, 0, 0)

        self.i_bus_m.define_values_pos_fault_pu(i_bus_m_seq0_pu, i_bus_m_seq1_pu, i_bus_m_seq2_pu)
        self.i_bus_n.define_values_pos_fault_pu(i_bus_n_seq0_pu, i_bus_n_seq1_pu, i_bus_n_seq2_pu)
        self.i_bus_p.define_values_pos_fault_pu(0, 0, 0)

    def calculate_internal_voltage(self, impressed_bus_current_pre_fault: complex):
        v_internal = (impressed_bus_current_pre_fault / self.branches_seq1[0].y_pu) + self.v_bus_m.pre().a().pu().rec()
        self.v_internal.define_value_pre_fault_pu(v_internal)
        self.v_internal.define_values_pos_fault_pu(0, v_internal, 0)


# The ActiveCompositeElement is only present to maintain symmetry with the PassiveCompositeElement and can be removed
# in the future if it remains unnecessary
class ActiveCompositeElement(CompositeElement):

    def __init__(self, elements: list[ActiveElement1Terminal]):

        super().__init__(elements)
