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


# Barrel short strip stave (middle) - not used further

# data = {{2.97, 0, 0, 0, 1, 6.20}, {2.97, 0, 0, 0, 2, 4.09}, {2.97, 0, 
#     0, 0, 3, 3.53}, {2.97, 0, 0, 0, 4, 2.90},
#    {0, 0.6, 0, 0, 1, 0.83}, {0, 0.6, 0, 0, 2, 8.59}, {0, 0.6, 0, 0, 3,
#      0.66}, {0, 0.6, 0, 0, 4, 0.62},
#    {0, 0, 1.47, 0, 1, 1.76}, {0, 0, 1.47, 0, 2, 1.61}, {0, 0, 1.47, 0,
#      3, 30.74}, {0, 0, 1.47, 0, 4, 1.44},
#    {0, 0, 0, 0.08, 1, 0.07}, {0, 0, 0, 0.08, 2, 0.02}, {0, 0, 0, 0.08,
#      3, 0.05}, {0, 0, 0, 0.08, 4, 0.07},
#    {0, 0, 0, 0.25, 1, 0.26}, {0, 0, 0, 0.25, 2, 0.07}, {0, 0, 0, 0.25,
#      3, 0.19}, {0, 0, 0, 0.25, 4, 0.23},
#    {0, 0, 0, 0.01, 1, 0.011}, {0, 0, 0, 0.01, 2, 0.003}, {0, 0, 0, 
#     0.01, 3, 0.006}, {0, 0, 0, 0.01, 4, 0.010}};
# Rfit[Rabc_, Rhcc_, Rfeast_, Rcm_, Pabc_, Phcc_, Pfeast_, Prest_, 
#   Type_] := (Pabc + Phcc + Pfeast + Prest)*Rcm + 
#   If[Type == 1, Pabc*Rabc, 0] + If[Type == 2, Phcc*Rhcc, 0] + 
#   If[Type == 3, Pfeast*Rfeast, 0]
# impedancefit = 
#  FindFit[data, {Rfit[rabc, rhcc, rfeast, rcm, pabc, phcc, pfeast, 
#     prest, type], rabc > 0, rhcc > 0, rfeast > 0, rcm > 0}, {rabc, 
#    rhcc, rfeast, rcm}, {pabc, phcc, pfeast, prest, type}]
# impedances = {rabc, rhcc, rfeast, rcm} /. impedancefit;

# Barrel short strip stave (EOS)

# data = {{2.97, 0, 0, 0, 1, 6.28}, {2.97, 0, 0, 0, 2, 3.46}, {2.97, 0, 
#     0, 0, 3, 3.56}, {2.97, 0, 0, 0, 4, 3.10},
#    {0, 0.6, 0, 0, 1, 0.70}, {0, 0.6, 0, 0, 2, 8.05}, {0, 0.6, 0, 0, 3,
#      0.57}, {0, 0.6, 0, 0, 4, 0.52},
#    {0, 0, 1.47, 0, 1, 1.77}, {0, 0, 1.47, 0, 2, 1.40}, {0, 0, 1.47, 0,
#      3, 30.52}, {0, 0, 1.47, 0, 4, 1.51},
#    {0, 0, 0, 0.37, 1, 0.38}, {0, 0, 0, 0.37, 2, 0.25}, {0, 0, 0, 0.37,
#      3, 0.33}, {0, 0, 0, 0.37, 4, 0.39},
#    {0, 0, 0, 0.25, 1, 0.30}, {0, 0, 0, 0.25, 2, 0.08}, {0, 0, 0, 0.25,
#      3, 0.21}, {0, 0, 0, 0.25, 4, 0.22},
#    {0, 0, 0, 0.01, 1, 0.013}, {0, 0, 0, 0.01, 2, 0.003}, {0, 0, 0, 
#     0.01, 3, 0.008}, {0, 0, 0, 0.01, 4, 0.010}};
# Rfit[Rabc_, Rhcc_, Rfeast_, Rcm_, Pabc_, Phcc_, Pfeast_, Prest_, 
#   Type_] := (Pabc + Phcc + Pfeast + Prest)*Rcm + 
#   If[Type == 1, Pabc*Rabc, 0] + If[Type == 2, Phcc*Rhcc, 0] + 
#   If[Type == 3, Pfeast*Rfeast, 0]
# impedancefit = 
#  FindFit[data, {Rfit[rabc, rhcc, rfeast, rcm, pabc, phcc, pfeast, 
#     prest, type], rabc > 0, rhcc > 0, rfeast > 0, rcm > 0}, {rabc, 
#    rhcc, rfeast, rcm}, {pabc, phcc, pfeast, prest, type}]
# impedances = {rabc, rhcc, rfeast, rcm} /. impedancefit;
# ssRc = 0.89*(1 + safetythermalimpedance)
# ssRm = (impedances[[4]] - 0.89)*(1 + safetythermalimpedance)
# ssRs = 0.02*(1 + safetythermalimpedance)
# ssReos = 15*(1 + safetythermalimpedance)
# ssRabc = impedances[[1]]*(1 + safetythermalimpedance)
# ssRhcc = impedances[[2]]*(1 + safetythermalimpedance)
# ssRfeast = impedances[[3]]*(1 + safetythermalimpedance)
# ssRt = ssRc + ssRm + ssRs

# Barrel long strip stave (middle) - not used further

# data = {{1.48, 0, 0, 0, 1, 5.18}, {1.48, 0, 0, 0, 2, 2.92}, {1.48, 0, 
#     0, 0, 3, 1.91}, {1.48, 0, 0, 0, 4, 1.57},
#    {0, 0.3, 0, 0, 1, 0.59}, {0, 0.3, 0, 0, 2, 7.96}, {0, 0.3, 0, 0, 3,
#      0.35}, {0, 0.3, 0, 0, 4, 0.33},
#    {0, 0, 0.88, 0, 1, 1.13}, {0, 0, 0.88, 0, 2, 1.04}, {0, 0, 0.88, 0,
#      3, 18.5}, {0, 0, 0.88, 0, 4, 0.94},
#    {0, 0, 0, 0.02, 1, 0.02}, {0, 0, 0, 0.02, 2, 0.01}, {0, 0, 0, 0.02,
#      3, 0.02}, {0, 0, 0, 0.02, 4, 0.02},
#    {0, 0, 0, 0.25, 1, 0.29}, {0, 0, 0, 0.25, 2, 0.08}, {0, 0, 0, 0.25,
#      3, 0.21}, {0, 0, 0, 0.25, 4, 0.26},
#    {0, 0, 0, 0.01, 1, 0.012}, {0, 0, 0, 0.01, 2, 0.003}, {0, 0, 0, 
#     0.01, 3, 0.007}, {0, 0, 0, 0.01, 4, 0.011}};
# Rfit[Rabc_, Rhcc_, Rfeast_, Rcm_, Pabc_, Phcc_, Pfeast_, Prest_, 
#   Type_] := (Pabc + Phcc + Pfeast + Prest)*Rcm + 
#   If[Type == 1, Pabc*Rabc, 0] + If[Type == 2, Phcc*Rhcc, 0] + 
#   If[Type == 3, Pfeast*Rfeast, 0]
# impedancefit = 
#  FindFit[data, {Rfit[rabc, rhcc, rfeast, rcm, pabc, phcc, pfeast, 
#     prest, type], rabc > 0, rhcc > 0, rfeast > 0, rcm > 0}, {rabc, 
#    rhcc, rfeast, rcm}, {pabc, phcc, pfeast, prest, type}]
# impedances = {rabc, rhcc, rfeast, rcm} /. impedancefit;

# Barrel long strip stave (EOS)

# data = {{1.48, 0, 0, 0, 1, 5.08}, {1.48, 0, 0, 0, 2, 2.49}, {1.48, 0, 
#     0, 0, 3, 1.86}, {1.48, 0, 0, 0, 4, 1.56},
#    {0, 0.3, 0, 0, 1, 0.50}, {0, 0.3, 0, 0, 2, 7.63}, {0, 0.3, 0, 0, 3,
#      0.31}, {0, 0.3, 0, 0, 4, 0.27},
#    {0, 0, 0.88, 0, 1, 1.05}, {0, 0, 0.88, 0, 2, 0.86}, {0, 0, 0.88, 0,
#      3, 18.34}, {0, 0, 0.88, 0, 4, 0.83},
#    {0, 0, 0, 0.11, 1, 0.10}, {0, 0, 0, 0.11, 2, 0.06}, {0, 0, 0, 0.11,
#      3, 0.07}, {0, 0, 0, 0.11, 4, 0.12},
#    {0, 0, 0, 0.25, 1, 0.28}, {0, 0, 0, 0.25, 2, 0.07}, {0, 0, 0, 0.25,
#      3, 0.21}, {0, 0, 0, 0.25, 4, 0.24},
#    {0, 0, 0, 0.01, 1, 0.012}, {0, 0, 0, 0.01, 2, 0.003}, {0, 0, 0, 
#     0.01, 3, 0.007}, {0, 0, 0, 0.01, 4, 0.011}};
# Rfit[Rabc_, Rhcc_, Rfeast_, Rcm_, Pabc_, Phcc_, Pfeast_, Prest_, 
#   Type_] := (Pabc + Phcc + Pfeast + Prest)*Rcm + 
#   If[Type == 1, Pabc*Rabc, 0] + If[Type == 2, Phcc*Rhcc, 0] + 
#   If[Type == 3, Pfeast*Rfeast, 0]
# impedancefit = 
#  FindFit[data, {Rfit[rabc, rhcc, rfeast, rcm, pabc, phcc, pfeast, 
#     prest, type], rabc > 0, rhcc > 0, rfeast > 0, rcm > 0}, {rabc, 
#    rhcc, rfeast, rcm}, {pabc, phcc, pfeast, prest, type}]
# impedances = {rabc, rhcc, rfeast, rcm} /. impedancefit;
# lsRc = 0.96*(1 + safetythermalimpedance)
# lsRm = (impedances[[4]] - 0.96)*(1 + safetythermalimpedance)
# lsRs = 0.02*(1 + safetythermalimpedance)
# lsReos = 15*(1 + safetythermalimpedance)
# lsRabc = impedances[[1]]*(1 + safetythermalimpedance)
# lsRhcc = impedances[[2]]*(1 + safetythermalimpedance)
# lsRfeast = impedances[[3]]*(1 + safetythermalimpedance)
# lsRt = lsRc + lsRm + lsRs
