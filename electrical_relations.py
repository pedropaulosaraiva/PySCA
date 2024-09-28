from electrical_values import ImmittanceConstant
import numpy as np


def calculate_current(y_pu: complex, v_bus_m: complex, v_bus_n: complex):
    v_pu = v_bus_m - v_bus_n
    i_pu = v_pu * y_pu

    return i_pu


def equivalent_y_series(y_1: complex, y_2: complex):
    if y_1 == float('inf'):
        y_series = y_2
    elif y_2 == float('inf'):
        y_series = y_1
    else:
        y_series = (y_1 * y_2) / (y_1 + y_2)
    return y_series


def delta2star(y_mn: complex, y_np: complex, y_mp: complex):
    try:
        y_m = (y_np * y_mp + y_mn * y_np + y_mn * y_mp) / y_np
        y_n = (y_np * y_mp + y_mn * y_np + y_mn * y_mp) / y_mp
        y_p = (y_np * y_mp + y_mn * y_np + y_mn * y_mp) / y_mn

    except ZeroDivisionError:
        def div_by_zero(dividend: complex, divisor: complex):
            try:
                return dividend / divisor
            except ZeroDivisionError:
                return float('inf')

        if (y_mn, y_np, y_mp) == (0, 0, 0):
            y_m, y_n, y_p = 0, 0, 0

        elif (y_mn, y_np) == (0, 0) or (y_mn, y_mp) == (0, 0) or (y_np, y_mp) == (0, 0):
            y_m = y_mp * 2 + y_mn * 2
            y_n = y_mn * 2 + y_np * 2
            y_p = y_mp * 2 + y_np * 2

        elif y_mn == 0 or y_np == 0 or y_mp == 0:
            y_m = div_by_zero(y_np * y_mp + y_mn * y_np + y_mn * y_mp, y_np)
            y_n = div_by_zero(y_np * y_mp + y_mn * y_np + y_mn * y_mp, y_mp)
            y_p = div_by_zero(y_np * y_mp + y_mn * y_np + y_mn * y_mp, y_mn)

        else:
            raise Exception("Error")

    return y_m, y_n, y_p


def star2delta(y_m: complex, y_n: complex, y_p: complex):
    y_mn = (y_m * y_n) / (y_m + y_n + y_p)
    y_np = (y_n * y_p) / (y_m + y_n + y_p)
    y_mp = (y_m * y_p) / (y_m + y_n + y_p)

    return y_mn, y_np, y_mp


def calculate_central_v_star(v_bus_m: complex, v_bus_n: complex, v_bus_p: complex, y_m: complex, y_n: complex,
                             y_p: complex):

    v_central = (v_bus_m * y_m + v_bus_n * y_n + v_bus_p * y_p) / (y_m + y_n + y_p)

    return v_central


# ! Perhaps there is a conceptual error in using the following matrix for current calculation to the 3 windings
# ! transformer
def calculate_admittance_matrix_mnp_directly(branches: list[ImmittanceConstant], id_bus_m: int, id_bus_n: int,
                                             id_bus_p: int):

    A = np.zeros((3, 3))
    for index, branch in enumerate(branches):
        if branch.id_bus_m == id_bus_m:
            A[index][0] = 1

            if branch.id_bus_n == id_bus_n:
                A[index][1] = -1
            elif branch.id_bus_n == id_bus_p:
                A[index][2] = -1
            elif branch.id_bus_n == 0:
                pass
            else:
                # ! raise another error
                raise KeyError
        elif branch.id_bus_m == id_bus_n:
            A[index][1] = 1

            if branch.id_bus_n == id_bus_p:
                A[index][2] = -1
            elif branch.id_bus_n == 0:
                pass
            else:
                # ! raise another error
                raise KeyError
        elif branch.id_bus_m == 0:

            if branch.id_bus_n == id_bus_n:
                A[index][1] = 1
            elif branch.id_bus_n == id_bus_p:
                A[index][2] = 1
            else:
                # ! raise another error
                raise KeyError
        else:
            # ! raise another error
            raise KeyError

    y_prim = np.array([[branches[0].y_pu, 0, 0],
                       [0, branches[1].y_pu, 0],
                       [0, 0, branches[2].y_pu]])
    A_t = np.transpose(A)

    y_matrix = np.matmul(np.matmul(A_t, y_prim), A)

    return y_matrix


if __name__ == '__main__':
    # Quick test for the functions in this module (doesn't fully ensure that there are no mistakes in the functions):

    print("Test for calculate_current function:\n"
          f"    T1 (expected result = 50): {calculate_current(10, 7, 2)}\n")

    if calculate_current(10, 7, 2) != 50:
        raise Warning('calculate_current have mistakes')

    print("Test for equivalent_y_series function:\n"
          f"    T1 (expected result = 5): {equivalent_y_series(10, 10)}\n")

    if equivalent_y_series(10, 10) != 5:
        raise Warning('equivalent_y_series have mistakes')

    print("Test for delta2star function:\n"
          f"    T1 (expected result = 30, 30, 30): {delta2star(10, 10, 10)}\n"
          f"    T2 (expected result = 0.7100, 35.4999, 14.2000): {delta2star(1/2, 1/0.1, 1/5)}\n"
          f"    T3 (expected result = 20, 20, 0): {delta2star(10, 0, 0)}\n")

    if delta2star(10, 10, 10) != (30, 30, 30):
        raise Warning('delta2star have mistakes')
    elif not (0.70, 35.4, 14.1) < delta2star(0.5, 10, 0.2) < (0.72, 35.5, 14.13):
        raise Warning('delta2star have mistakes')
    elif delta2star(10, 0, 0) != (20, 20, 0):
        raise Warning('delta2star have mistakes')

    print("Test for star2delta function:\n"
          f"    T1 (expected result = 3.333, 3.333, 3.333): {star2delta(10, 10, 10)}\n"
          f"    T2 (expected result = 2.9412, 0.5882, 1.1765): {star2delta(10, 5, 2)}\n"
          f"    T3 (expected result = 5, 0, 0): {star2delta(10, 10, 0)}")

    if not (3.3333, 3.3333, 3.3333) < star2delta(10, 10, 10) < (3.3334, 3.3334, 3.3334):
        raise Warning('star2delta have mistakes')
    elif not (2.9410, 0.5882, 1.1764) < star2delta(10, 5, 2) < (2.9412, 0.5883, 1.1765):
        raise Warning('star2delta have mistakes')
