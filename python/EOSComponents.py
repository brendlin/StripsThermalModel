#
# EOSComponents
#
# There is one EOS card per stave (petal) side, two per stave/petal. Note that these 
# components are not in IBM technology and will not suffer the current bump.

import SafetyFactors

eosV12 = 1.2 # voltage (1.2 volts)
eosV25 = 2.5 # voltage (2.5 volts)

# lpGBTx
lpgbtI = 0.625*(1 + SafetyFactors.safetycurrent)

# GBTIA
gbtiaI = 0.053*(1 + SafetyFactors.safetycurrent)

# GBLD10
# includes power for opto-converter
gbld25I = 0.018*(1 + SafetyFactors.safetycurrent)
gbld12I = 0.0095*(1 + SafetyFactors.safetycurrent)

