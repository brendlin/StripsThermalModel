#
# SensorLeakage
#
import GlobalSettings
import OperationalProfiles
import SensorProperties

# The sensor leakage power Qref  at a reference temperature Tref = -15 \[Degree]C is derived from
# measurements of the current density dependent on the fluence j in Neq/cm2  [ref Marcella Mikestikova]

# Leakage current as a function of flux
# in A/cm2

def iref500(j) :
    return max(0, (-0.14  + (3.40e-14) * j) / 1000000.) # the 1e6 is for micro-amps to amps

def iref700(j) :
    return max(0, (-0.761 + (4.02e-14) * j) / 1000000.) # the 1e6 is for micro-amps to amps

def oldiref(j) :
    return (1.22 + (2.68e-14) * j) / 1000000. # the 1e6 is for micro-amps to amps

if SensorProperties.vbias == 500 :
    iref = iref500
elif SensorProperties.vbias == 700 :
    iref = iref700
else :
    print 'SensorLeakage.py has no knowledge of this voltage: %.0f'%(SensorProperties.vbias)
    import sys; sys.exit()

qref = []

# size is nstep (???)
# Sensor area is in cm2
for i in range(GlobalSettings.nstep) :
    qref.append( SensorProperties.vbias * iref(OperationalProfiles.flux_list[i]*SensorProperties.area) )
