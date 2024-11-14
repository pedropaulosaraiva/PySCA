from electrical_values import (VoltageVariable, CurrentVariable, PuBase, PuBaseManager,
                               ImmittanceConstant, MatrixVariable)
import network_management as nm
import numpy as np
from base_elements import Element3Terminals
from electrical_relations import calculate_central_v_star, calculate_current, delta2star
from passive_elements.base_elements import PassiveElement3Terminals


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

    def __init__(self, number_buses: int, s_base: float, id_bus_reference: int, v_base_bus_reference: float):
        ground_bus = Bus(0)

        self.s_base = s_base
        self.id_bus_reference = id_bus_reference
        self.v_base_bus_reference = v_base_bus_reference

        self.buses = [ground_bus] + [Bus(i) for i in range(1, number_buses + 1)]
        self.n_buses = number_buses

        self.element_node_incidence_matrix = MatrixVariable()
        self.bus_incidence_matrix = MatrixVariable()

        self.primitive_admittance_matrix = MatrixVariable()
        self.primitive_impedance_matrix = MatrixVariable()

        self.bus_admittance_matrix = MatrixVariable()
        self.bus_impedance_matrix = MatrixVariable()

        self.vector_impressed_bus_currents = MatrixVariable()
        self.vector_bus_voltages = MatrixVariable()

        self.elements = []
        self.simplified_elements = []
        self.simplified_admittances_seq0 = []

    def add_elements(self, elements: list[Element3Terminals]):
        self.elements.append(elements)

    def simplify_elements(self, seq: str):
        self.simplified_elements = nm.simplify_elements(self.elements, seq)
        self.simplified_admittances_seq0 = nm.simplify_admittances_seq0(self.simplified_elements)

    def find_primitives_matrices(self, seq: str):
        primitive_matrices = nm.find_primitives_matrices(self.simplified_elements, seq,
                                                         self.simplified_admittances_seq0)
        primitive_admittance_matrix, primitive_impedance_matrix = primitive_matrices
        self.primitive_admittance_matrix.set_matrix(primitive_admittance_matrix, seq)
        self.primitive_impedance_matrix.set_matrix(primitive_impedance_matrix, seq)

    def find_incidences_matrices(self, seq: str):
        incidence_matrices = nm.find_incidences_matrices(self.simplified_elements, seq, self.n_buses,
                                                         self.simplified_admittances_seq0)
        element_node_incidence_matrix, bus_incidence_matrix = incidence_matrices
        self.element_node_incidence_matrix.set_matrix(element_node_incidence_matrix, seq)
        self.bus_incidence_matrix.set_matrix(bus_incidence_matrix, seq)

    def calculate_buses_matrices(self, seq: str):
        buses_matrices = nm.calculate_buses_matrices(self.bus_incidence_matrix.get_matrix(seq),
                                                     self.primitive_admittance_matrix.get_matrix(seq))
        bus_admittance_matrix, bus_impedance_matrix = buses_matrices
        self.bus_admittance_matrix.set_matrix(bus_admittance_matrix, seq)
        self.bus_impedance_matrix.set_matrix(bus_impedance_matrix, seq)

    def assign_bases(self, simplified_elements):
        v_base = nm.redefine_bases(simplified_elements, self.n_buses, self.id_bus_reference, self.v_base_bus_reference)

        for bus, v_base in zip(self.buses[1:], v_base):
            base: PuBase = bus.base_bus
            base.update_base(v_base, self.s_base)
