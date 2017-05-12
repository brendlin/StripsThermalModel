#
# OperationalProfiles
#
import math
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

# luminosity ramp
lumiramp = []
lumiramp.append(0)
for i in range(GlobalSettings.nstep) :
    # print math.floor(i*step)
    lumiramp.append(lumiramp[-1])
    lumiramp[-1] += GlobalSettings.step * luminosity[ int(math.floor(i*GlobalSettings.step)) ]


# Accumulated flux at end of each year for each barrel
# in neq/cm2 for the four barrels for 3000 fb-1, calculated by Paul Miyagawa for layout 5.01
totalfluxb1 = 5.31e14 * (1 + SafetyFactors.safetyfluence)
totalfluxb2 = 3.80e14 * (1 + SafetyFactors.safetyfluence)
totalfluxb3 = 2.86e14 * (1 + SafetyFactors.safetyfluence)
totalfluxb4 = 2.26e14 * (1 + SafetyFactors.safetyfluence)

# Flux (?)
fluxb1 = list( (totalfluxb1/3000.) * a for a in lumiramp )
fluxb2 = list( (totalfluxb2/3000.) * a for a in lumiramp )
fluxb3 = list( (totalfluxb3/3000.) * a for a in lumiramp )
fluxb4 = list( (totalfluxb4/3000.) * a for a in lumiramp )

# Total dose rates at representative strip system locations
# From ref. xxx total TID in kRad for an integrated luminosity of 3000fb^-1 for the four barrels, calculated by Paul Miyagawa for layout 5.01
b1TID = 23300. * (1 + SafetyFactors.safetyfluence)
b2TID = 12400. * (1 + SafetyFactors.safetyfluence)
b3TID =  6800. * (1 + SafetyFactors.safetyfluence)
b4TID =  3800. * (1 + SafetyFactors.safetyfluence)

tidb1 = list( (b1TID/3000.) * a for a in lumiramp )
tidb2 = list( (b2TID/3000.) * a for a in lumiramp )
tidb3 = list( (b3TID/3000.) * a for a in lumiramp )
tidb4 = list( (b4TID/3000.) * a for a in lumiramp )

# import ROOT
# from array import array
# g = ROOT.TGraph(len(tidb1),array('d',GlobalSettings.step_list),array('d',tidb1))
# g.Draw()
# raw_input('pause')

# Dose rate for each year for each barrel
hoursperyear = list( 24 * daysperyear[i] * eff[i] for i in range(len(daysperyear)))

doserateb1 = list( (b1TID/3000.)*luminosity[i]/float(hoursperyear[i]) for i in range(len(luminosity)) )
doserateb2 = list( (b2TID/3000.)*luminosity[i]/float(hoursperyear[i]) for i in range(len(luminosity)) )
doserateb3 = list( (b3TID/3000.)*luminosity[i]/float(hoursperyear[i]) for i in range(len(luminosity)) )
doserateb4 = list( (b4TID/3000.)*luminosity[i]/float(hoursperyear[i]) for i in range(len(luminosity)) )

