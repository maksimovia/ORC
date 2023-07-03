import prop
import numpy as np
import matplotlib.pyplot as plt

svedtol = 10 ** -6
s = 20


def init(streams_in, blocks_in, fluid_in, gas_in, fluidcond_in):
    global streams
    streams = streams_in
    global blocks
    blocks = blocks_in
    global fluid
    fluid = fluid_in
    global gas
    gas = gas_in
    global fluidcond
    fluidcond = fluidcond_in


def sved(func, pribl, svedtol):
    Xl = pribl[0]
    Xr = pribl[1]
    while abs(Xl - Xr) > svedtol:
        Xc = (Xl + Xr) / 2
        if np.sign(func(Xr)) != np.sign(func(Xc)):
            Xl = Xc
        else:
            Xr = Xc
    return Xc


class heater:
    def __init__(self, stream11, stream12, stream21, stream22, Toutmin, minDTheater):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.Toutmin = Toutmin
        self.minDTheater = minDTheater
    def calc(self):
        H11 = streams.at[self.stream11, "H"]
        H21 = streams.at[self.stream21, "H"]
        P1 = streams.at[self.stream11, "P"]
        P2 = streams.at[self.stream21, "P"]
        G1 = streams.at[self.stream11, "G"]
        G2 = streams.at[self.stream21, "G"]
        T12 = self.Toutmin
        H12 = prop.t_p(T12, P1, gas)["H"]
        step = (H11 - H12) / s

        def G2sved(G2):
            t1 = np.zeros(s + 1)
            t2 = np.zeros(s + 1)
            Q = np.zeros(s + 1)
            h11 = H11
            h21 = H21
            for i in range(s + 1):
                t1[i] = prop.h_p(h11, P1, gas)["T"]
                if i < s:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(s + 1):
                t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
                if i < s:
                    h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT = t1 - t2
            minDT = min(DT)
            return self.minDTheater - minDT

        G2 = sved(G2sved, [0, 9999], svedtol)
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, gas)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        T12 = t1[s]
        T22 = t2[0]
        H12 = h11
        H22 = h21
        DT = t1 - t2
        minDT = min(DT)
        S12 = prop.h_p(H12, P1, gas)["S"]
        S22 = prop.h_p(H22, P2, fluid)["S"]
        Q12 = prop.h_p(H12, P1, gas)["Q"]
        Q22 = prop.h_p(H22, P2, fluid)["Q"]
        streams.loc[self.stream12, "T":"G"] = [T12, P1, H12, S12, Q12, G1]
        streams.loc[self.stream22, "T":"G"] = [T22, P2, H22, S22, Q22, G2]
        blocks.loc["HEATER", "Q"] = Q[s]

    def TQ(stream11, stream12, stream21, stream22):
        H11 = streams.at[stream11, "H"]
        H21 = streams.at[stream21, "H"]
        H12 = streams.at[stream12, "H"]
        P1 = streams.at[stream12, "P"]
        P2 = streams.at[stream22, "P"]
        G1 = streams.at[stream11, "G"]
        G2 = streams.at[stream21, "G"]
        step = (H11 - H12) / s
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, gas)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        minDT = round(min(DT), 1)
        plt.title("HEATER: minDT={}°C".format(round(minDT, 1)))
        plt.xlabel("Q, кВт")
        plt.ylabel("T, °C")
        plt.grid(True)
        return plt.plot(Q, t2, Q, t1)


class pump:
    def __init__(self, stream1, stream2, Pout, KPDpump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.Pout = Pout
        self.KPDpump = KPDpump

    def calc(self):
        P1 = streams.at[self.stream1, "P"]
        H1 = streams.at[self.stream1, "H"]
        S1 = streams.at[self.stream1, "S"]
        G = streams.at[self.stream1, "G"]
        H2t = prop.p_s(self.Pout, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.KPDpump
        T2 = prop.h_p(H2, self.Pout, fluid)["T"]
        S2 = prop.h_p(H2, self.Pout, fluid)["S"]
        Q2 = prop.h_p(H2, self.Pout, fluid)["Q"]
        streams.loc[self.stream2, "T":"G"] = [T2, self.Pout, H2, S2, Q2, G]
        N = G * (H2 - H1)
        blocks.loc["PUMP", "N"] = N


class regen:
    def __init__(self, stream11, stream12, stream21, stream22, dTmin, dPreg1, dPreg2):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dTmin = dTmin
        self.dPreg1 = dPreg1
        self.dPreg2 = dPreg2
    def calc(self):
        H11 = streams.at[self.stream11, "H"]
        H21 = streams.at[self.stream21, "H"]
        T11 = streams.at[self.stream11, "T"]
        T21 = streams.at[self.stream21, "T"]
        S11 = streams.at[self.stream11, "S"]
        S21 = streams.at[self.stream21, "S"]
        P1 = streams.at[self.stream11, "P"] - self.dPreg1
        P2 = streams.at[self.stream21, "P"] - self.dPreg2
        G1 = streams.at[self.stream11, "G"]
        G2 = streams.at[self.stream21, "G"]
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        if np.isnan(H11):
            T22 = T21
            T12 = T11
            H12 = H11
            H22 = H21
            S22 = S21
            S12 = S11
            Q[s] = 0
            Q12 = streams.at[self.stream11, "Q"]
            Q22 = streams.at[self.stream21, "Q"]
        else:
            T12 = T21 + self.dTmin
            H12 = prop.t_p(T12, P1, fluid)["H"]
            step = (H11 - H12) / s
            h11 = H11
            h21 = H21
            for i in range(s + 1):
                t1[i] = prop.h_p(h11, P1, fluid)["T"]
                if i < s:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(s + 1):
                t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
                if i < s:
                    h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT = t1 - t2
            minDT = min(DT)
            S22 = prop.h_p(H22, P2, fluid)["S"]
            S12 = prop.h_p(H12, P1, fluid)["S"]
            Q12 = prop.h_p(H12, P1, fluid)["Q"]
            Q22 = prop.h_p(H22, P2, fluid)["Q"]
        streams.loc[self.stream12, "T":"G"] = [T12, P1, H12, S12, Q12, G1]
        streams.loc[self.stream22, "T":"G"] = [T22, P2, H22, S22, Q22, G2]
        blocks.loc["REGENERATOR", "Q"] = Q[s]

    def TQ(self):
        H11 = streams.at[self.stream11, "H"]
        H21 = streams.at[self.stream21, "H"]
        H12 = streams.at[self.stream12, "H"]
        P1 = streams.at[self.stream12, "P"]
        P2 = streams.at[self.stream22, "P"]
        G1 = streams.at[self.stream11, "G"]
        G2 = streams.at[self.stream21, "G"]
        step = (H11 - H12) / s
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, fluid)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluid)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        minDT = round(min(DT), 1)
        plt.title("REGEN: minDT={}°C".format(round(minDT, 1)))
        plt.xlabel("Q, кВт")
        plt.ylabel("T, °C")
        plt.grid(True)
        return plt.plot(Q, t2, Q, t1)


class turbine:
    def __init__(self, stream1, stream2, Pout, KPDturb):
        self.stream1 = stream1
        self.stream2 = stream2
        self.Pout = Pout
        self.KPDturb = KPDturb
    def calc(self):
        P1 = streams.at[self.stream1, "P"]
        H1 = streams.at[self.stream1, "H"]
        S1 = streams.at[self.stream1, "S"]
        G = streams.at[self.stream1, "G"]
        H2t = prop.p_s(self.Pout, S1, fluid)["H"]
        H2 = H1 - (H1 - H2t) * self.KPDturb
        T2 = prop.h_p(H2, self.Pout, fluid)["T"]
        S2 = prop.h_p(H2, self.Pout, fluid)["S"]
        Q2 = prop.h_p(H2, self.Pout, fluid)["Q"]
        streams.loc[self.stream2, "T":"G"] = [T2, self.Pout, H2, S2, Q2, G]
        N = G * (H1 - H2)
        blocks.loc["TURBINE", "N"] = N


class condenser:
    def __init__(self, stream11, stream12, stream21, stream22, minDTcond):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.minDTcond = minDTcond
    def calc(self):
        P1 = streams.at[self.stream11, "P"]
        H11 = streams.at[self.stream11, "H"]
        G1 = streams.at[self.stream11, "G"]
        H12 = prop.p_q(P1, 0, fluid)["H"]
        P2 = streams.at[self.stream21, "P"]
        H21 = streams.at[self.stream21, "H"]
        G2 = streams.at[self.stream21, "G"]
        step = (H11 - H12) / s

        def G2sved(G2):
            t1 = np.zeros(s + 1)
            t2 = np.zeros(s + 1)
            Q = np.zeros(s + 1)
            h11 = H11
            h21 = H21
            for i in range(s + 1):
                t1[i] = prop.h_p(h11, P1, fluid)["T"]
                if i < s:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(s + 1):
                t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
                if i < s:
                    h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT = t1 - t2
            minDT = round(min(DT), 5)
            delta = minDT - self.minDTcond
            return delta

        G2 = sved(G2sved, [0, 9999], svedtol)
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, fluid)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        T12 = t1[s]
        T22 = t2[0]
        H12 = h11
        H22 = h21
        DT = t1 - t2
        minDT = min(DT)
        S12 = prop.h_p(H12, P1, fluid)["S"]
        S22 = prop.h_p(H22, P2, fluidcond)["S"]
        Q12 = prop.h_p(H12, P1, fluid)["Q"]
        Q22 = prop.h_p(H22, P2, fluidcond)["Q"]
        streams.loc[self.stream12, "T":"G"] = [T12, P1, H12, S12, Q12, G1]
        streams.loc[self.stream21, "G"] = G2
        streams.loc[self.stream22, "T":"G"] = [T22, P2, H22, S22, Q22, G2]
        blocks.loc["CONDENSER", "Q"] = Q[s]

    def TQ(self):
        H11 = streams.at[self.stream11, "H"]
        H21 = streams.at[self.stream21, "H"]
        H12 = streams.at[self.stream12, "H"]
        P1 = streams.at[self.stream12, "P"]
        P2 = streams.at[self.stream22, "P"]
        G1 = streams.at[self.stream11, "G"]
        G2 = streams.at[self.stream21, "G"]
        step = (H11 - H12) / s
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, fluid)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        minDT = round(min(DT), 1)
        plt.title("CONDENSER: minDT={}°C".format(round(minDT, 1)))
        plt.xlabel("Q, кВт")
        plt.ylabel("T, °C")
        plt.grid(True)
        return plt.plot(Q, t2, Q, t1)


class cooler:
    def __init__(self, stream11, stream12, stream21, stream22, minDTcond, T1out, fluid):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.minDTcond = minDTcond
        self.T1out = T1out
        self.fluid = fluid
    def calc(self):
        P1 = streams.at[self.stream11, "P"]
        H11 = streams.at[self.stream11, "H"]
        G1 = streams.at[self.stream11, "G"]
        T12 = self.T1out
        H12 = prop.t_p(T12, P1, fluid)["H"]
        P2 = streams.at[self.stream21, "P"]
        H21 = streams.at[self.stream21, "H"]
        G2 = streams.at[self.stream21, "G"]
        step = (H11 - H12) / s

        def G2sved(G2):
            t1 = np.zeros(s + 1)
            t2 = np.zeros(s + 1)
            Q = np.zeros(s + 1)
            h11 = H11
            h21 = H21
            for i in range(s + 1):
                t1[i] = prop.h_p(h11, P1, fluid)["T"]
                if i < s:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(s + 1):
                t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
                if i < s:
                    h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT = t1 - t2
            minDT = round(min(DT), 5)
            delta = minDT - self.minDTcond
            return delta

        G2 = sved(G2sved, [0, 9999], svedtol)
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, fluid)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        T12 = t1[s]
        T22 = t2[0]
        H12 = h11
        H22 = h21
        DT = t1 - t2
        minDT = min(DT)
        S12 = prop.h_p(H12, P1, fluid)["S"]
        S22 = prop.h_p(H22, P2, fluidcond)["S"]
        Q12 = prop.h_p(H12, P1, fluid)["Q"]
        Q22 = prop.h_p(H22, P2, fluidcond)["Q"]
        streams.loc[self.stream12, "T":"G"] = [T12, P1, H12, S12, Q12, G1]
        streams.loc[self.stream21, "G"] = G2
        streams.loc[self.stream22, "T":"G"] = [T22, P2, H22, S22, Q22, G2]
        blocks.loc["CONDENSER", "Q"] = Q[s]

    def TQ(self):
        H11 = streams.at[self.stream11, "H"]
        H21 = streams.at[self.stream21, "H"]
        H12 = streams.at[self.stream12, "H"]
        P1 = streams.at[self.stream12, "P"]
        P2 = streams.at[self.stream22, "P"]
        G1 = streams.at[self.stream11, "G"]
        G2 = streams.at[self.stream21, "G"]
        step = (H11 - H12) / s
        t1 = np.zeros(s + 1)
        t2 = np.zeros(s + 1)
        Q = np.zeros(s + 1)
        h11 = H11
        h21 = H21
        for i in range(s + 1):
            t1[i] = prop.h_p(h11, P1, fluid)["T"]
            if i < s:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(s + 1):
            t2[s - i] = prop.h_p(h21, P2, fluidcond)["T"]
            if i < s:
                h22 = h21 + (Q[s - i] - Q[s - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        minDT = round(min(DT), 1)
        plt.title("COOLER: minDT={}°C".format(round(minDT, 1)))
        plt.xlabel("Q, кВт")
        plt.ylabel("T, °C")
        plt.grid(True)
        return plt.plot(Q, t2, Q, t1)
