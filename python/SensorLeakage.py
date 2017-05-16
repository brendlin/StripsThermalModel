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

def iref(j) :
    return max(0, (-0.14  + (3.40e-14) * j) / 1000000.)

def iref700(j) :
    return max(0, (-0.761 + (4.02e-14) * j) / 1000000.)

def oldiref(j) :
    return (1.22 + (2.68e-14) * j) / 1000000.

qrefb1 = []
qrefb2 = []
qrefb3 = []
qrefb4 = []

for i in range(GlobalSettings.nstep) :
    qrefb1.append( SensorProperties.vbias * iref(OperationalProfiles.fluxb1[i]*SensorProperties.area) )
    qrefb2.append( SensorProperties.vbias * iref(OperationalProfiles.fluxb2[i]*SensorProperties.area) )
    qrefb3.append( SensorProperties.vbias * iref(OperationalProfiles.fluxb3[i]*SensorProperties.area) )
    qrefb4.append( SensorProperties.vbias * iref(OperationalProfiles.fluxb4[i]*SensorProperties.area) )
