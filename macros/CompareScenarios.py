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
    
#-----------------------------------------------
def FindAutoLabel(config,nom,changed='') :
    env_config = ROOT.TEnv('%s/data/%s'%(the_path,config))
    nom = ROOT.TEnv('%s/data/%s'%(the_path,nom))

    if changed :
        for ci in changed.split(',') :
            env_config.SetValue(ci.split(':')[0],ci.split(':')[1])

    name = ''

    for i in range(env_config.GetTable().GetSize()) :
        tenvrec = env_config.GetTable().At(i)
        nm = tenvrec.GetName()
        if not nom.Defined(tenvrec.GetName()) or env_config.GetValue(nm,'') != nom.GetValue(nm,'') :
            if name :
                name += '; '
            variable = {'SafetyFactors.safetyfluence'         :'SF_{#font[52]{flux}}',
                        'SafetyFactors.safetythermalimpedance':'SF_{#font[52]{RThermal}}',
                        'SafetyFactors.safetycurrentd'        :'SF_{#font[52]{Idigital}}',
                        'SafetyFactors.safetycurrenta'        :'SF_{#font[52]{Ianalog}}',
                        'ThermalImpedances.rfeast'            :'R_{FEAST}',
                        'NominalPower.nfeast'                 :'_{}n_{FEAST}',
                        'NominalPower.nabc'                   :'nabc',
                        'SensorProperties.Rhvmux'             :'R_{HVMUX}',
                        }.get(tenvrec.GetName(),tenvrec.GetName())
            value = tenvrec.GetValue()
            if tenvrec.GetName() in ['SafetyFactors.safetyfluence',
                                     'SafetyFactors.safetythermalimpedance',
                                     'SafetyFactors.safetycurrentd',
                                     'SafetyFactors.safetycurrenta',
                                     ] :
                value = str(float(value) + 1.0)
            if tenvrec.GetName() == 'SensorProperties.Rhvmux' :
                value = '%s M#Omega'%(float(value)/1000000.)
            if tenvrec.GetName() == 'cooling' :
                value = '%s #circ^{}C'%(value).replace('-',' #minus^{}')
            name += '%s^{ }=^{ }%s'%(variable,value)
            name = name.replace('SafetyFactors.TIDpessimistic^{ }=^{ }True','Pessimistic TID')

    name = ' '+name
    return name

#-----------------------------------------------
def main(options,args):

    PlotUtils.ApplyGlobalStyle()
    PlotUtils.InitColorGradient()

    structure_names = []

    nominal_config = options.configs.split(',')[0]

    # Config must be loaded before loading any other module.
    Config.SetConfigFile('%s/data/%s'%(the_path,nominal_config),doprint=False)
    Config.SetMissingConfigsUsingCommandLine(options,nominal_config)

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
    

    for i,conf in enumerate(options.configs.split(',')) :
        changed = ''
        if i and options.change :
            changed = options.change
            if '::' in options.change :
                changed = options.change.split('::')[i-1]

        if options.autolabel :
            if i == 0 :
                name = ' nominal'
            else :
                name = FindAutoLabel(conf,nominal_config,changed=changed)
        if len(options.labels.split(',')) > i and options.labels.split(',')[i] :
            name = options.labels.split(',')[i]

        Config.SetConfigFile('%s/data/%s'%(the_path,conf),doprint=False)
        Config.SetMissingConfigsUsingCommandLine(options,conf)
        if changed :
            for ci in changed.split(',') :
                Config.SetValue(ci.split(':')[0],ci.split(':')[1])

        print 'CALCULATING scenario \"%s\" (%s):'%(name,Config.GetName())

        Config.ReloadAllPythonModules()
        Config.Print()

        results.append(SensorTemperatureCalc.CalculateSensorTemperature(options))
        structure_names.append(name)

    # reload nominal conf file - for labeing purposes
    Config.SetConfigFile('%s/data/%s'%(the_path,nominal_config),doprint=False)
    Config.SetMissingConfigsUsingCommandLine(options,nominal_config)
    Config.ReloadAllPythonModules()

    # Add some output directory specifications
    main_label = 'CompareModels'
    coolingtag = PlotUtils.GetCoolingOutputTag(CoolantTemperature.cooling)
    options.outdir = '_'.join([main_label,options.outdir,coolingtag]).lstrip('_').replace('__','_')

    import python.ExtendedModelSummaryPlots as ExtendedModelSummaryPlots
    ExtendedModelSummaryPlots.ProcessSummaryPlots(results,structure_names,options,plotaverage=False)

    # Save config files in the output directory
    for conf in options.configs.split(',') :
        os.system('cp %s/data/%s %s/plots/%s/.'%(the_path,conf,os.getcwd().split('/StripsThermalModel')[0],options.outdir))

    print 'done'
    return

#-----------------------------------------------
if __name__ == '__main__':

    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--configs',type='string',default='Endcap_R3.config',dest='configs',help='Configuration files (comma-separated) -- please make sure they are in the data/ directory')
    p.add_option('--labels',type='string',default='',dest='labels',help='Configuration labels (comma-separated)')
    p.add_option('--outdir',type='string',default='Comparison',dest='outdir',help='Output directory')
    p.add_option('--autolabel',action='store_true',default=False,dest='autolabel',help='Auto-labeling')
    # Syntax for using "change" option: comma-separate changes within a config file. Separate by "::" options intended for different config files.
    # You should specify 2x the same config file in the --config option.
    # python CompareScenarios.py --outdir Compare --configs C1.config,C1.config --autolabel --change "SafetyFactors.vbias:500,SafetyFactors.safetyfluence:0.5"
    # python CompareScenarios.py --outdir Compare --configs C1.config,C1.config,C1.config --autolabel --change "SafetyFactors.vbias:500::SafetyFactors.vbias:600::SafetyFactors.vbias:700"
    p.add_option('--change',type='string',default='',dest='change',help='Individual configs to change (e.g. \"cooling:ramp-30\"')
    Config.AddConfigurationOptions(p)

    options,args = p.parse_args()

    options.save = False

    if not options.autolabel and len(options.configs.split(',')) != len(options.labels.split(',')) :
        print 'ERROR: Length of labels does not equal the number of configs. Exiting.'
        import sys; sys.exit()

    main(options,args)
