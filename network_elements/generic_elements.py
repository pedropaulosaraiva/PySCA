from electrical_values import VoltageVariable, CurrentVariable, PuBase, PuBaseManager, ImmittanceConstant
from abc import ABC, abstractmethod
from electrical_relations import calculate_central_v_star, calculate_current, delta2star
from passive_elements.base_elements import Element3Terminals


class Bus:

    def __init__(self, id_bus: int):
        self.id_bus = id_bus

        default_base: PuBase = PuBase.default()
        self.base_bus = PuBaseManager.create_pu_base(default_base.v_base, default_base.s_base, id_bus)

        self.v_bus = VoltageVariable(self.base_bus)

    def define_voltages_pre_fault_pu(self, voltage_bus_pu: complex):
        self.v_bus.define_value_pre_fault_pu(voltage_bus_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex):
        self.v_bus.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)

