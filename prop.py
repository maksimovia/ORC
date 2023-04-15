from CoolProp.CoolProp import PropsSI
import json, CoolProp.CoolProp as CP
CP.set_config_string(CP.ALTERNATIVE_REFPROP_PATH, 'C:/Program Files (x86)/REFPROP')

def t_p(T,P,fluid):
    H = PropsSI('H','T', T+273.15, 'P', P*10**6, fluid)/1000
    S = PropsSI('S','T', T+273.15, 'P', P*10**6, fluid)/1000
    Q = PropsSI('Q','T', T+273.15, 'P', P*10**6, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}

def h_p(H,P,fluid):
    T = PropsSI('T', 'H', H*1000, 'P', P*10**6, fluid)-273.15
    S = PropsSI('S', 'H', H*1000, 'P', P*10**6, fluid)/1000
    Q = PropsSI('Q', 'H', H*1000, 'P', P*10**6, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}

def p_q(P,Q,fluid):
    T = PropsSI('T', 'P', P*10**6,'Q', Q, fluid)-273.15
    H = PropsSI('H', 'P', P*10**6,'Q', Q, fluid)/1000
    S = PropsSI('S', 'P', P*10**6,'Q', Q, fluid)/1000
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}

def t_q(T,Q,fluid):
    P = PropsSI('P', 'T', T+273.15, 'Q', Q, fluid)/(10**6)
    H = PropsSI('H', 'T', T+273.15, 'Q', Q, fluid)/1000
    S = PropsSI('S', 'P', P*10**6,  'Q', Q, fluid)/1000
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}

def p_s(P,S,fluid):
    T = PropsSI('T', 'P', P*10**6, 'S', S*1000, fluid)-273.15
    H = PropsSI('H', 'P', P*10**6, 'S', S*1000, fluid)/1000
    Q = PropsSI('Q', 'P', P*10**6, 'S', S*1000, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}

def t_s(T,S,fluid):
    P = PropsSI('P', 'T', T+273.15, 'S', S*1000, fluid)/(10**6)
    H = PropsSI('H', 'T', T+273.15, 'S', S*1000, fluid)/1000
    Q = PropsSI('Q', 'T', T+273.15, 'S', S*1000, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    return {'T':T, 'P':P, 'H':H, 'S':S, 'Q':Q}