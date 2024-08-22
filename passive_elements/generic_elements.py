from passive_elements.base_elements import Element2Terminals, Element1Terminal
from electrical_values import PuBase, ImmittanceConstant
from electrical_relations import calculate_current


class SeriesElement(Element2Terminals):

    def __init__(self, z_series_seq0_ohm_si: complex, z_series_seq1_ohm_si: complex, z_series_seq2_ohm_si: complex,
                 id_bus_m: int, id_bus_n: int):
        self.z_series_seq0_ohm_si = z_series_seq0_ohm_si
        self.z_series_seq1_ohm_si = z_series_seq1_ohm_si
        self.z_series_seq2_ohm_si = z_series_seq2_ohm_si

        pu_base: PuBase = PuBase.default()
        v_base_m = pu_base.v_base
        v_base_n = pu_base.v_base
        s_base = pu_base.s_base

        y_series_seq0_pu = pu_base.z_base / self.z_series_seq0_ohm_si
        y_series_seq1_pu = pu_base.z_base / self.z_series_seq1_ohm_si
        y_series_seq2_pu = pu_base.z_base / self.z_series_seq2_ohm_si

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, id_bus_n, v_base_m, v_base_n,
                         s_base)

    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m, self.id_bus_m, self.id_bus_n)]

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq0().pu().rec()
        y_pu = self.branches_seq0[0].y_pu
        i_seq0_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        v_bus_m = self.v_bus_m.pos().seq1().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq1().pu().rec()
        y_pu = self.branches_seq1[0].y_pu
        i_seq1_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        v_bus_m = self.v_bus_m.pos().seq2().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq2().pu().rec()
        y_pu = self.branches_seq2[0].y_pu
        i_seq2_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        self.i_bus_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)
        self.i_bus_n.define_values_pos_fault_pu(-i_seq0_pu, -i_seq1_pu, -i_seq2_pu)


class ShuntElement(Element1Terminal):

    def __init__(self, y_series_seq0_ohm_si: complex, y_series_seq1_ohm_si: complex, y_series_seq2_ohm_si: complex,
                 id_bus_m: int):
        self.y_series_seq0_ohm_si = y_series_seq0_ohm_si
        self.y_series_seq1_ohm_si = y_series_seq1_ohm_si
        self.y_series_seq2_ohm_si = y_series_seq2_ohm_si

        pu_base: PuBase = PuBase.default()
        v_base_m = pu_base.v_base
        v_base_n = pu_base.v_base
        s_base = pu_base.s_base

        y_series_seq0_pu = pu_base.z_base * self.y_series_seq0_ohm_si
        y_series_seq1_pu = pu_base.z_base * self.y_series_seq1_ohm_si
        y_series_seq2_pu = pu_base.z_base * self.y_series_seq2_ohm_si

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, v_base_m, s_base)

    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m, self.id_bus_m, 0)]

    def calculate_internal_currents_pos_fault_pu(self):
        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        y_pu = self.branches_seq0[0].y_pu
        i_seq0_pu = calculate_current(y_pu, v_bus_m, 0)

        v_bus_m = self.v_bus_m.pos().seq1().pu().rec()
        y_pu = self.branches_seq1[0].y_pu
        i_seq1_pu = calculate_current(y_pu, v_bus_m, 0)

        v_bus_m = self.v_bus_m.pos().seq2().pu().rec()
        y_pu = self.branches_seq2[0].y_pu
        i_seq2_pu = calculate_current(y_pu, v_bus_m, 0)

        self.i_bus_m.define_values_pos_fault_pu(i_seq0_pu, i_seq1_pu, i_seq2_pu)

