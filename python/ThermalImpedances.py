#
# ThermalImpedances
#
import Config
import SafetyFactors

# Thermal impedances in Kelvin/Watt from FEA by Graham Beck

# This is the function they use. I do not think we need it here, and instead we should
# rewrite this in a series of TF1 objects to rederive rabc, rhcc, rfeast, rcm for the petals.
# def Rfit(Rabc,Rhcc,Rfeast,Rcm,Pabc,Phcc,Pfeast,Prest,_type) :
#     ret = (Pabc + Phcc + Pfeast + Prest) * Rcm
#     ret += (_type == 1) * Pabc * Rabc
#     ret += (_type == 2) * Phcc * Rhcc
#     ret += (_type == 3) * Pfeast * Rfeast
#     return ret

# These impedances are determined from the data in the following 3 files:
# ThermalImpedances_LongStripEOS.txt
# ThermalImpedances_LongStripMiddle.txt
# ThermalImpedances_ShortStripEOS.txt
# ThermalImpedances_ShortStripMiddle.txt

Rc     = Config.GetDouble('ThermalImpedances.rc'      ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rm     = Config.GetDouble('ThermalImpedances.rm'      ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rs     = Config.GetDouble('ThermalImpedances.rs',0.02 ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Reos   = Config.GetDouble('ThermalImpedances.reos',15.,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rabc   = Config.GetDouble('ThermalImpedances.rabc'    ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rhcc   = Config.GetDouble('ThermalImpedances.rhcc'    ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rfeast = Config.GetDouble('ThermalImpedances.rfeast'  ,unit='K/W')*(1 + SafetyFactors.safetythermalimpedance)
Rt = Rc + Rm + Rs
