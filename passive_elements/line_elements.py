from passive_elements.base_elements import Element2Terminals, Element3Terminals
from electrical_values import PuBase, ImmittanceConstant
from electrical_relations import calculate_current, calculate_central_v_star, delta2star


class TransmissionLine(Element2Terminals):

    def __init__(self, z_series_seq0_ohm_per_km_si: complex, z_series_seq1_ohm_per_km_si: complex,
                 z_series_seq2_ohm_per_km_si: complex, line_length_km: float, id_bus_m: int, id_bus_n: int):
        
        self.z_series_seq0_ohm_si = (z_series_seq0_ohm_per_km_si * line_length_km)
        self.z_series_seq1_ohm_si = (z_series_seq1_ohm_per_km_si * line_length_km)
        self.z_series_seq2_ohm_si = (z_series_seq2_ohm_per_km_si * line_length_km)
        
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


class TransmissionLinePiModel(Element3Terminals):

    def __init__(self, z_series_seq0_ohm_per_km_si: complex, z_series_seq1_ohm_per_km_si: complex,
                 z_series_seq2_ohm_per_km_si: complex, y_shunt_seq0_s_per_km_si: complex,
                 y_shunt_seq1_s_per_km_si: complex, y_shunt_seq2_s_per_km_si: complex, line_length_km: float,
                 id_bus_m: int, id_bus_n: int):
        
        self.z_series_seq0_ohm_si = (z_series_seq0_ohm_per_km_si * line_length_km)
        self.z_series_seq1_ohm_si = (z_series_seq1_ohm_per_km_si * line_length_km)
        self.z_series_seq2_ohm_si = (z_series_seq2_ohm_per_km_si * line_length_km)

        self.y_shunt_seq0_ohm_si = (y_shunt_seq0_s_per_km_si * line_length_km)
        self.y_shunt_seq1_ohm_si = (y_shunt_seq1_s_per_km_si * line_length_km)
        self.y_shunt_seq2_ohm_si = (y_shunt_seq2_s_per_km_si * line_length_km)

        pu_base: PuBase = PuBase.default()
        v_base_m = pu_base.v_base
        v_base_n = pu_base.v_base
        s_base = pu_base.s_base

        y_series_seq0_pu = pu_base.z_base / self.z_series_seq0_ohm_si
        y_series_seq1_pu = pu_base.z_base / self.z_series_seq1_ohm_si
        y_series_seq2_pu = pu_base.z_base / self.z_series_seq2_ohm_si

        y_shunt_seq0_pu = pu_base.z_base * self.y_shunt_seq0_ohm_si
        y_shunt_seq1_pu = pu_base.z_base * self.y_shunt_seq0_ohm_si
        y_shunt_seq2_pu = pu_base.z_base * self.y_shunt_seq0_ohm_si

        super().__init__(y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, 
                         y_shunt_seq0_pu / 2, y_shunt_seq1_pu / 2, y_shunt_seq2_pu / 2,
                         y_shunt_seq0_pu / 2, y_shunt_seq1_pu / 2, y_shunt_seq2_pu / 2,
                         id_bus_m, id_bus_n, 0, v_base_m, v_base_n, PuBase.default().v_base, s_base)

    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        self.branches_seq0 = [ImmittanceConstant(y_series_mn_seq0_pu, self.base_m, self.id_bus_m, self.id_bus_n),
                              ImmittanceConstant(y_series_np_seq0_pu, self.base_m, self.id_bus_n, self.id_bus_p),
                              ImmittanceConstant(y_series_mp_seq0_pu, self.base_m, self.id_bus_m, self.id_bus_p)]

    def calculate_internal_currents_pos_fault_pu(self):

        v_bus_m = self.v_bus_m.pos().seq0().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq0().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq0().pu().rec()

        y_mn_pu = self.branches_seq0[0].y_pu
        y_np_pu = self.branches_seq0[1].y_pu
        y_mp_pu = self.branches_seq0[2].y_pu

        i_mn_seq0_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_seq0_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_seq0_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_seq0_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_seq0_pu = calculate_current(y_n, v_central_star, v_bus_n)
        i_bus_p_seq0_pu = calculate_current(y_p, v_central_star, v_bus_p)

        v_bus_m = self.v_bus_m.pos().seq1().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq1().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq1().pu().rec()

        y_mn_pu = self.branches_seq1[0].y_pu
        y_np_pu = self.branches_seq1[1].y_pu
        y_mp_pu = self.branches_seq1[2].y_pu

        i_mn_seq1_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_seq1_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_seq1_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_seq1_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_seq1_pu = calculate_current(y_n, v_central_star, v_bus_n)
        i_bus_p_seq1_pu = calculate_current(y_p, v_central_star, v_bus_p)

        v_bus_m = self.v_bus_m.pos().seq2().pu().rec()
        v_bus_n = self.v_bus_n.pos().seq2().pu().rec()
        v_bus_p = self.v_bus_p.pos().seq2().pu().rec()

        y_mn_pu = self.branches_seq2[0].y_pu
        y_np_pu = self.branches_seq2[1].y_pu
        y_mp_pu = self.branches_seq2[2].y_pu

        i_mn_seq2_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_seq2_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_seq2_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_seq2_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_seq2_pu = calculate_current(y_n, v_bus_n, v_central_star)
        i_bus_p_seq2_pu = calculate_current(y_p, v_bus_p, v_central_star)

        self.i_mn.define_values_pos_fault_pu(i_mn_seq0_pu, i_mn_seq1_pu, i_mn_seq2_pu)
        self.i_np.define_values_pos_fault_pu(i_np_seq0_pu, i_np_seq1_pu, i_np_seq2_pu)
        self.i_mp.define_values_pos_fault_pu(i_mp_seq0_pu, i_mp_seq1_pu, i_mp_seq2_pu)

        self.i_bus_m.define_values_pos_fault_pu(i_bus_m_seq0_pu, i_bus_m_seq1_pu, i_bus_m_seq2_pu)
        self.i_bus_n.define_values_pos_fault_pu(i_bus_n_seq0_pu, i_bus_n_seq1_pu, i_bus_n_seq2_pu)
        self.i_bus_p.define_values_pos_fault_pu(i_bus_p_seq0_pu, i_bus_p_seq1_pu, i_bus_p_seq2_pu)


if __name__ == "__main__":
    transmission_line = TransmissionLine(10, 10, 10,
                                         5, 1, 2)

    print(transmission_line)
