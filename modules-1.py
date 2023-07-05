import prop
from sqlite import read_stream, write_stream

tolerance = 10 ** -5
h_step = 20


def root(func, a, b, root_tol):
    while func(b)-func(a) > root_tol:
        dx = (b-a)/2
        x = a + dx
        if func(a)*func(x) < 0:
            b = x
        else:
            a = x
    return x


class HEATER:
    def __init__(self, stream11, stream12, stream21, stream22, dt, t_out):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.t_out = t_out

    def calc(self):
        T11 = read_stream(self.stream11)['T']
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']

        T21 = read_stream(self.stream21)['T']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']

        T12 = self.t_out
        H12 = prop.t_p(T12, P11)["H"]


        write_stream('HEAT-OUT',T12,P12,H12,S12,Q12,G1)
        write_stream('HEAT-TURB',T22,P22,H22,S22,Q22,G2)
        pass



    def TQ(self):
        pass


# class REGEN:
#     def __init__(self):
#     def calc(self):
#     def TQ(self):
#         pass
#
#
# class CONDENSER:
#     def __init__(self):
#     def calc(self):
#     def TQ(self):
#         pass
#
#
# class PUMP:
#     def __init__(self):
#     def calc(self):
#     def HS(self):
#         pass
#
#
# class TURBINE:
#     def __init__(self):
#     def calc(self):
#     def HS(self):
#         pass