#
# FrontEndComponents (before irradiation)
#
import Config
import SafetyFactors

# ABC and Hybrid Controller chips fabricated in 130 nm process
# known to suffer from increase in digital current due to ionizing radiation
descr_hybridV = 'Hybrid voltage'
hybridV = Config.GetDouble('FrontEndComponents.hybridV',1.5,unit='V',description=descr_hybridV)

# HCC digital
descr_hccId = 'HCC digital current'
hccId = Config.GetDouble('FrontEndComponents.hccId',0.125,unit='A',description=descr_hccId) * (1 + SafetyFactors.safetycurrent)

# HCC analog
descr_hccIa = 'HCC analog current'
hccIa = Config.GetDouble('FrontEndComponents.hccIa',0.075,unit='A',description=descr_hccIa) * (1 + SafetyFactors.safetycurrent)

# ABC digital
descr_abcId = 'ABC digital current'
abcId = Config.GetDouble('FrontEndComponents.abcId',0.035,unit='A',description=descr_abcId) * (1 + SafetyFactors.safetycurrent)

# ABC analog
descr_abcIa = 'ABC analog current'
abcIa = Config.GetDouble('FrontEndComponents.abcIa',0.066,unit='A',description=descr_abcIa) * (1 + SafetyFactors.safetycurrent)

# AMACII chip
amac15V     = 1.5
descr_amac15I = 'AMAC current of 1.5V circuit'
amac15I     = Config.GetDouble('FrontEndComponents.amac15I',0.045,unit='A',description=descr_amac15I) * (1 + SafetyFactors.safetycurrent)
#amac15eff   = 0.65
amac3V      = 3.0
descr_amac3I = 'AMAC current of 3V circuit'
amac3I      = Config.GetDouble('FrontEndComponents.amac3I',0.002,unit='A',description=descr_amac3I) * (1 + SafetyFactors.safetycurrent)
#amac3eff    = 0.65
