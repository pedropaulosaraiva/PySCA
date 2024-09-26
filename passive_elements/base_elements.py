from electrical_values import VoltageVariable, CurrentVariable, PuBase, PuBaseManager, ImmittanceConstant
from abc import ABC, abstractmethod
from electrical_relations import calculate_central_v_star, calculate_current, delta2star


class Element3Terminals(ABC):
    def __init__(self, y_series_mn_seq0_pu: complex, y_series_mn_seq1_pu: complex, y_series_mn_seq2_pu: complex,
                 y_series_np_seq0_pu: complex, y_series_np_seq1_pu: complex, y_series_np_seq2_pu: complex,
                 y_series_mp_seq0_pu: complex, y_series_mp_seq1_pu: complex, y_series_mp_seq2_pu: complex,
                 id_bus_m: int, id_bus_n: int, id_bus_p: int, v_base_m: float, v_base_n: float, v_base_p: float,
                 s_base: float):

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n
        self.id_bus_p = id_bus_p

        self.base_m = PuBaseManager.create_pu_base(v_base_m, s_base, id_bus_m)
        self.base_n = PuBaseManager.create_pu_base(v_base_n, s_base, id_bus_n)
        self.base_p = PuBaseManager.create_pu_base(v_base_p, s_base, id_bus_p)

        self.v_bus_m = VoltageVariable(self.base_m)
        self.v_bus_n = VoltageVariable(self.base_n)
        self.v_bus_p = VoltageVariable(self.base_p)

        self.i_bus_m = CurrentVariable(self.base_m)
        self.i_bus_n = CurrentVariable(self.base_n)
        self.i_bus_p = CurrentVariable(self.base_p)

        self.i_mn = CurrentVariable(self.base_m)
        self.i_np = CurrentVariable(self.base_n)
        self.i_mp = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = []
        self.branches_seq1: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq1_pu, self.base_m, id_bus_m,
                                                                           id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq1_pu, self.base_m, id_bus_n,
                                                                           id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq1_pu, self.base_m, id_bus_p,
                                                                           id_bus_m)]
        self.branches_seq2: list[ImmittanceConstant] = [ImmittanceConstant(y_series_mn_seq2_pu, self.base_m, id_bus_m,
                                                                           id_bus_n),
                                                        ImmittanceConstant(y_series_np_seq2_pu, self.base_m, id_bus_n,
                                                                           id_bus_p),
                                                        ImmittanceConstant(y_series_mp_seq2_pu, self.base_m, id_bus_m,
                                                                           id_bus_p)]

        self._define_seq0_topology(y_series_mn_seq0_pu, y_series_np_seq0_pu, y_series_mp_seq0_pu)

    @abstractmethod
    def _define_seq0_topology(self, y_series_mn_seq0_pu: complex, y_series_np_seq0_pu: complex,
                              y_series_mp_seq0_pu: complex):
        pass

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_bus_n = self.v_bus_n.pre().a().pu().rec()
        v_bus_p = self.v_bus_p.pre().a().pu().rec()

        y_mn_pu = self.branches_seq1[0].y_pu
        y_np_pu = self.branches_seq1[1].y_pu
        y_mp_pu = self.branches_seq1[2].y_pu

        i_mn_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        self.i_mn.define_value_pre_fault_pu(i_mn_pu)
        self.i_np.define_value_pre_fault_pu(i_np_pu)
        self.i_mp.define_value_pre_fault_pu(i_mp_pu)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_pu = calculate_current(y_n, v_bus_n, v_central_star)
        i_bus_p_pu = calculate_current(y_p, v_bus_p, v_central_star)

        self.i_bus_m.define_value_pre_fault_pu(i_bus_m_pu)
        self.i_bus_n.define_value_pre_fault_pu(i_bus_n_pu)
        self.i_bus_p.define_value_pre_fault_pu(i_bus_p_pu)

    @abstractmethod
    def calculate_internal_currents_pos_fault_pu(self):
        pass

    def admittance_representation(self, seq: str) -> list[ImmittanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex, voltage_bus_n_pu: complex,
                                     voltage_bus_p_pu: complex):

        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)
        self.v_bus_n.define_value_pre_fault_pu(voltage_bus_n_pu)
        self.v_bus_p.define_value_pre_fault_pu(voltage_bus_p_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex, voltage_bus_n_seq0_pu: complex,
                                     voltage_bus_n_seq1_pu: complex, voltage_bus_n_seq2_pu: complex,
                                     voltage_bus_p_seq0_pu: complex, voltage_bus_p_seq1_pu: complex,
                                     voltage_bus_p_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
        self.v_bus_n.define_values_pos_fault_pu(voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu)
        self.v_bus_p.define_values_pos_fault_pu(voltage_bus_p_seq0_pu, voltage_bus_p_seq1_pu, voltage_bus_p_seq2_pu)


class Element2Terminals(Element3Terminals, ABC):
    
    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 id_bus_n: int, v_base_m: float, v_base_n: float, s_base: float):
        
        Element3Terminals.__init__(self,  y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, 0,
                                   0, 0, 0, 0,
                                   0, id_bus_m, id_bus_n, 0, v_base_m, v_base_n,
                                   PuBase.default().v_base, s_base)

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_bus_n = self.v_bus_n.pre().a().pu().rec()
        y_pu = self.branches_seq1[0].y_pu
        i_pu = calculate_current(y_pu, v_bus_m, v_bus_n)

        self.i_bus_m.define_value_pre_fault_pu(i_pu)
        self.i_bus_n.define_value_pre_fault_pu(-i_pu)


class Element1Terminal(Element2Terminals, ABC):

    def __init__(self, y_series_seq0_pu: complex, y_series_seq1_pu: complex, y_series_seq2_pu: complex, id_bus_m: int,
                 v_base_m: float, s_base: float):

        Element2Terminals.__init__(self, y_series_seq0_pu, y_series_seq1_pu, y_series_seq2_pu, id_bus_m, 0,
                                   v_base_m, PuBase.default().v_base, s_base)

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()

        y_pu = self.branches_seq1[0].y_pu
        i_pu = calculate_current(y_pu, v_bus_m, 0)

        self.i_bus_m.define_value_pre_fault_pu(i_pu)


class CompositeElement:

    def __init__(self, elements: list[Element3Terminals]):

        self.elements = elements
        # ! Raise error if elements aren't in parallel

        id_bus_m, id_bus_n, id_bus_p = elements[0].id_bus_m, elements[0].id_bus_n, elements[0].id_bus_p
        base_m, base_n, base_p = elements[0].base_m, elements[0].base_n, elements[0].base_p

        self.id_bus_m = id_bus_m
        self.id_bus_n = id_bus_n
        self.id_bus_p = id_bus_p

        self.base_m = base_m
        self.base_n = base_n
        self.base_p = base_p

        self.v_bus_m = VoltageVariable(self.base_m)
        self.v_bus_n = VoltageVariable(self.base_n)
        self.v_bus_p = VoltageVariable(self.base_p)

        self.i_bus_m = CurrentVariable(self.base_m)
        self.i_bus_n = CurrentVariable(self.base_n)
        self.i_bus_p = CurrentVariable(self.base_p)

        self.i_mn = CurrentVariable(self.base_m)
        self.i_np = CurrentVariable(self.base_n)
        self.i_mp = CurrentVariable(self.base_m)

        self.branches_seq0: list[ImmittanceConstant] = self._composite_immittance('seq0')
        self.branches_seq1: list[ImmittanceConstant] = self._composite_immittance('seq1')
        self.branches_seq2: list[ImmittanceConstant] = self._composite_immittance('seq2')
        
    def _composite_immittance(self, seq: str):

        y_series_mn_pu = 0
        y_series_np_pu = 0
        y_series_mp_pu = 0

        branches_seq = []

        if seq == 'seq0':
            for element in self.elements:
                branches_seq.append(element.branches_seq0)

        elif seq == 'seq1':
            for element in self.elements:
                branches_seq.append(element.branches_seq1)

        elif seq == 'seq2':
            for element in self.elements:
                branches_seq.append(element.branches_seq2)
        else:
            pass
            # ! Raise an exception

        for branches in branches_seq:
            y_series_mn_pu += branches[0].y_pu
            y_series_np_pu += branches[1].y_pu
            y_series_mp_pu += branches[2].y_pu

        reference_branches = branches_seq[0]
        id_bus_m_immitance_0, id_bus_n_immitance_0 = reference_branches[0].id_bus_m, reference_branches[0].id_bus_n
        id_bus_n_immitance_1, id_bus_p_immitance_1 = reference_branches[1].id_bus_m, reference_branches[1].id_bus_n
        id_bus_m_immitance_2, id_bus_p_immitance_2 = reference_branches[2].id_bus_m, reference_branches[2].id_bus_n

        return [ImmittanceConstant(y_series_mn_pu, self.elements[0].base_m, id_bus_m_immitance_0, id_bus_n_immitance_0),
                ImmittanceConstant(y_series_np_pu, self.elements[0].base_m, id_bus_n_immitance_1, id_bus_p_immitance_1),
                ImmittanceConstant(y_series_mp_pu, self.elements[0].base_m, id_bus_m_immitance_2, id_bus_p_immitance_2)]

    def calculate_internal_currents_pre_fault_pu(self):
        v_bus_m = self.v_bus_m.pre().a().pu().rec()
        v_bus_n = self.v_bus_n.pre().a().pu().rec()
        v_bus_p = self.v_bus_p.pre().a().pu().rec()

        y_mn_pu = self.branches_seq1[0].y_pu
        y_np_pu = self.branches_seq1[1].y_pu
        y_mp_pu = self.branches_seq1[2].y_pu

        i_mn_pu = calculate_current(y_mn_pu, v_bus_m, v_bus_n)
        i_np_pu = calculate_current(y_np_pu, v_bus_n, v_bus_p)
        i_mp_pu = calculate_current(y_mp_pu, v_bus_m, v_bus_p)

        self.i_mn.define_value_pre_fault_pu(i_mn_pu)
        self.i_np.define_value_pre_fault_pu(i_np_pu)
        self.i_mp.define_value_pre_fault_pu(i_mp_pu)

        y_m, y_n, y_p = delta2star(y_mn_pu, y_np_pu, y_mp_pu)

        v_central_star = calculate_central_v_star(v_bus_m, v_bus_n, v_bus_p, y_m, y_n, y_p)

        i_bus_m_pu = calculate_current(y_m, v_bus_m, v_central_star)
        i_bus_n_pu = calculate_current(y_n, v_bus_n, v_central_star)
        i_bus_p_pu = calculate_current(y_p, v_bus_p, v_central_star)

        self.i_bus_m.define_value_pre_fault_pu(i_bus_m_pu)
        self.i_bus_n.define_value_pre_fault_pu(i_bus_n_pu)
        self.i_bus_p.define_value_pre_fault_pu(i_bus_p_pu)

        for element in self.elements:
            element.calculate_internal_currents_pre_fault_pu()

    def calculate_internal_currents_pos_fault_pu(self):
        i_mn_seq0_pu, i_np_seq0_pu, i_mp_seq0_pu = 0, 0, 0
        i_bus_m_seq0_pu, i_bus_n_seq0_pu, i_bus_p_seq0_pu = 0, 0, 0

        i_mn_seq1_pu, i_np_seq1_pu, i_mp_seq1_pu = 0, 0, 0
        i_bus_m_seq1_pu, i_bus_n_seq1_pu, i_bus_p_seq1_pu = 0, 0, 0

        i_mn_seq2_pu, i_np_seq2_pu, i_mp_seq2_pu = 0, 0, 0
        i_bus_m_seq2_pu, i_bus_n_seq2_pu, i_bus_p_seq2_pu = 0, 0, 0

        for element in self.elements:
            element.calculate_internal_currents_pos_fault_pu()

            i_mn_seq0_pu += element.i_mn.pos().seq0().pu().rec()
            i_np_seq0_pu += element.i_np.pos().seq0().pu().rec()
            i_mp_seq0_pu += element.i_mp.pos().seq0().pu().rec()

            i_bus_m_seq0_pu += element.i_bus_m.pos().seq0().pu().rec()
            i_bus_n_seq0_pu += element.i_bus_n.pos().seq0().pu().rec()
            i_bus_p_seq0_pu += element.i_bus_p.pos().seq0().pu().rec()

            i_mn_seq1_pu += element.i_mn.pos().seq1().pu().rec()
            i_np_seq1_pu += element.i_np.pos().seq1().pu().rec()
            i_mp_seq1_pu += element.i_mp.pos().seq1().pu().rec()

            i_bus_m_seq1_pu += element.i_bus_m.pos().seq1().pu().rec()
            i_bus_n_seq1_pu += element.i_bus_n.pos().seq1().pu().rec()
            i_bus_p_seq1_pu += element.i_bus_p.pos().seq1().pu().rec()

            i_mn_seq2_pu += element.i_mn.pos().seq2().pu().rec()
            i_np_seq2_pu += element.i_np.pos().seq2().pu().rec()
            i_mp_seq2_pu += element.i_mp.pos().seq2().pu().rec()

            i_bus_m_seq2_pu += element.i_bus_m.pos().seq2().pu().rec()
            i_bus_n_seq2_pu += element.i_bus_n.pos().seq2().pu().rec()
            i_bus_p_seq2_pu += element.i_bus_p.pos().seq2().pu().rec()

        self.i_mn.define_values_pos_fault_pu(i_mn_seq0_pu, i_mn_seq1_pu, i_mn_seq2_pu)
        self.i_np.define_values_pos_fault_pu(i_np_seq0_pu, i_np_seq1_pu, i_np_seq2_pu)
        self.i_mp.define_values_pos_fault_pu(i_mp_seq0_pu, i_mp_seq1_pu, i_mp_seq2_pu)

        self.i_bus_m.define_values_pos_fault_pu(i_bus_m_seq0_pu, i_bus_m_seq1_pu, i_bus_m_seq2_pu)
        self.i_bus_n.define_values_pos_fault_pu(i_bus_n_seq0_pu, i_bus_n_seq1_pu, i_bus_n_seq2_pu)
        self.i_bus_p.define_values_pos_fault_pu(i_bus_p_seq0_pu, i_bus_p_seq1_pu, i_bus_p_seq2_pu)

    def admittance_representation(self, seq: str) -> list[ImmittanceConstant]:
        if seq == "seq0":
            return self.branches_seq0
        elif seq == "seq1":
            return self.branches_seq1
        elif seq == "seq2":
            return self.branches_seq2

    def define_voltages_pre_fault_pu(self, voltage_bus_m_pu: complex, voltage_bus_n_pu: complex,
                                     voltage_bus_p_pu: complex):

        self.v_bus_m.define_value_pre_fault_pu(voltage_bus_m_pu)
        self.v_bus_n.define_value_pre_fault_pu(voltage_bus_n_pu)
        self.v_bus_p.define_value_pre_fault_pu(voltage_bus_p_pu)
        
        for element in self.elements:
            element.define_voltages_pre_fault_pu(voltage_bus_m_pu, voltage_bus_n_pu, voltage_bus_p_pu)

    def define_voltages_pos_fault_pu(self, voltage_bus_m_seq0_pu: complex, voltage_bus_m_seq1_pu: complex,
                                     voltage_bus_m_seq2_pu: complex, voltage_bus_n_seq0_pu: complex,
                                     voltage_bus_n_seq1_pu: complex, voltage_bus_n_seq2_pu: complex,
                                     voltage_bus_p_seq0_pu: complex, voltage_bus_p_seq1_pu: complex,
                                     voltage_bus_p_seq2_pu: complex):

        self.v_bus_m.define_values_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu)
        self.v_bus_n.define_values_pos_fault_pu(voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu)
        self.v_bus_p.define_values_pos_fault_pu(voltage_bus_p_seq0_pu, voltage_bus_p_seq1_pu, voltage_bus_p_seq2_pu)
        
        for element in self.elements:
            element.define_voltages_pos_fault_pu(voltage_bus_m_seq0_pu, voltage_bus_m_seq1_pu, voltage_bus_m_seq2_pu,
                                                 voltage_bus_n_seq0_pu, voltage_bus_n_seq1_pu, voltage_bus_n_seq2_pu,
                                                 voltage_bus_p_seq0_pu, voltage_bus_p_seq1_pu, voltage_bus_p_seq2_pu)
