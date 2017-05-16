#
# AbcTidBump
#
import ROOT

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
# y is dose rate
# f(x,y) is scale factor (TID bump profile)
tid_scale_overall_fit_function = ROOT.TF2("tid_scale_overall_fit_function", "[0] * exp([1]*(20 - x))* y^[2] + 1", -30, -5, 0, 65)
tid_scale_overall_fit_function.SetParameter(0, 0.38201)
tid_scale_overall_fit_function.SetParameter(1, 0.0245617)
tid_scale_overall_fit_function.SetParameter(2, 0.287121)

#--------------------------------------------
# s_shape(D)
#--------------------------------------------

