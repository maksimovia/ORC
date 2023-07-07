from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QLineEdit
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap

from sqlite import open_db, close_db, write_stream, read_block
import modules
import prop
from threading import Thread


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("пргм")
        self.setFixedSize(QSize(800, 700))

        self.start_button = QPushButton("го")
        self.start_button.clicked.connect(self.start)
        self.img = QLabel()
        self.img.setPixmap(QPixmap('qt/SIMPLE.png'))

        self.kpd_output = QLabel(f'КПД цикла равен 0%')

        # Параметры нагревающей среды:
        self.t_gas_input = QLineEdit()
        self.t_gas_input.setText('183.6')
        self.p_gas_input = QLineEdit()
        self.p_gas_input.setText('0.1')
        self.g_gas_input = QLineEdit()
        self.g_gas_input.setText('509')
        self.x_gas_input = QLineEdit()
        self.x_gas_input.setText('N2;0.78;O2;0.1;CO2;0.02;H2O;0.1')
        self.t_gas_out_input = QLineEdit()
        self.t_gas_out_input.setText('80')

        # Параметры охлаждающей среды:
        self.t_cool_input = QLineEdit()
        self.t_cool_input.setText('15')
        self.p_cool_input = QLineEdit()
        self.p_cool_input.setText('0.15')
        self.g_cool_input = QLineEdit()
        self.g_cool_input.setText('1000')
        self.x_cool_input = QLineEdit()
        self.x_cool_input.setText('WATER')

        # Параметры ОЦР:
        self.t_cond_input = QLineEdit()
        self.t_cond_input.setText('30')
        self.fluid_input = QLineEdit()
        self.fluid_input.setText('R236EA')
        self.p_pump_input = QLineEdit()
        self.p_pump_input.setText('3.3')
        self.kpd_pump_input = QLineEdit()
        self.kpd_pump_input.setText('0.85')
        self.kpd_turb_input = QLineEdit()
        self.kpd_turb_input.setText('0.85')
        self.dt_heat_input = QLineEdit()
        self.dt_heat_input.setText('10')
        self.dt_cond_input = QLineEdit()
        self.dt_cond_input.setText('5')
        self.cycle_tolerance_input = QLineEdit()
        self.cycle_tolerance_input.setText('10**-4')

        layout = QGridLayout()

        layout.addWidget(self.t_gas_input, 1, 0)
        layout.addWidget(self.p_gas_input, 2, 0)
        layout.addWidget(self.g_gas_input, 3, 0)
        layout.addWidget(self.x_gas_input, 4, 0)
        layout.addWidget(self.t_gas_out_input, 5, 0)

        layout.addWidget(self.t_cool_input, 1, 1)
        layout.addWidget(self.p_cool_input, 2, 1)
        layout.addWidget(self.g_cool_input, 3, 1)
        layout.addWidget(self.x_cool_input, 4, 1)

        layout.addWidget(self.t_cond_input, 1, 2)
        layout.addWidget(self.fluid_input, 2, 2)
        layout.addWidget(self.p_pump_input, 3, 2)
        layout.addWidget(self.kpd_pump_input, 4, 2)
        layout.addWidget(self.kpd_turb_input, 5, 2)
        layout.addWidget(self.dt_heat_input, 6, 2)
        layout.addWidget(self.dt_cond_input, 7, 2)
        layout.addWidget(self.cycle_tolerance_input, 8, 2)

        layout.addWidget(self.img, 0, 0)
        layout.addWidget(self.start_button, 3, 3)
        layout.addWidget(self.kpd_output, 1, 3)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start(self):
        print('def start')
        self.calc_thread()

    def calc_thread(self):
        new_thread = Thread(target=self.calc)
        new_thread.start()

    def calc(self):
        print('run calc')

        open_db()

        # Параметры нагревающей среды:
        X_gas = self.x_gas_input.text()
        T_gas = float(self.t_gas_input.text())
        P_gas = float(self.p_gas_input.text())
        G_gas = float(self.g_gas_input.text())
        T_gas_out = float(self.t_gas_out_input.text())
        # Параметры охлаждающей среды:
        X_cool = self.x_cool_input.text()
        T_cool = float(self.t_cool_input.text())
        P_cool = float(self.p_cool_input.text())
        G_cool = float(self.g_cool_input.text())
        # Параметры ОЦР:
        X_cond = self.fluid_input.text()
        T_cond = float(self.t_cond_input.text())
        p_pump = float(self.p_pump_input.text())
        kpd_pump = float(self.kpd_pump_input.text())
        kpd_turb = float(self.kpd_turb_input.text())
        dt_heat = float(self.dt_heat_input.text())
        dt_cond = float(self.dt_cond_input.text())
        cycle_tolerance = float(eval(self.cycle_tolerance_input.text()))
        write_stream('IN-HEAT', T_gas, P_gas, prop.t_p(T_gas, P_gas, X_gas)["H"], prop.t_p(T_gas, P_gas, X_gas)["S"],
                     prop.t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
        write_stream('IN-COND', T_cool, P_cool, prop.t_p(T_cool, P_cool, X_cool)["H"],
                     prop.t_p(T_cool, P_cool, X_cool)["S"],
                     prop.t_p(T_cool, P_cool, X_cool)["Q"], G_cool, X_cool)

        write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
                     prop.t_q(T_cond, 0, X_cond)["S"], 0, 1000, X_cond)

        for i in range(9999):
            pump = modules.PUMP('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
            self.img.setPixmap(QPixmap('qt/SIMPLE-CALC-PUMP.png'))
            pump.calc()

            heater = modules.HEATER('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', dt_heat, T_gas_out)
            self.img.setPixmap(QPixmap('qt/SIMPLE-CALC-HEAT.png'))
            heater.calc()

            turbine = modules.TURBINE('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turb)
            self.img.setPixmap(QPixmap('qt/SIMPLE-CALC-TURB.png'))
            turbine.calc()

            condenser = modules.CONDENSER('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond)
            self.img.setPixmap(QPixmap('qt/SIMPLE-CALC-COND.png'))
            condenser.calc()

            balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
                       read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
            if abs(balance) < cycle_tolerance:
                break

        KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
        self.kpd_output.setText(f"КПД равен {round(KPD,5)}%")
        close_db()


##############################


app = QApplication([])
window = Window()
window.show()
app.exec()