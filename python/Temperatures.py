#
# Temperatures
#
import ThermalImpedances
import GlobalSettings
from math import *

# Activation temperature (in kelvin)
tA = 6962.71
# Ref temperature (in Celcius, for consistency with equations)
Tref = -15

# In the nb file, these are =: (set delay), which correspond to functions in python.

def unref(qref,Ts) :
    return qref * (GlobalSettings.kelvin(Ts)/GlobalSettings.kelvin(Tref))**2 * exp(tA * (1./GlobalSettings.kelvin(Tref) - 1./GlobalSettings.kelvin(Ts)))

# Barrel short strip stave

def Tmod(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.Rc * (Peos + Pmod + Ps) + ThermalImpedances.Rm * (Pmod + Ps)

def Teos(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.Rc * (Peos + Pmod + Ps) + ThermalImpedances.Reos * Peos

def Tabc(Pabc,Peos,Pmod,Ps,Tc) :
    return Tmod(Peos,Pmod,Ps,Tc) + Pabc * ThermalImpedances.Rabc

def Thcc(Phcc,Peos,Pmod,Ps,Tc) :
    return Tmod(Peos,Pmod,Ps,Tc) + Phcc * ThermalImpedances.Rhcc

def Tfeast(Pfeast,Peos,Pmod,Ps,Tc) :
    return Tmod(Peos,Pmod,Ps,Tc) + Pfeast * ThermalImpedances.Rfeast

def T0(Peos,Pmod,Tc) :
    return Tc + (Peos + Pmod) * ThermalImpedances.Rc + Pmod * ThermalImpedances.Rm

def Ts(Peos,Pmod,Ps,Tc) :
    return T0(Peos,Pmod,Tc) + Ps * ThermalImpedances.Rt

def Qref(Ts,T0) :
    return (Ts - T0)/ThermalImpedances.Rt * (GlobalSettings.kelvin(-15)/GlobalSettings.kelvin(Ts))**2 * exp(tA * (1./GlobalSettings.kelvin(Ts) - 1./GlobalSettings.kelvin(-15)))
