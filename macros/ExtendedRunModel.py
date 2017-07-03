#!/usr/bin/env python

import os,sys
import math
import ROOT
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

ROOT.gROOT.SetBatch(True)

import python.PlotUtils as PlotUtils
import python.FluxAndTidParameterization as FluxAndTidParameterization
import python.Config as Config

def usage() :
    print "Usage:\n"
    print 'python '+sys.argv[0]+' --cooling <coolingScenarioTag> --barrel'
    print '--cooling:   cooling scheme: \"flat-25\",\"flat-35\",\"ramp-25\",\"ramp-35\"'
    print '--barrel:    run the barrel configuration'
    print '--endcap:    run the barrel configuration'
    print 'Example: '
    print 'python %s --cooling flat-25 --endcap'%(sys.argv[0])
    sys.exit()

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
    Config.SetConfigFile('%s/data/%s'%(the_path,config_files[0]),doprint=False)
    Config.SetMissingConfigsUsingCommandLine(options,config_files[0])

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
    import python.CoolantTemperature  as CoolantTemperature
    print 'importing modules done.'

    results = []

    #
    # Barrel configuration:
    #
    if options.barrel :

        # Loop over the layers:
        for conf in config_files :
            Config.SetConfigFile('%s/data/%s'%(the_path,conf),doprint=False)
            Config.SetMissingConfigsUsingCommandLine(options,conf)
            Config.ReloadAllPythonModules()
            Config.Print()

            results.append(SensorTemperatureCalc.CalculateSensorTemperature(options))

    #
    # Endcap configuration:
    #
    if options.endcap :

        # Loop over the rings (config files)
        for ring,conf in enumerate(config_files) :

            Config.SetConfigFile('%s/data/%s'%(the_path,conf),doprint=False)

            # Loop over the disks
            for disk in range(6) :
                Config.SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetFlux(ring,disk))
                Config.SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetTID(ring,disk))
                Config.SetMissingConfigsUsingCommandLine(options,conf)
                print 'CALCULATING Ring %d Disk %d (%s):'%(ring,disk,Config.GetName())
                Config.ReloadAllPythonModules()
                Config.Print()

                results.append(SensorTemperatureCalc.CalculateSensorTemperature(options))
                structure_names.append('R%dD%d'%(ring,disk))

    # Add some output directory specifications
    barrel_endcap = 'ExtendedModelBarrel' if options.barrel else 'ExtendedModelEndcap'
    coolingtag = PlotUtils.GetCoolingOutputTag(CoolantTemperature.cooling)
    options.outdir = '_'.join([barrel_endcap,options.outdir,coolingtag]).lstrip('_').replace('__','_')

    import python.ExtendedModelSummaryPlots as ExtendedModelSummaryPlots
    ExtendedModelSummaryPlots.ProcessSummaryPlots(results,structure_names,options,speciallegend=options.endcap,plotaverage=False)

    if options.endcap :
        ExtendedModelSummaryPlots.ProcessSummaryTables_Endcap(results,structure_names,options)

    # Save config files in the output directory
    for conf in config_files :
        os.system('cp %s/data/%s %s/plots/%s/.'%(the_path,conf,os.getcwd().split('/StripsThermalModel')[0],options.outdir))

    print 'done'
    return

#-----------------------------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 1:
        print "Wrong number of arguments"
        usage()

    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--barrel',action='store_true',default=False,dest='barrel',help='Run the barrel')
    p.add_option('--endcap',action='store_true',default=False,dest='endcap',help='Run the barrel')
    p.add_option('--outdir',type='string',default='',dest='outdir',help='Output directory')
    Config.AddConfigurationOptions(p)

    options,args = p.parse_args()

    options.save = False

    if options.barrel == options.endcap :
        print 'Error! Please specify either --barrel or --endcap (not both).'
        sys.exit()
    
    main(options,args)
