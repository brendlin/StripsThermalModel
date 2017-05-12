#
# ThermalImpedances
#

import SafetyFactors

# Thermal impedances in Kelvin/Watt from FEA by Graham Beck

Rfit  = (Pabc + Phcc + Pfeast + Prest) * Rcm
Rfit += (_type == 1) * Pabc * Rabc
Rfit += (_type == 2) * Phcc * Rhcc
Rfit += (_type == 3) * Pfeast * Rfeast

# These impedances are determined from the data in the following 3 files:
# ThermalImpedances_LongStripEOS.txt
# ThermalImpedances_LongStripMiddle.txt
# ThermalImpedances_ShortStripEOS.txt
# ThermalImpedances_ShortStripMiddle.txt

# The results of the fit (short strip) are:
# (EOS)
impedances_ss = {'rabc'  : 1.003, # 1
                 'rhcc'  :12.305, # 2
                 'rfeast':19.650, # 3
                 'rcm'   : 1.112, # Rc + Rm ? # 4
                 }

# short strip

ssRc = 0.89*(1 + SafetyFactors.safetythermalimpedance)
ssRm = (impedances_ss['rcm'] - 0.89)*(1 + SafetyFactors.safetythermalimpedance)
ssRs = 0.02*(1 + SafetyFactors.safetythermalimpedance)
ssReos = 15*(1 + SafetyFactors.safetythermalimpedance)
ssRabc = impedances_ss['rabc']*(1 + SafetyFactors.safetythermalimpedance)
ssRhcc = impedances_ss['rhcc']*(1 + SafetyFactors.safetythermalimpedance)
ssRfeast = impedances_ss['rfeast']*(1 + SafetyFactors.safetythermalimpedance)
ssRt = ssRc + ssRm + ssRs



# The results of the fit (long strip) are:
# (EOS)
impedances_ls = {'rabc'  : 2.194, # 1
                 'rhcc'  :24.195, # 2
                 'rfeast':19.062, # 3
                 'rcm'   : 1.239, # 4
                 }

# long strip

lsRc = 0.96*(1 + SafetyFactors.safetythermalimpedance)
lsRm = (impedances_ls['rcm'] - 0.96)*(1 + SafetyFactors.safetythermalimpedance)
lsRs = 0.02*(1 + SafetyFactors.safetythermalimpedance)
lsReos = 15*(1 + SafetyFactors.safetythermalimpedance)
lsRabc = impedances_ls['rabc']*(1 + SafetyFactors.safetythermalimpedance)
lsRhcc = impedances_ls['rhcc']*(1 + SafetyFactors.safetythermalimpedance)
lsRfeast = impedances_ls['rfeast']*(1 + SafetyFactors.safetythermalimpedance)
lsRt = lsRc + lsRm + lsRs

