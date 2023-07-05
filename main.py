from sqlite import open_db, close_db, write_stream, read_block
import modules

import prop

open_db()

# Параметры нагревающей среды:
X_gas = "N2;0.78;O2;0.1;CO2;0.02;H2O;0.1"
T_gas = 183.6
P_gas = 0.1
G_gas = 509
T_gas_out = 80

# Параметры охлаждающей среды:
X_cool = 'WATER'
T_cool = 15
P_cool = 0.2
G_cool = 10000

# Параметры ОЦР:
X_cond = 'R236EA'
T_cond = 30
p_pump = 3.4
kpd_pump = 0.9
kpd_turbine = 0.9

write_stream('IN-HEAT', T_gas, P_gas, prop.t_p(T_gas, P_gas, X_gas)["H"], prop.t_p(T_gas, P_gas, X_gas)["S"],
             prop.t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
write_stream('IN-COND', T_cool, P_cool, prop.t_p(T_cool, P_cool, X_cool)["H"], prop.t_p(T_cool, P_cool, X_cool)["S"],
             prop.t_p(T_cool, P_cool, X_cool)["Q"], G_cool, X_cool)
write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
             prop.t_q(T_cond, 0, X_cond)["S"], 0, 100, X_cond)

for i in range(4):
    pump = modules.PUMP('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
    pump.calc()
    heater = modules.HEATER('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', 5, 80)
    heater.calc()
    turbine = modules.TURBINE('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turbine)
    turbine.calc()
    condenser = modules.CONDENSER('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', 5)
    condenser.calc()

    balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
               read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
    print(balance)
    if abs(balance) < 10 ** -6:
        break

KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
print("KPD:", round(KPD * 100, 5))

close_db()
