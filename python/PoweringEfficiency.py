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
for i,constant in enumerate(feastfitconstants) :
    feast_fit_function.SetParameter(i,constant)

feast_func_fixedTemp = dict()
for ti in [10,20,30,40,50,60] :
    feast_func_fixedTemp[ti] = ROOT.TF1("feast_fit_function","[0] + [1]*x + [2]*x*x + [3]*x*x*x - (2./25.)*%d"%(ti),0,5)
    feast_func_fixedTemp[ti].SetParameters(*feastfitconstants)

feast_func_fixedCurr = dict()
for i in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0] :
    feast_func_fixedCurr[i] = ROOT.TF1("feast_fit_function","[0] + [1]*%0.1f + [2]*%0.2f + [3]*%0.3f - (2./25.)*x"%(i,i*i,i*i*i),-35,65)
    feast_func_fixedCurr[i].SetParameters(*feastfitconstants)


# New parameterization
feast_fit_function_new = ROOT.TF2("feast_fit_function_new","[0] + [1]*x + [2]*x*x + [3]*x*x*x + [4]*x*x*x*x + [5]*x*y + [6]*y",0,5,5,65)
feastfitconstants_new = []
feastfitconstants_new.append( 45.4342   )
feastfitconstants_new.append( 42.3338   )
feastfitconstants_new.append(-22.9184   )
feastfitconstants_new.append(  5.33573  )
feastfitconstants_new.append( -0.469755 )
feastfitconstants_new.append( -0.0153943)
feastfitconstants_new.append( -0.0193996)
for i,constant in enumerate(feastfitconstants_new) :
    feast_fit_function_new.SetParameter(i,constant)

feast_func_fixedTemp_new = dict()
for ti in [10,20,30,40,50,60] :
    feast_func_fixedTemp_new[ti] = ROOT.TF1("feast_fit_function_new","[0] + [1]*x + [2]*x*x + [3]*x*x*x + [4]*x*x*x*x + [5]*x*%d + [6]*%d"%(ti,ti),0,5)
    feast_func_fixedTemp_new[ti].SetParameters(*feastfitconstants_new)

feast_func_fixedCurr_new = dict()
for i in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0] :
    feast_func_fixedCurr_new[i] = ROOT.TF1("feast_fit_function_new","[0] + [1]*%0.1f + [2]*%0.2f + [3]*%0.3f + [4]*%0.4f + [5]*%0.1f*x + [6]*x"%(i,i*i,i*i*i,i*i*i*i,i),-35,65)
    feast_func_fixedCurr_new[i].SetParameters(*feastfitconstants_new)

descr_Vfeast = 'Minimum Feast input voltage (farthest from EOS)'
VfeastMin = Config.GetDouble('PoweringEfficiency.VfeastMin',10.790,unit='V',description=descr_Vfeast)

# EOS DCDC converter
descr_DCDC2eff = 'Efficiency of EOS DCDC2 converter'
DCDC2eff = Config.GetDouble('PoweringEfficiency.DCDC2eff',0.88,description=descr_DCDC2eff)

ModelVersion = Config.GetStr('PoweringEfficiency.ModelVersion','v01',description='Feast Efficiency Model Version')
if ModelVersion == 'v00' :
    function_used_in_model = feast_fit_function
elif ModelVersion == 'v01' :
    function_used_in_model = feast_fit_function_new
else :
    print 'Error! FEAST function PoweringEfficiency.ModelVersion %s is unknown! Exiting.'%(ModelVersion)
    import sys; sys.exit()

n_errors = [0]
def feasteff(tsensor,iload) :
    if iload > 4 :
        if n_errors[0] <= 5 :
            print 'Warning! Load (%2.2f) is higher than existing data.'%(iload)
        if n_errors[0] == 5 :
            print '(Suppressing additional FEAST efficiency errors)'
        n_errors[0] += 1
        return max(function_used_in_model.Eval(4,tsensor),30)
    return max(function_used_in_model.Eval(iload,tsensor),30)

# Scale factor for the current at a specific collected dose
