import matplotlib.pyplot as pt
import numpy as n
import math as m
import json, CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI as p
from scipy.optimize import root
import math


class Platetube:
    def calc(G1,G2,P1,P2,T11,T12,T21,T22,Q,fluid):
        
        R236ea = fluid

        Dvnes=0.01
        DeltaTube=0.001
        Dvnut=Dvnes-2*DeltaTube
        step=2.5*Dvnes        
        Hchan=0.25*Dvnes
        Deltaplate = 0.0005
        lambdaw = 20
        row=7900
        etta=1

        T1av = (T11+T12)/2
        T2av = (T21+T22)/2

        ro1 = p('D','T', T1av+273.15, 'P', P1, R236ea)
        ro2 = p('D','T', T2av+273.15, 'P', P2, R236ea)
        nu1 = p('V','T', T1av+273.15, 'P', P1, R236ea)/ro1
        nu2 = p('V','T', T2av+273.15, 'P', P2, R236ea)/ro2
        lambda1 = p('L','T', T1av+273.15, 'P', P1, R236ea)
        lambda2 = p('L','T', T2av+273.15, 'P', P2, R236ea)
        Pr1 = p('PRANDTL','T', T1av+273.15, 'P', P1, R236ea)
        Pr2 = p('PRANDTL','T', T2av+273.15, 'P', P2, R236ea)

        dTmax = T11 - T22
        dTmin = T12 - T21
        dT = (dTmax - dTmin) / (n.log(dTmax / dTmin))



        ############################################################################################
        Z=8
        w1= 30
        w2 = 3.2
        ############################################################################################

        Re2 = w2*Dvnut/nu2
        Nu2 = 0.021*Re2**0.8*Pr2**0.43
        def func(x):
            delta = 10**-5
            left = x
            right = 1/(2*n.log10((2.51/(Re2*(x)**(1/2)))+(delta/3.7)))**2
            return left-right
        sol = root(func, 0.01)
        f2=float(sol.x)
        alpha2 = Nu2*lambda2/Dvnut
        Re1 = w1*Dvnes/nu1


        Nu1 = 0.195*Re1**0.65*Pr1**(-1/3)


        f1 = 1.7*Re1**(-0.5)
        alpha1 = Nu1*lambda1/Dvnes
        KF = Q/dT
        
        F_vneshn = 4*(((2**0.5)*step/2)**2 - math.pi*(Dvnes**2)/4) + 2*Hchan* math.pi*Dvnes
        F_vntr = math.pi*(Dvnes-2*DeltaTube)*2*(Hchan+Deltaplate)
        F_trube = math.pi*Dvnes*2*(Hchan+Deltaplate)
        koef1 = F_vntr/F_vneshn
        koef2 = F_vneshn / F_trube
        def func(x):
            Fvnes=x
            a1 = 1/KF
            a2 = 1/(etta*alpha1*Fvnes)
            a3 = ((1/2)*(n.log(Dvnes/Dvnut))*(Dvnes/(lambdaw*(Fvnes/koef2))))
            a4 = 1/(alpha2*Fvnes*koef1)
            return a1-a2-a3-a4
        sol = root(func, 0.002)
        x=sol.x
        Fvnes=float(x)
        Nsumm = m.ceil(Fvnes/(F_vneshn)/Z)
        S2 = G2/(ro2*w2)

        S1 = G1/(ro1*w1)
        NH =  m.ceil(Nsumm*(n.pi*Dvnut**2)/(S2*4))
        NW =  m.ceil(S1/(4*NH*Hchan*(step-(Dvnut+2*DeltaTube))))
        NL =  m.ceil(4*S2/(NW*n.pi*Dvnut**2))
        S1_y = 4*NW*NH*Hchan*(step-(Dvnut+2*DeltaTube))
        S2_y = NW*NL*n.pi*Dvnut**2/4
        w1_y = G1/(ro1*S1_y)
        w2_y = G2/(ro2*S2_y)
        Nsumm_y = NH*NW*NL
        Fvnes_y =Nsumm_y*F_vneshn*Z

        W=round(NW*step, 4)
        H=round(NH*((Hchan+Deltaplate)*2), 4)
        L=round(NL*step*Z, 4)
        dP1_y = f1*Z*L/Dvnes*ro1*w1_y**2/2
        dP11_y = f1*Z*L/Dvnes*ro1*w1_y**2/2

        dP2_y = f2*Z*H/Dvnut*ro2*w2_y**2/2

        Ntryb = NW*NL*Z
        Nplate = NH*2*Z
        Ltryb = 2* (Hchan+Deltaplate)*NH
        Wplate = NW*step
        Lplate = NL*step

        V = n.pi*(Dvnes**2-Dvnut**2)/4*Ltryb*Ntryb + Lplate*Wplate*Deltaplate*Nplate
        # Плотность стали 
        ro_stal = 7832 # кг/м3

        

        Massa =   ro_stal * V 
        money = Massa*100
        return money