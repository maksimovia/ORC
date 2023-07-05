import prop
from sqlite import read_stream, write_stream, write_block
import numpy as np

tolerance = 10 ** -5
h_steps = 3


def root(func, a, b, root_tol):
    while abs(func(a) - func(b)) > root_tol:
        x = a + (b - a) / 2
        if func(a) * func(x) < 0:
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
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']

        T12 = self.T_out
        H12 = prop.t_p(T12, P11, fluid1)["H"]
        S12 = prop.t_p(T12, P11, fluid1)["S"]
        Q12 = prop.t_p(T12, P11, fluid1)["Q"]

        step = (H11 - H12) / h_steps

        def G2_func(G2):
            t1 = np.zeros(h_steps + 1)
            t2 = np.zeros(h_steps + 1)
            Q = np.zeros(h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(h_steps + 1):
                t1[i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(h_steps + 1):
                t2[h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < h_steps:
                    h22 = h21 + (Q[h_steps - i] - Q[h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dT - min_dt

        G2 = root(G2_func, 1, 10000, tolerance)
        t1 = np.zeros(h_steps + 1)
        t2 = np.zeros(h_steps + 1)
        Q = np.zeros(h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(h_steps + 1):
            t1[i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(h_steps + 1):
            t2[h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < h_steps:
                h22 = h21 + (Q[h_steps - i] - Q[h_steps - i - 1]) / G2
                h21 = h22
        T22 = t2[0]
        H22 = prop.t_p(T22, P21, fluid2)["H"]
        S22 = prop.t_p(T22, P21, fluid2)["S"]
        Q22 = prop.t_p(T22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('HEATER', Q[-1])
        pass


class PUMP:
    def __init__(self, stream1, stream2, p_out, kpd_pump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.kpd_pump
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H2 - H1)
        write_block('PUMP', N)

        pass


class TURBINE:
    def __init__(self, stream1, stream2, p_out, kpd_turb):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_turb = kpd_turb

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 - (H1 - H2t) * self.kpd_turb
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H1 - H2)
        write_block('TURBINE', N)
        pass


class CONDENSER:
    def __init__(self, stream11, stream12, stream21, stream22, dt):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt

    def calc(self):
        P1 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        H12 = prop.p_q(P1, 0, fluid1)["H"]
        P2 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        step = (H11 - H12) / h_steps

        def G2_func(G2):
            t1 = np.zeros(h_steps + 1)
            t2 = np.zeros(h_steps + 1)
            Q = np.zeros(h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(h_steps + 1):
                t1[i] = prop.h_p(h11, P1, fluid1)["T"]
                if i < h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(h_steps + 1):
                t2[h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
                if i < h_steps:
                    h22 = h21 + (Q[h_steps - i] - Q[h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt

        G2 = root(G2_func, 1, 10000, tolerance)
        t1 = np.zeros(h_steps + 1)
        t2 = np.zeros(h_steps + 1)
        Q = np.zeros(h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(h_steps + 1):
            t1[i] = prop.h_p(h11, P1, fluid1)["T"]
            if i < h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(h_steps + 1):
            t2[h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
            if i < h_steps:
                h22 = h21 + (Q[h_steps - i] - Q[h_steps - i - 1]) / G2
                h21 = h22
        T22 = t2[0]
        H22 = prop.t_p(T22, P2, fluid2)["H"]
        S22 = prop.t_p(T22, P2, fluid2)["S"]
        Q22 = prop.t_p(T22, P2, fluid2)["Q"]
        T12 = prop.h_p(H12, P1, fluid1)["T"]
        S12 = prop.h_p(H12, P1, fluid1)["S"]
        T21 = prop.h_p(H21, P2, fluid2)["T"]
        S21 = prop.h_p(H21, P2, fluid2)["S"]
        Q21 = prop.h_p(H21, P2, fluid2)["Q"]
        write_stream(self.stream12, T12, P1, H12, S12, 0, G1, fluid1)
        write_stream(self.stream21, T21, P2, H21, S21, Q21, G2, fluid2)
        write_stream(self.stream22, T22, P2, H22, S22, Q22, G2, fluid2)
        write_block('CONDENSER', Q[-1])
        pass

# class regen:
#     def __init__(self, stream11, stream12, stream21, stream22, dTmin, dPreg1, dPreg2):
#         self.stream11 = stream11
#         self.stream12 = stream12
#         self.stream21 = stream21
#         self.stream22 = stream22
#         self.dTmin = dTmin
#         self.dPreg1 = dPreg1
#         self.dPreg2 = dPreg2
#     def calc(self):
#         H11 = streams.at[self.stream11, "H"]
#         H21 = streams.at[self.stream21, "H"]
#         T11 = streams.at[self.stream11, "T"]
#         T21 = streams.at[self.stream21, "T"]
#         S11 = streams.at[self.stream11, "S"]
#         S21 = streams.at[self.stream21, "S"]
#         P1 = streams.at[self.stream11, "P"] - self.dPreg1
#         P2 = streams.at[self.stream21, "P"] - self.dPreg2
#         G1 = streams.at[self.stream11, "G"]
#         G2 = streams.at[self.stream21, "G"]
#         t1 = np.zeros(s + 1)
#         t2 = np.zeros(s + 1)
#         Q = np.zeros(s + 1)
#         if np.isnan(H11):
#             T22 = T21
#             T12 = T11
#             H12 = H11
#             H22 = H21
#             S22 = S21
#             S12 = S11
#             Q[s] = 0
#             Q12 = streams.at[self.stream11, "Q"]
#             Q22 = streams.at[self.stream21, "Q"]
#         else:
#             T12 = T21 + self.dTmin
#             H12 = prop.t_p(T12, P1, fluid)["H"]
#             step = (H11 - H12) / s
#             h11 = H11
#             h21 = H21
#             for i in range(s + 1):
#                 t1[i] = prop.h_p(h11, P1, fluid)["T"]
#                 if i < s:
#                     h12 = h11 - step
#                     dQ = G1 * (h11 - h12)
#                     h11 = h12
#                     Q[i + 1] = Q[i] + dQ
#             for i in range(s + 1):
#                 t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
#                 if i < s:
#                     h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
#                     h21 = h22
#             T12 = t1[s]
#             T22 = t2[0]
#             H12 = h11
#             H22 = h21
#             DT = t1 - t2
#             minDT = min(DT)
#             S22 = prop.h_p(H22, P2, fluid)["S"]
#             S12 = prop.h_p(H12, P1, fluid)["S"]
#             Q12 = prop.h_p(H12, P1, fluid)["Q"]
#             Q22 = prop.h_p(H22, P2, fluid)["Q"]
#         streams.loc[self.stream12, "T":"G"] = [T12, P1, H12, S12, Q12, G1]
#         streams.loc[self.stream22, "T":"G"] = [T22, P2, H22, S22, Q22, G2]
#         blocks.loc["REGENERATOR", "Q"] = Q[s]
