import numpy as np
import pandas as pd
import prop
from modules import PUMP, HEAT, TURB, COND, REG
from multiprocessing import Process, active_children
from time import sleep

global data
data = open("res.txt", "a")

KPDpump = 0.85
KPDturb = 0.85
KPDm = 0.99
KPDe = 0.99

dQreg = 0.99

dTheat = 10
dPheat = 0.95
dQheat = 0.996

hsteps = 30
Tcond = 30

Pgas = 0.1013
Ggas = 502
Xgas = ("N2;0.756199238;"
        "O2;0.139736654;"
        "H2O;0.063113472;"
        "CO2;0.031905376;"
        "AR;0.00904526;")
Tgas_out = 80

def cycle_calc(Tgas, Xorc, Ppump, dTreg, dPreg):
    streams_list = ["IN-HEAT", "HEAT-OUT", "PUMP-REG", "REG-HEAT", "HEAT-TURB", "TURB-REG", "REG-COND", "COND-PUMP", ]
    block_list = ["PUMP", "TURB", "HEAT", "COND", "REG", ]
    streams = pd.DataFrame(index=streams_list, columns=["T", "P", "H", "S", "Q", "G", "X"])
    blocks = pd.DataFrame(index=block_list, columns=["N", "Q", "dT", "T1i", "T2i", "Qi"])

    streams.loc['IN-HEAT'] = [Tgas, Pgas, prop.t_p(Tgas, Pgas, Xgas)['H'], prop.t_p(Tgas, Pgas, Xgas)['S'], prop.t_p(Tgas, Pgas, Xgas)['Q'], Ggas, Xgas]
    streams.loc['COND-PUMP'] = [Tcond, prop.t_q(Tcond, 0, Xorc)["P"], prop.t_q(Tcond, 0, Xorc)["H"], prop.t_q(Tcond, 0, Xorc)["S"], 0, 1000, Xorc]

    for i in range(100):
        PUMP('COND-PUMP', 'PUMP-REG', Ppump, KPDpump, streams, blocks).calc()
        if i == 0:
            streams.loc['REG-HEAT'] = streams.loc['PUMP-REG']
        else:
            REG('TURB-REG', 'REG-COND', 'PUMP-REG', 'REG-HEAT', dTreg, hsteps, dPreg, dQreg, Tgas_out, dTheat, streams, blocks).calc()
        HEAT('IN-HEAT', 'HEAT-OUT', 'REG-HEAT', 'HEAT-TURB', Tgas_out, dTheat, hsteps, dPheat, dQheat, streams, blocks).calc()
        TURB('HEAT-TURB', 'TURB-REG', prop.t_q(Tcond, 0, Xorc)["P"]+dPreg, KPDturb, streams, blocks).calc()
        REG('TURB-REG', 'REG-COND', 'PUMP-REG', 'REG-HEAT', dTreg, hsteps, dPreg, dQreg, Tgas_out, dTheat, streams, blocks).calc()
        COND('REG-COND', 'COND-PUMP', streams, blocks).calc()
        balance = abs(blocks.loc['HEAT', "Q"]*dQheat + blocks.loc['PUMP', "N"] - blocks.loc['COND', "Q"] - blocks.loc['TURB', "N"] - (1-dQreg)*blocks.loc['REG', 'Q']) / blocks.loc['HEAT', "Q"]
        if balance < 10**-5:
            break
    Nnet = blocks.loc['TURB', "N"]*KPDm*KPDe - blocks.loc['PUMP', "N"]/KPDm/KPDe
    KPDnet = Nnet / blocks.loc['HEAT', "Q"]
    print(Tgas, Xorc, round(Ppump,5), round(Nnet,5), round(KPDnet,5), round(blocks.loc['HEAT', "dT"],5), streams.loc['HEAT-TURB', "Q"], streams.loc['TURB-REG', "Q"], balance, dPreg, dTreg, (streams.loc['TURB-REG','H']-streams.loc['REG-COND','H'])/(streams.loc['TURB-REG','H']-prop.t_p(streams.loc['PUMP-REG','T'],streams.loc['REG-COND','P'],streams.loc['TURB-REG','X'])['H']))
    data.write( '\n'+ str(Tgas)
               +'\t'+ str(Xorc)
               +'\t'+ str(Ppump)
               +'\t'+ str(Nnet)
               +'\t'+ str(KPDnet)
               +'\t'+ str(blocks.loc['REG', "dT"])
               +'\t'+ str(blocks.loc['HEAT', "dT"])
               +'\t'+ str(streams.loc['HEAT-TURB', "Q"])
               +'\t'+ str(streams.loc['TURB-REG', "Q"])
               +'\t'+ str(balance)
               +'\t'+ str(dPreg)
               +'\t'+ str(dTreg)
               +'\t'+ str((streams.loc['TURB-REG', 'H'] - streams.loc['REG-COND', 'H']) / (streams.loc['TURB-REG', 'H'] -prop.t_p(streams.loc['PUMP-REG', 'T'], streams.loc['REG-COND', 'P'],streams.loc['TURB-REG', 'X'])['H'])))

Tgas = 200
Xorc = "R236ea"
Ppump = 6
dTreg = 5
dPreg = 10 * 10**-3

if __name__ == '__main__':
    for dPreg in np.linspace(0, 200 * 10**-3, 40):
        for dTreg in np.linspace(0.1, 40, 40):
            calculating = Process(target=cycle_calc, args=(Tgas, Xorc, Ppump, dTreg, dPreg))
            calculating.start()
            while len(active_children()) > 59:
                sleep(2)
    data.close()
