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
    pass


def find_incidences_matrices(simplified_elements: list):
    pass


def calculate_buses_matrices(bus_incidence_matrix, primitive_admittance_matrix):
    pass


def assign_bases(simplified_elements):
    pass