from sqlite import open_db, close_db, write_stream, read_stream, read_block
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
P_cool = 0.5
G_cool = 10000

# Параметры ОЦР:
X_cond = 'R236EA'
T_cond = 30
p_pump = 3.3
kpd_pump = 0.9
kpd_turbine = 0.9
dt_heat = 10
dt_cond = 5
dt_regen = 5
cycle_tolerance = 10**-6

write_stream('IN-HEAT', T_gas, P_gas, prop.t_p(T_gas, P_gas, X_gas)["H"], prop.t_p(T_gas, P_gas, X_gas)["S"],
             prop.t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
write_stream('IN-COND', T_cool, P_cool, prop.t_p(T_cool, P_cool, X_cool)["H"], prop.t_p(T_cool, P_cool, X_cool)["S"],
             prop.t_p(T_cool, P_cool, X_cool)["Q"], G_cool, X_cool)
write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
             prop.t_q(T_cond, 0, X_cond)["S"], 0, 100, X_cond)

for i in range(9999):
    pump = modules.PUMP('COND-PUMP', 'PUMP-REGEN', p_pump, kpd_pump)
    pump.calc()
    if i == 0:
        write_stream('REGEN-HEAT',read_stream('PUMP-REGEN')["T"],read_stream('PUMP-REGEN')["P"],
                     read_stream('PUMP-REGEN')["H"],read_stream('PUMP-REGEN')["S"],
                     read_stream('PUMP-REGEN')["Q"],read_stream('PUMP-REGEN')["G"],read_stream('PUMP-REGEN')["X"])
    else:
        regen = modules.REGEN('TURB-REGEN', 'REGEN-COND', 'PUMP-REGEN', 'REGEN-HEAT', dt_regen)
        regen.calc()
    heater = modules.HEATER('IN-HEAT', 'HEAT-OUT', 'REGEN-HEAT', 'HEAT-TURB', dt_heat, T_gas_out)
    heater.calc()
    turbine = modules.TURBINE('HEAT-TURB', 'TURB-REGEN', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turbine)
    turbine.calc()
    regen = modules.REGEN('TURB-REGEN', 'REGEN-COND', 'PUMP-REGEN', 'REGEN-HEAT', dt_regen)
    regen.calc()
    condenser = modules.CONDENSER('REGEN-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond)
    condenser.calc()

    balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
               read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
    print(balance)
    if abs(balance) < cycle_tolerance:
        break

KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
# print("KPD:", round(KPD * 100, 5))

close_db()
