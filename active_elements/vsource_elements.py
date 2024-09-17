from active_elements.base_elements import Element1Terminal
from electrical_values import ImmittanceConstant
from electrical_relations import (calculate_current, star2delta, delta2star,
                                  equivalent_y_series, calculate_admittance_matrix_mnp_directly)
import numpy as np


class NetworkEquivalent(Element1Terminal):

    def __init__(self, z_series_seq0_pu: complex, z_series_seq1_pu: complex, z_series_seq2_pu: complex, id_bus_m: int,
                 v_nom_kv: float, s_nom_mva: float):

        y_series_seq0_pu = z_series_seq0_pu**(-1)
        y_series_seq1_pu = z_series_seq1_pu**(-1)
        y_series_seq2_pu = z_series_seq2_pu**(-1)

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, v_nom_kv * 1000,
                         s_nom_mva * (10**6))

    @classmethod
    def defined_by_sc_capacity(cls, s_sc3_mva: complex, s_sc_1_mva: complex, id_bus_m: int, v_nom_kv: float,
                               s_nom_mva: float):
        s_sc3_pu = s_sc3_mva / s_nom_mva
        s_sc_1_pu = s_sc_1_mva / s_nom_mva

        z_series_seq1_pu = 1 / s_sc3_pu.conjugate()
        z_series_seq0_pu = ((3 / s_sc_1_pu.conjugate()) - (2 / s_sc3_pu.conjugate()))

        return cls(z_series_seq0_pu, z_series_seq1_pu, z_series_seq1_pu, id_bus_m, v_nom_kv, s_nom_mva)

    def _define_seq0_topology(self, y_series_seq0_pu: complex):
        self.branches_seq0 = ImmittanceConstant(y_series_seq0_pu, self.base_m, self.id_bus_m, 0)


class SynchronousGenerator(Element1Terminal):

    def __init__(self, z_series_seq0_pu: complex, z_series_seq1_pu: complex, z_series_seq2_pu: complex, id_bus_m: int,
                 v_nom_kv: float, s_nom_mva: float, connection: str, zn_grounded_pu=0 + 0j):

        self.connection = connection
        self.electromotive_force = None

        if connection == 'Yg':
            self.y_grounded = ImmittanceConstant(float('inf'), self.base_m, 0, 0)
        elif connection == 'Yzn':
            self.y_grounded = ImmittanceConstant(zn_grounded_pu ** (-1), self.base_m, 0, 0)
        elif (connection == 'Y') or (connection == 'Yn') or (connection == 'D'):
            self.y_grounded = ImmittanceConstant(0, self.base_m, 0, 0)
        else:
            # ! exception here:
            pass

        y_series_seq0_pu = z_series_seq0_pu**(-1)
        y_series_seq1_pu = z_series_seq1_pu**(-1)
        y_series_seq2_pu = z_series_seq2_pu**(-1)

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, v_nom_kv * 1000,
                         s_nom_mva * (10**6))

    def _define_seq0_topology(self, y_series_seq0_pu: complex):
        if (self.connection == "Yg") or (self.connection == 'Yzn'):
            y_series_seq0_pu = equivalent_y_series(y_series_seq0_pu, 3 * self.y_grounded.y_pu)
            self.branches_seq0 = ImmittanceConstant(y_series_seq0_pu, self.base_m, self.id_bus_m, 0)

        elif (self.connection == "D") or (self.connection == "Y") or (self.connection == "Yn"):
            self.branches_seq0 = ImmittanceConstant(0, self.base_m, self.id_bus_m, 0)


class SynchronousMotor(SynchronousGenerator):
    def __init__(self, z_series_seq0_pu: complex, z_series_seq1_pu: complex, z_series_seq2_pu: complex, id_bus_m: int,
                 v_nom_kv: float, s_nom_mva: float, connection: str, zn_grounded_pu=0 + 0j):

        super().__init__(z_series_seq0_pu, z_series_seq1_pu, z_series_seq2_pu, id_bus_m, v_nom_kv, s_nom_mva,
                         connection, zn_grounded_pu)
