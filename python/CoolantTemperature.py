
import GlobalSettings
import Config
import math

internal_coolantT = [[]]
internal_time_step_tc = [[]]

#
# To retrieve the n-year coolant scenario list
#
def GetCoolantT() :
    return internal_coolantT[0]

#
# To retrieve the n-step coolant list
#
def GetTimeStepTc() :
    return internal_time_step_tc[0]

# Coolant temperature in Celsius in each year for 14 y of operation
# Must be defined before loading the module.
cooling = Config.GetStr('cooling','flat-35',unit='$^{\circ}$C')

if 'flat' in cooling :
    temp = float(cooling.replace('flat',''))
    # print 'Setting cooling to \"%s\" (constant at %2.0f C)'%(cooling,temp)
    internal_coolantT[0] = [temp]*GlobalSettings.nyears

elif cooling == 'ramp-25' :
    # print 'Setting cooling to \"ramp-25\" (ramping down to -25 C)'
    internal_coolantT[0] = [   0,  -5, -10, -15, -15, -20, -20, -25, -25, -25, -25, -25, -25, -25 ]

elif cooling == 'ramp-35' :
    # print 'Setting cooling to \"ramp-35\" (ramping down to -35 C)'
    internal_coolantT[0] = [   0,  -5, -10, -15, -15, -20, -20, -25, -30, -35, -35, -35, -35, -35 ]

elif cooling == 'special' :
    # print 'Setting cooling to \"special\" (see CoolantTemperature.py)'
    internal_coolantT[0] = [   0,   0, -20, -20, -20, -35, -35, -35, -35, -35, -35, -35, -35, -35 ]

else :
    print 'Error! cooling is set incorrectly in Config file ("cooling") or by command line (--cooling).'
    print 'Please set a cooling scheme: \"flat-XX\",\"ramp-25\",\"ramp-35\".'
    import sys; sys.exit()

#
# Set the internal time_step_tc
#
# time_step_list is a list of each step through the years
internal_time_step_tc[0] = []
for i in range(GlobalSettings.nstep) :
    index = int( math.floor(i * GlobalSettings.step) )
    internal_time_step_tc[0].append( internal_coolantT[0][ index ] )
