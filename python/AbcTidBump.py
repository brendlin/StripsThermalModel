#
# AbcTidBump
#
import ROOT
from math import *
import Config

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
tid_scalefactor_constants = []
tid_scalefactor_constants.append(0.38201)
tid_scalefactor_constants.append(0.0245617)
tid_scalefactor_constants.append(0.287121)

# x is abc temperature
# y is dose rate (d above)
# f(x,y) is scale factor (TID bump profile)

tid_scalefactor_GeorgGraham_tf2 = ROOT.TF2("tid_scalefactor", "[0] * exp([1]*(20 - x))* y^[2] + 1", -30, -5, 0, 65)
tid_scalefactor_GeorgGraham_tf2.SetParameters(*tid_scalefactor_constants)

tid_scalefactor_GeorgGraham_tf2_fixedTemp = dict()
for ti in [-10,-15,-25] :
    # Projection in plane T = ti degC
    tid_scalefactor_GeorgGraham_tf2_fixedTemp[ti] = ROOT.TF1("tid_scalefactor_t%d"%(ti),("[0] * exp([1]*(20-%d))* x^[2] + 1"%(ti)).replace('--','+'), 0, 65)
    tid_scalefactor_GeorgGraham_tf2_fixedTemp[ti].SetParameters(*tid_scalefactor_constants)

#--------------------------------------------
# s_shape(D)
#--------------------------------------------
coeff1 = 1.8
coeff2 = 0.4

def norm(c1, c2):
    return (1 - exp(-c1*(log(c2/c1)/(c2-c1)))) - (1 - exp(-c2*(log(c2/c1)/(c2-c1))))
    
def tid_scalefactor_GeorgGraham(T, doserate, collecteddose) :
    return tid_scalefactor_GeorgGraham_tf2.Eval(T,doserate)

def tid_shape_GeorgGraham(T, doserate, collecteddose):
    return max( (1-exp(-coeff1 * (collecteddose - 400)/1000.)) - (1-exp(-coeff2 * (collecteddose-400)/1000.)), 0 )/float(norm(coeff1, coeff2))

def tid_scalePlusShape_GeorgGraham(T, doserate, collecteddose):
    return 1 + (tid_scalefactor_GeorgGraham_tf2.Eval(T, doserate)-1)*tid_shape_GeorgGraham(T, doserate, collecteddose)


##
# New TID parameterization
##
ROOT.gROOT.LoadMacro('share/toyTIDbumpShape.C')
def tid_scalefactor_Kyle(T, doserate, collecteddose) :
    return 1+ROOT.getBumpHeightScale(doserate,T)

def tid_shape_Kyle(T, dosereate, collecteddose) :
    # these numbers (0.47 tailspeed, 0.2 peak position) are taken from toyTIDbumpShape
    # Our collected dose is in kRad, but theirs is in MRad
    value = ROOT.getShape(1.,0.47,0.2).Eval(collecteddose/1000.)
    norm = ROOT.getShape(1.,0.47,0.2).Eval(999999.)
    return value/float(norm) - 1.

def tid_scalePlusShape_Kyle(T, doserate, collecteddose) :
    return ROOT.tid_new(T,doserate,collecteddose)

##
# Interface with rest of program:
##

ModelVersion = Config.GetStr('AbcTidBump.ModelVersion','v00',description='TID parameterization Model Version')
if ModelVersion == 'v00' :
    scalefactor_used_in_model = tid_scalefactor_GeorgGraham
    shape_used_in_model = tid_shape_GeorgGraham
    parameterization_used_in_model = tid_scalePlusShape_GeorgGraham
elif ModelVersion == 'v01' :
    scalefactor_used_in_model = tid_scalefactor_Kyle
    shape_used_in_model = tid_shape_Kyle
    parameterization_used_in_model = tid_scalePlusShape_Kyle
else :
    print 'Error! TID parameterization AbcTidBump.ModelVersion %s is unknown! Exiting.'%(ModelVersion)
    import sys; sys.exit()

def SaveAndReturn(function,a,b,c,the_dict) :
    if (a in the_dict.keys()) and (b in the_dict[a].keys()) and (c in the_dict[a][b].keys()) :
        return the_dict[a][b][c]
    result = function(a,b,c)
    if a not in the_dict      .keys() : the_dict[a]       = dict()
    if b not in the_dict[a]   .keys() : the_dict[a][b]    = dict()
    if c not in the_dict[a][b].keys() : the_dict[a][b][c] = result
    return result

saved_scalefactor = dict()
saved_shape = dict()
saved_scalePlusShape = dict()

def tid_scalefactor(T,doserate,collecteddose) :
    return SaveAndReturn(scalefactor_used_in_model,T,doserate,collecteddose,saved_scalefactor)

def tid_shape(T,doserate,collecteddose) :
    return SaveAndReturn(shape_used_in_model,T,doserate,collecteddose,saved_shape)

def tid_scalePlusShape(T, doserate, collecteddose) :
    return SaveAndReturn(parameterization_used_in_model,T,doserate,collecteddose,saved_scalePlusShape)
