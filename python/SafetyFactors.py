#
# Safety Factors
#
import Config

safetylayout = 0.0           # Safety factor on layout (number of channels,layers etc.)
if Config.Defined('SafetyFactors.safetylayout') :
    safetylayout = Config.GetDouble('SafetyFactors.safetylayout')

safetyfluence = 0.5          # safety factor on fluence (calculations, machine predictions etc.)
if Config.Defined('SafetyFactors.safetyfluence') :
    safetyfluence = Config.GetDouble('SafetyFactors.safetyfluence')

safetythermalimpedance = 0.2 # Safety factor on thermal impedance of local support
if Config.Defined('SafetyFactors.safetythermalimpedance') :
    safetythermalimpedance = Config.GetDouble('SafetyFactors.safetythermalimpedance')

safetycurrent = 0.2          # Safety factor on electrical power estimates
if Config.Defined('SafetyFactors.safetycurrent') :
    safetycurrent = Config.GetDouble('SafetyFactors.safetycurrent')

vbiasscale = 1.              # Scale factor for bias voltage (default is 500V)
if Config.Defined('SafetyFactors.vbiasscale') :
    vbiasscale = Config.GetDouble('SafetyFactors.vbiasscale')
