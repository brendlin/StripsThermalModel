#
# SensorProperties
#
import SafetyFactors

# Sensor area in cm2
area = 9.554*9.554

# Bias voltage (incl. resistors)
vbias = 500.*SafetyFactors.vbiasscale # bias voltage is 500V
Rhv    =   10000. # HV resistors are 2 times 5k
Rhvmux = 1000000. # parallel resistor for MUX operation is 1M
