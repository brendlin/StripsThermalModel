#
# NominalPower
#
import SafetyFactors
import SensorProperties
import GlobalSettings
import Layout
import CableLosses
import FrontEndComponents

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


# Short strip module
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


# Long strip module




# EOS power (including powering efficiency)
# Short strip EOS

def sseosP(Teos) :
    return 1 # Dummy number for now -- fix!

# Long strip EOS



# Stave power
# in Watt, 2x14 modules (including ohmic loss in tape) +2xEOS, nominal (no irradiation and leakage) 
# Tape loss is subtracted from module power and added with proper scaling

# Short strip stave

def ssPstavetape(Tabc,Thcc,Tfeast,d,D) :
    return 1 # Dummy number for now -- fix!

def ssPstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
    return 1 # Dummy number for now -- fix!

ssPstavebare = ssPstave(GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,1,0,0)

# Long strip stave

def lsPstavetape(Tabc,Thcc,Tfeast,d,D) :
    return 1 # Dummy number for now -- fix!

def lsPstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
    return 1 # Dummy number for now -- fix!

lsPstavebare = lsPstave(GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,1,0,0)


# Total barrel power
# including tape and cable losses and safety factor on layout

b1Ptotal = 2 * Layout.nstavesb1 * ssPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
b2Ptotal = 2 * Layout.nstavesb2 * ssPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
b3Ptotal = 2 * Layout.nstavesb3 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
b4Ptotal = 2 * Layout.nstavesb4 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
bPtotal = b1Ptotal + b2Ptotal + b3Ptotal + b4Ptotal
