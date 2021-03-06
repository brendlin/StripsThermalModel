#!/usr/bin/env python

import os,sys
import math
import ROOT
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)
ROOT.gROOT.SetMacroPath(the_path)

ROOT.gROOT.SetBatch(True)

import python.PlotUtils as PlotUtils
import python.FluxAndTidParameterization as FluxAndTidParameterization
import python.Config as Config

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
    PlotUtils.InitColorGradient()

    config_text = ''

    # Config must be loaded before loading any other module.
    Config.SetConfigFile('%s/data/%s'%(the_path,options.config),doprint=False)
    Config.SetMissingConfigsUsingCommandLine(options)
    if options.change :
        for ci in options.change.split(',') :
            Config.SetValue(ci.split(':')[0],ci.split(':')[1])

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

    config_text += '%% %s:\n'%(Config.GetName())
    config_text += Config.Print() + '\n'

    # Add some output directory specifications
    coolingtag = PlotUtils.GetCoolingOutputTag(CoolantTemperature.cooling)
    configtag = options.config.replace('.config','')
    options.outdir = '_'.join([configtag,options.outdir,coolingtag]).lstrip('_').replace('__','_')

    # The main calculations happen here:
    SensorTemperatureCalc.CalculateSensorTemperature(options)

    # Save config files in the output directory
    os.system('cp %s/data/%s %s/plots/%s/.'%(the_path,options.config,os.getcwd().split('/StripsThermalModel')[0],options.outdir))

    # Save config summary table
    outputpath = PlotUtils.GetOutputPath('SensorTemperatureCalc',options)
    f = open('%s/ConfigTables.txt'%(outputpath),'w')
    f.write(config_text)
    f.close()

    print 'done'
    return

#-----------------------------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 1:
        print "Wrong number of arguments"
        usage()

    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--config' ,type='string',default='Barrel_SS_B1.config',dest='config',help='Configuration file -- please make sure it is put in the data/ directory')
    p.add_option('--outdir',type='string',default='',dest='outdir',help='Output directory')
    p.add_option('--change',type='string',default='',dest='change',help='Individual configs to change (e.g. \"cooling:ramp-30\"')
    Config.AddConfigurationOptions(p)

    options,args = p.parse_args()
    
    main(options,args)
