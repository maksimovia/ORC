import prop

# class pump:
#     def __init__(self,stream1,stream2,Pout,KPDpump,fluid,streams):
#         self.stream1 = stream1
#         self.stream2 = stream2
#         self.streams = streams
#         self.Pout = Pout
#         self.KPDpump = KPDpump
#         self.fluid = fluid
        
#     def calc(self):
#         P1 = self.streams.at[self.stream1,"P"]
#         H1 = self.streams.at[self.stream1,"H"]
#         S1 = self.streams.at[self.stream1,"S"]
#         G = self.streams.at[self.stream1,"G"]
#         H2t = prop.p_s(self.Pout,S1,self.fluid)["H"]
#         H2 = H1 + (H2t-H1)/self.KPDpump
#         T2 = prop.h_p(H2,self.Pout,self.fluid)["T"]
#         S2 = prop.h_p(H2,self.Pout,self.fluid)["S"]
#         self.streams.loc[self.stream2, "T":"G"] = [T2, self.Pout, H2, S2, G]

        
class pump:
    def calc(stream1,stream2,Pout,KPDpump,fluid,streams,blocks):
        P1 = streams.at[stream1,"P"]
        H1 = streams.at[stream1,"H"]
        S1 = streams.at[stream1,"S"]
        G = streams.at[stream1,"G"]
        H2t = prop.p_s(Pout,S1,fluid)["H"]
        H2 = H1 + (H2t-H1)/KPDpump
        T2 = prop.h_p(H2,Pout,fluid)["T"]
        S2 = prop.h_p(H2,Pout,fluid)["S"]
        streams.loc[stream2, "T":"G"] = [T2, Pout, H2, S2, G]
        N = G*(H2-H1)
        blocks.loc['PUMP', 'N'] = N