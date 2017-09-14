#
# EOSComponents
#
# There is one EOS card per stave (petal) side, two per stave/petal. Note that these 
# components are not in IBM technology and will not suffer the current bump.

import Config
import SafetyFactors

descr_veos = 'EOS input voltage'
Veos = Config.GetDouble('EOSComponents.Veos',11.0,unit='V',description=descr_veos)

eosV12 = 1.2 # voltage (1.2 volts)
eosV25 = 2.5 # voltage (2.5 volts)

# lpGBTx
descr_lpgbtI = 'Current in lpGBT (voltage is 1.2 V)'
lpgbtI = Config.GetDouble('EOSComponents.lpgbtI',0.625,unit='A',description=descr_lpgbtI)*(1 + SafetyFactors.safetycurrentd)

# GBTIA
descr_gbtiaI = 'Current in GBTIA (voltage is 2.5 V)'
gbtiaI = Config.GetDouble('EOSComponents.gbtiaI',0.053,unit='A',description=descr_gbtiaI)*(1 + SafetyFactors.safetycurrentd)

# GBLD10
# includes power for opto-converter
descr_gbld25I = 'Current in GBLD10 2.5V circuit'
gbld25I = Config.GetDouble('EOSComponents.gbld25I',0.018,unit='A',description=descr_gbld25I)*(1 + SafetyFactors.safetycurrentd)
descr_gbld12I = 'Current in GBLD10 1.2V circuit'
gbld12I = Config.GetDouble('EOSComponents.gbld12I',0.0095,unit='A',description=descr_gbld12I)*(1 + SafetyFactors.safetycurrentd)
