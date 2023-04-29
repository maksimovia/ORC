from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
RP = REFPROPFunctionLibrary('C:/Program Files (x86)/REFPROP')

iUnits = 21
iMass = 2
iFlag = 0

def t_p(T,P,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TP', 'T;P;H;S', iUnits, iMass, iFlag, T+273.15, P*10**6, comp)
    if res.q<=0:
        Q=0
    elif res.q>=1:
        Q=1
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}

def h_p(H,P,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'HP', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, H*1000, P*10**6, comp)
    if res.q<=0:
        Q=0
    elif res.q>=1:
        Q=1
    else:
        Q = res.Output[4]
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}

def p_q(P,Q,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PQ', 'T;P;H;S', iUnits, iMass, iFlag, P*10**6, Q, comp)
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}

def t_q(T,Q,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TQ', 'T;P;H;S', iUnits, iMass, iFlag, T+273.15, Q, comp)
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}

def p_s(P,S,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, P*10**6, S*1000, comp)
    if res.q<=0:
        Q=0
    elif res.q>=1:
        Q=1
    else:
        Q = res.Output[4]
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}

def t_s(T,S,fluid):
    comp=[]
    for i in range(1, len(fluid.split(";")),2): comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, T+273.15, S*1000, comp)
    if res.q<=0:
        Q=0
    elif res.q>=1:
        Q=1
    else:
        Q = res.Output[4]
    return {'T':res.Output[0]-273.15, 'P':res.Output[1]/10**6, 'H':res.Output[2]/1000, 'S':res.Output[3]/1000, 'Q':Q}
