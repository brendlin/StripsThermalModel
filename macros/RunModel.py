#!/usr/bin/env python

import os,sys
import math
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

print 'importing modules'
import python.GlobalSettings      as GlobalSettings
import python.SafetyFactors       as SafetyFactors
import python.Layout              as Layout
import python.PoweringEfficiency  as PoweringEfficiency
import python.CableLosses         as CableLosses
import python.FrontEndComponents  as FrontEndComponents
import python.EOSComponents       as EOSComponents
import python.AbcTidBump          as AbcTidBump
import python.SensorProperties    as SensorProperties
import python.NominalPower        as NominalPower
import python.ThermalImpedances   as ThermalImpedances
import python.Temperatures        as Temperatures
import python.OperationalProfiles as OperationalProfiles
import python.SensorLeakage       as SensorLeakage
import python.SensorTemperatureCalc as SensorTemperatureCalc
print 'importing modules done.'


#-----------------------------------------------
def main(options,args) :

    # Coolant temperature in Celsius in each year for 14 y of operation
    if options.cooling == 'flat-25' :
        print 'Setting cooling to \"flat-25\" (constant at -25 C)'
        coolantT = [ -25, -25, -25, -25, -25, -25, -25, -25, -25, -25, -25, -25, -25, -25 ]
    elif options.cooling == 'flat-35' :
        print 'Setting cooling to \"flat-35\" (constant at -35 C)'
        coolantT = [ -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35, -35 ]
    elif options.cooling == 'ramp-25' :
        print 'Setting cooling to \"ramp-25\" (ramping down to -25 C)'
        coolantT = [   0,  -5, -10, -15, -15, -20, -20, -25, -25, -25, -25, -25, -25, -25 ]
    elif options.cooling == 'ramp-35' :
        print 'Setting cooling to \"ramp-35\" (ramping down to -35 C)'
        coolantT = [   0,  -5, -10, -15, -15, -20, -20, -25, -30, -35, -35, -35, -35, -35 ]
    else :
        print 'Error! Please set a cooling scheme --cooling (\"flat-25\",\"flat-35\",\"ramp-25\",\"ramp-35\").'
        sys.exit()

    # time_step_list is a list of each step through the years
    time_step_tc = []
    for i in range(GlobalSettings.nstep) :
        index = int( math.floor(i * GlobalSettings.step) )
        time_step_tc.append( coolantT[ index ] )

    print 'This is a safety factor: ',SafetyFactors.safetylayout

    # The main calculations happen here:
    SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc)

    print 'done'
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--cooling',type='string',default='',dest='cooling',help='Cooling scheme (\"-25\",\"-35\",\"ramp-25\",\"ramp-35\").')

    options,args = p.parse_args()
    
    main(options,args)
