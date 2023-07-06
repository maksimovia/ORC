from sqlite import open_db, close_db, write_stream, read_block, read_stream
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
P_cool = 0.15
G_cool = 1000

# Параметры ОЦР:
X_cond = 'R236EA'
T_cond = 30
p_pump = 3.3
kpd_pump = 0.85
kpd_turbine = 0.85
dt_heat = 10
dt_cond = 5
cycle_tolerance = 10**-4

write_stream('IN-HEAT', T_gas, P_gas, prop.t_p(T_gas, P_gas, X_gas)["H"], prop.t_p(T_gas, P_gas, X_gas)["S"],
             prop.t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
write_stream('IN-COND', T_cool, P_cool, prop.t_p(T_cool, P_cool, X_cool)["H"], prop.t_p(T_cool, P_cool, X_cool)["S"],
             prop.t_p(T_cool, P_cool, X_cool)["Q"], G_cool, X_cool)
write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
             prop.t_q(T_cond, 0, X_cond)["S"], 0, 1000, X_cond)

for i in range(9999):
    pump = modules.PUMP('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
    pump.calc()
    heater = modules.HEATER('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', dt_heat, T_gas_out)
    heater.calc()
    turbine = modules.TURBINE('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turbine)
    turbine.calc()
    condenser = modules.CONDENSER('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond)
    condenser.calc()

    balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
               read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
    print(balance)
    if abs(balance) < cycle_tolerance:
        break

KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
print("KPD:", round(KPD * 100, 10))

print()
print('IN-HEAT', read_stream('IN-HEAT'))
print('HEAT-OUT', read_stream('HEAT-OUT'))
print()
print('COND-PUMP', read_stream('COND-PUMP'))
print('PUMP-HEAT', read_stream('PUMP-HEAT'))
print('HEAT-TURB', read_stream('HEAT-TURB'))
print('TURB-COND', read_stream('TURB-COND'))
print('COND-PUMP', read_stream('COND-PUMP'))
print()
print('IN-COND', read_stream('IN-COND'))
print('COND-OUT', read_stream('COND-OUT'))

close_db()
