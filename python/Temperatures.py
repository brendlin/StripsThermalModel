#
# Temperatures
#
import ThermalImpedances

# Activation temperature (in Kelvin)
tA = 6962.71

# In the nb file, these are =: (set delay), which correspond to functions in python.

# Barrel short strip stave

def ssTmod(Peos,Pmod,Ps,Tc) :
    return Tc + ThermalImpedances.ssRc * (Peos + Pmod + Ps) + ThermalImpedances.ssRm * (Pmod + Ps)

def ssTeos(Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def ssTabc(Pabc,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def ssThcc(Phcc,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def ssTfeast(Pfeast,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def ssT0(Peos,Pmod,Tc) :
    return 1 # Dummy number for now -- fix!

def ssTs(Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def Qref(Ts,T0) :
    return 1 # Dummy number for now -- fix!


# Barrel long strip stave

def lsTmod(Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def lsTeos(Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def lsTabc(Pabc,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def lsThcc(Phcc,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def lsTfeast(Pfeast,Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!

def lsT0(Peos,Pmod,Tc) :
    return 1 # Dummy number for now -- fix!

def lsTs(Peos,Pmod,Ps,Tc) :
    return 1 # Dummy number for now -- fix!
