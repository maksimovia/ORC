import modules
import prop
import pandas as pd
# import matplotlib.pyplot as plt

# Таблицы с потоками и блоками:
streams = pd.read_excel("data.xlsx", sheet_name="SIMPLE-streams", index_col=0)
blocks = pd.read_excel("data.xlsx", sheet_name="SIMPLE-blocks", index_col=0)

# Параметры нагревающей среды:
streams.loc["IN-HEAT", "G"] = 509
gas = "N2;0.78;O2;0.1;CO2;0.02;H2O;0.1"
Tin = 183.6
Pgas = 0.1
Tout = 80

# Параметры охлаждающей среды:
streams.loc["IN-COND", "G"] = 1000
fluidcond = "WATER"
Tfluidcond = 15
Pfluidcond = 0.15

# Параметры ОЦР:
streams.loc["COND-PUMP", "G"] = 1000
fluid = "R236ea"
KPDpump = 0.85
KPDturb = 0.85
DTheat = 10
DTcond = 5
Pcond = prop.t_q(30, 0, fluid)["P"]
Ppump = 3.3

# Внесение входных данных в таблицу:
streams.loc["IN-HEAT", "T":"Q"] = list(prop.t_p(Tin, Pgas, gas).values())
streams.loc["IN-COND", "T":"Q"] = list(prop.t_p(Tfluidcond, Pfluidcond, fluidcond).values())
streams.loc["COND-PUMP", "T":"Q"] = list(prop.p_q(Pcond, 0, fluid).values())

# Итеративный расчет для сведения баланса:
modules.init(streams, blocks, fluid, gas, fluidcond)
for i in range(9999):

    PUMP = modules.pump('COND-PUMP', "PUMP-HEAT", Ppump, KPDpump)
    PUMP.calc()
    HEATER = modules.heater("IN-HEAT", "HEAT-OUT", "PUMP-HEAT", "HEAT-TURB", Tout, DTheat)
    HEATER.calc()
    TURBINE = modules.turbine("HEAT-TURB", "TURB-COND", Pcond, KPDturb)
    TURBINE.calc()
    CONDENSER = modules.condenser("TURB-COND", "COND-PUMP", "IN-COND", "COND-OUT", DTcond)
    CONDENSER.calc()

    Qbalance = (blocks.loc["HEATER", "Q"] + blocks.loc["PUMP", "N"] - blocks.loc["CONDENSER", "Q"] -
                blocks.loc["TURBINE", "N"]) / blocks.loc["HEATER", "Q"]
    if abs(Qbalance) < 10 ** -4:
        break

KPD = (blocks.loc["TURBINE", "N"] - blocks.loc["PUMP", "N"]) / blocks.loc["HEATER", "Q"]
print("KPD:", round(KPD * 100, 5))

#
print(streams)

#
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.figure(figsize=(16, 4))
# plt.subplot(1, 2, 1)
# HEATER.TQ("IN-HEAT", "HEAT-OUT", "PUMP-HEAT", "HEAT-TURB")
# plt.subplot(1, 2, 2)
# CONDENSER.TQ("TURB-COND", "COND-PUMP", "IN-COND", "COND-OUT")
# plt.show()
