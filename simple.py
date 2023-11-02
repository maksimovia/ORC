from PySide6.QtCore import QMimeData, Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QWidget, QMainWindow, QPushButton, QHBoxLayout, QTableWidget, \
    QTabWidget, QStatusBar, QTableWidgetItem, QApplication, QListWidget, QMenu
from PySide6.QtGui import QPixmap, QIcon, QCursor, QColor
from sqlite import open_db, close_db, read_block, write_stream, read_stream
from modules import Pump, Heat, Cond, Turb
import numpy as np
import prop
from threading import Thread
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Простой цикл Ренкина")
        self.setWindowIcon(QIcon('src/logo.png'))
        self.setFixedSize(800, 600)
        self.CentralWidget = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()

        # ###############tab-1############### #
        self.img_input = QLabel(parent=self.tab1)
        self.img_input.setPixmap(QPixmap('src/ORC-SIMPLE.png'))
        self.img_input.setGeometry(25, 25, 525, 525)

        self.t_gas_input = QLineEdit(parent=self.tab1)
        self.t_gas_input.setGeometry(50, 60, 50, 20)
        self.t_gas_input.setText('183.6')
        self.t_gas_txt = QLabel('T =', parent=self.tab1)
        self.t_gas_txt.setGeometry(30, 60, 20, 20)

        self.p_gas_input = QLineEdit(parent=self.tab1)
        self.p_gas_input.setGeometry(50, 80, 50, 20)
        self.p_gas_input.setText('0.1')
        self.p_gas_txt = QLabel('P =', parent=self.tab1)
        self.p_gas_txt.setGeometry(30, 80, 20, 20)

        self.g_gas_input = QLineEdit(parent=self.tab1)
        self.g_gas_input.setGeometry(50, 100, 50, 20)
        self.g_gas_input.setText('509')
        self.g_gas_txt = QLabel('G =', parent=self.tab1)
        self.g_gas_txt.setGeometry(30, 100, 20, 20)

        self.t_gas_out_input = QLineEdit(parent=self.tab1)
        self.t_gas_out_input.setGeometry(50, 300, 50, 20)
        self.t_gas_out_input.setText('80')
        self.t_gas_out_input_txt = QLabel('T =', parent=self.tab1)
        self.t_gas_out_input_txt.setGeometry(30, 300, 20, 20)

        self.t_cool_input = QLineEdit(parent=self.tab1)
        self.t_cool_input.setGeometry(470, 280, 50, 20)
        self.t_cool_input.setText('15')
        self.t_cool_input_txt = QLabel('T =', parent=self.tab1)
        self.t_cool_input_txt.setGeometry(450, 280, 20, 20)

        self.p_cool_input = QLineEdit(parent=self.tab1)
        self.p_cool_input.setGeometry(470, 300, 50, 20)
        self.p_cool_input.setText('0.15')
        self.p_cool_input_txt = QLabel('P =', parent=self.tab1)
        self.p_cool_input_txt.setGeometry(450, 300, 20, 20)

        self.t_cond_input = QLineEdit(parent=self.tab1)
        self.t_cond_input.setGeometry(345, 290, 50, 20)
        self.t_cond_input.setText('30')
        self.t_cond_input_txt = QLabel('Tконд =', parent=self.tab1)
        self.t_cond_input_txt.setGeometry(300, 290, 40, 20)

        self.p_pump_input = QLineEdit(parent=self.tab1)
        self.p_pump_input.setGeometry(205, 345, 50, 20)
        self.p_pump_input.setText('3.3')
        self.p_pump_input_txt = QLabel('P =', parent=self.tab1)
        self.p_pump_input_txt.setGeometry(180, 345, 20, 20)

        self.kpd_pump_input = QLineEdit(parent=self.tab1)
        self.kpd_pump_input.setGeometry(205, 365, 50, 20)
        self.kpd_pump_input.setText('0.85')
        self.kpd_pump_input_txt = QLabel('η =', parent=self.tab1)
        self.kpd_pump_input_txt.setGeometry(180, 365, 20, 20)

        self.kpd_pump_m_input = QLineEdit(parent=self.tab1)
        self.kpd_pump_m_input.setGeometry(210, 455, 50, 20)
        self.kpd_pump_m_input.setText('0.99')
        self.kpd_pump_m_input_txt = QLabel('ηм =', parent=self.tab1)
        self.kpd_pump_m_input_txt.setGeometry(180, 455, 25, 20)

        self.kpd_pump_e_input = QLineEdit(parent=self.tab1)
        self.kpd_pump_e_input.setGeometry(210, 475, 50, 20)
        self.kpd_pump_e_input.setText('0.99')
        self.kpd_pump_e_input_txt = QLabel('ηэ =', parent=self.tab1)
        self.kpd_pump_e_input_txt.setGeometry(180, 475, 25, 20)

        self.kpd_turb_input = QLineEdit(parent=self.tab1)
        self.kpd_turb_input.setGeometry(360, 110, 50, 20)
        self.kpd_turb_input.setText('0.85')
        self.kpd_turb_input_txt = QLabel('η =', parent=self.tab1)
        self.kpd_turb_input_txt.setGeometry(335, 110, 20, 20)

        self.kpd_turb_m_input = QLineEdit(parent=self.tab1)
        self.kpd_turb_m_input.setGeometry(360+115, 130, 50, 20)
        self.kpd_turb_m_input.setText('0.99')
        self.kpd_turb_m_input_txt = QLabel('ηм =', parent=self.tab1)
        self.kpd_turb_m_input_txt.setGeometry(335+110, 130, 25, 20)

        self.kpd_turb_e_input = QLineEdit(parent=self.tab1)
        self.kpd_turb_e_input.setGeometry(360+115, 150, 50, 20)
        self.kpd_turb_e_input.setText('0.99')
        self.kpd_turb_e_input_txt = QLabel('ηэ =', parent=self.tab1)
        self.kpd_turb_e_input_txt.setGeometry(335+110, 150, 25, 20)

        self.dt_heat_input = QLineEdit(parent=self.tab1)
        self.dt_heat_input.setGeometry(180, 180, 50, 20)
        self.dt_heat_input.setText('10')
        self.dt_heat_input_txt = QLabel('ΔT =', parent=self.tab1)
        self.dt_heat_input_txt.setGeometry(155, 180, 25, 20)

        self.dt_cond_input = QLineEdit(parent=self.tab1)
        self.dt_cond_input.setGeometry(345, 310, 50, 20)
        self.dt_cond_input.setText('5')
        self.dt_cond_input_txt = QLabel('ΔT =', parent=self.tab1)
        self.dt_cond_input_txt.setGeometry(300, 310, 40, 20)

        self.x_gas_input = QLineEdit(parent=self.tab1)
        self.x_gas_input.setGeometry(600, 100, 180, 25)
        self.x_gas_input.setText('N2;0.7798;O2;0.1226;CO2;0.0305;H2O;0.0605;AR;0.0066')
        self.x_gas_input_txt = QLabel('Состав нагревающего потока:', parent=self.tab1)
        self.x_gas_input_txt.setGeometry(600, 75, 180, 25)

        self.x_cool_input = QLineEdit(parent=self.tab1)
        self.x_cool_input.setGeometry(600, 150, 180, 25)
        self.x_cool_input.setText('WATER')
        self.x_cool_input_txt = QLabel('Охлаждающий поток:', parent=self.tab1)
        self.x_cool_input_txt.setGeometry(600, 125, 180, 25)

        self.fluid_input = QLineEdit(parent=self.tab1)
        self.fluid_input.setGeometry(600, 200, 180, 25)
        self.fluid_input.setText('R236EA')
        self.fluid_input_txt = QLabel('Теплоноситель:', parent=self.tab1)
        self.fluid_input_txt.setGeometry(600, 175, 180, 25)

        self.cycle_tolerance_input = QLineEdit(parent=self.tab1)
        self.cycle_tolerance_input.setGeometry(600, 250, 180, 25)
        self.cycle_tolerance_input.setText('10**-6')
        self.cycle_tolerance_input_txt = QLabel('Сходимость по балансу:', parent=self.tab1)
        self.cycle_tolerance_input_txt.setGeometry(600, 225, 180, 25)

        self.cycle_tolerance_root = QLineEdit(parent=self.tab1)
        self.cycle_tolerance_root.setGeometry(600, 300, 180, 25)
        self.cycle_tolerance_root.setText('10**-6')
        self.cycle_tolerance_root_txt = QLabel('Точность поиска корней:', parent=self.tab1)
        self.cycle_tolerance_root_txt.setGeometry(600, 275, 180, 25)

        self.cycle_step_h = QLineEdit(parent=self.tab1)
        self.cycle_step_h.setGeometry(600, 350, 180, 25)
        self.cycle_step_h.setText('20')
        self.cycle_step_h_txt = QLabel('Шагов в T-Q анализе:', parent=self.tab1)
        self.cycle_step_h_txt.setGeometry(600, 325, 180, 25)

        self.start_button = QPushButton("го", parent=self.tab1)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(600, 425, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab1)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(600, 475, 180, 25)
        # ###############tab-1-end############### #

        # ###############tab-2############### #
        self.img_calc = QLabel(parent=self.tab2)
        self.img_calc.setPixmap(QPixmap('src/ORC-SIMPLE.png'))
        self.img_calc.setGeometry(25, 25, 525, 525)

        # ########### - цифры
        self.calc_IN_HEAT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_IN_HEAT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_IN_HEAT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_IN_HEAT_T.setGeometry(30, 70, 100, 20)
        self.calc_IN_HEAT_P.setGeometry(30, 85, 100, 20)
        self.calc_IN_HEAT_G.setGeometry(30, 100, 100, 20)

        self.calc_HEAT_OUT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HEAT_OUT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HEAT_OUT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HEAT_OUT_T.setGeometry(30, 300, 100, 20)
        self.calc_HEAT_OUT_P.setGeometry(30, 315, 100, 20)
        self.calc_HEAT_OUT_G.setGeometry(30, 330, 100, 20)

        self.calc_HEAT_TURB_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HEAT_TURB_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HEAT_TURB_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HEAT_TURB_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_HEAT_TURB_T.setGeometry(200, 55, 100, 20)
        self.calc_HEAT_TURB_P.setGeometry(200, 70, 100, 20)
        self.calc_HEAT_TURB_G.setGeometry(200, 85, 100, 20)
        self.calc_HEAT_TURB_Q.setGeometry(200, 100, 100, 20)

        self.calc_TURB_COND_T = QLabel('T = ?', parent=self.tab2)
        self.calc_TURB_COND_P = QLabel('P = ?', parent=self.tab2)
        self.calc_TURB_COND_G = QLabel('G = ?', parent=self.tab2)
        self.calc_TURB_COND_Q = QLabel('Q = ?', parent=self.tab2)

        self.calc_TURB_COND_T.setGeometry(340, 250, 100, 20)
        self.calc_TURB_COND_P.setGeometry(340, 265, 100, 20)
        self.calc_TURB_COND_G.setGeometry(340, 280, 100, 20)
        self.calc_TURB_COND_Q.setGeometry(340, 295, 100, 20)

        self.calc_COND_PUMP_T = QLabel('T = ?', parent=self.tab2)
        self.calc_COND_PUMP_P = QLabel('P = ?', parent=self.tab2)
        self.calc_COND_PUMP_G = QLabel('G = ?', parent=self.tab2)
        self.calc_COND_PUMP_T.setGeometry(300, 360, 100, 20)
        self.calc_COND_PUMP_P.setGeometry(300, 375, 100, 20)
        self.calc_COND_PUMP_G.setGeometry(300, 390, 100, 20)

        self.calc_PUMP_HEAT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_PUMP_HEAT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_PUMP_HEAT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_PUMP_HEAT_T.setGeometry(150, 300, 100, 20)
        self.calc_PUMP_HEAT_P.setGeometry(150, 315, 100, 20)
        self.calc_PUMP_HEAT_G.setGeometry(150, 330, 100, 20)

        self.calc_IN_COND_T = QLabel('T = ?', parent=self.tab2)
        self.calc_IN_COND_P = QLabel('P = ?', parent=self.tab2)
        self.calc_IN_COND_G = QLabel('G = ?', parent=self.tab2)
        self.calc_IN_COND_T.setGeometry(475, 270, 100, 20)
        self.calc_IN_COND_P.setGeometry(475, 285, 100, 20)
        self.calc_IN_COND_G.setGeometry(475, 300, 100, 20)

        self.calc_COND_OUT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_COND_OUT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_COND_OUT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_COND_OUT_T.setGeometry(475, 395, 100, 20)
        self.calc_COND_OUT_P.setGeometry(475, 410, 100, 20)
        self.calc_COND_OUT_G.setGeometry(475, 425, 100, 20)

        self.calc_PUMP_N = QLabel('N = ?', parent=self.tab2)
        self.calc_TURB_N = QLabel('N = ?', parent=self.tab2)
        self.calc_PUMP_N.setGeometry(210, 365, 100, 20)
        self.calc_TURB_N.setGeometry(375, 120, 100, 20)

        self.calc_HEAT_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_COND_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_HEAT_Q.setGeometry(150, 190, 100, 20)
        self.calc_COND_Q.setGeometry(450, 340, 100, 20)

        self.calc_HEAT_DT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_COND_DT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_HEAT_DT.setGeometry(150, 205, 100, 20)
        self.calc_COND_DT.setGeometry(450, 355, 100, 20)

        # ########### - цифры

        # self.img_calcer = QLabel(parent=self.tab2)
        # self.img_calcer.setPixmap(QPixmap('src/calcer.png'))

        self.graph_balance = FigureCanvasQTAgg(plt.Figure(dpi=75))
        self.balance_ax = self.graph_balance.figure.subplots()
        self.balance_ax.grid(True)
        self.balance_ax.set_title('Тепловой баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.graph_balance.draw()
        self.graph_balance_cont = QWidget(parent=self.tab2)
        graph_balance_lay = QHBoxLayout()
        graph_balance_lay.addWidget(self.graph_balance)
        self.graph_balance_cont.setLayout(graph_balance_lay)
        self.graph_balance_cont.setGeometry(520, 0, 300, 300)

        self.calc_balance = QLabel('Δ = ?', parent=self.tab2)
        self.calc_balance.setGeometry(600, 290, 200, 25)

        self.kpd_output_text = QLabel('η =', parent=self.tab2)
        self.kpd_output_text.setGeometry(600, 350, 25, 25)
        self.kpd_output = QLineEdit(parent=self.tab2)
        self.kpd_output.setGeometry(620, 350, 158, 25)
        self.kpd_output.setText(' ')

        self.start_button = QPushButton("го", parent=self.tab2)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(600, 375, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab2)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(600, 425, 180, 25)

        self.stop_optimus_button = QPushButton("Пропуск итерации", parent=self.tab2)
        self.stop_optimus_button.clicked.connect(self.skip_iter)
        self.stop_optimus_button.setGeometry(600, 475, 180, 25)
        # ###############tab-2-end############### #

        # ###############tab-3############### #
        self.table_blocks = QTableWidget(parent=self.tab3)
        self.table_blocks.setGeometry(30, 30, 302, 200)
        self.table_blocks.setColumnCount(3)
        self.table_blocks.setRowCount(4)
        self.table_blocks.setHorizontalHeaderLabels(["Блок", "Q", "ΔT"])
        self.block_list = ['HEATER', 'TURBINE', 'CONDENSER', 'PUMP']
        for i in range(3):
            self.table_blocks.setColumnWidth(i, 95)
        for i in range(4):
            self.table_blocks.setItem(i, 0, QTableWidgetItem(self.block_list[i]))

        #TQ
        self.graph_tq_heat = FigureCanvasQTAgg(plt.Figure(dpi = 75))
        self.tq_heat_ax = self.graph_tq_heat.figure.subplots()
        self.tq_heat_ax.grid(True)
        self.tq_heat_ax.set_xlabel('Q, кВт')
        self.tq_heat_ax.set_ylabel('T, °C')
        self.graph_tq_heat.draw()
        self.graph_tq_heat_cont = QWidget(parent=self.tab3)
        graph_tq_heat_lay = QHBoxLayout()
        graph_tq_heat_lay.addWidget(self.graph_tq_heat)
        self.graph_tq_heat_cont.setLayout(graph_tq_heat_lay)
        self.graph_tq_heat_cont.setGeometry(50, 250, 350, 300)

        self.graph_tq_cond = FigureCanvasQTAgg(plt.Figure(dpi = 75))
        self.tq_cond_ax = self.graph_tq_cond.figure.subplots()
        self.tq_cond_ax.grid(True)
        self.tq_cond_ax.set_xlabel('Q, кВт')
        self.tq_cond_ax.set_ylabel('T, °C')
        self.graph_tq_cond.draw()
        self.graph_tq_cond_cont = QWidget(parent=self.tab3)
        graph_tq_cond_lay = QHBoxLayout()
        graph_tq_cond_lay.addWidget(self.graph_tq_cond)
        self.graph_tq_cond_cont.setLayout(graph_tq_cond_lay)
        self.graph_tq_cond_cont.setGeometry(400, 250, 350, 300)
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


        # ###############tab-5############### #

        self.opt_fluid_txt = QLabel('Список теплоносителей:', parent=self.tab5)
        self.opt_fluid_txt.setGeometry(50, 10, 180, 25)
        self.opt_fluid_txt = QLabel('Доступно:', parent=self.tab5)
        self.opt_fluid_txt.setGeometry(50, 25, 180, 25)
        self.opt_fluid = QListWidget(parent=self.tab5)
        self.opt_fluid.setGeometry(50, 50, 100, 125)
        self.opt_fluid.addItems(['R236ea', 'R123', 'R124', 'R134a', 'Isobutane', 'R717', 'R245fa', 'R22', 'R41', 'R12', 'R32', 'CO2', 'WATER'])
        self.opt_fluid.itemDoubleClicked.connect(self.fluid_clicked)

        self.opt_fluid_txt = QLabel('Выбрано:', parent=self.tab5)
        self.opt_fluid_txt.setGeometry(180, 25, 180, 25)
        self.opt_fluid_selected = QListWidget(parent=self.tab5)
        self.opt_fluid_selected.setGeometry(180, 50, 100, 125)
        self.opt_fluid_selected.itemDoubleClicked.connect(self.fluid_selected_clicked)


        self.opt_pmin_txt = QLabel('Начальное давление:', parent=self.tab5)
        self.opt_pmin_txt.setGeometry(50, 75+100, 180, 25)
        self.opt_pmin = QLineEdit(parent=self.tab5)
        self.opt_pmin.setGeometry(50, 100+100, 180, 25)
        self.opt_pmin.setText('3')

        self.opt_pmax_txt = QLabel('Конечное давление:', parent=self.tab5)
        self.opt_pmax_txt.setGeometry(50, 125+100, 180, 25)
        self.opt_pmax = QLineEdit(parent=self.tab5)
        self.opt_pmax.setGeometry(50, 150+100, 180, 25)
        self.opt_pmax.setText('15')

        self.opt_pstep_txt = QLabel('Шаг изменения давления:', parent=self.tab5)
        self.opt_pstep_txt.setGeometry(50, 175+100, 180, 25)
        self.opt_pstep = QLineEdit(parent=self.tab5)
        self.opt_pstep.setGeometry(50, 200+100, 180, 25)
        self.opt_pstep.setText('1')

        self.start_optimus_button = QPushButton("го", parent=self.tab5)
        self.start_optimus_button.clicked.connect(self.optimus_start)
        self.start_optimus_button.setGeometry(60, 350, 175, 25)

        self.stop_optimus_button = QPushButton("стоп", parent=self.tab5)
        self.stop_optimus_button.clicked.connect(self.stop)
        self.stop_optimus_button.setGeometry(60, 400, 175, 25)

        self.stop_optimus_button = QPushButton("Пропуск итерации", parent=self.tab5)
        self.stop_optimus_button.clicked.connect(self.skip_iter)
        self.stop_optimus_button.setGeometry(60, 450, 175, 25)


        self.optimus_table = QTableWidget(parent=self.tab5)
        self.optimus_table.setGeometry(425, 50, 341, 400)
        self.optimus_table.setColumnCount(9)
        self.optimus_table.setRowCount(1)
        self.optimus_table.setHorizontalHeaderLabels(["X", "P", "KPD", "Nturb","Npump","Qheat","Qcond","Q1", "Q2"])
        self.optimus_table.setColumnWidth(0, 50)
        self.optimus_table.setColumnWidth(1, 50)
        self.optimus_table.setColumnWidth(2, 50)
        self.optimus_table.setColumnWidth(3, 50)
        self.optimus_table.setColumnWidth(4, 50)
        self.optimus_table.setColumnWidth(5, 50)
        self.optimus_table.setColumnWidth(6, 50)
        self.optimus_table.setColumnWidth(7, 50)
        self.optimus_table.setColumnWidth(8, 50)
        self.optimus_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.optimus_table.customContextMenuRequested.connect(self.contextMenuEvent)
        # ###############tab-5-end############### #

        # ###############central-tab############### #
        self.tab_menu = QTabWidget(parent=self.CentralWidget)
        self.tab_menu.setGeometry(0, 0, 800, 600)
        self.tab_menu.addTab(self.tab1, "Ввод данных")
        self.tab_menu.addTab(self.tab2, "Расчёт")
        self.tab_menu.addTab(self.tab3, "Блоки")
        self.tab_menu.addTab(self.tab4, "Потоки")
        self.tab_menu.addTab(self.tab5, "Оптимизация")
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

    def skip_iter(self):
        print('skip')
        self.opt_iter_Flag = False


    def contextMenuEvent(self, pos):
        context_menu = QMenu(self)
        action1 = context_menu.addAction("Копировать")
        action1.triggered.connect(self.context_menu_copy)
        context_menu.exec(QCursor.pos())

    def context_menu_copy(self):
        html = '<table><tbody>'
        selectedItems = self.optimus_table.selectedItems()
        if selectedItems != []:
            column_list = []
            for item in selectedItems:
                column_list.append(item.column())
            items = [item.text() for item in self.optimus_table.selectedItems()]
            for j in range(int(len(items)/(max(column_list)-min(column_list)+1))):
                html += '<tr>'
                x = max(column_list) - min(column_list) + 1
                for k in range(x):
                    html += '<td>%s</td>' % items[x*j+k]
                html += '</tr>'
        html += '</tbody></table>'
        mime = QMimeData()
        mime.setHtml(html)
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime)

    def fluid_clicked(self, item):
        self.opt_fluid_selected.addItem(item.text())

    def fluid_selected_clicked(self, item):
        self.opt_fluid_selected.takeItem(self.opt_fluid_selected.row(item))

    def optimus_start(self):
        print('start opt')
        self.balance_ax.clear()
        self.balance_ax.set_title('Тепловой баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_root.text())) / 10, 1])
        self.balance_ax.axhline(float(eval(self.cycle_tolerance_root.text())), color='red', linestyle='--')
        self.balance_ax.grid(True)
        self.balance_cumm = []
        self.balance_ax.plot(self.balance_cumm)
        self.graph_balance.draw()
        self.graph_balance.flush_events()

        self.status_img.setText('⏳')
        self.status_txt.setText('Запущен расчёт')
        self.kpd_output.setText(" ")
        self.time_flag = True
        self.time_start = datetime.datetime.now()
        self.calc_Flag = True
        self.opt_iter_Flag = True
        self.thread_calc = Thread(target=self.calc_optimus)
        self.thread_calc.start()
        self.thread_timer = Thread(target=self.timer)
        self.thread_timer.start()

    def calc_optimus(self):
        fluid_list = []
        for x in range(self.opt_fluid_selected.count()):
            fluid_list.append(self.opt_fluid_selected.item(x).text())
        i = 0
        for X_cond in fluid_list:
            for p_pump in np.arange(float(self.opt_pmin.text()),float(self.opt_pmax.text()) + float(self.opt_pstep.text()),float(self.opt_pstep.text())):
                self.optimus_table.insertRow(i)
                self.optimus_table.setItem(i, 0, QTableWidgetItem(str(X_cond)))
                self.optimus_table.setItem(i, 1, QTableWidgetItem(str(round(p_pump,5))))
                self.optimus_table.setItem(i, 2, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 3, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 4, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 5, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 6, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 7, QTableWidgetItem(' '))
                self.optimus_table.setItem(i, 8, QTableWidgetItem(' '))


                i = i+1

        i=0
        for X_cond in fluid_list:
            for p_pump in np.arange(float(self.opt_pmin.text()), float(self.opt_pmax.text())+float(self.opt_pstep.text()), float(self.opt_pstep.text())):
                if i > 0:
                    self.optimus_table.item(i-1, 0).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 1).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 2).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 3).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 4).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 5).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 6).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 7).setBackground(QColor(255, 255, 255))
                    self.optimus_table.item(i-1, 8).setBackground(QColor(255, 255, 255))

                self.optimus_table.item(i, 0).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 1).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 2).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 3).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 4).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 5).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 6).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 7).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 8).setBackground(QColor(0,204,102))

                self.opt_iter_Flag = True
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

                T_cond = float(self.t_cond_input.text())
                kpd_pump = float(self.kpd_pump_input.text())
                kpd_turb = float(self.kpd_turb_input.text())
                kpd_pump_m = float(self.kpd_pump_m_input.text())
                kpd_turb_m = float(self.kpd_turb_m_input.text())
                kpd_pump_e = float(self.kpd_pump_e_input.text())
                kpd_turb_e = float(self.kpd_turb_e_input.text())

                dt_heat = float(self.dt_heat_input.text())
                dt_cond = float(self.dt_cond_input.text())
                root_tolerance = float(eval(self.cycle_tolerance_root.text()))
                h_steps = float(self.cycle_step_h.text())

                cycle_tolerance = float(eval(self.cycle_tolerance_input.text()))
                tolerance_exp = abs(int(np.log10(cycle_tolerance)))

                self.calc_IN_HEAT_T.setText(f'T = {round(float(T_gas), tolerance_exp)}')
                self.calc_IN_HEAT_P.setText(f'P = {round(float(P_gas), tolerance_exp)}')
                self.calc_IN_HEAT_G.setText(f'G = {round(float(G_gas), tolerance_exp)}')
                self.calc_IN_COND_T.setText(f'T = {round(float(T_cool), tolerance_exp)}')
                self.calc_IN_COND_P.setText(f'P = {round(float(P_cool), tolerance_exp)}')
                self.calc_IN_COND_G.setText(f'G = {round(float(1000), tolerance_exp)}')

                write_stream('IN-HEAT', T_gas, P_gas, prop.t_p(T_gas, P_gas, X_gas)["H"], prop.t_p(T_gas, P_gas, X_gas)["S"],
                             prop.t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
                write_stream('IN-COND', T_cool, P_cool, prop.t_p(T_cool, P_cool, X_cool)["H"],
                             prop.t_p(T_cool, P_cool, X_cool)["S"],
                             prop.t_p(T_cool, P_cool, X_cool)["Q"], 1000, X_cool)
                write_stream('COND-PUMP', T_cond, prop.t_q(T_cond, 0, X_cond)["P"], prop.t_q(T_cond, 0, X_cond)["H"],
                             prop.t_q(T_cond, 0, X_cond)["S"], 0, 1000, X_cond)

                for j in range(9999):
                    if self.opt_iter_Flag is False:
                        break

                    if self.calc_Flag is False:
                        self.time_flag = False
                        self.status_img.setText('🛑')
                        self.status_txt.setText('Расчёт остановлен')
                        break

                    pump = Pump('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
                    # self.img_calcer.setGeometry(165, 370, 100, 100)
                    pump.calc()
                    self.calc_PUMP_HEAT_T.setText(f'T = {round(float(read_stream("PUMP-HEAT")["T"]), tolerance_exp)}')
                    self.calc_PUMP_HEAT_P.setText(f'P = {round(float(read_stream("PUMP-HEAT")["P"]), tolerance_exp)}')
                    self.calc_PUMP_HEAT_G.setText(f'G = {round(float(read_stream("PUMP-HEAT")["G"]), tolerance_exp)}')
                    self.calc_PUMP_N.setText(f'N = {round(float(read_block("PUMP")["Q"]), tolerance_exp)}')

                    heater = Heat('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', dt_heat, T_gas_out, root_tolerance, h_steps)
                    # self.img_calcer.setGeometry(68, 162, 100, 100)
                    heater.calc()
                    self.calc_HEAT_OUT_T.setText(f'T = {round(float(read_stream("HEAT-OUT")["T"]), tolerance_exp)}')
                    self.calc_HEAT_OUT_P.setText(f'P = {round(float(read_stream("HEAT-OUT")["P"]), tolerance_exp)}')
                    self.calc_HEAT_OUT_G.setText(f'G = {round(float(read_stream("HEAT-OUT")["G"]), tolerance_exp)}')
                    self.calc_HEAT_TURB_T.setText(f'T = {round(float(read_stream("HEAT-TURB")["T"]), tolerance_exp)}')
                    self.calc_HEAT_TURB_P.setText(f'P = {round(float(read_stream("HEAT-TURB")["P"]), tolerance_exp)}')
                    self.calc_HEAT_TURB_G.setText(f'G = {round(float(read_stream("HEAT-TURB")["G"]), tolerance_exp)}')
                    self.calc_HEAT_TURB_Q.setText(f'Q = {round(float(read_stream("HEAT-TURB")["Q"]), tolerance_exp)}')
                    self.calc_HEAT_Q.setText(f'Q = {round(float(read_block("HEATER")["Q"]), tolerance_exp)}')
                    self.calc_HEAT_DT.setText(f'ΔT = {round(float(read_block("HEATER")["DT"]), tolerance_exp)}')

                    turbine = Turb('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turb)
                    # self.img_calcer.setGeometry(315, 145, 100, 100)
                    turbine.calc()
                    self.calc_TURB_COND_T.setText(f'T = {round(float(read_stream("TURB-COND")["T"]), tolerance_exp)}')
                    self.calc_TURB_COND_P.setText(f'P = {round(float(read_stream("TURB-COND")["P"]), tolerance_exp)}')
                    self.calc_TURB_COND_G.setText(f'G = {round(float(read_stream("TURB-COND")["G"]), tolerance_exp)}')
                    self.calc_TURB_COND_Q.setText(f'Q = {round(float(read_stream("TURB-COND")["Q"]), tolerance_exp)}')
                    self.calc_TURB_N.setText(f'N = {round(float(read_block("TURBINE")["Q"]), tolerance_exp)}')

                    condenser = Cond('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond, root_tolerance, h_steps)
                    # self.img_calcer.setGeometry(360, 310, 100, 100)
                    condenser.calc()
                    self.calc_COND_PUMP_T.setText(f'T = {round(float(read_stream("COND-PUMP")["T"]), tolerance_exp)}')
                    self.calc_COND_PUMP_P.setText(f'P = {round(float(read_stream("COND-PUMP")["P"]), tolerance_exp)}')
                    self.calc_COND_PUMP_G.setText(f'G = {round(float(read_stream("COND-PUMP")["G"]), tolerance_exp)}')
                    self.calc_COND_OUT_T.setText(f'T = {round(float(read_stream("COND-OUT")["T"]), tolerance_exp)}')
                    self.calc_COND_OUT_P.setText(f'P = {round(float(read_stream("COND-OUT")["P"]), tolerance_exp)}')
                    self.calc_COND_OUT_G.setText(f'G = {round(float(read_stream("COND-OUT")["G"]), tolerance_exp)}')
                    self.calc_COND_Q.setText(f'Q = {round(float(read_block("CONDENSER")["Q"]), tolerance_exp)}')
                    self.calc_COND_DT.setText(f'ΔT = {round(float(read_block("CONDENSER")["DT"]), tolerance_exp)}')
                    self.calc_IN_COND_G.setText(f'G = {round(float(read_stream("COND-OUT")["G"]), tolerance_exp)}')

                    balance = abs(read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
                               read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
                    self.calc_balance.setText(f"Δ = {balance}")
                    self.balance_cumm.append(balance)
                    self.balance_ax.clear()
                    self.balance_ax.set_title('Тепловой баланс')
                    self.balance_ax.set_xlabel('Итерация')
                    self.balance_ax.set_ylim([cycle_tolerance/10,1])
                    self.balance_ax.semilogy()
                    self.balance_ax.axhline(cycle_tolerance, color='red', linestyle='--')
                    self.balance_ax.plot(self.balance_cumm)
                    self.balance_ax.grid(True)
                    self.graph_balance.draw()
                    self.graph_balance.flush_events()

                    if balance < cycle_tolerance:
                        break
                if self.opt_iter_Flag is False:
                    KPD = 0
                    self.kpd_output.setText("Итерация пропущена")
                    self.optimus_table.setItem(i, 2, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 3, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 4, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 4, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 5, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 6, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 7, QTableWidgetItem(str('-')))
                    self.optimus_table.setItem(i, 8, QTableWidgetItem(str('-')))

                    i = i + 1
                    close_db()
                    continue

                KPD = (read_block('TURBINE')["Q"]*kpd_turb_m*kpd_turb_e - read_block('PUMP')["Q"]*kpd_pump_e*kpd_pump_e) / read_block('HEATER')["Q"]
                print(X_cond, p_pump, KPD, read_block("TURBINE")["Q"],read_block("PUMP")["Q"],read_block("HEATER")["Q"],read_block("CONDENSER")["Q"],read_stream("HEAT-TURB")["Q"], read_stream("TURB-COND")["Q"])
                self.kpd_output.setText(str(round(KPD, tolerance_exp+2)))
                self.optimus_table.setItem(i, 2, QTableWidgetItem(str(round(KPD, 5))))
                self.optimus_table.setItem(i, 3, QTableWidgetItem(str(round(float(read_block("TURBINE")["Q"]), tolerance_exp))))
                self.optimus_table.setItem(i, 4, QTableWidgetItem(str(round(float(read_block("PUMP")["Q"]), tolerance_exp))))
                self.optimus_table.setItem(i, 5, QTableWidgetItem(str(round(float(read_block("HEATER")["Q"]), tolerance_exp))))
                self.optimus_table.setItem(i, 6, QTableWidgetItem(str(round(float(read_block("CONDENSER")["Q"]), tolerance_exp))))
                self.optimus_table.setItem(i, 7, QTableWidgetItem(str(round(float(read_stream("HEAT-TURB")["Q"]), tolerance_exp))))
                self.optimus_table.setItem(i, 8, QTableWidgetItem(str(round(float(read_stream("TURB-COND")["Q"]), tolerance_exp))))
                self.optimus_table.item(i, 2).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 3).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 4).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 5).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 6).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 7).setBackground(QColor(0,204,102))
                self.optimus_table.item(i, 8).setBackground(QColor(0,204,102))

                i = i + 1
                close_db()

        # self.img_calcer.setGeometry(0, 0, 0, 0)
        self.time_flag = False
        if self.calc_Flag is True:
            self.status_img.setText('✔️')
            self.status_txt.setText('Расчёт завершён успешно')
        else:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')

        print('end opt')


    def start(self):
        self.tab_menu.setCurrentIndex(1)
        self.balance_ax.clear()
        self.balance_ax.set_title('Тепловой баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_root.text())) / 10, 1])
        self.balance_ax.axhline(float(eval(self.cycle_tolerance_root.text())), color='red', linestyle='--')

        self.balance_ax.grid(True)
        self.balance_cumm = []
        self.balance_ax.plot(self.balance_cumm)
        self.graph_balance.draw()
        self.graph_balance.flush_events()

        print('start')
        self.status_img.setText('⏳')
        self.status_txt.setText('Запущен расчёт')
        self.kpd_output.setText(" ")

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
        self.status_img.setText('🛑')
        self.status_txt.setText('Остановка расчёта')
        if self.thread_calc.is_alive() is False:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')

    def timer(self):
        while self.time_flag is True:
            self.status_time.setText(f'Время расчёта: {(datetime.datetime.now() - self.time_start).seconds} с')
            time.sleep(0.5)

    def calc(self):
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
        root_tolerance = float(eval(self.cycle_tolerance_root.text()))
        h_steps = float(self.cycle_step_h.text())

        cycle_tolerance = float(eval(self.cycle_tolerance_input.text()))
        tolerance_exp = abs(int(np.log10(cycle_tolerance)))

        self.calc_IN_HEAT_T.setText(f'T = {round(float(T_gas), tolerance_exp)}')
        self.calc_IN_HEAT_P.setText(f'P = {round(float(P_gas), tolerance_exp)}')
        self.calc_IN_HEAT_G.setText(f'G = {round(float(G_gas), tolerance_exp)}')
        self.calc_IN_COND_T.setText(f'T = {round(float(T_cool), tolerance_exp)}')
        self.calc_IN_COND_P.setText(f'P = {round(float(P_cool), tolerance_exp)}')
        self.calc_IN_COND_G.setText(f'G = {round(float(1000), tolerance_exp)}')

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
                self.status_img.setText('🛑')
                self.status_txt.setText('Расчёт остановлен')
                break

            pump = Pump('COND-PUMP', 'PUMP-HEAT', p_pump, kpd_pump)
            # self.img_calcer.setGeometry(165, 370, 100, 100)
            pump.calc()
            self.calc_PUMP_HEAT_T.setText(f'T = {round(float(read_stream("PUMP-HEAT")["T"]), tolerance_exp)}')
            self.calc_PUMP_HEAT_P.setText(f'P = {round(float(read_stream("PUMP-HEAT")["P"]), tolerance_exp)}')
            self.calc_PUMP_HEAT_G.setText(f'G = {round(float(read_stream("PUMP-HEAT")["G"]), tolerance_exp)}')
            self.calc_PUMP_N.setText(f'N = {round(float(read_block("PUMP")["Q"]), tolerance_exp)}')

            heater = Heat('IN-HEAT', 'HEAT-OUT', 'PUMP-HEAT', 'HEAT-TURB', dt_heat, T_gas_out, root_tolerance, h_steps)
            # self.img_calcer.setGeometry(68, 162, 100, 100)
            heater.calc()
            self.calc_HEAT_OUT_T.setText(f'T = {round(float(read_stream("HEAT-OUT")["T"]), tolerance_exp)}')
            self.calc_HEAT_OUT_P.setText(f'P = {round(float(read_stream("HEAT-OUT")["P"]), tolerance_exp)}')
            self.calc_HEAT_OUT_G.setText(f'G = {round(float(read_stream("HEAT-OUT")["G"]), tolerance_exp)}')
            self.calc_HEAT_TURB_T.setText(f'T = {round(float(read_stream("HEAT-TURB")["T"]), tolerance_exp)}')
            self.calc_HEAT_TURB_P.setText(f'P = {round(float(read_stream("HEAT-TURB")["P"]), tolerance_exp)}')
            self.calc_HEAT_TURB_G.setText(f'G = {round(float(read_stream("HEAT-TURB")["G"]), tolerance_exp)}')
            self.calc_HEAT_TURB_Q.setText(f'Q = {round(float(read_stream("HEAT-TURB")["Q"]), tolerance_exp)}')

            self.calc_HEAT_Q.setText(f'Q = {round(float(read_block("HEATER")["Q"]), tolerance_exp)}')
            self.calc_HEAT_DT.setText(f'ΔT = {round(float(read_block("HEATER")["DT"]), tolerance_exp)}')

            turbine = Turb('HEAT-TURB', 'TURB-COND', prop.t_q(T_cond, 0, X_cond)["P"], kpd_turb)
            # self.img_calcer.setGeometry(315, 145, 100, 100)
            turbine.calc()
            self.calc_TURB_COND_T.setText(f'T = {round(float(read_stream("TURB-COND")["T"]), tolerance_exp)}')
            self.calc_TURB_COND_P.setText(f'P = {round(float(read_stream("TURB-COND")["P"]), tolerance_exp)}')
            self.calc_TURB_COND_G.setText(f'G = {round(float(read_stream("TURB-COND")["G"]), tolerance_exp)}')
            self.calc_TURB_COND_Q.setText(f'Q = {round(float(read_stream("TURB-COND")["Q"]), tolerance_exp)}')
            self.calc_TURB_N.setText(f'N = {round(float(read_block("TURBINE")["Q"]), tolerance_exp)}')

            condenser = Cond('TURB-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond, root_tolerance, h_steps)
            # self.img_calcer.setGeometry(360, 310, 100, 100)
            condenser.calc()
            self.calc_COND_PUMP_T.setText(f'T = {round(float(read_stream("COND-PUMP")["T"]), tolerance_exp)}')
            self.calc_COND_PUMP_P.setText(f'P = {round(float(read_stream("COND-PUMP")["P"]), tolerance_exp)}')
            self.calc_COND_PUMP_G.setText(f'G = {round(float(read_stream("COND-PUMP")["G"]), tolerance_exp)}')
            self.calc_COND_OUT_T.setText(f'T = {round(float(read_stream("COND-OUT")["T"]), tolerance_exp)}')
            self.calc_COND_OUT_P.setText(f'P = {round(float(read_stream("COND-OUT")["P"]), tolerance_exp)}')
            self.calc_COND_OUT_G.setText(f'G = {round(float(read_stream("COND-OUT")["G"]), tolerance_exp)}')
            self.calc_COND_Q.setText(f'Q = {round(float(read_block("CONDENSER")["Q"]), tolerance_exp)}')
            self.calc_COND_DT.setText(f'ΔT = {round(float(read_block("CONDENSER")["DT"]), tolerance_exp)}')
            self.calc_IN_COND_G.setText(f'G = {round(float(read_stream("COND-OUT")["G"]), tolerance_exp)}')

            balance = abs(read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
                       read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
            self.calc_balance.setText(f"Δ = {balance}")
            self.balance_cumm.append(balance)
            self.balance_ax.clear()
            self.balance_ax.set_title('Тепловой баланс')
            self.balance_ax.set_xlabel('Итерация')
            self.balance_ax.semilogy()
            self.balance_ax.set_ylim([cycle_tolerance/10,1])
            self.balance_ax.axhline(cycle_tolerance, color='red', linestyle='--')
            self.balance_ax.plot(self.balance_cumm)
            self.balance_ax.grid(True)
            self.graph_balance.draw()
            self.graph_balance.flush_events()

            if balance < cycle_tolerance:
                break

        KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
        print(X_cond, p_pump, KPD, read_stream("HEAT-TURB")["Q"], read_stream("TURB-COND")["Q"])
        self.kpd_output.setText(str(round(KPD, tolerance_exp+2)))

        for i in range(8):
            stream = list(read_stream(str(self.streams_list[i])).values())
            for j in range(6):
                value = str(round(stream[j], tolerance_exp))
                self.table_streams.setItem(i, j+1, QTableWidgetItem(value))
            self.table_streams.setItem(i, 7, QTableWidgetItem(str(stream[6])))
        for i in range(4):
            value = round(list(read_block(str(self.block_list[i])).values())[0], tolerance_exp)
            self.table_blocks.setItem(i, 1, QTableWidgetItem(str(value)))
            value = round(list(read_block(str(self.block_list[i])).values())[1], tolerance_exp)
            self.table_blocks.setItem(i, 2, QTableWidgetItem(str(value)))

        ##
        self.tq_heat_ax.clear()
        self.tq_heat_ax.grid(True)
        self.tq_heat_ax.set_title('Утилизатор')
        self.tq_heat_ax.set_xlabel('Q, кВт')
        self.tq_heat_ax.set_ylabel('T, °C')
        self.tq_heat_ax.plot(heater.TQ()[0], heater.TQ()[2], heater.TQ()[0], heater.TQ()[1])
        self.graph_tq_heat.draw()
        self.tq_cond_ax.clear()
        self.tq_cond_ax.grid(True)
        self.tq_cond_ax.set_title('Конденсатор')
        self.tq_cond_ax.set_xlabel('Q, кВт')
        self.tq_cond_ax.set_ylabel('T, °C')
        self.tq_cond_ax.plot(condenser.TQ()[0], condenser.TQ()[2], condenser.TQ()[0], condenser.TQ()[1])
        self.graph_tq_cond.draw()
        ##

        close_db()
        # self.img_calcer.setGeometry(0, 0, 0, 0)
        self.time_flag = False
        if self.calc_Flag is True:
            self.status_img.setText('✔️')
            self.status_txt.setText('Расчёт завершён успешно')
        else:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')

        print('end calc')
##############################


app = QApplication([])
window = Window()
window.show()
app.exec()
