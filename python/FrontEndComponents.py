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
hccId = Config.GetDouble('FrontEndComponents.hccId',0.125,unit='A',description=descr_hccId) * (1 + SafetyFactors.safetycurrentd)

# HCC analog
descr_hccIa = 'HCC analog current'
hccIa = Config.GetDouble('FrontEndComponents.hccIa',0.075,unit='A',description=descr_hccIa) * (1 + SafetyFactors.safetycurrenta)

# ABC digital
descr_abcId = 'ABC digital current'
abcId = Config.GetDouble('FrontEndComponents.abcId',0.0425,unit='A',description=descr_abcId) * (1 + SafetyFactors.safetycurrentd)

# ABC analog
descr_abcIa = 'ABC analog current'
abcIa = Config.GetDouble('FrontEndComponents.abcIa',0.070,unit='A',description=descr_abcIa) * (1 + SafetyFactors.safetycurrenta)

# AMACII chip
amac15V     = 1.5
descr_amac15I = 'AMAC current of 1.5V circuit'
amac15I     = Config.GetDouble('FrontEndComponents.amac15I',0.0517,unit='A',description=descr_amac15I) * (1 + SafetyFactors.safetycurrentd)
#amac15eff   = 0.65
amac3V      = 3.0
descr_amac3I = 'AMAC current of 3V circuit'
amac3I      = Config.GetDouble('FrontEndComponents.amac3I',0.0012,unit='A',description=descr_amac3I) * (1 + SafetyFactors.safetycurrentd)
#amac3eff    = 0.65
ldoI        = Config.GetDouble('FrontEndComponents.ldoI',0.0019,unit='A',description='LDO quiescent current') * (1 + SafetyFactors.safetycurrentd)
