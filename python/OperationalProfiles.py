#
# OperationalProfiles
#
import math
import Config
import SafetyFactors
import GlobalSettings

# Luminosity profile
# Luminosity per year in fb^-1/y for 14 y of operation
luminosity = [ 61, 163, 203, 203, 0, 305, 400, 400, 0, 440, 440, 440, 440, 440 ]

# days per year of operation
daysperyear = [ 80, 160, 160, 160, 1, 200, 200, 200, 1, 220, 220, 220, 220, 220]

# Efficiency (?)
eff = [ 0.294, 0.294, 0.294, 0.294, 0.294, 0.294,
        0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308 ]

# luminosity ramp - size is nstep+1 (including time t=0)
lumiramp = []
lumiramp.append(0)
for i in range(GlobalSettings.nstep) :
    lumiramp.append(lumiramp[-1])
    lumiramp[-1] += GlobalSettings.step * luminosity[ int(math.floor(i*GlobalSettings.step)) ]


# Accumulated flux at end of each year for each barrel
# in neq/cm2 for the four barrels for 3000 fb-1, calculated by Paul Miyagawa for layout 5.01
totalflux = Config.GetDouble('OperationalProfiles.totalflux') * (1 + SafetyFactors.safetyfluence)

# Flux
flux_list = list( (totalflux/3000.) * a for a in lumiramp )

# Total dose rates at representative strip system locations
# From ref. xxx total TID in kRad for an integrated luminosity of 3000fb^-1 for the four barrels, calculated by Paul Miyagawa for layout 5.01
tid_in_3000fb = Config.GetDouble('OperationalProfiles.tid_in_3000fb') * (1 + SafetyFactors.safetyfluence)

tid_dose = list( (tid_in_3000fb/3000.) * a for a in lumiramp )

# Dose rate for each year for each barrel
hoursperyear = list( 24 * daysperyear[i] * eff[i] for i in range(len(daysperyear)))

doserate = []

# size of these is nstep
for i in range(GlobalSettings.nstep) :
    year_i = int(math.floor(i*GlobalSettings.step))
    doserate.append( (tid_in_3000fb/3000.)*luminosity[year_i]/float(hoursperyear[year_i]) )
