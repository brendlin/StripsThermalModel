#
# PoweringEfficiency
#

import ROOT

# Fit function used: a+b Subscript[i, load]+c Subsuperscript[i, load, 2]+d Subsuperscript[i, load, 3]-(2 T)/25, with the coefficients:
# a=58.0448, b=29.6715, c=-12.4747, d=1.40142
feastfitconstants = []
feastfitconstants.append( 58.0448 )
feastfitconstants.append( 29.6715 )
feastfitconstants.append(-12.4747 )
feastfitconstants.append(  1.40142)

# x is load current
# y is temperature
# f(x,y) is efficiency
feast_fit_function = ROOT.TF2("feast_fit_function","[0] + [1]*x + [2]*x*x + [3]*x*x*x - (2./25.)*y",0,5,5,65)
feast_fit_function.SetParameter(0,feastfitconstants[0])
feast_fit_function.SetParameter(1,feastfitconstants[1])
feast_fit_function.SetParameter(2,feastfitconstants[2])
feast_fit_function.SetParameter(3,feastfitconstants[3])

Vfeast = 10.5 # Feast input voltage
DCDC2eff = 0.88 # DCDC2 efficiency

def feasteff(tsensor,iload) :
    return feastfitconstants[0] + feastfitconstants[1]*iload + feastfitconstants[2]*iload*iload + feastfitconstants[2]*iload*iload*iload - (2./25.) * tsensor

# Scale factor for the current at a specific collected dose
