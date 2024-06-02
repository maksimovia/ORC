import prop
from scipy.optimize import root_scalar, minimize_scalar
import numpy as np


class PUMP:
    def __init__(self, stream1, stream2, p_out, kpd_pump, streams, blocks):
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump
        self.streams = streams
        self.blocks = blocks
        self.H1 = streams.loc[stream1]['H']
        self.S1 = streams.loc[stream1]['S']
        self.G = streams.loc[stream1]['G']
        self.X = streams.loc[stream1]['X']

    def calc(self):
        H2t = prop.p_s(self.p_out, self.S1, self.X)["H"]
        H2 = self.H1 + (H2t - self.H1) / self.kpd_pump
        T2 = prop.h_p(H2, self.p_out, self.X)["T"]
        S2 = prop.h_p(H2, self.p_out, self.X)["S"]
        Q2 = prop.h_p(H2, self.p_out, self.X)["Q"]
        N = self.G * (H2 - self.H1)
        self.streams.loc[self.stream2] = [T2, self.p_out, H2, S2, Q2, self.G, self.X]
        self.blocks.loc["PUMP", "N"] = N
        pass


class HEAT:
    def __init__(self, stream11, stream12, stream21, stream22, Tgas_out, dTheat, hsteps, dP, dQ, streams, blocks):
        self.H11 = prop.t_p(streams.loc[stream11]["T"],streams.loc[stream11]["P"],streams.loc[stream11]["X"])["H"]
        self.H12 = prop.t_p(Tgas_out,streams.loc[stream11]["P"],streams.loc[stream11]["X"])["H"]
        self.H21 = prop.t_p(streams.loc[stream21]["T"],streams.loc[stream21]["P"],streams.loc[stream21]["X"])["H"]
        self.hsteps = hsteps
        self.streams = streams
        self.blocks = blocks
        self.stream21 = stream21
        self.stream22 = stream22
        self.stream11 = stream11
        self.stream12 = stream12
        self.dTheat = dTheat
        self.G1 = streams.loc[stream11]["G"]
        self.P11 = streams.loc[stream11]["P"]
        self.P21 = streams.loc[stream21]["P"]
        self.fluid1 = streams.loc[stream11]["X"]
        self.fluid2 = streams.loc[stream21]["X"]
        self.dP = dP
        self.dQ = dQ

    def calc(self):
        step = (self.H11-self.H12)/self.hsteps
        dP2 = self.P21 * (1 - self.dP)
        def G_sved(G2):
            p2 = self.P21
            t1 = np.zeros(self.hsteps + 1)
            t2 = np.zeros(self.hsteps + 1)
            Q = np.zeros(self.hsteps + 1)
            h11 = self.H11
            h21 = self.H21
            for i in range(self.hsteps + 1):
                t1[i] = prop.h_p(h11, self.P11, self.fluid1)["T"]
                if i < self.hsteps:
                    h12 = h11 - step
                    dQ = self.G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.hsteps + 1):
                t2[self.hsteps - i] = prop.h_p(h21, p2, self.fluid2)["T"]
                if i < self.hsteps:
                    h22 = h21+(Q[self.hsteps-i]-Q[self.hsteps-i-1])*self.dQ/G2
                    h21 = h22
                    p2 = p2 - dP2 / (self.hsteps)
            DT = t1 - t2
            min_dt = min(DT[:-1])
            return self.dTheat - min_dt
        G2 = self.streams.loc[self.stream21, "G"]*0.4+root_scalar(G_sved, bracket=[10, 10000], xtol=10**-5).root*(1-0.4)
        p2 = self.P21
        t1 = np.zeros(self.hsteps + 1)
        t2 = np.zeros(self.hsteps + 1)
        Q = np.zeros(self.hsteps + 1)
        h11 = self.H11
        h21 = self.H21
        for i in range(self.hsteps + 1):
            t1[i] = prop.h_p(h11, self.P11, self.fluid1)["T"]
            if i < self.hsteps:
                h12 = h11 - step
                dQ = self.G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.hsteps + 1):
            t2[self.hsteps - i] = prop.h_p(h21, p2, self.fluid2)["T"]
            if i < self.hsteps:
                h22 = h21 + (Q[self.hsteps - i] - Q[self.hsteps - i - 1]) * self.dQ / G2
                h21 = h22
                p2 = p2 - dP2 / (self.hsteps)
        DT = t1 - t2
        min_dt = min(DT[:-1])
        T12 = t1[-1]
        S12 = prop.h_p(h12, self.P11, self.fluid1)["S"]
        Q12 = prop.h_p(h12, self.P11, self.fluid1)["Q"]
        S22 = prop.h_p(h22, p2, self.fluid2)["S"]
        Q22 = prop.h_p(h22, p2, self.fluid2)["Q"]
        self.streams.loc[self.stream12] = [T12, self.P11, h12, S12, Q12, self.G1, self.fluid1]
        self.streams.loc[self.stream22] = [t2[0], p2, h22, S22, Q22, G2, self.fluid2]
        self.blocks.loc['HEAT'] = [0, Q[-1], min_dt, t1, t2, Q]
        pass


class TURB:
    def __init__(self, stream1, stream2, p_out, kpd_turb, streams, blocks):
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_turb = kpd_turb
        self.streams = streams
        self.blocks = blocks
        self.H1 = streams.loc[stream1]['H']
        self.S1 = streams.loc[stream1]['S']
        self.G = streams.loc[stream1]['G']
        self.X = streams.loc[stream1]['X']

    def calc(self):
        H2t = prop.p_s(self.p_out, self.S1, self.X)["H"]
        H2 = self.H1 - (self.H1 - H2t) * self.kpd_turb
        T2 = prop.h_p(H2, self.p_out, self.X)["T"]
        S2 = prop.h_p(H2, self.p_out, self.X)["S"]
        Q2 = prop.h_p(H2, self.p_out, self.X)["Q"]
        self.streams.loc[self.stream2] = [T2, self.p_out, H2, S2, Q2, self.G, self.X]
        N = self.G * (self.H1 - H2)
        self.blocks.loc["TURB", "N"] = N
        pass


class COND:
    def __init__(self, stream1, stream2, streams, blocks):
        self.H11 = prop.t_p(streams.loc[stream1]["T"],streams.loc[stream1]["P"],streams.loc[stream1]["X"])["H"]
        self.Q12 = 0
        self.streams = streams
        self.blocks = blocks
        self.stream1 = stream1
        self.stream2 = stream2
        self.G1 = streams.loc[stream1]["G"]
        self.P11 = streams.loc[stream1]["P"]
        self.fluid1 = streams.loc[stream1]["X"]

    def calc(self):
        H12 = prop.p_q(self.P11, self.Q12, self.fluid1)["H"]
        T12 = prop.p_q(self.P11, self.Q12, self.fluid1)["T"]
        S12 = prop.p_q(self.P11, self.Q12, self.fluid1)["S"]
        Q = self.G1*(self.H11 - H12)
        self.streams.loc[self.stream2] = [T12, self.P11, H12, S12, self.Q12, self.G1, self.fluid1]
        self.blocks.loc["COND", "Q"] = Q


class REG:
    def __init__(self, stream11, stream12, stream21, stream22, dTreg, hsteps, dP, dQ, Tgas_out, dTheat, streams, blocks):
        self.H11 = prop.t_p(streams.loc[stream11]["T"],streams.loc[stream11]["P"],streams.loc[stream11]["X"])["H"]
        self.H21 = prop.t_p(streams.loc[stream21]["T"],streams.loc[stream21]["P"],streams.loc[stream21]["X"])["H"]
        self.hsteps = hsteps
        self.streams = streams
        self.blocks = blocks
        self.stream21 = stream21
        self.stream22 = stream22
        self.stream11 = stream11
        self.stream12 = stream12
        self.dTreg = dTreg
        self.G1 = streams.loc[stream11]["G"]
        self.G2 = streams.loc[stream21]["G"]
        self.T11 = streams.loc[stream11]["T"]
        self.T21 = streams.loc[stream21]["T"]
        self.P11 = streams.loc[stream11]["P"]
        self.P21 = streams.loc[stream21]["P"]
        self.fluid1 = streams.loc[stream11]["X"]
        self.fluid2 = streams.loc[stream21]["X"]
        self.Tgas_out = Tgas_out
        self.dTheat = dTheat
        self.dP = dP
        self.dQ = dQ

    def calc(self):

        def T22_sved(T22):
            p2 = self.P21
            p1 = self.P11
            H22 = prop.t_p(T22, self.P21, self.fluid2)["H"]
            step = (H22 - self.H21) / self.hsteps
            t1 = np.zeros(self.hsteps + 1)
            t2 = np.zeros(self.hsteps + 1)
            Q = np.zeros(self.hsteps + 1)
            h21 = self.H21
            h11 = self.H11
            for i in range(self.hsteps + 1):
                t2[i] = prop.h_p(h21, p2, self.fluid2)["T"]
                if i < self.hsteps:
                    h22 = h21 + step
                    dQ = self.G2 * (h22 - h21) / self.dQ
                    h21 = h22
                    p2 = p2 - self.dP / (self.hsteps)
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.hsteps + 1):
                t1[self.hsteps - i] = prop.h_p(h11, p1, self.fluid1)["T"]
                if i < self.hsteps:
                    h12 = h11 - (Q[self.hsteps - i] - Q[self.hsteps - i - 1]) / self.G1
                    h11 = h12
                    p1 = p1 - self.dP / (self.hsteps)

            DT = t1 - t2
            min_dt = min(DT[:-1])
            T12 = t1[0]
            S12 = prop.h_p(h12, p1, self.fluid1)["S"]
            Q12 = prop.h_p(h12, p1, self.fluid1)["Q"]
            S22 = prop.h_p(h22, p2, self.fluid2)["S"]
            Q22 = prop.h_p(h22, p2, self.fluid2)["Q"]
            self.streams.loc[self.stream12] = [T12, p1, h12, S12, Q12, self.G1, self.fluid1]
            self.streams.loc[self.stream22] = [t2[-1], p2, h22, S22, Q22, self.G2, self.fluid2]
            self.blocks.loc['REG'] = [0, Q[-1], min_dt, t1, t2, Q]
            return abs(self.dTreg - min_dt)
        minimize_scalar(T22_sved, bounds=[self.T21, self.Tgas_out-self.dTheat-0.5])
        pass
