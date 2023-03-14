import prop
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root


plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12

class heater:
    def calc(stream11,stream12,stream21,stream22,Toutmin,minDTheater,fluid1,fluid2,streams,blocks):
        H11 = streams.at[stream11,"H"]
        H21 = streams.at[stream21,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        T12 = Toutmin
        H12 = prop.t_p(T12,P1,fluid1)["H"]
        s = 50
        step = (H11-H12)/s
        
        def G2sved(G2):
            t1  = np.zeros(s+1)
            t2  = np.zeros(s+1)
            Q   = np.zeros(s+1)
            h11 = H11
            h21 = H21
            for i in range(s+1):
                t1[i] = prop.h_p(h11,P1,fluid1)["T"]                
                if i < s:
                    h12 = h11-step
                    dQ = G1*(h11-h12)
                    h11 = h12
                    Q[i+1] = Q[i]+dQ
            for i in range(s+1):
                t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
                if i < s:
                    h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT=t1-t2
            minDT=round(min(DT),5)
            return minDT-minDTheater
        sol = root(G2sved, G2)
        G2 = float(sol.x)
        
        t1  = np.zeros(s+1)
        t2  = np.zeros(s+1)
        Q   = np.zeros(s+1)
        h11 = H11
        h21 = H21
        for i in range(s+1):
            t1[i] = prop.h_p(h11,P1,fluid1)["T"]
            if i < s:
                h12 = h11-step
                dQ = G1*(h11-h12)
                h11 = h12
                Q[i+1] = Q[i]+dQ
        for i in range(s+1):
            t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
            if i < s:
                h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                h21 = h22
        T12 = t1[s]
        T22 = t2[0]
        H12 = h11
        H22 = h21
        DT=t1-t2
        minDT=round(min(DT),5)
        S12 = prop.h_p(H12,P1,fluid1)["S"]
        S22 = prop.h_p(H22,P2,fluid2)["S"]
        Q12 = prop.h_p(H12,P1,fluid1)["Q"]
        Q22 = prop.h_p(H22,P2,fluid2)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q12]
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q22]
        blocks.loc['HEATER','Q'] = Q[s]
    def TQ(stream11,stream12,stream21,stream22,fluid1,fluid2,streams):
        H11 = streams.at[stream11,"H"]
        H21 = streams.at[stream21,"H"]
        H12 = streams.at[stream12,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        s=50
        step = (H11-H12)/s
        t1  = np.zeros(s+1)
        t2  = np.zeros(s+1)
        Q   = np.zeros(s+1)
        h11 = H11
        h21 = H21
        for i in range(s+1):
            t1[i] = prop.h_p(h11,P1,fluid1)["T"]
            if i < s:
                h12 = h11-step
                dQ = G1*(h11-h12)
                h11 = h12
                Q[i+1] = Q[i]+dQ
        for i in range(s+1):
            t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
            if i < s:
                h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                h21 = h22
        DT=t1-t2
        minDT=round(min(DT),5)
        plt.title('HEATER: minDT={}°C'.format(round(minDT,2)))
        plt.xlabel('Q, кВт')
        plt.ylabel('T, °C')
        plt.grid(True)
        return plt.plot(Q,t2,Q,t1)

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
        H11 = streams.at[stream11,"H"]
        H21 = streams.at[stream21,"H"]
        T11 = streams.at[stream11,"T"]
        T21 = streams.at[stream21,"T"]
        S11 = streams.at[stream11,"S"]
        S21 = streams.at[stream21,"S"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        s = 50
        t1   = np.zeros(s+1)
        t2   = np.zeros(s+1)
        Q    = np.zeros(s+1)
        if np.isnan(H11):
            T22 = T21
            T12 = T11
            H12 = H11
            H22 = H21
            S22 = S21
            S12 = S11
            Q[s] = 0
            Q12 = streams.at[stream11,"Q"]
            Q22 = streams.at[stream21,"Q"]
        else:
            T12 = T21+dTmin
            H12 = prop.t_p(T12,P1,fluid)["H"]
            step = (H11-H12)/s
            h11 = H11
            h21 = H21
            for i in range(s+1):
                t1[i] = prop.h_p(h11,P1,fluid)["T"]
                if i < s:
                    h12 = h11-step
                    dQ = G1*(h11-h12)
                    h11 = h12
                    Q[i+1] = Q[i]+dQ
            for i in range(s+1):
                t2[s-i] = prop.h_p(h21,P2,fluid)["T"]
                if i < s:
                    h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT=t1-t2
            minDT=round(min(DT),5)
            if minDT < dTmin:
                print('!REGEN:minDT<dTmin=',minDT)
            S22 = prop.h_p(H22,P2,fluid)["S"]
            S12 = prop.h_p(H12,P1,fluid)["S"]
            Q12 = prop.h_p(H12,P1,fluid)["Q"]
            Q22 = prop.h_p(H22,P2,fluid)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q12]
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q22]
        blocks.loc['REGENERATOR','Q'] = Q[s]
    def TQ(stream11,stream12,stream21,stream22,fluid,streams):
        H11 = streams.at[stream11,"H"]
        H21 = streams.at[stream21,"H"]
        H12 = streams.at[stream12,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        s=50
        step = (H11-H12)/s
        t1  = np.zeros(s+1)
        t2  = np.zeros(s+1)
        Q   = np.zeros(s+1)
        h11 = H11
        h21 = H21
        for i in range(s+1):
            t1[i] = prop.h_p(h11,P1,fluid)["T"]
            if i < s:
                h12 = h11-step
                dQ = G1*(h11-h12)
                h11 = h12
                Q[i+1] = Q[i]+dQ
        for i in range(s+1):
            t2[s-i] = prop.h_p(h21,P2,fluid)["T"]
            if i < s:
                h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                h21 = h22
        DT=t1-t2
        minDT=round(min(DT),5)
        plt.title('REGEN: minDT={}°C'.format(round(minDT,2)))
        plt.xlabel('Q, кВт')
        plt.ylabel('T, °C')
        plt.grid(True)
        return plt.plot(Q,t2,Q,t1)
    
    
##########################################################
    def cost(stream11,stream12,stream21,stream22,dP0, streams,blocks):
        #исходные данные:
        G1  = streams.at[stream11,"G"]
        G2  = streams.at[stream21,"G"]
        P1  = streams.at[stream11,"P"]
        P2  = streams.at[stream21,"P"]
        T11 = streams.at[stream11,"T"]
        T12 = streams.at[stream12,"T"]
        T21 = streams.at[stream21,"T"]
        T22 = streams.at[stream22,"T"]
        Q   = blocks.at["REGENERATOR","Q"]
        fluid = 'REFPROP::R236ea'
        
        from TO_constr import Platetube
        money = Platetube.calc(G1,G2,P1,P2,T11,T12,T21,T22,Q, dP0, fluid)
        blocks.loc['REGENERATOR','COST'] = money
        return money
##########################################################
        
        

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
    def calc(stream11,stream12,stream21,stream22,minDTcond,fluid2,fluid1,streams,blocks):
        P1  = streams.at[stream11,"P"]
        H11 = streams.at[stream11,"H"]
        G1  = streams.at[stream11,"G"]
        H12 = prop.p_q(P1,0,fluid1)["H"]
        P2  = streams.at[stream21,"P"]
        H21 = streams.at[stream21,"H"]
        G2  = streams.at[stream21,"G"]
        s = 50
        step = (H11-H12)/s
        def G2sved(G2):
            t1  = np.zeros(s+1)
            t2  = np.zeros(s+1)
            Q   = np.zeros(s+1)
            h11 = H11
            h21 = H21
            for i in range(s+1):
                t1[i] = prop.h_p(h11,P1,fluid1)["T"]                
                if i < s:
                    h12 = h11-step
                    dQ = G1*(h11-h12)
                    h11 = h12
                    Q[i+1] = Q[i]+dQ
            for i in range(s+1):
                t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
                if i < s:
                    h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                    h21 = h22
            T12 = t1[s]
            T22 = t2[0]
            H12 = h11
            H22 = h21
            DT=t1-t2
            minDT=round(min(DT),5)
            return minDT-minDTcond
        sol = root(G2sved, G2)
        G2 = float(sol.x)
        t1  = np.zeros(s+1)
        t2  = np.zeros(s+1)
        Q   = np.zeros(s+1)
        h11 = H11
        h21 = H21
        for i in range(s+1):
            t1[i] = prop.h_p(h11,P1,fluid1)["T"]
            if i < s:
                h12 = h11-step
                dQ = G1*(h11-h12)
                h11 = h12
                Q[i+1] = Q[i]+dQ
        for i in range(s+1):
            t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
            if i < s:
                h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                h21 = h22
        T12 = t1[s]
        T22 = t2[0]
        H12 = h11
        H22 = h21
        DT=t1-t2
        minDT=round(min(DT),5)
        S12 = prop.h_p(H12,P1,fluid1)["S"]
        S22 = prop.h_p(H22,P2,fluid2)["S"]
        Q12 = prop.h_p(H12,P1,fluid1)["Q"]
        Q22 = prop.h_p(H22,P2,fluid2)["Q"]
        streams.loc[stream12, "T":"Q"] = [T12,P1,H12,S12,G1,Q12]
        streams.loc[stream21, "G"] = G2
        streams.loc[stream22, "T":"Q"] = [T22,P2,H22,S22,G2,Q22]
        blocks.loc['CONDENSER', 'Q'] = Q[s]
    def TQ(stream11,stream12,stream21,stream22,fluid2,fluid1,streams):
        H11 = streams.at[stream11,"H"]
        H21 = streams.at[stream21,"H"]
        H12 = streams.at[stream12,"H"]
        P1 = streams.at[stream11,"P"]
        P2 = streams.at[stream21,"P"]
        G1 = streams.at[stream11,"G"]
        G2 = streams.at[stream21,"G"]
        s=50
        step = (H11-H12)/s
        t1  = np.zeros(s+1)
        t2  = np.zeros(s+1)
        Q   = np.zeros(s+1)
        h11 = H11
        h21 = H21
        for i in range(s+1):
            t1[i] = prop.h_p(h11,P1,fluid1)["T"]
            if i < s:
                h12 = h11-step
                dQ = G1*(h11-h12)
                h11 = h12
                Q[i+1] = Q[i]+dQ
        for i in range(s+1):
            t2[s-i] = prop.h_p(h21,P2,fluid2)["T"]
            if i < s:
                h22 = h21+(Q[s-i]-Q[s-i-1])/G2
                h21 = h22
        DT=t1-t2
        minDT=round(min(DT),5)
        plt.title('CONDENSER: minDT={}°C'.format(round(minDT,2)))
        plt.xlabel('Q, кВт')
        plt.ylabel('T, °C')
        plt.grid(True)
        return plt.plot(Q,t2,Q,t1)