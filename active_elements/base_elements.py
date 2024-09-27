from electrical_values import VoltageVariable, CurrentVariable, PuBaseManager, ImmittanceConstant
from abc import ABC, abstractmethod


class ActiveElement1Terminal(ABC):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        self.id_bus_m = id_bus_m

        self.base_m = PuBaseManager.create_pu_base(v_base_m, s_base, id_bus_m)

        self.v_bus_m = VoltageVariable(self.base_m)

        self.i_bus_m = CurrentVariable(self.base_m)

        self.i_mn = CurrentVariable(self.base_m)

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


class ActiveCompositeElement:

    def __init__(self, elements: list[ActiveElement1Terminal]):

        self.elements = elements
        # ! Raise error if elements aren't in parallel

        id_bus_m = elements[0].id_bus_m
        base_m = elements[0].base_m

        self.id_bus_m = id_bus_m

        self.base_m = base_m

        self.v_bus_m = VoltageVariable(self.base_m)

        self.i_bus_m = CurrentVariable(self.base_m)

        self.i_mn = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = self._composite_immittance('seq0')
        self.branches_seq1: list[ImmittanceConstant] = self._composite_immittance('seq1')
        self.branches_seq2: list[ImmittanceConstant] = self._composite_immittance('seq2')

    def _composite_immittance(self, seq: str):

        y_series_mn_pu = 0

        branches_seq = []

        if seq == 'seq0':
            for element in self.elements:
                branches_seq.append(element.branches_seq0)

        elif seq == 'seq1':
            for element in self.elements:
                branches_seq.append(element.branches_seq1)

        elif seq == 'seq2':
            for element in self.elements:
                branches_seq.append(element.branches_seq2)
        else:
            pass
            # ! Raise an exception

        for branches in branches_seq:
            y_series_mn_pu += branches[0].y_pu

        reference_branches = branches_seq[0]
        id_bus_m_immitance_0, id_bus_n_immitance_0 = reference_branches[0].id_bus_m, reference_branches[0].id_bus_n

        return [ImmittanceConstant(y_series_mn_pu, self.elements[0].base_m, id_bus_m_immitance_0, id_bus_n_immitance_0)]

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

        for element in self.elements:
            element.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)

        for element in self.elements:
            element.define_voltages_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
