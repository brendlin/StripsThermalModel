#
# AbcTidBump
#
import ROOT
from math import *

# Scale factor of digital current parametrized through factorization of:
#____________________________________________

# s(T,d,D) = s_overall(T,d) * s_shape(D)
#____________________________________________

# T: temperature of chip [degC]
# d: dose rate [kRad/hr]
# D: collected dose [kRad/cm^2]

#--------------------------------------------
# s_overall(T,d)
#--------------------------------------------
# Fit function used:  a * exp(b*(20 - T))* d^c + 1
# a = 0.38201, b = 0.0245617, c = 0.287121

# x is abc temperature
# y is dose rate (d above)
# f(x,y) is scale factor (TID bump profile)
tid_scale_overall_fit_function = ROOT.TF2("tid_scale_overall_fit_function", "[0] * exp([1]*(20 - x))* y^[2] + 1", -30, -5, 0, 65)
tid_scale_overall_fit_function.SetParameter(0, 0.38201)
tid_scale_overall_fit_function.SetParameter(1, 0.0245617)
tid_scale_overall_fit_function.SetParameter(2, 0.287121)

#--------------------------------------------
# s_shape(D)
#--------------------------------------------
coeff1 = 1.8
coeff2 = 0.4

def norm(c1, c2):
    return (1 - exp(-c1*(log(c2/c1)/(c2-c1)))) - (1 - exp(-c2*(log(c2/c1)/(c2-c1))))
    
def tid_scale_shape(collecteddose):
    return max( (1-exp(-coeff1 * (collecteddose - 400)/1000)) - (1-exp(-coeff2 * (collecteddose-400)/1000)), 0 )/norm(coeff1, coeff2)

#--------------------------------------------
# Combined scalefactor of digital ABC current:
#--------------------------------------------

def tid_scale_combined_factor(T, doserate, collecteddose):
    return 1 + (tid_scale_overall_fit_function.Eval(T, doserate)*tid_scale_shape(collecteddose)

# Plotting
#    canTidProfile = TCanvas("canTidProfile", "TID bump profile", 0, 0, 600, 600)
#    canAbcTid  = TCanvas("canAbcTid", "canAbcTid", 0, 0, 600, 600)
