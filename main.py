from sqlite import open_db, close_db, read_stream, write_stream
import prop
open_db()
close_db()
open_db()

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

# Поток после конденсатора
T_cond = 25
P_cond = 0.24
X_cond = 'R236ea'
G_cond = 300
write_stream('COND-PUMP',T_cond,P_cond,prop.t_p(T_cond,P_cond,X_cond)["H"],prop.t_p(T_cond,P_cond,X_cond)["S"],prop.t_p(T_cond,P_cond,X_cond)["Q"],G_cond,X_cond)

import modules1
pump = modules1.PUMP('COND-PUMP','PUMP-HEAT', p_pump, kpd_pump)
pump.calc()

heater = modules1.HEATER('IN-HEAT','HEAT-OUT','PUMP-HEAT','HEAT-TURB', 5, 80)
heater.calc()



close_db()
