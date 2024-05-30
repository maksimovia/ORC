import prop
from sqlite import read_stream, write_stream, write_block
import numpy as np
from scipy import optimize


def root(func, a, root_tol):
    x = float(optimize.root(func, a, tol=root_tol).x)
    return x


class Heat:
    def __init__(self, stream11, stream12, stream21, stream22, dt, t_out, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dT = dt
        self.T_out = t_out
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        T11 = read_stream(self.stream11)['T']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        T12 = self.T_out
        H12 = prop.t_p(T12, P11, fluid1)["H"]
        S12 = prop.t_p(T12, P11, fluid1)["S"]
        Q12 = prop.t_p(T12, P11, fluid1)["Q"]
        step = (H11 - H12) / self.h_steps

        T21 = read_stream(self.stream21)['T']

        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT[:-1])
            return self.dT - min_dt
        G2 = root(G2_func, G1 * (H11 - H12) / (prop.t_p(T11, P21, fluid2)['H'] - H21), self.root_tolerance)

        # if G2 > G1*(H11-H12)/(prop.p_q(P21, 1, fluid2)['H']-H21):
        #     print('!!!')
        #     G2 = G1*(H11-H12)/(prop.p_q(P21, 1, fluid2)['H']-H21)



        if read_stream('HEAT-TURB')["G"] != None:         ###!!!
            G2 = (G2 + read_stream('HEAT-TURB')["G"])/2   ###!!!

        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22

        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        H22 = h22
        dQ = 0.996
        H22 = H21 + dQ*(H22-H21)
        dP = 0.95
        P21 = P21*dP
        T22 = prop.h_p(H22, P21, fluid2)["T"]
        S22 = prop.h_p(H22, P21, fluid2)["S"]
        Q22 = prop.h_p(H22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('HEATER', Q[-1], min_dt)
        pass

    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2


class Pump:
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
        write_block('PUMP', N, 0)
        pass


class Turb:
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
        write_block('TURBINE', N, 0)
        pass


class Cond:
    def __init__(self, stream11, stream12, stream21, stream22, dt, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P1 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        T11 = read_stream(self.stream11)['T']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        H12 = prop.p_q(P1, 0, fluid1)["H"]
        P2 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        step = (H11 - H12) / self.h_steps

        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = prop.h_p(h11, P1, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt
        G2 = root(G2_func, G1*(H11-H12)/(prop.t_p(prop.p_q(P1,0,fluid1)["T"], P2, fluid2)['H']-H21), self.root_tolerance)
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P1, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        H22 = h22
        S22 = prop.h_p(H22, P2, fluid2)["S"]
        Q22 = prop.h_p(H22, P2, fluid2)["Q"]
        T12 = prop.h_p(H12, P1, fluid1)["T"]
        S12 = prop.h_p(H12, P1, fluid1)["S"]
        T21 = prop.h_p(H21, P2, fluid2)["T"]
        S21 = prop.h_p(H21, P2, fluid2)["S"]
        Q21 = prop.h_p(H21, P2, fluid2)["Q"]
        write_stream(self.stream12, T12, P1, H12, S12, 0, G1, fluid1)
        write_stream(self.stream21, T21, P2, H21, S21, Q21, G2, fluid2)
        write_stream(self.stream22, T22, P2, H22, S22, Q22, G2, fluid2)
        write_block('CONDENSER', Q[-1], min_dt)
        pass

    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2


class Regen:
    def __init__(self, stream11, stream12, stream21, stream22, dt, dtheat, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.dtheat = dtheat
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        T11 = read_stream(self.stream11)['T']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        T21 = read_stream(self.stream21)['T']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']
        fluid2 = read_stream(self.stream21)['X']

        def T22_func(T22):
            T22 = max(T21, min(T22, read_stream("HEAT-OUT")["T"] - self.dtheat))
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            step = (H22 - H21) / self.h_steps
            for i in range(self.h_steps + 1):
                t2[i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + step
                    dQ = G2 * (h22 - h21)
                    h21 = h22
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                    h11 = h12
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt

        if T11 - self.dt < T21:
            T22 = T21
            T12 = T11
            Q = np.zeros(self.h_steps + 1)
            Q[-1] = 0
            min_dt = min(T12-T21, T11-T22)
            H12 = H11
            S12 = prop.h_p(H11, P11, fluid1)["S"]
            Q12 = prop.h_p(H11, P11, fluid1)["Q"]
            H22 = H21
            S22 = prop.h_p(H21, P21, fluid2)["S"]
            Q22 = prop.h_p(H21, P21, fluid2)["Q"]
        else:
            T22 = root(T22_func, (T11+T21)/2, self.root_tolerance)
            if T22 > (read_stream("HEAT-OUT")["T"] - self.dtheat-1):  ###!!!
                T22 = (read_stream("HEAT-OUT")["T"] - self.dtheat-1)  ###!!!
            else:
                T22 = T22
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            step = (H22 - H21) / self.h_steps
            for i in range(self.h_steps + 1):
                t2[i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + step
                    dQ = G2 * (h22 - h21)
                    h21 = h22
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                    h11 = h12
            DT = t1 - t2
            min_dt = min(DT)
            T22 = t2[-1]
            T12 = t1[0]

            H12 = h12
            dQ = 0.99
            dP1 = 0.95
            dP2 = 0.98
            P11 = P11*dP1
            T12 = prop.h_p(H12, P11, fluid1)["T"]
            S12 = prop.h_p(H12, P11, fluid1)["S"]
            Q12 = prop.h_p(H12, P11, fluid1)["Q"]
            P21 = P21*dP2
            H22 = H21 + dQ*(H22-H21)
            T22 = prop.h_p(H22, P21, fluid2)["T"]
            S22 = prop.h_p(H22, P21, fluid2)["S"]
            Q22 = prop.h_p(H22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('REGEN', Q[-1], min_dt)
        pass

    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2
