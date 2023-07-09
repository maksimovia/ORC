from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from sqlite import *
from modules import *
import prop
from threading import Thread
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("пргм")
        self.setFixedSize(800, 600)
        self.CentralWidget = QWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        # ###############tab-1############### #
        self.img_input = QLabel(parent=self.tab1)
        self.img_input.setPixmap(QPixmap('qt/ORC-SIMPLE.png'))
        self.img_input.setGeometry(25, 25, 525, 525)

        self.t_gas_input = QLineEdit(parent=self.tab1)
        self.t_gas_input.setGeometry(50, 50, 50, 20)
        self.t_gas_input.setText('183.6')
        self.t_gas_txt = QLabel('T=', parent=self.tab1)
        self.t_gas_txt.setGeometry(30, 50, 20, 20)

        self.p_gas_input = QLineEdit(parent=self.tab1)
        self.p_gas_input.setGeometry(50, 75, 50, 20)
        self.p_gas_input.setText('0.1')
        self.p_gas_txt = QLabel('P=', parent=self.tab1)
        self.p_gas_txt.setGeometry(30, 75, 20, 20)

        self.g_gas_input = QLineEdit(parent=self.tab1)
        self.g_gas_input.setGeometry(50, 100, 50, 20)
        self.g_gas_input.setText('509')
        self.g_gas_txt = QLabel('G=', parent=self.tab1)
        self.g_gas_txt.setGeometry(30, 100, 20, 20)

        self.t_gas_out_input = QLineEdit(parent=self.tab1)
        self.t_gas_out_input.setGeometry(50, 300, 50, 20)
        self.t_gas_out_input.setText('80')
        self.t_gas_out_input_txt = QLabel('T=', parent=self.tab1)
        self.t_gas_out_input_txt.setGeometry(30, 300, 20, 20)

        self.t_cool_input = QLineEdit(parent=self.tab1)
        self.t_cool_input.setGeometry(470, 275, 50, 20)
        self.t_cool_input.setText('15')
        self.t_cool_input_txt = QLabel('T=', parent=self.tab1)
        self.t_cool_input_txt.setGeometry(450, 275, 20, 20)

        self.p_cool_input = QLineEdit(parent=self.tab1)
        self.p_cool_input.setGeometry(470, 300, 50, 20)
        self.p_cool_input.setText('0.15')
        self.p_cool_input_txt = QLabel('P=', parent=self.tab1)
        self.p_cool_input_txt.setGeometry(450, 300, 20, 20)

        self.t_cond_input = QLineEdit(parent=self.tab1)
        self.t_cond_input.setGeometry(345, 285, 50, 20)
        self.t_cond_input.setText('30')
        self.t_cond_input_txt = QLabel('Tконд=', parent=self.tab1)
        self.t_cond_input_txt.setGeometry(300, 285, 40, 20)

        self.p_pump_input = QLineEdit(parent=self.tab1)
        self.p_pump_input.setGeometry(205, 340, 50, 20)
        self.p_pump_input.setText('3.3')
        self.p_pump_input_txt = QLabel('P1=', parent=self.tab1)
        self.p_pump_input_txt.setGeometry(180, 340, 20, 20)

        self.kpd_pump_input = QLineEdit(parent=self.tab1)
        self.kpd_pump_input.setGeometry(205, 365, 50, 20)
        self.kpd_pump_input.setText('0.85')
        self.kpd_pump_input_txt = QLabel('η=', parent=self.tab1)
        self.kpd_pump_input_txt.setGeometry(180, 365, 20, 20)

        self.kpd_turb_input = QLineEdit(parent=self.tab1)
        self.kpd_turb_input.setGeometry(360, 110, 50, 20)
        self.kpd_turb_input.setText('0.85')
        self.kpd_turb_input_txt = QLabel('η=', parent=self.tab1)
        self.kpd_turb_input_txt.setGeometry(335, 110, 20, 20)

        self.dt_heat_input = QLineEdit(parent=self.tab1)
        self.dt_heat_input.setGeometry(180, 180, 50, 20)
        self.dt_heat_input.setText('10')
        self.dt_heat_input_txt = QLabel('ΔT=', parent=self.tab1)
        self.dt_heat_input_txt.setGeometry(155, 180, 20, 20)

        self.dt_cond_input = QLineEdit(parent=self.tab1)
        self.dt_cond_input.setGeometry(345, 310, 50, 20)
        self.dt_cond_input.setText('5')
        self.dt_cond_input_txt = QLabel('ΔT=', parent=self.tab1)
        self.dt_cond_input_txt.setGeometry(300, 310, 40, 20)

        self.x_gas_input = QLineEdit(parent=self.tab1)
        self.x_gas_input.setGeometry(600, 200, 180, 25)
        self.x_gas_input.setText('N2;0.78;O2;0.1;CO2;0.02;H2O;0.1')
        self.x_gas_input_txt = QLabel('Состав нагревающего потока:', parent=self.tab1)
        self.x_gas_input_txt.setGeometry(600, 175, 180, 25)

        self.x_cool_input = QLineEdit(parent=self.tab1)
        self.x_cool_input.setGeometry(600, 250, 180, 25)
        self.x_cool_input.setText('WATER')
        self.x_cool_input_txt = QLabel('Охлаждающий поток:', parent=self.tab1)
        self.x_cool_input_txt.setGeometry(600, 225, 180, 25)

        self.fluid_input = QLineEdit(parent=self.tab1)
        self.fluid_input.setGeometry(600, 300, 180, 25)
        self.fluid_input.setText('R236EA')
        self.fluid_input_txt = QLabel('Теплоноситель:', parent=self.tab1)
        self.fluid_input_txt.setGeometry(600, 275, 180, 25)

        self.cycle_tolerance_input = QLineEdit(parent=self.tab1)
        self.cycle_tolerance_input.setGeometry(600, 350, 180, 25)
        self.cycle_tolerance_input.setText('10**-4')
        self.cycle_tolerance_input_txt = QLabel('Сходимость по балансу:', parent=self.tab1)
        self.cycle_tolerance_input_txt.setGeometry(600, 325, 180, 25)

        self.start_button = QPushButton("го", parent=self.tab1)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(600, 425, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab1)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(600, 475, 180, 25)
        # ###############tab-1-end############### #

        # ###############tab-2############### #
        self.img_calc = QLabel(parent=self.tab2)
        self.img_calc.setPixmap(QPixmap('qt/ORC-SIMPLE.png'))
        self.img_calc.setGeometry(25, 25, 525, 525)

        self.img_calcer = QLabel(parent=self.tab2)
        self.img_calcer.setPixmap(QPixmap('qt/calcer.png'))
        self.img_calcer.setGeometry(0, 0, 0, 0)

        self.graph_balance = FigureCanvasQTAgg(plt.Figure())
        self.balance_ax = self.graph_balance.figure.subplots()
        self.graph_balance.draw()
        self.graph_balance_cont = QWidget(parent=self.tab2)
        graph_balance_lay = QHBoxLayout()
        graph_balance_lay.addWidget(self.graph_balance)
        self.graph_balance_cont.setLayout(graph_balance_lay)
        self.graph_balance_cont.setGeometry(530, 0, 270, 250)

        self.kpd_output = QLabel('КПД равен _%', parent=self.tab2)
        self.kpd_output.setGeometry(600, 400, 180, 25)

        self.start_button = QPushButton("го", parent=self.tab2)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(600, 425, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab2)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(600, 475, 180, 25)
        # ###############tab-2-end############### #


        # ###############tab-3############### #
        self.table_blocks = QTableWidget(parent=self.tab3)
        self.table_blocks.setGeometry(30, 30, 297, 200)
        self.table_blocks.setColumnCount(2)
        self.table_blocks.setRowCount(4)
        self.table_blocks.setHorizontalHeaderLabels(["Блок", "Q"])
        self.block_list = ['HEATER', 'TURBINE', 'CONDENSER', 'PUMP']
        for i in range(2):
            self.table_blocks.setColumnWidth(i, 140)
        for i in range(4):
            self.table_blocks.setItem(i, 0, QTableWidgetItem(self.block_list[i]))
        # ###############tab-3-end############### #


        # ###############tab-4############### #
        self.table_streams = QTableWidget(parent=self.tab4)
        self.table_streams.setGeometry(30, 30, 737, 500)
        self.table_streams.setColumnCount(8)
        self.table_streams.setRowCount(8)
        self.table_streams.setHorizontalHeaderLabels(["Поток", "T", "P", "H", "S", "Q", "G", "X"])
        self.streams_list = ['HEAT-TURB', 'TURB-COND', 'COND-PUMP', 'PUMP-HEAT',
                        'IN-HEAT', 'HEAT-OUT', 'IN-COND', 'COND-OUT']
        for i in range(8):
            self.table_streams.setColumnWidth(i, 90)
            self.table_streams.setItem(i, 0, QTableWidgetItem(self.streams_list[i]))
        # ###############tab-4-end############### #

        # ###############central-tab############### #
        self.tab_menu = QTabWidget(parent=self.CentralWidget)
        self.tab_menu.setGeometry(0, 0, 800, 600)
        self.tab_menu.addTab(self.tab1, "Ввод данных")
        self.tab_menu.addTab(self.tab2, "Расчёт")
        self.tab_menu.addTab(self.tab3, "Блоки")
        self.tab_menu.addTab(self.tab4, "Потоки")
        self.setCentralWidget(self.CentralWidget)

        # ###############status-bar############### #
        self.status_img = QLabel('_')
        self.status_txt = QLabel('Ожидание запуска')
        self.status_time = QLabel('')
        statusbar = QStatusBar()
        statusbar.addWidget(self.status_img)
        statusbar.addWidget(self.status_txt)
        statusbar.addWidget(self.status_time)
        self.setStatusBar(statusbar)

    def start(self):
        self.tab_menu.setCurrentIndex(1)
        self.balance_ax.clear()
        self.balance_cumm = [0]
        self.balance_ax.plot(self.balance_cumm)
        self.graph_balance.draw()

        print('start')
        self.status_img.setText('...')
        self.status_txt.setText('Запущен расчёт.')
        self.kpd_output.setText(f"КПД равен _%")

        self.time_flag = True
        self.time_start = datetime.datetime.now()

        self.calc_Flag = True
        self.thread_calc = Thread(target=self.calc)
        self.thread_calc.start()

        self.thread_timer = Thread(target=self.timer)
        self.thread_timer.start()

    def stop(self):
        print('stop')
        self.calc_Flag = False
        self.status_img.setText('...')
        self.status_txt.setText('Остановка расчёта.')
        if self.thread_calc.is_alive() is False:
            self.status_txt.setText('Расчёт остановлен.')

    def timer(self):
        while self.time_flag is True:
            self.status_time.setText(f'Время расчёта: {(datetime.datetime.now() - self.time_start).seconds} с')
            time.sleep(0.5)

    def calc(self):
        print('start calc')
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
                     prop.t_p(T_cool, P_cool, X_cool)["Q"], 1000, X_cool)

        write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
                     prop.t_q(T_cond, 0, X_cond)["S"], 0, 1000, X_cond)

        for i in range(9999):
            if self.calc_Flag is False:
                self.time_flag = False
                self.status_img.setText('-')
                self.status_txt.setText('Расчёт остановлен.')
                break

            pump = Pump('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
            self.img_calcer.setGeometry(165, 370, 100, 100)
            pump.calc()

            heater = Heat('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', dt_heat, T_gas_out)
            self.img_calcer.setGeometry(68, 162, 100, 100)
            heater.calc()

            turbine = Turb('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turb)
            self.img_calcer.setGeometry(315, 145, 100, 100)
            turbine.calc()

            condenser = Cond('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond)
            self.img_calcer.setGeometry(360, 310, 100, 100)
            condenser.calc()

            balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
                       read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
            self.balance_cumm.append(balance)
            self.balance_ax.clear()
            self.balance_ax.plot(self.balance_cumm)
            self.graph_balance.draw()
            self.graph_balance.flush_events()

            if abs(balance) < cycle_tolerance:
                break

        KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
        self.kpd_output.setText(f"КПД равен {round(KPD,5)}%")

        for i in range(8):
            stream = list(read_stream(str(self.streams_list[i])).values())
            for j in range(6):
                value = str(round(stream[j], abs(int(np.log10(cycle_tolerance)))))
                self.table_streams.setItem(i, j+1, QTableWidgetItem(value))
            self.table_streams.setItem(i, 7, QTableWidgetItem(str(stream[6])))
        for i in range(4):
            value = round(list(read_block(str(self.block_list[i])).values())[0], abs(int(np.log10(cycle_tolerance))))
            self.table_blocks.setItem(i, 1, QTableWidgetItem(str(value)))

        close_db()
        self.time_flag = False
        if self.calc_Flag is True:
            self.status_img.setText('+')
            self.status_txt.setText('Расчёт завершён успешно.')
        print('end calc')
##############################


app = QApplication([])
window = Window()
window.show()
app.exec()
