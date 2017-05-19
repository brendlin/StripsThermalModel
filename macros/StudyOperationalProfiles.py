#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.OperationalProfiles as OperationalProfiles
import python.GlobalSettings as GlobalSettings
import python.PlotUtils as PlotUtils

#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()

    gr = dict()

    # integrated luminosity
    gr['intLumi'] = PlotUtils.MakeGraph('IntegratedLuminosity','Integrated luminosity',
                                        'Time [year]','#lower[-0.2]{#scale[0.60]{#int}}Ldt [fb^{-1}]',
                                        GlobalSettings.time_step_list,
                                        OperationalProfiles.lumiramp
                                        )
    
    c = ROOT.TCanvas('blah','blah',600,500)
    gr['intLumi'].Draw('al')
    c.Print('%s/plots/IntegratedLuminosity.eps'%(the_path))



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
    c.Print('%s/plots/YearlyRunProfile.eps'%(the_path))



    # accumulated total ionizing dose
    gr['tidb1'] = PlotUtils.MakeGraph('TidB1','B1','Time [year]','Dose [kRad]',
                                           GlobalSettings.time_step_list,
                                           OperationalProfiles.tidb1)
    gr['tidb2'] = PlotUtils.MakeGraph('TidB2','B2','Time [year]','Dose [kRad]',
                                           GlobalSettings.time_step_list,
                                           OperationalProfiles.tidb2)
    gr['tidb3'] = PlotUtils.MakeGraph('TidB3','B3','Time [year]','Dose [kRad]',
                                           GlobalSettings.time_step_list,
                                           OperationalProfiles.tidb3)
    gr['tidb4'] = PlotUtils.MakeGraph('TidB4','B4','Time [year]','Dose [kRad]',
                                           GlobalSettings.time_step_list,
                                           OperationalProfiles.tidb4)

    leg = ROOT.TLegend(0.22,0.65,0.43,0.82)
    PlotUtils.SetStyleLegend(leg)
    colors = {'tidb1':ROOT.kGreen,'tidb2':ROOT.kBlue,
              'tidb3':ROOT.kRed+1,'tidb4':ROOT.kOrange+1}

    for g in ['tidb1','tidb2','tidb3','tidb4'] :
        gr[g].SetLineColor(colors.get(g,ROOT.kBlack))
        leg.AddEntry(gr[g],gr[g].GetTitle(),'l')

    c.Clear()
    gr['tidb1'].Draw('al')
    gr['tidb2'].Draw('l')
    gr['tidb3'].Draw('l')
    gr['tidb4'].Draw('l')
    leg.Draw()
    c.Print('%s/plots/TotalIonizingDoseBarrel.eps'%(the_path))
    raw_input('pause')


    # dose rates
    gr['doserateb1'] = PlotUtils.MakeGraph('DoseRateB1','B1','Time [year]','Dose rate [kRad/h]',
                                           GlobalSettings.time_step_list[1:],
                                           OperationalProfiles.doserateb1)
    gr['doserateb2'] = PlotUtils.MakeGraph('DoseRateB2','B2','Time [year]','Dose rate [kRad/h]',
                                           GlobalSettings.time_step_list[1:],
                                           OperationalProfiles.doserateb2)
    gr['doserateb3'] = PlotUtils.MakeGraph('DoseRateB3','B3','Time [year]','Dose rate [kRad/h]',
                                           GlobalSettings.time_step_list[1:],
                                           OperationalProfiles.doserateb3)
    gr['doserateb4'] = PlotUtils.MakeGraph('DoseRateB4','B4','Time [year]','Dose rate [kRad/h]',
                                           GlobalSettings.time_step_list[1:],
                                           OperationalProfiles.doserateb4)

    leg = ROOT.TLegend(0.72,0.61,0.93,0.78)
    PlotUtils.SetStyleLegend(leg)
    colors = {'doserateb1':ROOT.kGreen,'doserateb2':ROOT.kBlue,
              'doserateb3':ROOT.kRed+1,'doserateb4':ROOT.kOrange+1}

    for g in ['doserateb1','doserateb2','doserateb3','doserateb4'] :
        gr[g].SetLineColor(colors.get(g,ROOT.kBlack))
        leg.AddEntry(gr[g],gr[g].GetTitle(),'l')

    c.Clear()
    gr['doserateb1'].Draw('al')
    gr['doserateb2'].Draw('l')
    gr['doserateb3'].Draw('l')
    gr['doserateb4'].Draw('l')
    leg.Draw()
    c.Print('%s/plots/DoseRateBarrel.eps'%(the_path))

    raw_input('pause')
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
