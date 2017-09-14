#
# SensorProperties
#
import Config
import SafetyFactors

# Sensor area in cm2
area = Config.GetDouble('SensorProperties.area',unit='cm$^2$',description='Sensor area on the module')

# Bias voltage (incl. resistors)
vbias = SafetyFactors.vbias
Rhv_descr = 'HV resistors are 2 times 5k'
Rhv    = Config.GetDouble('SensorProperties.Rhv',10000.,unit='$\Omega$',description=Rhv_descr)
Rhvmux_descr = 'parallel resistor for MUX operation is 1M'
Rhvmux = Config.GetDouble('SensorProperties.Rhvmux',1000000.,unit='$\Omega$',description=Rhvmux_descr)
