from CoolProp.CoolProp import PropsSI as prop
import json, CoolProp.CoolProp as CP
CP.set_config_string(CP.ALTERNATIVE_REFPROP_PATH, 'C:/Program Files (x86)/REFPROP')

def t_p(T,P,fluid):
    T = T
    H = prop('H','T', T+273.15, 'P', P*10**6, fluid)/1000
    P = P
    Q = prop('Q','T', T+273.15, 'P', P*10**6, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    S = prop('S','T', T+273.15, 'P', P*10**6, fluid)/1000
    ro = prop('D','T', T+273.15, 'P', P*10**6, fluid)
    nu = prop('V','T', T+273.15, 'P', P*10**6, fluid)/ro
    Pr = prop('PRANDTL','T', T+273.15, 'P', P*10**6, fluid)
    lamda = prop('L','T', T+273.15, 'P', P*10**6, fluid)
    
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S,'ro':ro,'nu':nu,'Pr':Pr,'lamda':lamda}

def h_p(H,P,fluid):
    T = prop('T','H', H*1000, 'P', P*10**6, fluid)-273.15
    H = H
    P = P
    Q = prop('Q','H', H*1000, 'P', P*10**6, fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    S = prop('S','H', H*1000, 'P', P*10**6, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def p_q(P,Q,fluid):
    T = prop('T', 'P', P*10**6,'Q', Q, fluid)-273.15
    H = prop('H', 'P', P*10**6,'Q', Q, fluid)/1000
    P = P
    Q = Q
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    S = prop('S', 'P', P*10**6,'Q', Q, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def t_q(T,Q,fluid):
    T = T
    H = prop('H', 'T', T+273.15,'Q', Q, fluid)/1000
    P = prop('P', 'T', T+273.15,'Q', Q, fluid)/(10**6)
    Q = Q
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    S = prop('S', 'P', P*10**6,'Q', Q, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def p_s(P,S,fluid):
    T = prop('T','P', P*10**6,'S', S*1000,  fluid)-273.15
    H = prop('H','P', P*10**6,'S', S*1000,  fluid)/1000
    P = P
    Q = prop('Q','P', P*10**6,'S', S*1000,  fluid)
    if Q>=1:
        Q=1
    elif Q<=0:
        Q=0
    S = S
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}
