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


class Network:

    def __init__(self, number_buses: int, s_base: complex, id_bus_reference: int, v_base_bus_reference: complex):
        ground_bus = Bus(0)

        self.buses = [ground_bus] + [Bus(i) for i in range(1, number_buses + 1)]

        self.element_node_incidence_matrix = None
        self.bus_incidence_matrix = None

        self.primitive_admittance_matrix = None
        self.primitive_impedance_matrix = None

        self.bus_admittance_matrix = None
        self.bus_impedance_matrix = None

        self.vector_impressed_bus_currents = None
        self.vector_bus_voltages = None

        self.elements = []
        self.simplified_elements = []

    def add_elements(self, elements: list):
        self.elements.append(elements)

    def simplify_elements(self, elements: list):
        pass

    def find_primitives_matrices(self, simplified_elements: list):
        pass

    def find_incidences_matrices(self, simplified_elements: list):
        pass

    def calculate_buses_matrices(self, bus_incidence_matrix, primitive_admittance_matrix):
        pass

    def assign_bases(self, simplified_elements):
        pass
