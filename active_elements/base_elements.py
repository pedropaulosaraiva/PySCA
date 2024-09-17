from electrical_values import VoltageVariable, CurrentVariable, PuBaseManager, ImmittanceConstant
from abc import ABC, abstractmethod
from electrical_relations import calculate_central_v_star, calculate_current, delta2star


class Element1Terminal(ABC):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        self.id_bus_m = id_bus_m

        self.base_m = PuBaseManager.create_pu_base(v_base_m, s_base, id_bus_m)

        self.v_bus_m = VoltageVariable(self.base_m)

        self.i_bus_m = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = []
        self.branches_seq1: list[ImmittanceConstant] = [ImmittanceConstant(y_series_seq1_pu, self.base_m, id_bus_m,
                                                                           0)]
        self.branches_seq2: list[ImmittanceConstant] = [ImmittanceConstant(y_series_seq2_pu, self.base_m, id_bus_m,
                                                                           0)]

        self._define_seq0_topology(y_series_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_seq0_pu: complex):
        pass

    def calculate_internal_currents_pre_fault_pu(self):
        pass

    def calculate_internal_currents_pos_fault_pu(self):
        pass

    def admittance_representation(self, seq: str) -> list[ImmittanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex):

        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
