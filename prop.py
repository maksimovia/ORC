from CoolProp.CoolProp import PropsSI as prop
import json, CoolProp.CoolProp as CP
CP.set_config_string(CP.ALTERNATIVE_REFPROP_PATH, 'C:/Program Files (x86)/REFPROP')

def t_p(T,P,fluid):
    T = T
    H = prop('H','T', T+273.15, 'P', P*10**6, fluid)/1000
    P = P
    Q = prop('Q','T', T+273.15, 'P', P*10**6, fluid)
    S = prop('S','T', T+273.15, 'P', P*10**6, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def h_p(H,P,fluid):
    T = prop('T','H', H*1000, 'P', P*10**6, fluid)-273.15
    H = H
    P = P
    Q = prop('Q','H', H*1000, 'P', P*10**6, fluid)-273.15
    S = prop('S','H', H*1000, 'P', P*10**6, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def p_q(P,Q,fluid):
    T = prop('T','Q', Q, 'P', P*10**6, fluid)-273.15
    H = prop('H','Q', Q, 'P', P*10**6, fluid)/1000
    P = P
    Q = Q
    S = prop('H','Q', Q, 'P', P*10**6, fluid)/1000
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}

def p_s(P,S,fluid):
    T = prop('T','S', S*1000, 'P', P*10**6, fluid)-273.15
    H = prop('H','S', S*1000, 'P', P*10**6, fluid)/1000
    P = P
    Q = prop('Q','S', S*1000, 'P', P*10**6, fluid)
    S = S
    return {'T':T,'H':H,'P':P,'Q':Q,'S':S}
