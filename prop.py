from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
RP = REFPROPFunctionLibrary('C:/Program Files (x86)/REFPROP')

iUnits = 21
iMass = 2
iFlag = 0
RP.PREOSdll(0)


def t_p(t, p, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TP', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, t + 273.15, p * 10 ** 6, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def h_p(h, p, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'HP', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, h * 1000, p * 10 ** 6, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def p_q(p, q, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PQ', 'T;P;H;S', iUnits, iMass, iFlag, p * 10 ** 6, q, comp)
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def t_q(t, q, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TQ', 'T;P;H;S', iUnits, iMass, iFlag, t + 273.15, q, comp)
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def p_s(p, s, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, p * 10 ** 6, s * 1000, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def t_s(t, s, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, t + 273.15, s * 1000, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}
