import prop
import numpy as np
        
class pump:
    def calc(stream1,stream2,Pout,KPDpump,fluid,streams,blocks):
        P1 = streams.at[stream1,"P"]
        H1 = streams.at[stream1,"H"]
        S1 = streams.at[stream1,"S"]
        G = streams.at[stream1,"G"]
        H2t = prop.p_s(Pout,S1,fluid)["H"]
        H2 = H1 + (H2t-H1)/KPDpump
        T2 = prop.h_p(H2,Pout,fluid)["T"]
        S2 = prop.h_p(H2,Pout,fluid)["S"]
        Q2 = prop.h_p(H2,Pout,fluid)["Q"]
        streams.loc[stream2, "T":"Q"] = [T2, Pout, H2, S2, G,Q2]
        N = G*(H2-H1)
        blocks.loc['PUMP', 'N'] = N
        
class regen:
    def calc(stream11,stream12,stream21,stream22,dTmin,fluid,streams,blocks):
        T11 = streams.at[stream11,"T"]
        H11 = streams.at[stream11,"H"]
        T21 = streams.at[stream21,"T"]
        H21 = streams.at[stream21,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        S21 = streams.at[stream21,"S"]
        S11 = streams.at[stream11,"S"]
        if np.isnan(T11):
            T22 = T21
            T12 = T11
            H12 = H11
            H22 = H21
            S22 = S21
            S12 = S11
            Q = 0
            Q1 = streams.at[stream11,"Q"]
            Q2 = streams.at[stream21,"Q"]
        else:
            T12 = T21+dTmin
            H12 = prop.t_p(T12,P1,fluid)["H"]
            Q = G1*(H11-H12)
            H22 = H21 + (Q/G2) 
            T22 = prop.h_p(H22,P2,fluid)["T"]
            S22 = prop.h_p(H22,P2,fluid)["S"]
            S12 = prop.h_p(H12,P1,fluid)["S"]
            Q1 = prop.h_p(H12,P1,fluid)["Q"]
            Q2 = prop.h_p(H22,P2,fluid)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q1]
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q2]
        blocks.loc['REGENERATOR','Q'] = Q
        
class heater:
    def calc(stream11,stream12,stream21,stream22,dTmin_heat,Toutmin,fluid1,fluid2,streams,blocks):
        T11 = streams.at[stream11,"T"]
        H11 = streams.at[stream11,"H"]
        T21 = streams.at[stream21,"T"]
        H21 = streams.at[stream21,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        T22 = T11-dTmin_heat
        H22 = prop.t_p(T22,P2,fluid2)["H"]
        Q = G2*(H22-H21)
        H12 = H11 - (Q/G1)
        T12 = prop.h_p(H12,P1,fluid1)["T"]
        if T12 < Toutmin:
            T12 = Toutmin
            H12 = prop.t_p(T12,P1,fluid1)["H"]
            Q = G1*(H12-H11)
            H22 = H21 - (Q/G2)
            T22 = prop.h_p(H22,P2,fluid2)["T"]
        S22 = prop.h_p(H22,P2,fluid2)["S"]
        S12 = prop.h_p(H12,P1,fluid1)["S"]
        Q1 = prop.h_p(H12,P1,fluid1)["Q"]
        Q2 = prop.h_p(H22,P2,fluid2)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q1]
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q2]
        blocks.loc['HEATER','Q'] = Q
        
class heater80:
    def calc(stream11,stream12,stream21,stream22,dTmin_heat,Toutmin,fluid1,fluid2,streams,blocks):
        T11 = streams.at[stream11,"T"]
        H11 = streams.at[stream11,"H"]
        T21 = streams.at[stream21,"T"]
        H21 = streams.at[stream21,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        T12 = Toutmin
        H12 = prop.t_p(T12,P1,fluid1)["H"]
        Q = G1*(H11-H12)
        T22 = T11-dTmin_heat
        H22 = prop.t_p(T22,P2,fluid2)["H"]
        G2 = Q/(H22-H21)
        S22 = prop.h_p(H22,P2,fluid2)["S"]
        S12 = prop.h_p(H12,P1,fluid1)["S"]
        Q1 = prop.h_p(H12,P1,fluid1)["Q"]
        Q2 = prop.h_p(H22,P2,fluid2)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q1]
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q2]
        blocks.loc['HEATER','Q'] = Q

class turbine:
    def calc(stream1,stream2,Pout,KPDturb,fluid,streams,blocks):
        P1 = streams.at[stream1,"P"]
        H1 = streams.at[stream1,"H"]
        S1 = streams.at[stream1,"S"]
        G = streams.at[stream1,"G"]
        H2t = prop.p_s(Pout,S1,fluid)["H"]
        H2 = H1 - (H1 - H2t)*KPDturb
        T2 = prop.h_p(H2,Pout,fluid)["T"]
        S2 = prop.h_p(H2,Pout,fluid)["S"]
        Q2 = prop.h_p(H2,Pout,fluid)["Q"]
        streams.loc[stream2, "T":"Q"] = [T2, Pout, H2, S2, G,Q2]
        N = G*(H1-H2)
        blocks.loc['TURBINE', 'N'] = N

class condenser:
    def calc(stream1,stream2, fluid,streams,blocks):
        Pcond = streams.at[stream1,"P"]
        H1 = streams.at[stream1,"H"]
        G = streams.at[stream1,"G"]
        H2 = prop.p_q(Pcond,0,fluid)["H"]
        T2 = prop.p_q(Pcond,0,fluid)["T"]
        S2 = prop.p_q(Pcond,0,fluid)["S"]
        Q = G*(H1-H2)
        streams.loc[stream2, "T":"Q"] = [T2, Pcond, H2, S2, G,0]
        blocks.loc['CONDENSER', 'Q'] = Q