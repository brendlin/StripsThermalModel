#
# PoweringEfficiency
#

import ROOT
import Config

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

feast_func_fixedTemp = dict()
for ti in [10,20,30,40,50,60] :
    feast_func_fixedTemp[ti] = ROOT.TF1("feast_fit_function","[0] + [1]*x + [2]*x*x + [3]*x*x*x - (2./25.)*%d"%(ti),0,5)
    feast_func_fixedTemp[ti].SetParameters(*feastfitconstants)

descr_Vfeast = 'Feast input voltage'
Vfeast = Config.GetDouble('PoweringEfficiency.Vfeast',10.5,unit='V',description=descr_Vfeast)

# EOS DCDC converter
descr_DCDC2eff = 'Efficiency of EOS DCDC2 converter'
DCDC2eff = Config.GetDouble('PoweringEfficiency.DCDC2eff',0.88,description=descr_DCDC2eff)

n_errors = [0]

def feasteff(tsensor,iload) :
    if iload > 4 :
        if n_errors[0] <= 5 :
            print 'Warning! Load (%2.2f) is higher than existing data.'%(iload)
        if n_errors[0] == 5 :
            print '(Suppressing additional FEAST efficiency errors)'
        n_errors[0] += 1
        return max(feast_fit_function.Eval(4,tsensor),30)
    return max(feast_fit_function.Eval(iload,tsensor),30)

# Scale factor for the current at a specific collected dose
