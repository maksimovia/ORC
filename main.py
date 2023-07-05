from sqlite import open_db, close_db, read_stream, write_stream
import prop
open_db()
close_db()
open_db()


G_gas = 509
T_gas = 183.6
P_gas = 0.1
T_gas_out = 80
X_gas = "N2;0.78;O2;0.1;CO2;0.02;H2O;0.1"


# Заполнение строки IN-HEAT
write_stream('IN-HEAT',T_gas,P_gas,prop.t_p(T_gas,P_gas,X_gas)["H"],prop.t_p(T_gas,P_gas,X_gas)["S"],prop.t_p(T_gas,P_gas,X_gas)["Q"],G_gas,X_gas)
write_stream('PUMP-HEAT',50,0.25,prop.t_p(50,0.25,'R236ea')["H"],1,1,300,'R236ea')



import modules1
heater = modules1.HEATER('IN-HEAT','HEAT-OUT','PUMP-HEAT','HEAT-TURB', 5, 80)
heater.calc()



close_db()
