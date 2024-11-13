import numpy as np
from collections import defaultdict
from electrical_values import ImmittanceConstant, PuBase
from electrical_relations import equivalent_y_series
from base_elements import Element3Terminals, Element2Terminals, Element1Terminal, CompositeElement
from active_elements.base_elements import ActiveElement1Terminal
from passive_elements.base_elements import PassiveElement3Terminals, PassiveElement2Terminals, PassiveElement1Terminal
from passive_elements.transformer_elements import Transformer2Windings, Transformer3Windings


def simplify_elements(elements: list[Element3Terminals], seq: str) -> list[Element3Terminals]:
    primitive_incidence_matrix = find_primitive_incidence_matrix(elements)

    # Create a dict with a default value of an empty list for KeyError
    connections_indexes = defaultdict(list)
    for index, connection in enumerate(primitive_incidence_matrix):
        connections_indexes[str(connection)].append(index)

    indexes_per_connection: list[list[int]] = [index_connection for index_connection in connections_indexes.values()]

    simplified_elements = []
    for indexes in indexes_per_connection:

        if len(indexes) == 1:
            simplified_elements.append(elements[indexes[0]])
        elif len(indexes) > 1:
            parallel_elements = [elements[index] for index in indexes]
            composite_element = CompositeElement(parallel_elements)
            # ! Raise exception if elements aren't the same type
            simplified_elements.append(composite_element)

    return simplified_elements


def find_primitive_incidence_matrix(elements: list[Element3Terminals]) -> list[list[int]]:
    primitive_incidence_matrix = []

    for element in elements:
        element_id_bus_m, element_id_bus_n, element_id_bus_p = element.id_bus_m, element.id_bus_n, element.id_bus_p

        element_incidence_line = [0] * (max(element_id_bus_m, element_id_bus_n, element_id_bus_p) + 1)

        (element_incidence_line[element_id_bus_m], element_incidence_line[element_id_bus_n],
         element_incidence_line[element_id_bus_p]) = 1, 1, 1

        element_incidence_line[0] = 0

        primitive_incidence_matrix.append(element_incidence_line)

    return primitive_incidence_matrix


def seq0_topology(simplified_elements: list[Element3Terminals]) -> tuple[list[list[int]], list[ImmittanceConstant]]:
    primitive_incidence_matrix = []
    admittances_seq0 = []

    for element in simplified_elements:
        for admittance in element.branches_seq0:
            if admittance.y_pu != 0:
                admittance_id_bus_m, admittance_id_bus_n = admittance.id_bus_m, admittance.id_bus_n

                admittance_incidence_line = [0] * (max(admittance_id_bus_m, admittance_id_bus_n) + 1)

                admittance_incidence_line[admittance_id_bus_m], admittance_incidence_line[admittance_id_bus_n] = 1, 1

                admittance_incidence_line[0] = 0

                primitive_incidence_matrix.append(admittance_incidence_line)

                admittances_seq0.append(admittance)

    return primitive_incidence_matrix, admittances_seq0


def simplify_admittances_seq0(simplified_elements: list[Element3Terminals]) -> list[ImmittanceConstant]:
    primitive_incidence_matrix, admittances_seq0 = seq0_topology(simplified_elements)

    # Create a dict with a default value of an empty list for KeyError
    connections_indexes = defaultdict(list)
    for index, connection in enumerate(primitive_incidence_matrix):
        connections_indexes[str(connection)].append(index)

    indexes_per_connection: list[list[int]] = [index_connection for index_connection in connections_indexes.values()]

    simplified_admittances_seq0 = []
    for indexes in indexes_per_connection:

        if len(indexes) == 1:
            simplified_admittances_seq0.append(admittances_seq0[indexes[0]])
        elif len(indexes) > 1:
            parallel_admittances = [admittances_seq0[index] for index in indexes]
            equivalent_y_pu = float('inf')
            for admittance in parallel_admittances:
                equivalent_y_pu = equivalent_y_series(equivalent_y_pu, admittance.y_pu)

            equivalent_immittance = ImmittanceConstant(equivalent_y_pu, PuBase.default(),
                                                       parallel_admittances[0].id_bus_m,
                                                       parallel_admittances[0].id_bus_n)

            simplified_admittances_seq0.append(equivalent_immittance)

    return simplified_admittances_seq0

# ! Implement a function to test partial parallels like a 3 windings transformer with a simple line or 2 windings
# ! transformer


def find_primitives_matrices(simplified_elements: list[Element3Terminals], seq: str,
                             simplified_admittances_seq0: list[ImmittanceConstant]) -> tuple:
    primitive_admittance_row = np.array([], dtype=complex)

    if seq == 'seq1' or seq == 'seq2':
        for element in simplified_elements:
            branch: list[ImmittanceConstant] = element.admittance_representation(seq)

            for admittance in branch:
                if admittance.y_pu != 0:
                    primitive_admittance = np.array([admittance.y_pu], dtype=complex)
                    primitive_admittance_row = np.hstack((primitive_admittance_row, primitive_admittance))

    elif seq == 'seq0':
        for admittance in simplified_admittances_seq0:
            primitive_admittance = np.array([admittance.y_pu], dtype=complex)
            primitive_admittance_row = np.hstack((primitive_admittance_row, primitive_admittance))

    else:
        pass  # ! raise seq error

    primitive_admittance_matrix = np.diag(primitive_admittance_row)
    primitive_impedance_matrix = np.linalg.inv(primitive_admittance_matrix)
    return primitive_admittance_matrix, primitive_impedance_matrix


def find_incidences_matrices(simplified_elements: list[Element3Terminals], seq: str, n_buses: int,
                             simplified_admittances_seq0: list[ImmittanceConstant]) -> tuple:
    incidence_matrix = np.array([0] * n_buses, dtype=int)

    if seq == 'seq1' or seq == 'seq2':
        for element in simplified_elements:
            branch: list[ImmittanceConstant] = element.admittance_representation(seq)

            for admittance in branch:
                if admittance.y_pu != 0:
                    primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
                    (primitive_incidence_row[0, admittance.id_bus_m],
                     primitive_incidence_row[0, admittance.id_bus_n]) = 1, -1

                    incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))
    elif seq == 'seq0':
        for admittance in simplified_admittances_seq0:
            primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
            (primitive_incidence_row[0, admittance.id_bus_m],
             primitive_incidence_row[0, admittance.id_bus_n]) = 1, -1

            incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

    else:
        pass  # ! raise seq error

    # Elimination of bus zero column and the first null row
    element_node_incidence_matrix = incidence_matrix[1:, :]
    bus_incidence_matrix = incidence_matrix[1:, 1:]

    return bus_incidence_matrix, element_node_incidence_matrix


def find_incidence_base_matrix(simplified_elements: list[Element3Terminals], n_buses: int):
    incidence_matrix = np.array([0] * n_buses, dtype=int)

    for element in simplified_elements:
        branch: list[ImmittanceConstant] = element.admittance_representation('seq1')

        if isinstance(element, Transformer2Windings):
            v_pri = element.base_m.v_base
            v_sec = element.base_n.v_base

            admittance = branch[0]
            primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
            (primitive_incidence_row[0, admittance.id_bus_m],
             primitive_incidence_row[0, admittance.id_bus_n]) = 1*(1/v_pri), -1*(1/v_sec)

            incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

        elif isinstance(element, Transformer3Windings):
            v_pri = element.base_m.v_base
            v_sec = element.base_n.v_base
            v_ter = element.base_p.v_base

            admittance = branch[0]
            primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
            (primitive_incidence_row[0, admittance.id_bus_m],
             primitive_incidence_row[0, admittance.id_bus_n]) = 1 * (1 / v_pri), -1 * (1 / v_sec)

            incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

            admittance = branch[1]
            primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
            (primitive_incidence_row[0, admittance.id_bus_m],
             primitive_incidence_row[0, admittance.id_bus_n]) = 1 * (1 / v_sec), -1 * (1 / v_ter)

            incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

            admittance = branch[2]
            primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
            (primitive_incidence_row[0, admittance.id_bus_m],
             primitive_incidence_row[0, admittance.id_bus_n]) = 1 * (1 / v_pri), -1 * (1 / v_ter)

            incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))
        elif isinstance(element, Element1Terminal):
            pass
        else:
            for admittance in branch:
                if admittance.y_pu != 0:
                    primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
                    (primitive_incidence_row[0, admittance.id_bus_m],
                     primitive_incidence_row[0, admittance.id_bus_n]) = 1, -1

                    incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

    # Elimination of bus zero column and the first null row
    incidence_base_matrix = incidence_matrix[1:, 1:]

    return incidence_base_matrix


def calculate_number_branches(simplified_elements: list[Element3Terminals], seq: str) -> int:
    n_branches = 0

    for element in simplified_elements:
        branch: list[ImmittanceConstant] = element.admittance_representation(seq)
        for admittance in branch:
            if admittance.y_pu != 0:
                n_branches += 1

    return n_branches


def calculate_buses_matrices(bus_incidence_matrix: np.ndarray, primitive_admittance_matrix: np.ndarray) -> tuple:
    transpose_bus_incidence_matrix = np.transpose(bus_incidence_matrix)

    bus_admittance_matrix = np.matmul(transpose_bus_incidence_matrix,
                                      np.matmul(primitive_admittance_matrix, bus_incidence_matrix))

    bus_impedance_matrix = np.linalg.inv(bus_admittance_matrix)

    return bus_admittance_matrix, bus_impedance_matrix


def assign_bases(simplified_elements: list[Element3Terminals]):
    pass
