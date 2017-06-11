#
# FrontEndComponents (before irradiation)
#

import SafetyFactors

# ABC and Hybrid Controller chips fabricated in 130 nm process
# known to suffer from increase in digital current due to ionizing radiation
hybridV = 1.5

# HCC digital
hccId = 0.125 * (1 + SafetyFactors.safetycurrent)

# HCC analog
hccIa = 0.075 * (1 + SafetyFactors.safetycurrent)

# ABC digital
abcId = 0.035 * (1 + SafetyFactors.safetycurrent)

# ABC analog
abcIa = 0.066 * (1 + SafetyFactors.safetycurrent)

# AMACII chip
amac15V     = 1.5
amac15I     = 0.045 * (1 + SafetyFactors.safetycurrent)
#amac15eff   = 0.65
amac3V      = 3.0
amac3I      = 0.002 * (1 + SafetyFactors.safetycurrent)
#amac3eff    = 0.65
