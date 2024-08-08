from passive_elements.generic_elements import Element2TerminalsDefinedBySI, Element3TerminalsDefinedBySI
from electrical_values import VoltageVariable, CurrentVariable, PuBase, ImpedanceConstant

class TransmissionLine(Element2TerminalsDefinedBySI):

    def __init__(self, z_series_seq0_Ohm_per_km_SI: complex, z_series_seq1_Ohm_per_km_SI: complex,
                 z_series_seq2_Ohm_per_km_SI: complex, line_lenght_km: float, id_barM: int, id_barN: int):
        self.z_series_seq0_Ohm_SI = (z_series_seq0_Ohm_per_km_SI * line_lenght_km)
        self.z_series_seq1_Ohm_SI = (z_series_seq1_Ohm_per_km_SI * line_lenght_km)
        self.z_series_seq2_Ohm_SI = (z_series_seq2_Ohm_per_km_SI * line_lenght_km)

        super().__init__(self.z_series_seq0_Ohm_SI, self.z_series_seq1_Ohm_SI, self.z_series_seq2_Ohm_SI, id_barM,
                         id_barN)

    def _define_seq0_topology(self, z_series_seq0_pu):
        self.branches_seq0 = [ImpedanceConstant(z_series_seq0_pu, self.base_m, self.id_bar_m, self.id_bar_n)]

    def calculate_internal_currents_pre_fault_pu(self):
        v_barM = self.v_bar_m.pre().a().pu().rec()
        v_barN = self.v_bar_n.pre().a().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq1[0].z_pu
        i_pu = v_pu / z_pu

        self.i_bar_m.define_value_pre_fault_pu(i_pu)
        self.i_bar_n.define_value_pre_fault_pu(i_pu)

    def calculate_internal_currents_pos_fault_pu(self):
        v_barM = self.v_bar_m.pos().seq0().pu().rec()
        v_barN = self.v_bar_n.pos().seq0().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq0[0].z_pu
        i_seq0_pu = v_pu / z_pu

        v_barM = self.v_bar_m.pos().seq1().pu().rec()
        v_barN = self.v_bar_n.pos().seq1().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq1[0].z_pu
        i_seq1_pu = v_pu / z_pu

        v_barM = self.v_bar_m.pos().seq2().pu().rec()
        v_barN = self.v_bar_n.pos().seq2().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq2[0].z_pu
        i_seq2_pu = v_pu / z_pu

        self.i_bar_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
        self.i_bar_n.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)


class TransmissionLinePiModel(Element3TerminalsDefinedBySI):

    def __init__(self, z_series_seq0_Ohm_per_km_SI: complex, z_series_seq1_Ohm_per_km_SI: complex,
                 z_series_seq2_Ohm_per_km_SI: complex, y_shunt_seq0_Ohm_per_km_SI: complex,
                 y_shunt_seq1_Ohm_per_km_SI: complex, y_shunt_seq2_Ohm_per_km_SI: complex, line_lenght_km: float,
                 id_barM: int, id_barN: int):
        self.z_series_seq0_Ohm_SI = (z_series_seq0_Ohm_per_km_SI * line_lenght_km)
        self.z_series_seq1_Ohm_SI = (z_series_seq1_Ohm_per_km_SI * line_lenght_km)
        self.z_series_seq2_Ohm_SI = (z_series_seq2_Ohm_per_km_SI * line_lenght_km)

        self.z_shunt_seq0_Ohm_SI = (y_shunt_seq0_Ohm_per_km_SI * line_lenght_km) ** (-1)
        self.z_shunt_seq1_Ohm_SI = (y_shunt_seq1_Ohm_per_km_SI * line_lenght_km) ** (-1)
        self.z_shunt_seq2_Ohm_SI = (y_shunt_seq2_Ohm_per_km_SI * line_lenght_km) ** (-1)

        super().__init__(self.z_series_seq0_Ohm_SI, self.z_series_seq1_Ohm_SI, self.z_series_seq2_Ohm_SI,
                         self.z_shunt_seq0_Ohm_SI / 2, self.z_shunt_seq1_Ohm_SI / 2, self.z_shunt_seq2_Ohm_SI / 2,
                         self.z_shunt_seq0_Ohm_SI / 2, self.z_shunt_seq1_Ohm_SI / 2, self.z_shunt_seq2_Ohm_SI / 2,
                         id_barM, id_barN, 0)

    def _define_seq0_topology(self, z_series_MN_seq0_pu: complex, z_series_NP_seq0_pu: complex,
                              z_series_PM_seq0_pu: complex):
        self.branches_seq0 = [ImpedanceConstant(z_series_MN_seq0_pu, self.base_m, self.id_bar_m, self.id_bar_n),
                              ImpedanceConstant(z_series_NP_seq0_pu, self.baseN, self.id_bar_n, self.id_bar_p),
                              ImpedanceConstant(z_series_PM_seq0_pu, self.baseP, self.id_bar_p, self.id_bar_m)]

    def calculate_internal_currents_pre_fault_pu(self):
        # ! Do it star to delta conversions
        v_barM = self.V_barM.pre().a().pu().rec()
        v_barN = self.V_barN.pre().a().pu().rec()
        v_barP = self.V_barP.pre().a().pu().rec()

        v_MN_pu = v_barM - v_barN
        v_NP_pu = v_barN - v_barP
        v_PM_pu = v_barP - v_barM

        z_MN_pu = self.branches_seq1[0].z_pu
        z_NP_pu = self.branches_seq1[1].z_pu
        z_PM_pu = self.branches_seq1[2].z_pu

        i_MN_pu = v_MN_pu / z_MN_pu
        i_NP_pu = v_NP_pu / z_NP_pu
        i_PM_pu = v_PM_pu / z_PM_pu

        self.I_barM.define_value_pre_fault_pu(i_MN_pu)
        self.I_barN.define_value_pre_fault_pu(i_NP_pu)
        self.I_barP.define_value_pre_fault_pu(i_PM_pu)

    def calculate_internal_currents_pos_fault_pu(self):
        # Do it this module
        v_barM = self.V_barM.pos().seq0().pu().rec()
        v_barN = self.V_barN.pos().seq0().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq0[0].z_pu
        i_seq0_pu = v_pu / z_pu

        v_barM = self.V_barM.pos().seq1().pu().rec()
        v_barN = self.V_barN.pos().seq1().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq1[0].z_pu
        i_seq1_pu = v_pu / z_pu

        v_barM = self.V_barM.pos().seq2().pu().rec()
        v_barN = self.V_barN.pos().seq2().pu().rec()
        v_pu = v_barM - v_barN
        z_pu = self.branches_seq2[0].z_pu
        i_seq2_pu = v_pu / z_pu

        self.I_barM.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
        self.I_barN.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)


if __name__ == "__main__":
    transmissionline = TransmissionLine(10, 10, 10,
                                        5, 1, 2)

    print(transmissionline)