#
# Safety Factors
#
import Config

# safety factor on fluence (calculations, machine predictions etc.)
safetyfluence_descr = 'Fractional safety factor increase over 3935 fb$^{-1}$'
safetyfluence = Config.GetDouble('SafetyFactors.safetyfluence',0.0,description=safetyfluence_descr)

# Safety factor on thermal impedance of local support
safetythermal_descr = 'Fractional thermal impedance safety factor increase'
safetythermalimpedance = Config.GetDouble('SafetyFactors.safetythermalimpedance',0.0,description=safetythermal_descr)

# Safety factor on digital current estimates
safetycurrentd_descr = 'Fractional digital current safety factor increase'
safetycurrentd = Config.GetDouble('SafetyFactors.safetycurrentd',0.0,description=safetycurrentd_descr)

# Safety factor on analog current estimates
safetycurrenta_descr = 'Fractional analog current safety factor increase'
safetycurrenta = Config.GetDouble('SafetyFactors.safetycurrenta',0.0,description=safetycurrenta_descr)

# Bias voltage (default is 500V)
vbias_descr = 'HV bias voltage (default is 500V)'
vbias = Config.GetDouble('SafetyFactors.vbias',500.,unit='V',description=vbias_descr)
