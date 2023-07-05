import prop
from sqlite import read_stream, write_stream
import numpy as np

tolerance = 10 ** -5
h_steps = 5


def root(func, a, b, root_tol):
    while func(b)-func(a) > root_tol:
        x = a + (b-a)/2
        if func(a)*func(x) < 0:
            b = x
        else:
            a = x
    return x


class HEATER:
    def __init__(self, stream11, stream12, stream21, stream22, dt, t_out):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dT = dt
        self.T_out = t_out

    def calc(self):
        T11 = read_stream(self.stream11)['T']
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']

        print(read_stream(self.stream21)['T'])
        T21 = read_stream(self.stream21)['T']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']
        fluid2 = read_stream(self.stream21)['X']

        T12 = self.T_out
        H12 = prop.t_p(T12, P11, fluid1)["H"]
        S12 = prop.t_p(T12, P11, fluid1)["S"]
        Q12 = prop.t_p(T12, P11, fluid1)["Q"]

        ##########################################

        step = (H11 - H12) / h_steps

        def G2_root(G2):
            t1 = np.zeros(h_steps + 1)
            t2 = np.zeros(h_steps + 1)
            Q = np.zeros(h_steps + 1)
            h11 = H11
            h21 = H21
            print(t1,Q)
            for i in t1:
                t1[i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in t1:
                t2[h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < h_steps:
                    h22 = h21 + (Q[h_steps - i] - Q[h_steps - i - 1]) / G2
                    h21 = h22

            DT = t1 - t2
            minDT = min(DT)
            return self.dT - minDT

        ###########################################

        T22 = 1
        H22 = 1
        S22  =1
        Q22 = 1
        write_stream(self.stream12,T12,P11,H12,S12,Q12,G1,fluid1)
        write_stream(self.stream22,T22,P21,H22,S22,Q22,G2,fluid2)
        pass



    def TQ(self):
        pass


# class REGEN:
#     def __init__(self):
#     def calc(self):
#     def TQ(self):
#         pass
#
#
# class CONDENSER:
#     def __init__(self):
#     def calc(self):
#     def TQ(self):
#         pass
#
#
# class PUMP:
#     def __init__(self):
#     def calc(self):
#     def HS(self):
#         pass
#
#
# class TURBINE:
#     def __init__(self):
#     def calc(self):
#     def HS(self):
#         pass