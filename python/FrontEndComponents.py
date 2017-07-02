#
# FrontEndComponents (before irradiation)
#
import Config
import SafetyFactors

# ABC and Hybrid Controller chips fabricated in 130 nm process
# known to suffer from increase in digital current due to ionizing radiation
hybridV = Config.GetDouble('FrontEndComponents.hybridV',1.5,unit='V')

# HCC digital
hccId = Config.GetDouble('FrontEndComponents.hccId',0.125,unit='A') * (1 + SafetyFactors.safetycurrent)

# HCC analog
hccIa = Config.GetDouble('FrontEndComponents.hccIa',0.075,unit='A') * (1 + SafetyFactors.safetycurrent)

# ABC digital
abcId = Config.GetDouble('FrontEndComponents.abcId',0.035,unit='A') * (1 + SafetyFactors.safetycurrent)

# ABC analog
abcIa = Config.GetDouble('FrontEndComponents.abcIa',0.066,unit='A') * (1 + SafetyFactors.safetycurrent)

# AMACII chip
amac15V     = 1.5
amac15I     = Config.GetDouble('FrontEndComponents.amac15I',0.045,unit='A') * (1 + SafetyFactors.safetycurrent)
#amac15eff   = 0.65
amac3V      = 3.0
amac3I      = Config.GetDouble('FrontEndComponents.amac3I',0.002,unit='A') * (1 + SafetyFactors.safetycurrent)
#amac3eff    = 0.65
