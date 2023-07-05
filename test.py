import numpy as np


def G2_root(G2):
    t1 = np.zeros(h_steps + 1)
    t2 = np.zeros(h_steps + 1)
    Q = np.zeros(h_steps + 1)
    h11 = H11
    h21 = H21
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
