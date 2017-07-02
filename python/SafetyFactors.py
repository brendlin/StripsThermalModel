#
# Safety Factors
#
import Config

# Safety factor on layout (number of channels,layers etc.)
safetylayout_descr = 'For barrel only -- not used anymore'
safetylayout = Config.GetDouble('SafetyFactors.safetylayout',0.0,description=safetylayout_descr)

# safety factor on fluence (calculations, machine predictions etc.)
safetyfluence_descr = 'Fractional safety factor increase over 3935 fb$^{-1}$'
safetyfluence = Config.GetDouble('SafetyFactors.safetyfluence',0.0,description=safetyfluence_descr)

# Safety factor on thermal impedance of local support
safetythermal_descr = 'Fractional thermal impedance safety factor increase'
safetythermalimpedance = Config.GetDouble('SafetyFactors.safetythermalimpedance',0.0,description=safetythermal_descr)

# Safety factor on electrical power estimates
safetycurrent_descr = 'Fractional current safety factor increase'
safetycurrent = Config.GetDouble('SafetyFactors.safetycurrent',0.0,description=safetycurrent_descr)

# Scale factor for bias voltage (default is 500V)
vbiasscale_descr = 'HV safety factor -- multiply 500V by this number'
vbiasscale = Config.GetDouble('SafetyFactors.vbiasscale',1.,description=vbiasscale_descr)
