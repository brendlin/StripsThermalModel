#
# NominalPower
#
import SensorProperties

# Moving nomsensorT to GlobalSettings since it seems more appropriate there.
# nomsensorT = 0


# Module power (including powering efficiency)
# General parameters

Rtape = 0.01 # tape resistance is 0.01 Ohm per module worst case
Pamac = 1 # FIX ME
Pfamac = 1 # FIX ME # Power in the FEAST chip due to AMAC supply*)

def Prhv(Is) :
    return SensorProperties.Rhv*Is*Is

Phvmux = SensorProperties.vbias*SensorProperties.vbias/float(SensorProperties.Rhvmux + SensorProperties.Rhv)

def Phv(Is) :
    return Phvmux + Prhv(Is)


# Shortstripmodule
# module Short strip

def ssIabc(Tabc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPabc(Tabc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssIhcc(Thcc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPhcc(Thcc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssIfeast(Tabc,Thcc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPfeast(Tabc,Thcc,Tfeast,d,D) :
    return 1 # Dummy number for now -- fix!

def ssIdig(Tabc,Thcc,d,D) :
    return 1 # Dummy number for now -- fix!

def ssItape(Tabc,Thcc,Tfeast,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPtape(Tabc,Thcc,Tfeast,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPmod(Tabc,Thcc,Tfeast,d,D,Is) :
    return 1 # Dummy number for now -- fix!



# EOS power (including powering efficiency)
# Short strip EOS

def sseosP(Teos) :
    return 1 # Dummy number for now -- fix!
