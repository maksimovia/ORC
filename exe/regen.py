from PyQt6.QtWidgets import QLabel, QLineEdit, QWidget, QMainWindow, QPushButton, QHBoxLayout, QTableWidget,\
    QTabWidget, QStatusBar, QTableWidgetItem, QApplication
from PyQt6.QtGui import QPixmap, QIcon
import numpy as np
from threading import Thread
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

#######################################################################################

import os
import sys

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

#######################################################################################

def root(func, a, b, root_tol):
    x = 10000
    while abs(func(a) - func(b)) > root_tol:
        x = a + (b - a) / 2
        if func(a) * func(x) < 0:
            b = x
        else:
            a = x
    return x


class Heat:
    def __init__(self, stream11, stream12, stream21, stream22, dt, t_out, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dT = dt
        self.T_out = t_out
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']

        T12 = self.T_out
        H12 = t_p(T12, P11, fluid1)["H"]
        S12 = t_p(T12, P11, fluid1)["S"]
        Q12 = t_p(T12, P11, fluid1)["Q"]

        step = (H11 - H12) / self.h_steps

        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dT - min_dt

        G2 = root(G2_func, 1, 10000, self.root_tolerance)
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        H22 = t_p(T22, P21, fluid2)["H"]
        S22 = t_p(T22, P21, fluid2)["S"]
        Q22 = t_p(T22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('HEATER', Q[-1], min_dt)

        pass

    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2


class Pump:
    def __init__(self, stream1, stream2, p_out, kpd_pump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.kpd_pump
        T2 = h_p(H2, self.p_out, fluid)["T"]
        S2 = h_p(H2, self.p_out, fluid)["S"]
        Q2 = h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H2 - H1)
        write_block('PUMP', N, 0)
        pass


class Turb:
    def __init__(self, stream1, stream2, p_out, kpd_turb):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_turb = kpd_turb

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 - (H1 - H2t) * self.kpd_turb
        T2 = h_p(H2, self.p_out, fluid)["T"]
        S2 = h_p(H2, self.p_out, fluid)["S"]
        Q2 = h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H1 - H2)
        write_block('TURBINE', N, 0)
        pass


class Cond:
    def __init__(self, stream11, stream12, stream21, stream22, dt, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P1 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        H12 = p_q(P1, 0, fluid1)["H"]
        P2 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        step = (H11 - H12) / self.h_steps

        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = h_p(h11, P1, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = h_p(h21, P2, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt
        G2 = root(G2_func, 100, 100000, self.root_tolerance)
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P1, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P2, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        H22 = t_p(T22, P2, fluid2)["H"]
        S22 = t_p(T22, P2, fluid2)["S"]
        Q22 = t_p(T22, P2, fluid2)["Q"]
        T12 = h_p(H12, P1, fluid1)["T"]
        S12 = h_p(H12, P1, fluid1)["S"]
        T21 = h_p(H21, P2, fluid2)["T"]
        S21 = h_p(H21, P2, fluid2)["S"]
        Q21 = h_p(H21, P2, fluid2)["Q"]
        write_stream(self.stream12, T12, P1, H12, S12, 0, G1, fluid1)
        write_stream(self.stream21, T21, P2, H21, S21, Q21, G2, fluid2)
        write_stream(self.stream22, T22, P2, H22, S22, Q22, G2, fluid2)
        write_block('CONDENSER', Q[-1], min_dt)
        pass

    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2


class Regen:
    def __init__(self, stream11, stream12, stream21, stream22, dt, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        T21 = read_stream(self.stream21)['T']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']
        fluid2 = read_stream(self.stream21)['X']
        T12 = T21 + self.dt
        H12 = t_p(T12, P11, fluid1)["H"]
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        step = (H11 - H12) / self.h_steps
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        T12 = t1[-1]
        H12 = t_p(T12, P11, fluid1)["H"]
        S12 = t_p(T12, P11, fluid1)["S"]
        Q12 = t_p(T12, P11, fluid1)["Q"]
        H22 = t_p(T22, P21, fluid2)["H"]
        S22 = t_p(T22, P21, fluid2)["S"]
        Q22 = t_p(T22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('REGEN', Q[-1], min_dt)
        pass
    def TQ(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        H12 = read_stream(self.stream12)['H']
        step = (H11 - H12) / self.h_steps
        G2 = read_stream(self.stream21)['G']
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        return Q, t1, t2

#######################################################################################
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
RP = REFPROPFunctionLibrary('C:/Program Files (x86)/REFPROP')

iUnits = 21
iMass = 2
iFlag = 0


def t_p(t, p, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TP', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, t + 273.15, p * 10 ** 6, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def h_p(h, p, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'HP', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, h * 1000, p * 10 ** 6, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def p_q(p, q, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PQ', 'T;P;H;S', iUnits, iMass, iFlag, p * 10 ** 6, q, comp)
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def t_q(t, q, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TQ', 'T;P;H;S', iUnits, iMass, iFlag, t + 273.15, q, comp)
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def p_s(p, s, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'PS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, p * 10 ** 6, s * 1000, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}


def t_s(t, s, fluid):
    comp = []
    for i in range(1, len(fluid.split(";")), 2):
        comp.append(float(fluid.split(";")[i]))
    res = RP.REFPROPdll(fluid, 'TS', 'T;P;H;S;QMASS', iUnits, iMass, iFlag, t + 273.15, s * 1000, comp)
    if res.q <= 0:
        q = 0
    elif res.q >= 1:
        q = 1
    else:
        q = res.Output[4]
    return {'T': res.Output[0] - 273.15, 'P': res.Output[1] / 10 ** 6, 'H': res.Output[2] / 1000,
            'S': res.Output[3] / 1000, 'Q': q}

#######################################################################################
import sqlite3


def open_db():
    global connection
    global cursor

    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    if cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='streams' ''').fetchone() is None:
        cursor.execute('''CREATE TABLE IF NOT EXISTS streams
        (NAME TEXT DEFAULT NULL,
        T REAL DEFAULT NULL,
        P REAL DEFAULT NULL,
        H REAL DEFAULT NULL,
        S REAL DEFAULT NULL,
        Q REAL DEFAULT NULL,
        G REAL DEFAULT NULL,
        X TEXT DEFAULT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
        (NAME TEXT DEFAULT NULL,
        Q REAL DEFAULT NULL,
        dT REAL DEFAULT NULL)''')

        cursor.execute('''INSERT INTO streams(NAME) VALUES
        ('IN-HEAT'),
        ('HEAT-OUT'),
        ('COND-PUMP'),
        ('PUMP-HEAT'),
        ('HEAT-TURB'),
        ('TURB-COND'),
        ('IN-COND'),
        ('COND-OUT'),
        ('PUMP-REGEN'),
        ('REGEN-HEAT'),
        ('TURB-REGEN'),
        ('REGEN-COND')
        ''')

        cursor.execute('''INSERT INTO blocks(NAME) VALUES
        ('PUMP'),
        ('TURBINE'),
        ('CONDENSER'),
        ('HEATER'),
        ('REGEN')
        ''')
    print('open DB')
    pass


def close_db():
    connection.commit()
    cursor.close()
    connection.close()
    print('close DB')
    pass


def write_stream(stream, t, p, h, s, q, g, x):
    cursor.execute('''UPDATE streams SET T=?,P=?, H=?, S=?, Q=?, G=?, X=? WHERE NAME==? ''',
                   [t, p, h, s, q, g, x, stream])
    pass


def write_block(block, q, dt):
    cursor.execute('''UPDATE blocks SET Q=?, DT=? WHERE NAME==? ''', [q, dt, block])
    pass


def read_block(block):
    q = cursor.execute('''SELECT Q FROM blocks WHERE NAME==? ''', [block]).fetchone()
    dt = cursor.execute('''SELECT DT FROM blocks WHERE NAME==? ''', [block]).fetchone()
    return {'Q': q[0],'DT': dt[0]}


def read_stream(stream):
    t = cursor.execute('''SELECT T FROM streams WHERE NAME==? ''', [stream]).fetchone()
    p = cursor.execute('''SELECT P FROM streams WHERE NAME==? ''', [stream]).fetchone()
    h = cursor.execute('''SELECT H FROM streams WHERE NAME==? ''', [stream]).fetchone()
    s = cursor.execute('''SELECT S FROM streams WHERE NAME==? ''', [stream]).fetchone()
    q = cursor.execute('''SELECT Q FROM streams WHERE NAME==? ''', [stream]).fetchone()
    g = cursor.execute('''SELECT G FROM streams WHERE NAME==? ''', [stream]).fetchone()
    x = cursor.execute('''SELECT X FROM streams WHERE NAME==? ''', [stream]).fetchone()
    return {'T': t[0], 'P': p[0], 'H': h[0], 'S': s[0], 'Q': q[0], 'G': g[0], 'X': x[0]}
#######################################################################################





class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Цикл Ренкина с регенератором")
        self.setWindowIcon(QIcon(resource_path('logo.png')))
        self.setFixedSize(800, 600)
        self.CentralWidget = QWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        # ###############tab-1############### #
        self.img_input = QLabel(parent=self.tab1)
        self.img_input.setPixmap(QPixmap(resource_path('ORC-REGEN.png')))
        self.img_input.setGeometry(25, 50, 525, 525)

        self.t_gas_input = QLineEdit(parent=self.tab1)
        self.t_gas_input.setGeometry(50, 40, 50, 20)
        self.t_gas_input.setText('183.6')
        self.t_gas_txt = QLabel('T =', parent=self.tab1)
        self.t_gas_txt.setGeometry(30, 40, 20, 20)

        self.p_gas_input = QLineEdit(parent=self.tab1)
        self.p_gas_input.setGeometry(50, 60, 50, 20)
        self.p_gas_input.setText('0.1')
        self.p_gas_txt = QLabel('P =', parent=self.tab1)
        self.p_gas_txt.setGeometry(30, 60, 20, 20)

        self.g_gas_input = QLineEdit(parent=self.tab1)
        self.g_gas_input.setGeometry(50, 80, 50, 20)
        self.g_gas_input.setText('509')
        self.g_gas_txt = QLabel('G =', parent=self.tab1)
        self.g_gas_txt.setGeometry(30, 80, 20, 20)

        self.t_gas_out_input = QLineEdit(parent=self.tab1)
        self.t_gas_out_input.setGeometry(50, 280, 50, 20)
        self.t_gas_out_input.setText('80')
        self.t_gas_out_input_txt = QLabel('T =', parent=self.tab1)
        self.t_gas_out_input_txt.setGeometry(30, 280, 20, 20)

        self.t_cool_input = QLineEdit(parent=self.tab1)
        self.t_cool_input.setGeometry(470, 355, 50, 20)
        self.t_cool_input.setText('15')
        self.t_cool_input_txt = QLabel('T =', parent=self.tab1)
        self.t_cool_input_txt.setGeometry(450, 355, 20, 20)

        self.p_cool_input = QLineEdit(parent=self.tab1)
        self.p_cool_input.setGeometry(470, 375, 50, 20)
        self.p_cool_input.setText('0.15')
        self.p_cool_input_txt = QLabel('P =', parent=self.tab1)
        self.p_cool_input_txt.setGeometry(450, 375, 20, 20)

        self.t_cond_input = QLineEdit(parent=self.tab1)
        self.t_cond_input.setGeometry(330, 390, 50, 20)
        self.t_cond_input.setText('30')
        self.t_cond_input_txt = QLabel('Tконд =', parent=self.tab1)
        self.t_cond_input_txt.setGeometry(285, 390, 40, 20)

        self.p_pump_input = QLineEdit(parent=self.tab1)
        self.p_pump_input.setGeometry(205, 415, 50, 20)
        self.p_pump_input.setText('3.3')
        self.p_pump_input_txt = QLabel('P =', parent=self.tab1)
        self.p_pump_input_txt.setGeometry(180, 415, 20, 20)

        self.kpd_pump_input = QLineEdit(parent=self.tab1)
        self.kpd_pump_input.setGeometry(205, 435, 50, 20)
        self.kpd_pump_input.setText('0.85')
        self.kpd_pump_input_txt = QLabel('η =', parent=self.tab1)
        self.kpd_pump_input_txt.setGeometry(180, 435, 20, 20)

        self.kpd_turb_input = QLineEdit(parent=self.tab1)
        self.kpd_turb_input.setGeometry(360, 100, 50, 20)
        self.kpd_turb_input.setText('0.85')
        self.kpd_turb_input_txt = QLabel('η =', parent=self.tab1)
        self.kpd_turb_input_txt.setGeometry(335, 100, 20, 20)

        self.dt_heat_input = QLineEdit(parent=self.tab1)
        self.dt_heat_input.setGeometry(180, 180, 50, 20)
        self.dt_heat_input.setText('10')
        self.dt_heat_input_txt = QLabel('ΔT =', parent=self.tab1)
        self.dt_heat_input_txt.setGeometry(155, 180, 25, 20)

        self.dt_cond_input = QLineEdit(parent=self.tab1)
        self.dt_cond_input.setGeometry(330, 410, 50, 20)
        self.dt_cond_input.setText('5')
        self.dt_cond_input_txt = QLabel('ΔT =', parent=self.tab1)
        self.dt_cond_input_txt.setGeometry(285, 410, 40, 20)

        self.dt_regen_input = QLineEdit(parent=self.tab1)
        self.dt_regen_input.setGeometry(320, 310, 50, 20)
        self.dt_regen_input.setText('5')
        self.dt_regen_input_txt = QLabel('ΔT =', parent=self.tab1)
        self.dt_regen_input_txt.setGeometry(295, 310, 25, 20)

        self.x_gas_input = QLineEdit(parent=self.tab1)
        self.x_gas_input.setGeometry(600, 100, 180, 25)
        self.x_gas_input.setText('N2;0.78;O2;0.1;CO2;0.02;H2O;0.1')
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
        self.cycle_tolerance_input.setText('10**-4')
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
        self.img_calc.setPixmap(QPixmap(resource_path('ORC-REGEN.png')))
        self.img_calc.setGeometry(25, 50, 525, 525)

        # ########### - цифры
        self.calc_IN_HEAT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_IN_HEAT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_IN_HEAT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_IN_HEAT_T.setGeometry(30, 55, 100, 20)
        self.calc_IN_HEAT_P.setGeometry(30, 70, 100, 20)
        self.calc_IN_HEAT_G.setGeometry(30, 85, 100, 20)

        self.calc_HEAT_OUT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HEAT_OUT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HEAT_OUT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HEAT_OUT_T.setGeometry(30, 280, 100, 20)
        self.calc_HEAT_OUT_P.setGeometry(30, 295, 100, 20)
        self.calc_HEAT_OUT_G.setGeometry(30, 310, 100, 20)

        self.calc_HEAT_TURB_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HEAT_TURB_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HEAT_TURB_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HEAT_TURB_T.setGeometry(200, 55, 100, 20)
        self.calc_HEAT_TURB_P.setGeometry(200, 70, 100, 20)
        self.calc_HEAT_TURB_G.setGeometry(200, 85, 100, 20)

        self.calc_TURB_REGEN_T = QLabel('T = ?', parent=self.tab2)
        self.calc_TURB_REGEN_P = QLabel('P = ?', parent=self.tab2)
        self.calc_TURB_REGEN_G = QLabel('G = ?', parent=self.tab2)
        self.calc_TURB_REGEN_T.setGeometry(420, 225, 100, 20)
        self.calc_TURB_REGEN_P.setGeometry(420, 240, 100, 20)
        self.calc_TURB_REGEN_G.setGeometry(420, 255, 100, 20)

        self.calc_REGEN_COND_T = QLabel('T = ?', parent=self.tab2)
        self.calc_REGEN_COND_P = QLabel('P = ?', parent=self.tab2)
        self.calc_REGEN_COND_G = QLabel('G = ?', parent=self.tab2)
        self.calc_REGEN_COND_T.setGeometry(350, 320, 100, 20)
        self.calc_REGEN_COND_P.setGeometry(350, 335, 100, 20)
        self.calc_REGEN_COND_G.setGeometry(350, 350, 100, 20)

        self.calc_COND_PUMP_T = QLabel('T = ?', parent=self.tab2)
        self.calc_COND_PUMP_P = QLabel('P = ?', parent=self.tab2)
        self.calc_COND_PUMP_G = QLabel('G = ?', parent=self.tab2)
        self.calc_COND_PUMP_T.setGeometry(300, 440, 100, 20)
        self.calc_COND_PUMP_P.setGeometry(300, 455, 100, 20)
        self.calc_COND_PUMP_G.setGeometry(300, 470, 100, 20)

        self.calc_PUMP_REGEN_T = QLabel('T = ?', parent=self.tab2)
        self.calc_PUMP_REGEN_P = QLabel('P = ?', parent=self.tab2)
        self.calc_PUMP_REGEN_G = QLabel('G = ?', parent=self.tab2)
        self.calc_PUMP_REGEN_T.setGeometry(135, 385, 100, 20)
        self.calc_PUMP_REGEN_P.setGeometry(135, 400, 100, 20)
        self.calc_PUMP_REGEN_G.setGeometry(135, 415, 100, 20)

        self.calc_REGEN_HEAT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_REGEN_HEAT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_REGEN_HEAT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_REGEN_HEAT_T.setGeometry(135, 280, 100, 20)
        self.calc_REGEN_HEAT_P.setGeometry(135, 295, 100, 20)
        self.calc_REGEN_HEAT_G.setGeometry(135, 310, 100, 20)

        self.calc_IN_COND_T = QLabel('T = ?', parent=self.tab2)
        self.calc_IN_COND_P = QLabel('P = ?', parent=self.tab2)
        self.calc_IN_COND_G = QLabel('G = ?', parent=self.tab2)
        self.calc_IN_COND_T.setGeometry(475, 350, 100, 20)
        self.calc_IN_COND_P.setGeometry(475, 365, 100, 20)
        self.calc_IN_COND_G.setGeometry(475, 380, 100, 20)

        self.calc_COND_OUT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_COND_OUT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_COND_OUT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_COND_OUT_T.setGeometry(475, 460, 100, 20)
        self.calc_COND_OUT_P.setGeometry(475, 475, 100, 20)
        self.calc_COND_OUT_G.setGeometry(475, 490, 100, 20)

        self.calc_PUMP_N = QLabel('N = ?', parent=self.tab2)
        self.calc_TURB_N = QLabel('N = ?', parent=self.tab2)
        self.calc_PUMP_N.setGeometry(210, 440, 100, 20)
        self.calc_TURB_N.setGeometry(345, 100, 100, 20)

        self.calc_HEAT_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_COND_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_HEAT_Q.setGeometry(150, 165, 100, 20)
        self.calc_COND_Q.setGeometry(450, 410, 100, 20)

        self.calc_HEAT_DT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_COND_DT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_HEAT_DT.setGeometry(150, 180, 100, 20)
        self.calc_COND_DT.setGeometry(450, 425, 100, 20)

        self.calc_REGEN_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_REGEN_Q.setGeometry(290, 285, 100, 20)

        self.calc_REGEN_DT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_REGEN_DT.setGeometry(290, 300, 100, 20)

        # ########### - цифры

        self.img_calcer = QLabel(parent=self.tab2)
        self.img_calcer.setPixmap(QPixmap(resource_path('calcer.png')))
        self.img_calcer.setGeometry(0, 0, 0, 0)

        self.graph_balance = FigureCanvasQTAgg(plt.Figure(dpi=75))
        self.balance_ax = self.graph_balance.figure.subplots()
        self.balance_ax.grid(True)
        self.balance_ax.set_title('Невязка по балансу')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_input.text())), 10 ** 0])
        self.graph_balance.draw()
        self.graph_balance_cont = QWidget(parent=self.tab2)
        graph_balance_lay = QHBoxLayout()
        graph_balance_lay.addWidget(self.graph_balance)
        self.graph_balance_cont.setLayout(graph_balance_lay)
        self.graph_balance_cont.setGeometry(520, 0, 300, 300)

        self.kpd_output = QLabel('КПД равен _', parent=self.tab2)
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
        self.table_blocks.setGeometry(30, 30, 302, 200)
        self.table_blocks.setColumnCount(3)
        self.table_blocks.setRowCount(5)
        self.table_blocks.setHorizontalHeaderLabels(["Блок", "Q", "ΔT"])
        self.block_list = ['HEATER', 'TURBINE', 'CONDENSER', 'PUMP', 'REGEN']
        for i in range(3):
            self.table_blocks.setColumnWidth(i, 95)
        for i in range(5):
            self.table_blocks.setItem(i, 0, QTableWidgetItem(self.block_list[i]))

        #TQ
        self.graph_tq_heat = FigureCanvasQTAgg(plt.Figure(dpi = 65))
        self.tq_heat_ax = self.graph_tq_heat.figure.subplots()
        self.tq_heat_ax.grid(True)
        self.tq_heat_ax.set_xlabel('Q, кВт')
        self.tq_heat_ax.set_ylabel('T, °C')
        self.graph_tq_heat.draw()
        self.graph_tq_heat_cont = QWidget(parent=self.tab3)
        graph_tq_heat_lay = QHBoxLayout()
        graph_tq_heat_lay.addWidget(self.graph_tq_heat)
        self.graph_tq_heat_cont.setLayout(graph_tq_heat_lay)
        self.graph_tq_heat_cont.setGeometry(10, 260, 290, 280)

        self.graph_tq_regen = FigureCanvasQTAgg(plt.Figure(dpi = 65))
        self.tq_regen_ax = self.graph_tq_regen.figure.subplots()
        self.tq_regen_ax.grid(True)
        self.tq_regen_ax.set_xlabel('Q, кВт')
        self.tq_regen_ax.set_ylabel('T, °C')
        self.graph_tq_regen.draw()
        self.graph_tq_regen_cont = QWidget(parent=self.tab3)
        graph_tq_regen_lay = QHBoxLayout()
        graph_tq_regen_lay.addWidget(self.graph_tq_regen)
        self.graph_tq_regen_cont.setLayout(graph_tq_regen_lay)
        self.graph_tq_regen_cont.setGeometry(265, 260, 290, 280)

        self.graph_tq_cond = FigureCanvasQTAgg(plt.Figure(dpi = 65))
        self.tq_cond_ax = self.graph_tq_cond.figure.subplots()
        self.tq_cond_ax.grid(True)
        self.tq_cond_ax.set_xlabel('Q, кВт')
        self.tq_cond_ax.set_ylabel('T, °C')
        self.graph_tq_cond.draw()
        self.graph_tq_cond_cont = QWidget(parent=self.tab3)
        graph_tq_cond_lay = QHBoxLayout()
        graph_tq_cond_lay.addWidget(self.graph_tq_cond)
        self.graph_tq_cond_cont.setLayout(graph_tq_cond_lay)
        self.graph_tq_cond_cont.setGeometry(520, 260, 290, 280)
        # ###############tab-3-end############### #

        # ###############tab-4############### #
        self.table_streams = QTableWidget(parent=self.tab4)
        self.table_streams.setGeometry(30, 30, 744, 500)
        self.table_streams.setColumnCount(8)
        self.table_streams.setRowCount(10)
        self.table_streams.setHorizontalHeaderLabels(["Поток", "T", "P", "H", "S", "Q", "G", "X"])
        self.streams_list = ['HEAT-TURB', 'TURB-REGEN', 'REGEN-COND', 'COND-PUMP', 'PUMP-REGEN', 'REGEN-HEAT',
                             'IN-HEAT', 'HEAT-OUT', 'IN-COND', 'COND-OUT']
        for i in range(8):
            self.table_streams.setColumnWidth(i, 90)
        for i in range(10):
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
        self.status_img = QLabel('⏹')
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
        self.balance_ax.set_title('Невязка по балансу')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_input.text())), 10 ** 0])
        self.balance_ax.grid(True)
        self.balance_cumm = []
        self.balance_ax.plot(self.balance_cumm)
        self.graph_balance.draw()

        print('start')
        self.status_img.setText('⏳')
        self.status_txt.setText('Запущен расчёт')
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
        dt_regen = float(self.dt_regen_input.text())
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

        write_stream('IN-HEAT', T_gas, P_gas, t_p(T_gas, P_gas, X_gas)["H"], t_p(T_gas, P_gas, X_gas)["S"],
                     t_p(T_gas, P_gas, X_gas)["Q"], G_gas, X_gas)
        write_stream('IN-COND', T_cool, P_cool, t_p(T_cool, P_cool, X_cool)["H"],
                     t_p(T_cool, P_cool, X_cool)["S"],
                     t_p(T_cool, P_cool, X_cool)["Q"], 1000, X_cool)

        write_stream('COND-PUMP', T_cond, t_q(T_cond, 0, X_cond)["P"], t_q(T_cond, 0, X_cond)["H"],
                     t_q(T_cond, 0, X_cond)["S"], 0, 1000, X_cond)

        for i in range(9999):
            if self.calc_Flag is False:
                self.time_flag = False
                self.status_img.setText('🛑')
                self.status_txt.setText('Расчёт остановлен')
                break

            pump = Pump('COND-PUMP', 'PUMP-REGEN', p_pump, kpd_pump)
            self.img_calcer.setGeometry(165, 440, 100, 100)
            pump.calc()
            self.calc_PUMP_REGEN_T.setText(f'T = {round(float(read_stream("PUMP-REGEN")["T"]), tolerance_exp)}')
            self.calc_PUMP_REGEN_P.setText(f'P = {round(float(read_stream("PUMP-REGEN")["P"]), tolerance_exp)}')
            self.calc_PUMP_REGEN_G.setText(f'G = {round(float(read_stream("PUMP-REGEN")["G"]), tolerance_exp)}')
            self.calc_PUMP_N.setText(f'N = {round(float(read_block("PUMP")["Q"]), tolerance_exp)}')

            if i == 0:
                self.img_calcer.setGeometry(205, 273, 100, 100)
                write_stream('REGEN-HEAT', read_stream('PUMP-REGEN')["T"], read_stream('PUMP-REGEN')["P"],
                             read_stream('PUMP-REGEN')["H"], read_stream('PUMP-REGEN')["S"],
                             read_stream('PUMP-REGEN')["Q"], read_stream('PUMP-REGEN')["G"],
                             read_stream('PUMP-REGEN')["X"])
                self.calc_REGEN_HEAT_T.setText(f'T = {round(float(read_stream("REGEN-HEAT")["T"]), tolerance_exp)}')
                self.calc_REGEN_HEAT_P.setText(f'P = {round(float(read_stream("REGEN-HEAT")["P"]), tolerance_exp)}')
                self.calc_REGEN_HEAT_G.setText(f'G = {round(float(read_stream("REGEN-HEAT")["G"]), tolerance_exp)}')
                self.calc_REGEN_Q.setText(f'Q = 0')
            else:
                regenerator = Regen('TURB-REGEN', 'REGEN-COND', 'PUMP-REGEN', 'REGEN-HEAT', dt_regen, root_tolerance, h_steps)
                self.img_calcer.setGeometry(205, 273, 100, 100)
                regenerator.calc()
                self.calc_REGEN_COND_T.setText(f'T = {round(float(read_stream("REGEN-COND")["T"]), tolerance_exp)}')
                self.calc_REGEN_COND_P.setText(f'P = {round(float(read_stream("REGEN-COND")["P"]), tolerance_exp)}')
                self.calc_REGEN_COND_G.setText(f'G = {round(float(read_stream("REGEN-COND")["G"]), tolerance_exp)}')
                self.calc_REGEN_HEAT_T.setText(f'T = {round(float(read_stream("REGEN-HEAT")["T"]), tolerance_exp)}')
                self.calc_REGEN_HEAT_P.setText(f'P = {round(float(read_stream("REGEN-HEAT")["P"]), tolerance_exp)}')
                self.calc_REGEN_HEAT_G.setText(f'G = {round(float(read_stream("REGEN-HEAT")["G"]), tolerance_exp)}')
                self.calc_REGEN_Q.setText(f'Q = {round(float(read_block("REGEN")["Q"]), tolerance_exp)}')
                self.calc_REGEN_DT.setText(f'ΔT = {round(float(read_block("REGEN")["DT"]), tolerance_exp)}')

            heater = Heat('IN-HEAT', 'HEAT-OUT', 'REGEN-HEAT', 'HEAT-TURB', dt_heat, T_gas_out, root_tolerance, h_steps)
            self.img_calcer.setGeometry(70, 135, 100, 100)
            heater.calc()
            self.calc_HEAT_OUT_T.setText(f'T = {round(float(read_stream("HEAT-OUT")["T"]), tolerance_exp)}')
            self.calc_HEAT_OUT_P.setText(f'P = {round(float(read_stream("HEAT-OUT")["P"]), tolerance_exp)}')
            self.calc_HEAT_OUT_G.setText(f'G = {round(float(read_stream("HEAT-OUT")["G"]), tolerance_exp)}')
            self.calc_HEAT_TURB_T.setText(f'T = {round(float(read_stream("HEAT-TURB")["T"]), tolerance_exp)}')
            self.calc_HEAT_TURB_P.setText(f'P = {round(float(read_stream("HEAT-TURB")["P"]), tolerance_exp)}')
            self.calc_HEAT_TURB_G.setText(f'G = {round(float(read_stream("HEAT-TURB")["G"]), tolerance_exp)}')
            self.calc_HEAT_Q.setText(f'Q = {round(float(read_block("HEATER")["Q"]), tolerance_exp)}')
            self.calc_HEAT_DT.setText(f'ΔT = {round(float(read_block("HEATER")["DT"]), tolerance_exp)}')

            turbine = Turb('HEAT-TURB', 'TURB-REGEN', t_q(T_cond, 0, X_cond)["P"], kpd_turb)
            self.img_calcer.setGeometry(315, 127, 100, 100)
            turbine.calc()
            self.calc_TURB_REGEN_T.setText(f'T = {round(float(read_stream("TURB-REGEN")["T"]), tolerance_exp)}')
            self.calc_TURB_REGEN_P.setText(f'P = {round(float(read_stream("TURB-REGEN")["P"]), tolerance_exp)}')
            self.calc_TURB_REGEN_G.setText(f'G = {round(float(read_stream("TURB-REGEN")["G"]), tolerance_exp)}')
            self.calc_TURB_N.setText(f'N = {round(float(read_block("TURBINE")["Q"]), tolerance_exp)}')

            regenerator = Regen('TURB-REGEN', 'REGEN-COND', 'PUMP-REGEN', 'REGEN-HEAT', dt_regen, root_tolerance, h_steps)
            self.img_calcer.setGeometry(205, 273, 100, 100)
            regenerator.calc()
            self.calc_REGEN_COND_T.setText(f'T = {round(float(read_stream("REGEN-COND")["T"]), tolerance_exp)}')
            self.calc_REGEN_COND_P.setText(f'P = {round(float(read_stream("REGEN-COND")["P"]), tolerance_exp)}')
            self.calc_REGEN_COND_G.setText(f'G = {round(float(read_stream("REGEN-COND")["G"]), tolerance_exp)}')
            self.calc_REGEN_HEAT_T.setText(f'T = {round(float(read_stream("REGEN-HEAT")["T"]), tolerance_exp)}')
            self.calc_REGEN_HEAT_P.setText(f'P = {round(float(read_stream("REGEN-HEAT")["P"]), tolerance_exp)}')
            self.calc_REGEN_HEAT_G.setText(f'G = {round(float(read_stream("REGEN-HEAT")["G"]), tolerance_exp)}')
            self.calc_REGEN_Q.setText(f'Q = {round(float(read_block("REGEN")["Q"]), tolerance_exp)}')
            self.calc_REGEN_DT.setText(f'ΔT = {round(float(read_block("REGEN")["DT"]), tolerance_exp)}')

            condenser = Cond('REGEN-COND', 'COND-PUMP', 'IN-COND', 'COND-OUT', dt_cond, root_tolerance, h_steps)
            self.img_calcer.setGeometry(350, 380, 100, 100)
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

            balance = (read_block('HEATER')["Q"] + read_block('PUMP')["Q"] - read_block('TURBINE')["Q"] -
                       read_block('CONDENSER')["Q"]) / read_block('HEATER')["Q"]
            self.balance_cumm.append(abs(balance))
            self.balance_ax.clear()
            self.balance_ax.set_title('Невязка по балансу')
            self.balance_ax.set_xlabel('Итерация')
            self.balance_ax.semilogy()
            self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_input.text())), 10 ** 0])
            self.balance_ax.plot(self.balance_cumm)
            self.balance_ax.grid(True)
            self.graph_balance.draw()
            self.graph_balance.flush_events()

            if abs(balance) < cycle_tolerance:
                break

        KPD = (read_block('TURBINE')["Q"] - read_block('PUMP')["Q"]) / read_block('HEATER')["Q"]
        self.kpd_output.setText(f"КПД равен {round(KPD,5)}")

        for i in range(10):
            stream = list(read_stream(str(self.streams_list[i])).values())
            for j in range(6):
                value = str(round(stream[j], tolerance_exp))
                self.table_streams.setItem(i, j+1, QTableWidgetItem(value))
            self.table_streams.setItem(i, 7, QTableWidgetItem(str(stream[6])))
        for i in range(5):
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

        self.tq_regen_ax.clear()
        self.tq_regen_ax.grid(True)
        self.tq_regen_ax.set_title('Регенератор')
        self.tq_regen_ax.set_xlabel('Q, кВт')
        self.tq_regen_ax.set_ylabel('T, °C')
        self.tq_regen_ax.plot(regenerator.TQ()[0], regenerator.TQ()[2], regenerator.TQ()[0], regenerator.TQ()[1])
        self.graph_tq_regen.draw()

        self.tq_cond_ax.clear()
        self.tq_cond_ax.grid(True)
        self.tq_cond_ax.set_title('Конденсатор')
        self.tq_cond_ax.set_xlabel('Q, кВт')
        self.tq_cond_ax.set_ylabel('T, °C')
        self.tq_cond_ax.plot(condenser.TQ()[0], condenser.TQ()[2], condenser.TQ()[0], condenser.TQ()[1])
        self.graph_tq_cond.draw()
        ##

        close_db()
        self.img_calcer.setGeometry(0, 0, 0, 0)
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
