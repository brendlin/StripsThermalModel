#
# NominalPower
#
import Config
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

nabc   = Config.GetInt('NominalPower.nabc')
nhcc   = Config.GetInt('NominalPower.nhcc')
nlpgbt = Config.GetInt('NominalPower.nlpgbt')
ngbld  = Config.GetInt('NominalPower.ngbld')

# Short strip module
# module Short strip

def Iabc(Tabc,d,D) :
    return nabc * (AbcTidBump.tid_scale_combined_factor(Tabc, d, D) * FrontEndComponents.abcId + FrontEndComponents.abcIa)

def Pabc(Tabc,d,D) :
    return FrontEndComponents.hybridV * Iabc(Tabc, d, D)

def Ihcc(Thcc,d,D) :
    return nhcc * (AbcTidBump.tid_scale_combined_factor(Thcc, d, D) * FrontEndComponents.hccId + FrontEndComponents.hccIa)

def Phcc(Thcc,d,D) :
    return FrontEndComponents.hybridV * Ihcc(Thcc, d, D)

def Ifeast(Tabc,Thcc,d,D) :
    return Iabc(Tabc, d, D) + Ihcc(Thcc, d, D)

def Pfeast(Tabc,Thcc,Tfeast,d,D) :
    return Pfamac + ( Pabc(Tabc,d,D) + Phcc(Thcc,d,D) ) * (100 / float( PoweringEfficiency.feasteff(Tfeast,Ifeast(Tabc,Thcc,d,D)) ) - 1)

def Idig(Tabc,Thcc,d,D) :
    return nabc * AbcTidBump.tid_scale_combined_factor(Tabc,d,D) * FrontEndComponents.abcId + nhcc * AbcTidBump.tid_scale_combined_factor(Thcc,d,D) * FrontEndComponents.hccId

def Itape(Tabc,Thcc,Tfeast,d,D) :
    return ( Pabc(Tabc, d, D) + Phcc(Thcc, d, D) + Pamac + Pfeast(Tabc,Thcc,Tfeast,d,D) ) / float(PoweringEfficiency.Vfeast)

def Ptape(Tabc,Thcc,Tfeast,d,D) :
    return (Layout.nmod * Itape(Tabc,Thcc,Tfeast,d,D) )**2 * Rtape

def Pmod(Tabc,Thcc,Tfeast,d,D,Is) :
    return Pabc(Tabc,d,D) + Phcc(Thcc,d,D) + Pamac + Pfeast(Tabc,Thcc,Tfeast,d,D) + Ptape(Tabc,Thcc,Tfeast,d,D) + Phv(Is)

# EOS power (including powering efficiency)

eosI  = ( (nlpgbt * EOSComponents.lpgbtI + ngbld * EOSComponents.gbld12I) / float(PoweringEfficiency.DCDC2eff) ) * (EOSComponents.eosV12/float(EOSComponents.eosV25))
eosI += EOSComponents.gbtiaI + ngbld * EOSComponents.gbld25I

def eosP(Teos) :
    return EOSComponents.eosV25 * eosI * 100 / float(PoweringEfficiency.feasteff(Teos, eosI))

# Stave power
# in Watt, 2x14 modules (including ohmic loss in tape) +2xEOS, nominal (no irradiation and leakage) 
# Tape loss is subtracted from module power and added with proper scaling

def Pstavetape(Tabc,Thcc,Tfeast,d,D) :
    n2_from_1_to_nmod = list( n**2 for n in range(1,Layout.nmod+1) )
    sum_n2_from_1_to_nmod = sum(n2_from_1_to_nmod)
    return (Ptape(Tabc, Thcc, Tfeast, d, D) / float(Layout.nmod)**2 ) * sum_n2_from_1_to_nmod

def Pstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
    return 2 * (Layout.nmod * (Pmod(Tabc,Thcc,Tfeast,d,D,Is) - Ptape(Tabc,Thcc,Tfeast,d,D) +
                               Is * SensorProperties.vbias) + Pstavetape(Tabc,Thcc,Tfeast,d,D) + eosP(Teos) )

Pstavebare = Pstave(GlobalSettings.nomsensorT,
                    GlobalSettings.nomsensorT,
                    GlobalSettings.nomsensorT,
                    GlobalSettings.nomsensorT,1,0,0)

# Total barrel power
# including tape and cable losses and safety factor on layout

# b1Ptotal = 2 * Layout.nstavesb1 * ssPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b2Ptotal = 2 * Layout.nstavesb2 * ssPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b3Ptotal = 2 * Layout.nstavesb3 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b4Ptotal = 2 * Layout.nstavesb4 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# bPtotal = b1Ptotal + b2Ptotal + b3Ptotal + b4Ptotal
