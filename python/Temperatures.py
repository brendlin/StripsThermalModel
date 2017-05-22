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

def ssTmod(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.ssRc * (Peos + Pmod + Ps) + ThermalImpedances.ssRm * (Pmod + Ps)

def ssTeos(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.ssRc * (Peos + Pmod + Ps) + ThermalImpedances.ssReos * Peos

def ssTabc(Pabc,Peos,Pmod,Ps,Tc) :
    return ssTmod(Peos,Pmod,Ps,Tc) + Pabc * ThermalImpedances.ssRabc

def ssThcc(Phcc,Peos,Pmod,Ps,Tc) :
    return ssTmod(Peos,Pmod,Ps,Tc) + Phcc * ThermalImpedances.ssRhcc

def ssTfeast(Pfeast,Peos,Pmod,Ps,Tc) :
    return ssTmod(Peos,Pmod,Ps,Tc) + Pfeast * ThermalImpedances.ssRfeast

def ssT0(Peos,Pmod,Tc) :
    return Tc + (Peos + Pmod) * ThermalImpedances.ssRc + Pmod * ThermalImpedances.ssRm

def ssTs(Peos,Pmod,Ps,Tc) :
    return ssT0(Peos,Pmod,Tc) + Ps * ThermalImpedances.ssRt

def Qref(Ts,T0) :
    return (Ts - T0)/ThermalImpedances.ssRt * (GlobalSettings.kelvin(-15)/GlobalSettings.kelvin(Ts))**2 * exp(tA * (1./GlobalSettings.kelvin(Ts) - 1./GlobalSettings.kelvin(-15)))


# Barrel long strip stave

def lsTmod(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.lsRc * (Peos + Pmod + Ps) + ThermalImpedances.lsRm * (Pmod + Ps)

def lsTeos(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.lsRc * (Peos + Pmod + Ps) + ThermalImpedances.lsReos * Peos

def lsTabc(Pabc,Peos,Pmod,Ps,Tc) :
    return lsTmod(Peos,Pmod,Ps,Tc) + Pabc * ThermalImpedances.lsRabc

def lsThcc(Phcc,Peos,Pmod,Ps,Tc) :
    return lsTmod(Peos,Pmod,Ps,Tc) + Phcc * ThermalImpedances.lsRhcc

def lsTfeast(Pfeast,Peos,Pmod,Ps,Tc) :
    return lsTmod(Peos,Pmod,Ps,Tc) + Pfeast * ThermalImpedances.lsRfeast

def lsT0(Peos,Pmod,Tc) :
    return Tc + (Peos + Pmod) * ThermalImpedances.lsRc + Pmod * ThermalImpedances.lsRm

def lsTs(Peos,Pmod,Ps,Tc) :
    return lsT0(Peos,Pmod,Tc) + Ps * ThermalImpedances.lsRt

