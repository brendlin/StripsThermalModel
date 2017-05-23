#!/usr/bin/env python

import os,sys
import math
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PlotUtils as PlotUtils

def usage() :
    print "Usage:\n"
    print 'python '+sys.argv[0]+' --cooling <coolingScenarioTag>'
    print '--cooling:   cooling scheme: \"flat-25\",\"flat-35\",\"ramp-25\",\"ramp-35\"'
    print '--config:    configuration file: \"Barrel_SS_B1.config\",\"Barrel_SS_B2.config\",\"Barrel_LS_B3.config\",\"Barrel_LS_B4.config\"'
    print 'Example: '
    print 'python '+sys.argv[0]+' --cooling flat-25'
    sys.exit()
    
#-----------------------------------------------
def main(options,args):

    PlotUtils.ApplyGlobalStyle()

    # Config must be loaded before loading any other module.
    import python.Config as Config
    Config.SetConfigFile('%s/data/%s'%(the_path,options.config))

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
        print 'Error! Please set a cooling scheme: \"flat-25\",\"flat-35\",\"ramp-25\",\"ramp-35\".'
        usage()

    # time_step_list is a list of each step through the years
    time_step_tc = []
    for i in range(GlobalSettings.nstep) :
        index = int( math.floor(i * GlobalSettings.step) )
        time_step_tc.append( coolantT[ index ] )

    # The main calculations happen here:
    SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc,options)

    print 'done'
    return

#-----------------------------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 1:
        print "Wrong number of arguments"
        usage()

    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--cooling',type='string',default='',dest='cooling',help='Cooling scheme (\"-flat25\",\"-flat35\",\"ramp-25\",\"ramp-35\").')
    p.add_option('--config' ,type='string',default='Barrel_SS_B1.config',dest='config',help='Configuration file -- please make sure it is put in the data/ directory')

    options,args = p.parse_args()
    
    main(options,args)
