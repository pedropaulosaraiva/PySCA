from electrical_values import VoltageVariable, CurrentVariable, PuBaseManager, ImmittanceConstant
from base_elements import Element1Terminal, CompositeElement

from abc import abstractmethod


class ActiveElement1Terminal(Element1Terminal):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, v_base_m, s_base)

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


# The ActiveCompositeElement is only present to maintain symmetry with the PassiveCompositeElement and can be removed
# in the future if it remains unnecessary
class ActiveCompositeElement(CompositeElement):

    def __init__(self, elements: list[ActiveElement1Terminal]):

        super().__init__(elements)
