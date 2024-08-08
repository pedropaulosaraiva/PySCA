from passive_elements.generic_elements import Element2TerminalsDefinedByPU, Element3TerminalsDefinedByPU
from electrical_values import VoltageVariable, CurrentVariable, PuBase, ImpedanceConstant


class Transformer2Windings(Element2TerminalsDefinedByPU):

    def __init__(self, z_series_seq1_pu: complex, id_barM: int, id_barN: int, v_nom_pri_kv: float, v_nom_sec_kv: float,
                 s_nom_MVA: float, primary_connection: str, secondary_connection: str, delay_pri2sec: float):

        self.primary_connection = primary_connection
        self.secondary_connection = secondary_connection
        self.delay_pri2sec = delay_pri2sec

        super().__init__(z_series_seq1_pu, z_series_seq1_pu, z_series_seq1_pu, id_barM, id_barN, v_nom_pri_kv,
                         v_nom_sec_kv, s_nom_MVA)

    def _define_seq0_topology(self, z_series_seq0_pu):
        if self.primary_connection == "Yg":

            if self.primary_connection == "Yg":
                self.branches_seq0 = [ImpedanceConstant(z_series_seq0_pu, self.base_m, self.id_bar_m, self.id_bar_n)]
            elif self.primary_connection == "D":
                self.branches_seq0 = [ImpedanceConstant(z_series_seq0_pu, self.base_m, self.id_bar_m, 0)]
            elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
                pass

        elif self.primary_connection == "D":

            if self.primary_connection == "Yg":
                self.branches_seq0 = [ImpedanceConstant(z_series_seq0_pu, self.base_m, 0, self.id_bar_n)]
            elif self.primary_connection == "D":
                pass
            elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
                pass

        elif (self.primary_connection == "Y") or (self.primary_connection == "Yn"):
            pass


    def calculate_internal_currents_pre_fault_pu(self):
        v_barM = self.v_bar_m.pre().a().pu().rec()
        v_barN = self.v_bar_n.pre().a().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq1[0].z_pu
        i_pu = v_pu / z_pu

        self.i_bar_m.define_value_pre_fault_pu(i_pu)
        self.i_bar_n.define_value_pre_fault_pu(i_pu)

    def calculate_internal_currents_pos_fault_pu(self):
        # ! Do it the topology implications in zero sequence
        v_barM = self.v_bar_m.pos().seq0().pu().rec()
        v_barN = self.v_bar_n.pos().seq0().pu().rec()
        v_pu = v_barM - v_barN
        i_seq0_pu = v_pu / self.branches_seq0[0].z_pu

        v_barM = self.v_bar_m.pos().seq1().pu().rec()
        v_barN = self.v_bar_n.pos().seq1().pu().rec()
        v_pu = v_barM - v_barN
        i_seq1_pu = v_pu / self.branches_seq1[0].z_pu

        v_barM = self.v_bar_m.pos().seq2().pu().rec()
        v_barN = self.v_bar_n.pos().seq2().pu().rec()
        v_pu = v_barM - v_barN
        i_seq2_pu = v_pu / self.branches_seq1[0].z_pu

        self.i_bar_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
