#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.GlobalSettings as GlobalSettings
import python.PlotUtils as PlotUtils

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

    # Config must be loaded before loading any other module.
    import python.Config as Config
    Config.SetConfigFile('%s/data/%s'%(the_path,config_files[0]),doprint=False)
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
              }

    c.Clear()
    for i,name in enumerate(structure_names) :
        nm = 'tid%s'%(name)
        gr[nm].SetLineColor(colors.get(name,ROOT.kBlack))
        leg.AddEntry(gr[nm],gr[nm].GetTitle(),'l')
        gr[nm].Draw('l' if i else 'al')
    leg.Draw()
    c.Print('%s/plots/OperationalProfiles/TotalIonizingDoseBarrel.eps'%(the_path))

    # dose rates -- plot
    leg = ROOT.TLegend(0.72,0.61,0.93,0.78)
    PlotUtils.SetStyleLegend(leg)

    c.Clear()
    for i,name in enumerate(structure_names) :
        nm = 'doserate%s'%(name)
        gr[nm].SetLineColor(colors.get(name,ROOT.kBlack))
        leg.AddEntry(gr[nm],gr[nm].GetTitle(),'l')
        gr[nm].Draw('l' if i else 'al')
    leg.Draw()
    c.Print('%s/plots/OperationalProfiles/DoseRateBarrel.eps'%(the_path))

    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--barrel',action='store_true',default=True,dest='barrel',help='Run the barrel')
    
    options,args = p.parse_args()
    
    main(options,args)
