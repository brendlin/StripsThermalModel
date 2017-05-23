#
# NominalPower
#
import SafetyFactors
import SensorProperties
import GlobalSettings
import Layout
import CableLosses
import FrontEndComponents
import PoweringEfficiency
import EOSComponents
import AbcTidBump

# Moving nomsensorT to GlobalSettings since it seems more appropriate there.
# nomsensorT = 0


# Module power (including powering efficiency)
# General parameters

Rtape = 0.01 # tape resistance is 0.01 Ohm per module worst case
Pamac = (FrontEndComponents.amac15V * FrontEndComponents.amac15I + FrontEndComponents.amac3V * FrontEndComponents.amac3I) * (1 + SafetyFactors.safetycurrent)

# Power in the FEAST chip due to AMAC supply
Pfamac  = (PoweringEfficiency.Vfeast - FrontEndComponents.amac15V) * FrontEndComponents.amac15I
Pfamac += (PoweringEfficiency.Vfeast - FrontEndComponents.amac3V ) * FrontEndComponents.amac3I

def Prhv(Is) :
    return SensorProperties.Rhv*Is*Is

Phvmux = SensorProperties.vbias*SensorProperties.vbias/float(SensorProperties.Rhvmux + SensorProperties.Rhv)

def Phv(Is) :
    return Phvmux + Prhv(Is)


# Short strip module
# module Short strip

def ssIabc(Tabc,d,D) :
    return 20 * (AbcTidBump.tid_scale_combined_factor(Tabc, d, D) * FrontEndComponents.abcId + FrontEndComponents.abcIa)

def ssPabc(Tabc,d,D) :
    return FrontEndComponents.hybridV * ssIabc(Tabc, d, D)

def ssIhcc(Thcc,d,D) :
    return 2 * (AbcTidBump.tid_scale_combined_factor(Thcc, d, D) * FrontEndComponents.hccId + FrontEndComponents.hccIa)

def ssPhcc(Thcc,d,D) :
    return FrontEndComponents.hybridV * ssIhcc(Thcc, d, D)

def ssIfeast(Tabc,Thcc,d,D) :
    return ssIabc(Tabc, d, D) + ssIhcc(Thcc, d, D)

def ssPfeast(Tabc,Thcc,Tfeast,d,D) :
    return Pfamac + ( ssPabc(Tabc,d,D) + ssPhcc(Thcc,d,D) ) * (100 / float( PoweringEfficiency.feasteff(Tfeast,ssIfeast(Tabc,Thcc,d,D)) ) - 1)

def ssIdig(Tabc,Thcc,d,D) :
    return 20 * AbcTidBump.tid_scale_combined_factor(Tabc,d,D) * FrontEndComponents.abcId + 2 * AbcTidBump.tid_scale_combined_factor(Thcc,d,D) * FrontEndComponents.hccId

def ssItape(Tabc,Thcc,Tfeast,d,D) :
    return ( ssPabc(Tabc, d, D) + ssPhcc(Thcc, d, D) + Pamac + ssPfeast(Tabc,Thcc,Tfeast,d,D) ) / float(PoweringEfficiency.Vfeast)

def ssPtape(Tabc,Thcc,Tfeast,d,D) :
    return (Layout.nmod * ssItape(Tabc,Thcc,Tfeast,d,D) )**2 * Rtape

def ssPmod(Tabc,Thcc,Tfeast,d,D,Is) :
    return ssPabc(Tabc,d,D) + ssPhcc(Thcc,d,D) + Pamac + ssPfeast(Tabc,Thcc,Tfeast,d,D) + ssPtape(Tabc,Thcc,Tfeast,d,D) + Phv(Is)


# Long strip module

def lsIabc(Tabc,d,D) :
    return 10 * (AbcTidBump.tid_scale_combined_factor(Tabc, d, D) * FrontEndComponents.abcId + FrontEndComponents.abcIa)

def lsPabc(Tabc,d,D) :
    return FrontEndComponents.hybridV * lsIabc(Tabc, d, D)

def lsIhcc(Thcc,d,D) :
    return (AbcTidBump.tid_scale_combined_factor(Thcc, d, D) * FrontEndComponents.hccId + FrontEndComponents.hccIa)

def lsPhcc(Thcc,d,D) :
    return FrontEndComponents.hybridV * lsIhcc(Thcc, d, D)

def lsIfeast(Tabc,Thcc,d,D) :
    return lsIabc(Tabc, d, D) + lsIhcc(Thcc, d, D)

def lsPfeast(Tabc,Thcc,Tfeast,d,D) :
    return Pfamac + ( lsPabc(Tabc,d,D) + lsPhcc(Thcc,d,D) ) * (100 / float( PoweringEfficiency.feasteff(Tfeast,lsIfeast(Tabc,Thcc,d,D)) ) - 1)

def lsIdig(Tabc,Thcc,d,D) :
    return (10 * AbcTidBump.tid_scale_combined_factor(Tabc,d,D) * FrontEndComponents.abcId + AbcTidBump.tid_scale_combined_factor(Thcc,d,D) * FrontEndComponents.hccId)

def lsItape(Tabc,Thcc,Tfeast,d,D) :
    return ( lsPabc(Tabc, d, D) + lsPhcc(Thcc, d, D) + Pamac + lsPfeast(Tabc,Thcc,Tfeast,d,D) ) / float(PoweringEfficiency.Vfeast)

def lsPtape(Tabc,Thcc,Tfeast,d,D) :
    return (Layout.nmod * lsItape(Tabc,Thcc,Tfeast,d,D) )**2 * Rtape

def lsPmod(Tabc,Thcc,Tfeast,d,D,Is) :
    return lsPabc(Tabc,d,D) + lsPhcc(Thcc,d,D) + Pamac + lsPfeast(Tabc,Thcc,Tfeast,d,D) + lsPtape(Tabc,Thcc,Tfeast,d,D) + Phv(Is)



# EOS power (including powering efficiency)
# Short strip EOS

sseosI  = ( (2 * EOSComponents.lpgbtI + 2 * EOSComponents.gbld12I) / float(PoweringEfficiency.DCDC2eff) ) * (EOSComponents.eosV12/float(EOSComponents.eosV25))
sseosI += EOSComponents.gbtiaI + 2 * EOSComponents.gbld25I

def sseosP(Teos) :
    return EOSComponents.eosV25 * sseosI * 100 / float(PoweringEfficiency.feasteff(Teos, sseosI))



# Long strip EOS

lseosI  = ( (EOSComponents.lpgbtI + EOSComponents.gbld12I) / float(PoweringEfficiency.DCDC2eff) ) * (EOSComponents.eosV12/float(EOSComponents.eosV25))
lseosI += EOSComponents.gbtiaI + EOSComponents.gbld25I

def lseosP(Teos) :
    return EOSComponents.eosV25 * lseosI * 100 / float(PoweringEfficiency.feasteff(Teos, lseosI))



# Stave power
# in Watt, 2x14 modules (including ohmic loss in tape) +2xEOS, nominal (no irradiation and leakage) 
# Tape loss is subtracted from module power and added with proper scaling

# Short strip stave

def ssPstavetape(Tabc,Thcc,Tfeast,d,D) :
    n2_from_1_to_nmod = list( n**2 for n in range(1,Layout.nmod+1) )
    sum_n2_from_1_to_nmod = sum(n2_from_1_to_nmod)
    return (ssPtape(Tabc, Thcc, Tfeast, d, D) / float(Layout.nmod)**2 ) * sum_n2_from_1_to_nmod

def ssPstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
    return 2 * (Layout.nmod * (ssPmod(Tabc,Thcc,Tfeast,d,D,Is) - ssPtape(Tabc,Thcc,Tfeast,d,D) +
                               Is * SensorProperties.vbias) + ssPstavetape(Tabc,Thcc,Tfeast,d,D) + sseosP(Teos) )

ssPstavebare = ssPstave(GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,
                        GlobalSettings.nomsensorT,1,0,0)

# Long strip stave

def lsPstavetape(Tabc,Thcc,Tfeast,d,D) :
    n2_from_1_to_nmod = list( n**2 for n in range(1,Layout.nmod+1) )
    sum_n2_from_1_to_nmod = sum(n2_from_1_to_nmod)
    return (lsPtape(Tabc, Thcc, Tfeast, d, D) / float(Layout.nmod)**2 ) * sum_n2_from_1_to_nmod

def lsPstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
    return 2 * (Layout.nmod * (lsPmod(Tabc,Thcc,Tfeast,d,D,Is) - lsPtape(Tabc,Thcc,Tfeast,d,D) +
                               Is * SensorProperties.vbias) + lsPstavetape(Tabc,Thcc,Tfeast,d,D) + lseosP(Teos) )

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
