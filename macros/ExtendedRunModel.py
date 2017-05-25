#!/usr/bin/env python

import os,sys
import math
import ROOT
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

ROOT.gROOT.SetBatch(True)

import python.PlotUtils as PlotUtils

def usage() :
    print "Usage:\n"
    print 'python '+sys.argv[0]+' --cooling <coolingScenarioTag> --barrel'
    print '--cooling:   cooling scheme: \"flat-25\",\"flat-35\",\"ramp-25\",\"ramp-35\"'
    print '--barrel:    run the barrel configuration'
    print '--endcap:    run the barrel configuration'
    print 'Example: '
    print 'python %s --cooling flat-25 --endcap'%(sys.argv[0])
    sys.exit()
    
def GetFlux(ring,disk) :
    return 2e14 + (1e15 - 2e14)*((5-ring) + disk)/10.

def GetTID(ring,disk) :
    return 3e3 + (3e4 - 3e3)*(5-ring)/5.

#-----------------------------------------------
def main(options,args):

    PlotUtils.ApplyGlobalStyle()

    if options.barrel :
        config_files = ['Barrel_SS_B1.config',
                        'Barrel_SS_B2.config',
                        'Barrel_LS_B3.config',
                        'Barrel_LS_B4.config'
                        ]
        structure_names = ['B1','B2','B3','B4']

    else :
        config_files = ['Endcap_R0.config',
                        'Endcap_R1.config',
                        'Endcap_R2.config',
                        'Endcap_R3.config',
                        'Endcap_R4.config',
                        'Endcap_R5.config'
                        ]
        structure_names = []

    # Config must be loaded before loading any other module.
    import python.Config as Config
    Config.SetConfigFile('%s/data/%s'%(the_path,config_files[0]),doprint=options.barrel)

    if options.endcap :
        Config.SetValue('OperationalProfiles.totalflux',GetFlux(0,0))
        Config.SetValue('OperationalProfiles.tid_in_3000fb',GetTID(0,0))
        print 'CALCULATING Ring %d Disk %d:'%(0,0)
        Config.Print()

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

    results = []

    #
    # Barrel configuration:
    #
    if options.barrel :
        # The first calculation happens here:
        results.append(SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc,options))

        # Now do the other structures:
        for conf in config_files[1:] :
            Config.SetConfigFile('%s/data/%s'%(the_path,conf))
            Config.ReloadAllPythonModules()
            results.append(SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc,options))

    #
    # Endcap configuration:
    #
    if options.endcap :
        # The first calculation happens here:
        results.append(SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc,options))
        structure_names.append('R%dD%d'%(0,0))

        # Loop over the rings (config files)
        for ring,conf in enumerate(config_files) :

            # (We already loaded config file 0
            if ring != 0 :
                Config.SetConfigFile('%s/data/%s'%(the_path,conf),doprint=False)

            for disk in range(6) :
                if ring == 0 and disk == 0 :
                    continue # we already did the first point.
                Config.SetValue('OperationalProfiles.totalflux',GetFlux(ring,disk))
                Config.SetValue('OperationalProfiles.tid_in_3000fb',GetTID(ring,disk))
                print 'CALCULATING Ring %d Disk %d:'%(ring,disk)
                Config.Print()

                Config.ReloadAllPythonModules()
                results.append(SensorTemperatureCalc.CalculateSensorTemperature(time_step_tc,options))
                structure_names.append('R%dD%d'%(ring,disk))

    import python.ExtendedModelSummaryPlots as ExtendedModelSummaryPlots
    ExtendedModelSummaryPlots.ProcessSummaryPlots(results,structure_names,options)

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
    p.add_option('--barrel',action='store_true',default=False,dest='barrel',help='Run the barrel')
    p.add_option('--endcap',action='store_true',default=False,dest='endcap',help='Run the barrel')

    options,args = p.parse_args()

    options.save = False

    if options.barrel == options.endcap :
        print 'Error! Please specify either --barrel or --endcap (not both).'
        sys.exit()
    
    main(options,args)
