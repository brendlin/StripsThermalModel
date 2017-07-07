#
# AbcTidBump
#
#import ROOT
#from math import *
import math

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
tid_scale_overall_fit_constants = []
tid_scale_overall_fit_constants.append(0.38201)
tid_scale_overall_fit_constants.append(0.0245617)
tid_scale_overall_fit_constants.append(0.287121)

# x is abc temperature
# y is dose rate (d above)
# f(x,y) is scale factor (TID bump profile)
# tid_scale_overall_fit_function = ROOT.TF2("tid_scale_overall_fit_function", "[0] * exp([1]*(20 - x))* y^[2] + 1", -30, -5, 0, 65)
# tid_scale_overall_fit_function.SetParameters(*tid_scale_overall_fit_constants)

def tid_scale_overall_fit_function_Python(T, doserate) :
    a = tid_scale_overall_fit_constants[0]
    b = tid_scale_overall_fit_constants[1]
    c = tid_scale_overall_fit_constants[2]
    return a * math.exp(b*(20.-T)) * math.pow(doserate,c) + 1

#--------------------------------------------
# s_shape(D)
#--------------------------------------------
coeff1 = 1.8
coeff2 = 0.4

def norm(c1, c2):
    return (1 - math.exp(-c1*(log(c2/c1)/(c2-c1)))) - (1 - math.exp(-c2*(log(c2/c1)/(c2-c1))))
    
def tid_scale_shape(collecteddose):
    return max( (1-math.exp(-coeff1 * (collecteddose - 400)/1000.)) - (1-math.exp(-coeff2 * (collecteddose-400)/1000.)), 0 )/float(norm(coeff1, coeff2))

#--------------------------------------------
# Combined scalefactor of digital ABC current:
#--------------------------------------------

def tid_scale_combined_factor(T, doserate, collecteddose):
    return 1 + (tid_scale_overall_fit_function.Eval(T, doserate)-1)*tid_scale_shape(collecteddose)

def tid_scale_combined_factor_Python(T, doserate, collecteddose) :
    return 1 + (tid_scale_overall_fit_function_Python(T, doserate)-1)*tid_scale_shape(collecteddose)
