import numpy as np
from collections import defaultdict
from electrical_values import ImmittanceConstant
from base_elements import Element3Terminals, CompositeElement
from active_elements.base_elements import ActiveElement1Terminal
from passive_elements.base_elements import PassiveElement3Terminals, PassiveElement2Terminals, PassiveElement1Terminal


def simplify_elements(elements: list):
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


def find_primitive_incidence_matrix(elements: list) -> list[list[int]]:
    primitive_incidence_matrix = []

    for element in elements:
        element_id_bus_m, element_id_bus_n, element_id_bus_p = element.id_bus_m, element.id_bus_n, element.id_bus_p

        element_incidence_line = [0] * (max(element_id_bus_m, element_id_bus_n, element_id_bus_p) + 1)

        (element_incidence_line[element_id_bus_m], element_incidence_line[element_id_bus_n],
         element_incidence_line[element_id_bus_p]) = 1, 1, 1

        element_incidence_line[0] = 0

        primitive_incidence_matrix.append(element_incidence_line)

    return primitive_incidence_matrix


def find_primitives_matrices(simplified_elements: list[Element3Terminals], seq: str):
    primitive_admittance_row = np.array([], dtype=complex)

    for element in simplified_elements:
        branch: list[ImmittanceConstant] = element.admittance_representation(seq)

        for admittance in branch:
            if admittance.y_pu != 0:
                primitive_admittance = np.array([admittance.y_pu], dtype=complex)
                primitive_admittance_row = np.hstack((primitive_admittance_row, primitive_admittance))

    primitive_admittance_matrix = np.diag(primitive_admittance_row)
    primitive_impedance_matrix = np.linalg.inv(primitive_admittance_matrix)
    return primitive_admittance_matrix, primitive_impedance_matrix


def find_incidences_matrices(simplified_elements: list[Element3Terminals], seq: str, n_buses: int):
    incidence_matrix = np.array([0] * n_buses, dtype=int)

    for element in simplified_elements:
        branch: list[ImmittanceConstant] = element.admittance_representation(seq)
        element_id_bus_m, element_id_bus_n, element_id_bus_p = element.id_bus_m, element.id_bus_n, element.id_bus_p

        for admittance in branch:
            if admittance.y_pu != 0:
                primitive_incidence_row = np.zeros((1, n_buses), dtype=int)
                (primitive_incidence_row[0, element_id_bus_m],
                 primitive_incidence_row[0, element_id_bus_n],
                 primitive_incidence_row[0, element_id_bus_p]) = 1, -1, -1

                incidence_matrix = np.vstack((incidence_matrix, primitive_incidence_row))

    # Elimination of bus zero column and the first null row
    element_node_incidence_matrix = incidence_matrix[1:, :]
    bus_incidence_matrix = incidence_matrix[1:, 1:]

    return bus_incidence_matrix, element_node_incidence_matrix


def calculate_number_branches(simplified_elements: list[Element3Terminals], seq: str):
    n_branches = 0

    for element in simplified_elements:
        branch: list[ImmittanceConstant] = element.admittance_representation(seq)
        for admittance in branch:
            if admittance.y_pu != 0:
                n_branches += 1

    return n_branches


def calculate_buses_matrices(bus_incidence_matrix, primitive_admittance_matrix):
    pass


def assign_bases(simplified_elements):
    pass
