from passive_elements.base_elements import Element2Terminals, Element3Terminals, Element1Terminal
from electrical_values import ImmittanceConstant
from electrical_relations import (calculate_current, star2delta, delta2star,
                                  equivalent_y_series, calculate_admittance_matrix_mnp_directly)
import numpy as np


class Transformer2Windings(Element2Terminals):

    def __init__(self, z_series_pu: complex, id_bus_m: int, id_bus_n: int, v_nom_pri_kv: float,
                 v_nom_sec_kv: float, s_nom_mva: float, primary_connection: str, secondary_connection: str,
                 delay_pri2sec: float, tap_primary=1, tap_secondary=1,
                 zn_grounded_primary_pu=0 + 0j, zn_grounded_secondary_pu=0 + 0j):

        self.primary_connection = primary_connection
        self.secondary_connection = secondary_connection
        self.connections = (primary_connection, secondary_connection)
        self.delay_pri2sec = delay_pri2sec

        for index, connection in enumerate(self.connections):
            self.y_grounded_primary, self.y_grounded_secondary = None, None
            y_grounded = [self.y_grounded_primary, self.y_grounded_secondary]
            zn_grounded = (zn_grounded_primary_pu, zn_grounded_secondary_pu)
            if connection == 'Yg':
                y_grounded[index] = ImmittanceConstant(float('inf'), self.base_m, 0, 0)
            elif connection == 'Yzn':
                y_grounded[index] = ImmittanceConstant(zn_grounded[index] ** (-1), self.base_m,
                                                       0, 0)
            elif (connection == 'Y') or (connection == 'Yn') or (connection == 'D'):
                y_grounded[index] = ImmittanceConstant(0, self.base_m, 0, 0)
            else:
                # ! exception here:
                pass
        # ! Raise an exception if tap is complex

        super().__init__(z_series_pu ** (-1), z_series_pu ** (-1), z_series_pu ** (-1),
                         id_bus_m, id_bus_n, v_nom_pri_kv * tap_primary * 1000, v_nom_sec_kv * tap_secondary * 1000,
                         s_nom_mva * (10**6))

    def _define_seq0_topology(self, y_series_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):

        if (self.primary_connection == "Yg") or (self.primary_connection == 'Yzn'):
            y_series_seq0_pu = equivalent_y_series(y_series_seq0_pu, 3 * self.y_grounded_primary.y_pu)

            if (self.primary_connection == "Yg") or (self.primary_connection == 'Yzn'):
                y_series_seq0_pu = equivalent_y_series(y_series_seq0_pu, 3 * self.y_grounded_secondary.y_pu)

                self.branches_seq0 = [ImmittanceConstant(y_series_seq0_pu, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

            elif self.primary_connection == "D":
                self.branches_seq0 = [ImmittanceConstant(y_series_seq0_pu, self.base_m, self.id_bus_m, 0),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

            elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

        elif self.primary_connection == "D":
            if (self.primary_connection == "Yg") or (self.primary_connection == 'Yzn'):
                y_series_seq0_pu = equivalent_y_series(y_series_seq0_pu, 3 * self.y_grounded_secondary.y_pu)

                self.branches_seq0 = [ImmittanceConstant(y_series_seq0_pu, self.base_m, 0, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

            elif self.primary_connection == "D":
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m, self.id_bus_m, 0),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

            elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

        elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
            self.branches_seq0 = [ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                  ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n),
                                  ImmittanceConstant(0, self.base_m, self.id_bus_m, self.id_bus_n)]

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq0().pu().rec()
        y_pu = self.branches_seq0[0].y_pu
        if self.branches_seq0[0].id_bus_m == 0:
            i_seq0_pu = calculate_current(y_pu, 0, v_bus_n)
        elif self.branches_seq0[0].id_bus_n == 0:
            i_seq0_pu = calculate_current(y_pu, v_bus_m, 0)
        else:
            i_seq0_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        v_bus_m = self.v_bus_m.pos().seq1().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq1().pu().rec()
        y_pu = self.branches_seq1[0].y_pu
        i_seq1_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        v_bus_m = self.v_bus_m.pos().seq2().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq2().pu().rec()
        y_pu = self.branches_seq2[0].y_pu
        i_seq2_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        if self.branches_seq0[0].id_bus_m == 0:
            self.i_bus_m.define_values_pos_fault_pu(0, i_seq1_pu, i_seq2_pu)
            self.i_bus_n.define_values_pos_fault_pu(-i_seq0_pu, -i_seq1_pu, -i_seq2_pu)
        elif self.branches_seq0[0].id_bus_n == 0:
            self.i_bus_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
            self.i_bus_n.define_values_pos_fault_pu(0, -i_seq1_pu, -i_seq2_pu)
        else:
            self.i_bus_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
            self.i_bus_n.define_values_pos_fault_pu(-i_seq0_pu, -i_seq1_pu, -i_seq2_pu)


class Transformer3Windings(Element3Terminals):

    def __init__(self, z_series_prisec_pu: complex, z_series_priter_pu: complex, z_series_secter_pu: complex,
                 id_bus_m: int, id_bus_n: int, id_bus_p: int, v_nom_pri_kv: float, v_nom_sec_kv: float,
                 v_nom_ter_kv: float, s_nom_pri_mva: float, s_nom_sec_mva: float,
                 primary_connection: str, secondary_connection: str, tertiary_connection: str,
                 delay_pri2sec: float, delay_pri2ter: float, tap_primary=1, tap_secondary=1, tap_tertiary=1,
                 zn_grounded_primary_pu=0 + 0j, zn_grounded_secondary_pu=0 + 0j, zn_grounded_tertiary_pu=0 + 0j):

        self.primary_connection = primary_connection
        self.secondary_connection = secondary_connection
        self.tertiary_connection = tertiary_connection
        self.connections = (self.primary_connection, self.secondary_connection, self.tertiary_connection)

        self.delay_pri2sec = delay_pri2sec
        self.delay_pri2ter = delay_pri2ter

        y_m_pu, y_n_pu, y_p_pu = self._calculate_star_model(z_series_prisec_pu, z_series_priter_pu, z_series_secter_pu)
        y_mn_pu, y_np_pu, y_mp_pu = star2delta(y_m_pu, y_n_pu, y_p_pu)

        for index, connection in enumerate(self.connections):
            self.y_grounded_primary, self.y_grounded_secondary, self.y_grounded_tertiary = None, None, None
            y_grounded = [self.y_grounded_primary, self.y_grounded_secondary, self.y_grounded_tertiary]
            zn_grounded = (zn_grounded_primary_pu, zn_grounded_secondary_pu, zn_grounded_tertiary_pu)
            if connection == 'Yg':
                y_grounded[index] = ImmittanceConstant(float('inf'), self.base_m, 0, 0)
            elif connection == 'Yzn':
                y_grounded[index] = ImmittanceConstant(zn_grounded[index] ** (-1), self.base_m,
                                                       0, 0)
            elif (connection == 'Y') or (connection == 'Yn') or (connection == 'D'):
                y_grounded[index] = ImmittanceConstant(0, self.base_m, 0, 0)
            else:
                # ! exception here:
                pass
        # ! Raise an exception if tap is complex

        super().__init__(y_mn_pu, y_mn_pu, y_mn_pu, y_np_pu, y_np_pu, y_np_pu, y_mp_pu, y_mp_pu, y_mp_pu,
                         id_bus_m, id_bus_n, id_bus_p, v_nom_pri_kv * tap_primary * 1000,
                         v_nom_sec_kv * tap_secondary * 1000, v_nom_ter_kv * tap_tertiary * 1000, 
                         s_nom_pri_mva * 10 ** 6)
        
    def _calculate_star_model(self, z_ps_pu, z_pt_pu, z_st_pu):
        
        y_m_pu = ((1 / 2) * (z_ps_pu + z_pt_pu - z_st_pu)) ** (-1)
        y_n_pu = ((1 / 2) * (z_ps_pu - z_pt_pu + z_st_pu)) ** (-1)
        y_p_pu = ((1 / 2) * (-z_ps_pu + z_pt_pu + z_st_pu)) ** (-1)

        return y_m_pu, y_n_pu, y_p_pu

    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        y_m, y_n, y_p = delta2star(y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu)
        # ! Sequence zero configurations
        if (self.primary_connection == "Yg") or (self.primary_connection == 'Yzn'):
            y_m = equivalent_y_series(y_m, 3 * self.y_grounded_primary.y_pu)
            self._is_primary_Yg_or_Yzn(y_m, y_n, y_p)

        elif self.primary_connection == "D":
            self._is_primary_D(y_m, y_n, y_p)

        elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
            self._is_primary_Y_or_Yn(y_m, y_n, y_p)
                
    def _is_primary_Yg_or_Yzn(self, y_m: complex, y_n: complex, y_p: complex):

        if (self.secondary_connection == "Yg") or (self.secondary_connection == 'Yzn'):
            y_n = equivalent_y_series(y_n, 3 * self.y_grounded_secondary.y_pu)

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu = star2delta(y_m, y_n, y_p)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif self.tertiary_connection == "D":
                y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu = star2delta(y_m, y_n, y_p)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, 0),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         self.id_bus_m, 0)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):
                y_series_mn_seq0_pu = equivalent_y_series(y_m, y_n)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, 0)]

        elif self.secondary_connection == "D":

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu = star2delta(y_m, y_n, y_p)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, 0),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         0, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif self.tertiary_connection == "D":
                y_parallel = y_n + y_p
                y_series_mn_seq0_pu = equivalent_y_series(y_m, y_parallel)

                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                y_series_mn_seq0_pu = equivalent_y_series(y_m, y_n)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         self.id_bus_m, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

        elif (self.secondary_connection == "Y") or (self.secondary_connection == "Yn"):
            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mp_seq0_pu = equivalent_y_series(y_m, y_p)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif self.tertiary_connection == "D":
                y_series_mp_seq0_pu = equivalent_y_series(y_m, y_p)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         self.id_bus_m, 0)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

    def _is_primary_D(self, y_m: complex, y_n: complex, y_p: complex):
        if (self.secondary_connection == "Yg") or (self.secondary_connection == 'Yzn'):
            y_n = equivalent_y_series(y_n, 3 * self.y_grounded_secondary.y_pu)

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu = star2delta(y_m, y_n, y_p)
                self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m,
                                                         0, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         0, self.id_bus_p)]

            elif self.tertiary_connection == "D":
                y_parallel = y_m + y_p
                y_series_np_seq0_pu = equivalent_y_series(y_n, y_parallel)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):
                y_series_np_seq0_pu = equivalent_y_series(y_n, y_m)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

        elif self.secondary_connection == "D":

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_parallel = y_m + y_n
                y_series_mp_seq0_pu = equivalent_y_series(y_p, y_parallel)
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         0, self.id_bus_p)]

            elif self.tertiary_connection == "D":

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

        elif (self.secondary_connection == "Y") or (self.secondary_connection == "Yn"):
            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mp_seq0_pu = equivalent_y_series(y_m, y_p)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         0, self.id_bus_p)]

            elif self.tertiary_connection == "D":

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

    def _is_primary_Y_or_Yn(self, y_m: complex, y_n: complex, y_p: complex):
        if (self.secondary_connection == "Yg") or (self.secondary_connection == 'Yzn'):
            y_n = equivalent_y_series(y_n, 3 * self.y_grounded_secondary.y_pu)

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_np_seq0_pu = equivalent_y_series(y_n, y_p)
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif self.tertiary_connection == "D":
                y_series_np_seq0_pu = equivalent_y_series(y_n, y_p)

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(y_series_np_seq0_pu, self.base_m,
                                                         self.id_bus_n, 0),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

        elif self.secondary_connection == "D":

            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):
                y_p = equivalent_y_series(y_p, 3 * self.y_grounded_tertiary.y_pu)
                y_series_mp_seq0_pu = equivalent_y_series(y_p, y_n)
                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(y_series_mp_seq0_pu, self.base_m,
                                                         0, self.id_bus_p)]

            elif self.tertiary_connection == "D":

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

        elif (self.secondary_connection == "Y") or (self.secondary_connection == "Yn"):
            if (self.tertiary_connection == "Yg") or (self.tertiary_connection == 'Yzn'):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif self.tertiary_connection == "D":

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

            elif (self.tertiary_connection == "Y") or (self.tertiary_connection == "Yn"):

                self.branches_seq0 = [ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_n),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_n, self.id_bus_p),
                                      ImmittanceConstant(0, self.base_m,
                                                         self.id_bus_m, self.id_bus_p)]

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq0().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq0().pu().rec()
        
        v_seq0 = np.array([[v_bus_m],
                           [v_bus_n],
                           [v_bus_p]])
        
        y_matrix_seq0 = calculate_admittance_matrix_mnp_directly(self.branches_seq0,
                                                                 self.id_bus_m, self.id_bus_n, self.id_bus_p)
        
        i_seq0 = np.matmul(y_matrix_seq0, v_seq0)

        v_bus_m = self.v_bus_m.pos().seq1().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq1().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq1().pu().rec()

        v_seq1 = np.array([[v_bus_m],
                           [v_bus_n],
                           [v_bus_p]])

        y_matrix_seq1 = calculate_admittance_matrix_mnp_directly(self.branches_seq1,
                                                                 self.id_bus_m, self.id_bus_n, self.id_bus_p)

        i_seq1 = np.matmul(y_matrix_seq1, v_seq1)

        v_bus_m = self.v_bus_m.pos().seq2().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq2().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq2().pu().rec()

        v_seq2 = np.array([[v_bus_m],
                           [v_bus_n],
                           [v_bus_p]])

        y_matrix_seq2 = calculate_admittance_matrix_mnp_directly(self.branches_seq2,
                                                                 self.id_bus_m, self.id_bus_n, self.id_bus_p)

        i_seq2 = np.matmul(y_matrix_seq2, v_seq2)
        
        self.i_bus_m.define_values_pos_fault_pu(i_seq0[0][0], i_seq1[0][0], i_seq2[0][0])
        self.i_bus_n.define_values_pos_fault_pu(i_seq0[1][0], i_seq1[1][0], i_seq2[1][0])
        self.i_bus_p.define_values_pos_fault_pu(i_seq0[2][0], i_seq1[2][0], i_seq2[2][0])


class GroundingTransformer(Element1Terminal):

    def __init__(self, z_series_pu: complex, id_bus_m: int, v_nom_kv: float,
                 s_nom_mva: float, zn_grounded_primary_pu=0 + 0j):

        z_series_seq0 = z_series_pu + 3 * zn_grounded_primary_pu
        y_series_seq0 = z_series_seq0 ** (-1)

        super().__init__(y_series_seq0, 0, 0, id_bus_m,
                         v_nom_kv * 1000, s_nom_mva * 10 ** 6)

    def _define_seq0_topology(self, y_series_mn_seq0_pu, y_series_np_seq0_pu,
                              y_series_mp_seq0_pu):
        self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m, self.id_bus_m, 0)]

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        y_pu = self.branches_seq0[0].y_pu

        i_seq0_pu = calculate_current(y_pu, v_bus_m, 0)

        self.i_bus_m.define_values_pos_fault_pu(i_seq0_pu, 0, 0)
