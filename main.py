from sqlite import open_db, close_db, read_stream, write_stream, read_block, write_block
import modules

import prop
open_db()

# Параметры нагревающей среды:
# Параметры охлаждающей среды:
# Параметры ОЦР:




# Входной поток газа
G_gas = 509
T_gas = 183.6
P_gas = 0.1
T_gas_out = 80
X_gas = "N2;0.78;O2;0.1;CO2;0.02;H2O;0.1"
write_stream('IN-HEAT',T_gas,P_gas,prop.t_p(T_gas,P_gas,X_gas)["H"],prop.t_p(T_gas,P_gas,X_gas)["S"],prop.t_p(T_gas,P_gas,X_gas)["Q"],G_gas,X_gas)


# Насос
p_pump = 3.4
kpd_pump = 0.9

# Турбина
kpd_turbine = 0.9

# Поток охлаждающий
T_cool = 15
P_cool = 0.2
X_cool = 'WATER'
G_cool = 10000
write_stream('IN-COND',T_cool,P_cool,prop.t_p(T_cool,P_cool,X_cool)["H"],prop.t_p(T_cool,P_cool,X_cool)["S"],prop.t_p(T_cool,P_cool,X_cool)["Q"],G_cool,X_cool)

# Поток после конденсатора
T_cond = 30
X_cond = 'R236ea'
P_cond = prop.t_q(T_cond,0,X_cond)["P"]
G_cond = 300
write_stream('COND-PUMP',T_cond,prop.t_q(T_cond,0,X_cond)["P"],prop.t_q(T_cond,0,X_cond)["H"],prop.t_q(T_cond,0,X_cond)["S"],0,G_cond,X_cond)


for i in range(4):
    pump = modules.PUMP('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
    pump.calc()
    heater = modules.HEATER('IN-HEAT','HEAT-OUT','PUMP-HEAT','HEAT-TURB', 5, 80)
    heater.calc()
    turbine = modules.TURBINE('HEAT-TURB','TURB-COND', P_cond, kpd_turbine)
    turbine.calc()
    condenser = modules.CONDENSER('TURB-COND','COND-PUMP','IN-COND','COND-OUT', 5)
    condenser.calc()

    balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"]-read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
    print(balance)
    if abs(balance) < 10**-6:
        break

KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
print("KPD:", round(KPD * 100, 5))

close_db()
