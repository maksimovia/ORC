from modules import init, pump, regen, heater, turbine, condenser
import pandas as pd
import prop

# Таблицы с потоками и блоками:
streams = pd.read_excel("data.xlsx", sheet_name="REGEN-streams", index_col=0)
blocks = pd.read_excel("data.xlsx", sheet_name="REGEN-blocks", index_col=0)

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
DTreg = 5
DTcond = 5
Pcond = prop.t_q(30, 0, fluid)["P"]
Ppump = 3.3
dPreg1 = 0
dPreg2 = 0

# Внесение входных данных в таблицу:
streams.loc["IN-HEAT", "T":"Q"] = list(prop.t_p(Tin, Pgas, gas).values())
streams.loc["IN-COND", "T":"Q"] = list(prop.t_p(Tfluidcond, Pfluidcond, fluidcond).values())
streams.loc["COND-PUMP", "T":"Q"] = list(prop.p_q(Pcond, 0, fluid).values())

# Для графика
from jupyterplot import ProgressPlot

pp = ProgressPlot()
balance = []

# Итеративный расчет для сведения баланса:
init(streams, blocks, fluid, gas, fluidcond)
for i in range(9999):

    pump.calc("COND-PUMP", "PUMP-REG", Ppump, KPDpump)
    regen.calc("TURB-REG", "REG-COND", "PUMP-REG", "REG-HEAT", DTreg, dPreg1, dPreg2)
    heater.calc("IN-HEAT", "HEAT-OUT", "REG-HEAT", "HEAT-TURB", Tout, DTheat)
    turbine.calc("HEAT-TURB", "TURB-REG", Pcond + dPreg1, KPDturb)
    regen.calc("TURB-REG", "REG-COND", "PUMP-REG", "REG-HEAT", DTreg, dPreg1, dPreg2)
    condenser.calc("REG-COND", "COND-PUMP", "IN-COND", "COND-OUT", DTcond)

    Qbalance = (blocks.loc["HEATER", "Q"] + blocks.loc["PUMP", "N"] - blocks.loc["CONDENSER", "Q"] - blocks.loc[
        "TURBINE", "N"]) / blocks.loc["HEATER", "Q"]
    balance.append(Qbalance)
    pp.update(Qbalance)
    if abs(Qbalance) < 10 ** -4:
        break

pp.finalize()

KPD = (blocks.loc["TURBINE", "N"] - blocks.loc["PUMP", "N"]) / blocks.loc["HEATER", "Q"]
print("KPD:", round(KPD * 100, 5))

#
print(streams)

#
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.figure(figsize=(16, 4))
plt.subplot(1, 3, 1)
heater.TQ("IN-HEAT", "HEAT-OUT", "REG-HEAT", "HEAT-TURB")
plt.subplot(1, 3, 2)
regen.TQ("TURB-REG", "REG-COND", "PUMP-REG", "REG-HEAT")
plt.subplot(1, 3, 3)
condenser.TQ("REG-COND","COND-PUMP", "IN-COND", "COND-OUT")
plt.show()