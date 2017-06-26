#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.GlobalSettings as GlobalSettings
import python.PlotUtils as PlotUtils
import python.FluxAndTidParameterization as FluxAndTidParameterization
import python.TAxisFunctions as taxisfunc

#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()

    if options.barrel :
        config_files = ['Barrel_SS_B1.config',
                        'Barrel_SS_B2.config',
                        'Barrel_LS_B3.config',
                        'Barrel_LS_B4.config'
                        ]
        structure_names = ['B1','B2','B3','B4']

    if options.endcap :
        config_files = ['Endcap_R0.config',
                        'Endcap_R1.config',
                        'Endcap_R2.config',
                        'Endcap_R3.config',
                        'Endcap_R4.config',
                        'Endcap_R5.config',
                        ]
        structure_names = ['R0','R1','R2','R3','R4','R5']

    # Config must be loaded before loading any other module.
    import python.Config as Config
    Config.SetConfigFile('%s/data/%s'%(the_path,config_files[0]),doprint=False)

    if not Config.Defined('OperationalProfiles.totalflux') :
        Config.SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetMaxFlux(config_files[0]))

    if not Config.Defined('OperationalProfiles.tid_in_3000fb') :
        Config.SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetMaxTID(config_files[0]))

    import python.OperationalProfiles as OperationalProfiles

    gr = dict()

    # integrated luminosity
    gr['intLumi'] = PlotUtils.MakeGraph('IntegratedLuminosity','Integrated luminosity',
                                        'Time [year]','#lower[-0.2]{#scale[0.60]{#int}}Ldt [fb^{-1}]',
                                        GlobalSettings.time_step_list,
                                        OperationalProfiles.lumiramp
                                        )
    
    c = ROOT.TCanvas('blah','blah',600,500)
    gr['intLumi'].Draw('al')
    barrel_endcap = '_Barrel' if options.barrel else '_Endcap'
    c.Print('%s/plots/OperationalProfiles/IntegratedLuminosity.eps'%(the_path))



    # lumi per year
    gr['lumi/yr'] = PlotUtils.MakeGraph('LuminosityPerYear','Luminosity per year [fb^{-1}/yr]',
                                        'Time [year]','see legend',
                                        list(range(1,GlobalSettings.nyears+1)),
                                        OperationalProfiles.luminosity
                                        )
    # days per year
    gr['days/yr'] = PlotUtils.MakeGraph('DaysPerYear','Days per year',
                                        'Time [year]','see legend',
                                        list(range(1,GlobalSettings.nyears+1)),
                                        OperationalProfiles.daysperyear
                                        )
    # efficiency
    gr['eff'] = PlotUtils.MakeGraph('OperatingEfficiency','Operating Efficiency [%]',
                                    'Time [year]','see legend',
                                    list(range(1,GlobalSettings.nyears+1)),
                                    list(a*100. for a in OperationalProfiles.eff)
                                    )

    colors = {'lumi/yr':ROOT.kGreen,'days/yr':ROOT.kBlue,'eff':ROOT.kRed+1}
    leg = ROOT.TLegend(0.54,0.24,0.84,0.41)
    PlotUtils.SetStyleLegend(leg)
    for g in ['lumi/yr','days/yr','eff'] :
        gr[g].SetMarkerColor(colors.get(g,ROOT.kBlack))
        leg.AddEntry(gr[g],gr[g].GetTitle(),'p')

    c.Clear()
    gr['lumi/yr'].Draw('ap')
    gr['days/yr'].Draw('p')
    gr['eff'].Draw('p')
    leg.Draw()
    c.Print('%s/plots/OperationalProfiles/YearlyRunProfile.eps'%(the_path))

    for i,conf in enumerate(config_files) :
        Config.SetConfigFile('%s/data/%s'%(the_path,conf),doprint=False)
        if not Config.Defined('OperationalProfiles.totalflux') :
            Config.SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetMaxFlux(conf))
        if not Config.Defined('OperationalProfiles.tid_in_3000fb') :
            Config.SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetMaxTID(conf))
        Config.ReloadAllPythonModules()

        # accumulated total ionizing dose
        name = structure_names[i]
        gr['tid%s'%name] = PlotUtils.MakeGraph('Tid%s'%(name),name,'Time [year]','Dose [kRad]',
                                               GlobalSettings.time_step_list,
                                               OperationalProfiles.tid_dose)

        # dose rates
        gr['doserate%s'%name] = PlotUtils.MakeGraph('DoseRate%s'%name,name,'Time [year]','Dose rate [kRad/h]',
                                                    GlobalSettings.time_step_list[1:],
                                                    OperationalProfiles.doserate)

    # accumulated total ionizing dose -- plot
    leg = ROOT.TLegend(0.22,0.65,0.43,0.82)
    PlotUtils.SetStyleLegend(leg)

    colors = {'B1':ROOT.kGreen,
              'B2':ROOT.kBlue,
              'B3':ROOT.kRed+1,
              'B4':ROOT.kOrange+1,
              'R0':ROOT.kRed+1,
              'R1':ROOT.kBlue+1,
              'R2':ROOT.kGreen+1,
              'R3':ROOT.kOrange+1,
              'R4':ROOT.kMagenta+1,
              'R5':ROOT.kCyan+1,
              }

    c.Clear()
    for i,name in enumerate(structure_names) :
        nm = 'tid%s'%(name)
        gr[nm].SetLineColor(colors.get(name,ROOT.kBlack))
        leg.AddEntry(gr[nm],gr[nm].GetTitle(),'l')
        gr[nm].Draw('l' if i else 'al')
    leg.Draw()
    taxisfunc.AutoFixYaxis(c,ignorelegend=True)
    c.Print('%s/plots/OperationalProfiles/TotalIonizingDose%s.eps'%(the_path,barrel_endcap))

    # dose rates -- plot
    leg = ROOT.TLegend(0.72,0.66,0.93,0.83)
    PlotUtils.SetStyleLegend(leg)

    c.Clear()
    for i,name in enumerate(structure_names) :
        nm = 'doserate%s'%(name)
        gr[nm].SetLineColor(colors.get(name,ROOT.kBlack))
        leg.AddEntry(gr[nm],gr[nm].GetTitle(),'l')
        gr[nm].Draw('l' if i else 'al')
    leg.Draw()
    taxisfunc.AutoFixYaxis(c,ignorelegend=True,minzero=True)
    c.Print('%s/plots/OperationalProfiles/DoseRate%s.eps'%(the_path,barrel_endcap))

    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--barrel',action='store_true',default=False,dest='barrel',help='Run the barrel')
    p.add_option('--endcap',action='store_true',default=False,dest='endcap',help='Run the barrel')
    
    options,args = p.parse_args()

    if options.barrel == options.endcap :
        print 'Error! Please specify either --barrel or --endcap (not both).'
        sys.exit()

    main(options,args)
