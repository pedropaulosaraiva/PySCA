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
    y_m = y_np / (y_np * y_mp + y_mn * y_np + y_mn * y_mp)
    y_n = y_mp / (y_np * y_mp + y_mn * y_np + y_mn * y_mp)
    y_p = y_mn / (y_np * y_mp + y_mn * y_np + y_mn * y_mp)

    return y_m, y_n, y_p


def star2delta(y_m: complex, y_n: complex, y_p: complex):
    y_mn = (y_m + y_n + y_p) / (y_m * y_n)
    y_np = (y_m + y_n + y_p) / (y_n * y_p)
    y_mp = (y_m + y_n + y_p) / (y_m * y_p)

    return y_mn, y_np, y_mp


def calculate_central_v_star(v_bus_m: complex, v_bus_n: complex, v_bus_p: complex, y_m: complex, y_n: complex,
                             y_p: complex):

    v_central = (v_bus_m * y_m + v_bus_n * y_n + v_bus_p * y_p) / (y_m + y_n + y_p)

    return v_central

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
    a = equivalent_y_series(2,2)
    print(a)