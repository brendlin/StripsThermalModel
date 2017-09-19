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

Rtape_descr = 'tape resistance is 0.01 $\Omega$ per module worst case'
Rtape = Config.GetDouble('NominalPower.Rtape',0.01,unit='$\Omega$',description=Rtape_descr)
Pamac = (FrontEndComponents.amac15V * FrontEndComponents.amac15I + FrontEndComponents.amac3V * FrontEndComponents.amac3I)

# Power in the FEAST chip due to AMAC supply
Pfamac  = (PoweringEfficiency.Vfeast - FrontEndComponents.amac15V) * FrontEndComponents.amac15I
Pfamac += (PoweringEfficiency.Vfeast - FrontEndComponents.amac3V ) * FrontEndComponents.amac3I

def Phv_R(Is) :
    return SensorProperties.Rhv*Is*Is

Phv_Mux = SensorProperties.vbias*SensorProperties.vbias/float(SensorProperties.Rhvmux + SensorProperties.Rhv)

nabc   = Config.GetInt('NominalPower.nabc',description='Number of ABCs on the hybrid')
nhcc   = Config.GetInt('NominalPower.nhcc',description='Number of HCCs on the hybrid')
nlpgbt = Config.GetInt('NominalPower.nlpgbt',description='Number of lpGBTs on this module\'s EOS')
ngbld  = Config.GetInt('NominalPower.ngbld',description='Number of GBLDs on this module\'s EOS')
ngbtia = Config.GetInt('NominalPower.ngbtia',description='Number of GBTIAs on this module\'s EOS')

# nfeast in the module. To be used in determining the FEAST efficiency due to possible reduction in current
nfeast = Config.GetInt('NominalPower.nfeast',1,description='Number of FEAST chips on the hybrid')

# Short strip module
# module Short strip

def Iabc_digital(Tabc,d,D) :
    return nabc * (AbcTidBump.tid_scalePlusShape(Tabc, d, D) * FrontEndComponents.abcId)

def Iabc(Tabc,d,D) :
    return Iabc_digital(Tabc,d,D) + (nabc * FrontEndComponents.abcIa)

def Pabc(Tabc,d,D) :
    return FrontEndComponents.hybridV * Iabc(Tabc, d, D)

def Ihcc_digital(Thcc,d,D) :
    return nhcc * (AbcTidBump.tid_scalePlusShape(Thcc, d, D) * FrontEndComponents.hccId)

def Ihcc(Thcc,d,D) :
    return Ihcc_digital(Thcc,d,D) + (nhcc * FrontEndComponents.hccIa)

def Phcc(Thcc,d,D) :
    return FrontEndComponents.hybridV * Ihcc(Thcc, d, D)

# TOTAL feast current (load) given n feasts on the module
def Ifeast(Tabc,Thcc,d,D) :
    return Iabc(Tabc, d, D) + Ihcc(Thcc, d, D)

# TOTAL feast power (due to ABC,HCC) given n feasts on the module
def Pfeast_ABC_HCC(Tabc,Thcc,Tfeast,d,D) :
    return ( Pabc(Tabc,d,D) + Phcc(Thcc,d,D) ) * (100 / float( PoweringEfficiency.feasteff(Tfeast,Ifeast(Tabc,Thcc,d,D)/float(nfeast)) ) - 1)

# TOTAL feast power given n feasts on the module
def Pfeast(Tabc,Thcc,Tfeast,d,D) :
    return Pfamac + Pfeast_ABC_HCC(Tabc,Thcc,Tfeast,d,D)

def Idig(Tabc,Thcc,d,D) :
    return Iabc_digital(Tabc,d,D) + Ihcc_digital(Thcc,d,D)

# Input from module FEAST and LDOs (e.g. load on the tape)
def Itape(Tabc,Thcc,Tfeast,d,D) :
    return ( Pabc(Tabc, d, D) + Phcc(Thcc, d, D) + Pamac + Pfeast(Tabc,Thcc,Tfeast,d,D) ) / float(PoweringEfficiency.Vfeast)

# Input from this module's feast plus any current from the previous modules
def Itape_Cumulative(Tabc,Thcc,Tfeast,d,D,itape_previous_modules=0) :
    return Itape(Tabc,Thcc,Tfeast,d,D) + itape_previous_modules

# Tape power loss (due to load on tape) due to items on the module
def Ptape(Tabc,Thcc,Tfeast,d,D) :
    return (Itape(Tabc,Thcc,Tfeast,d,D) )**2 * Rtape

# Cumulative tape power loss (due to items on the module, plus previous modules)
def Ptape_Cumulative(Tabc,Thcc,Tfeast,d,D,itape_previous_modules=0) :
    return ( Itape_Cumulative(Tabc,Thcc,Tfeast,d,D,itape_previous_modules) )**2 * Rtape

def Pmod(Tabc,Thcc,Tfeast,d,D,Is,itape_previous_modules=0) :
    return Pabc(Tabc,d,D) + Phcc(Thcc,d,D) + Pamac + Pfeast(Tabc,Thcc,Tfeast,d,D) + Ptape_Cumulative(Tabc,Thcc,Tfeast,d,D,itape_previous_modules) + Phv_R(Is) + Phv_Mux

# EOS current (load) on FEAST
eosI  = ( (nlpgbt * EOSComponents.lpgbtI + ngbld * EOSComponents.gbld12I) / float(PoweringEfficiency.DCDC2eff) ) * (EOSComponents.eosV12/float(EOSComponents.eosV25))
eosI += ngbtia * EOSComponents.gbtiaI + ngbld * EOSComponents.gbld25I

# EOS power (including powering efficiency)
def eosP(Teos) :
    return EOSComponents.eosV25 * eosI * 100 / float(PoweringEfficiency.feasteff(Teos, eosI))

# Tape current load due to EOS
def Itape_eos(Teos) :
    return eosP(Teos) / float(EOSComponents.Veos)

# Stave power
# in Watt, 2x14 modules (including ohmic loss in tape) +2xEOS, nominal (no irradiation and leakage) 
# Tape loss is subtracted from module power and added with proper scaling

# def Pstavetape(Tabc,Thcc,Tfeast,d,D) :
#     n2_from_1_to_nmod = list( n**2 for n in range(1,Layout.nmod+1) )
#     sum_n2_from_1_to_nmod = sum(n2_from_1_to_nmod)
#     return (Ptape(Tabc, Thcc, Tfeast, d, D) / float(Layout.nmod)**2 ) * sum_n2_from_1_to_nmod

# Factor of 2 is for two modules on each side of a stave
# def Pstave(Tabc,Thcc,Tfeast,Teos,d,D,Is) :
#     return 2 * (Layout.nmod * (Pmod(Tabc,Thcc,Tfeast,d,D,Is) - Ptape(Tabc,Thcc,Tfeast,d,D) +
#                                Is * SensorProperties.vbias) + Pstavetape(Tabc,Thcc,Tfeast,d,D) + eosP(Teos) )

# Pstavebare = Pstave(GlobalSettings.nomsensorT,
#                     GlobalSettings.nomsensorT,
#                     GlobalSettings.nomsensorT,
#                     GlobalSettings.nomsensorT,1,0,0)

# Total barrel power
# including tape and cable losses and safety factor on layout
# Ptotal = 2 * Layout.nstaves * Pstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b2Ptotal = 2 * Layout.nstavesb2 * ssPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b3Ptotal = 2 * Layout.nstavesb3 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# b4Ptotal = 2 * Layout.nstavesb4 * lsPstavebare * (1 + CableLosses.losstype1)*(1 + CableLosses.lossouter)*(1 + SafetyFactors.safetylayout) / 1000.
# bPtotal = b1Ptotal + b2Ptotal + b3Ptotal + b4Ptotal
