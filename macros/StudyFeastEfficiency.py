#!/usr/bin/env python

import ROOT
import os,sys
from array import array
import math

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PoweringEfficiency as PoweringEfficiency
import python.PlotUtils as PlotUtils
from python.PlotUtils import MakeGraph
import python.TAxisFunctions as TAxisFunctions

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()

    feast_data = dict()
    feast_data['v00'] = dict()
    feast_data['v00']['data'] = open('%s/data/FeastEfficiencyData.txt'%(the_path),'r')
    feast_data['v01'] = dict()
    feast_data['v01']['data'] = open('%s/data/FeastEfficiencyData_v01.txt'%(the_path),'r')

    # Collect data at T=10C and T=60C separately, for plotting. Also for fixed currents.
    for k in feast_data.keys() :
        feast_data[k]['isoTemp'] = dict()
        feast_data[k]['isoTemp'][10] = {'x':[],'y':[]}
        feast_data[k]['isoTemp'][60] = {'x':[],'y':[]}

        feast_data[k]['isoCurr'] = dict()
        for i in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0] :
            feast_data[k]['isoCurr'][i] = {'x':[],'y':[]}

    for k in feast_data.keys() :
        for line in feast_data[k]['data'] :
            line = line.replace('\n','')
            datapoint = line.split()

            if not isFloat(datapoint[0]) :
                continue

            # separate data collected at 10C and 60C
            if math.fabs(float(datapoint[1]) - 10) < 1.0 :
                feast_data[k]['isoTemp'][10]['x'].append(float(datapoint[0]))
                feast_data[k]['isoTemp'][10]['y'].append(float(datapoint[2]))

            # separate data collected at 10C and 60C
            if math.fabs(float(datapoint[1]) - 60) < 10.0 :
                feast_data[k]['isoTemp'][60]['x'].append(float(datapoint[0]))
                feast_data[k]['isoTemp'][60]['y'].append(float(datapoint[2]))

            # separate by current
            for i in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0] :
                if math.fabs(float(datapoint[0]) - i) < 0.01 :
                    feast_data[k]['isoCurr'][i]['x'].append(float(datapoint[1]))
                    feast_data[k]['isoCurr'][i]['y'].append(float(datapoint[2]))

    c = ROOT.TCanvas('feast_fit_function','Feast Efficiency fit function',600,500)
    
    # Iso-temperature plots
    for i,k in enumerate(feast_data.keys()) :
        for j,temp in enumerate([10,60]) :
            graph = MakeGraph('FeastEfficiencyData',
                              'T^{ }=^{ }%d#circ C data'%(temp),'I_{load} [A]','FEAST efficiency [%]',
                              feast_data[k]['isoTemp'][temp]['x'],
                              feast_data[k]['isoTemp'][temp]['y'])
            graph.SetMarkerColor(ROOT.kBlue)
            if temp == 60 :
                graph.SetMarkerColor(ROOT.kOrange+8)
            graph.GetHistogram().GetYaxis().SetRangeUser(58,82)
            graph.GetHistogram().GetXaxis().SetRangeUser(0.25,4.25)
            if k == 'v00' :
                graph.SetMarkerStyle(24)
            graph.Draw('p' if (i+j) else 'ap')
            feast_data[k]['isoTemp'][temp]['graph'] = graph

    for func in PoweringEfficiency.feast_func_fixedTemp.keys() :
        colors = {10:ROOT.kBlue,60:ROOT.kOrange+8}
        PoweringEfficiency.feast_func_fixedTemp[func].SetLineColor(colors.get(func,ROOT.kGray))
        PoweringEfficiency.feast_func_fixedTemp[func].SetLineStyle(7)
        PoweringEfficiency.feast_func_fixedTemp[func].Draw('same')

    for func in PoweringEfficiency.feast_func_fixedTemp_new.keys() :
        colors = {10:ROOT.kBlue,60:ROOT.kOrange+8}
        PoweringEfficiency.feast_func_fixedTemp_new[func].SetLineColor(colors.get(func,ROOT.kGray))
        PoweringEfficiency.feast_func_fixedTemp_new[func].Draw('same')

    # Re-draw to put them on top
    for i,k in enumerate(feast_data.keys()) :
        for j,temp in enumerate([10,60]) :
            feast_data[k]['isoTemp'][temp]['graph'].Draw('p')

    # plot
    leg= ROOT.TLegend(0.68,0.70,0.95,0.94)
    for k in feast_data.keys() :
        for t in [10,60] :
            gr = feast_data[k]['isoTemp'][t]['graph']
            if k == 'v01' :
                leg.AddEntry(gr,gr.GetTitle(),'p')
    for func in PoweringEfficiency.feast_func_fixedTemp_new.keys() :
        if func not in [10,60] :
            continue
        gr = PoweringEfficiency.feast_func_fixedTemp_new[func]
        leg.AddEntry(gr,"Fit, T = %d#circ C"%(func),"l")
    PlotUtils.SetStyleLegend(leg)

    dummy1 = ROOT.TGraph(1,array('d',[0]),array('d',[0]))
    dummy1.SetMarkerStyle(24)
    dummy1.SetTitle('Old data')
    dummy2 = ROOT.TGraph(1,array('d',[0]),array('d',[0]))
    dummy2.SetTitle('Old function')
    dummy2.SetLineStyle(7)
    dummy2.SetLineWidth(2)
    leg.AddEntry(dummy1,dummy1.GetTitle(),'p')
    leg.AddEntry(dummy2,dummy2.GetTitle(),'l')

    leg.Draw()
    TAxisFunctions.SetXaxisRanges(c,0.25,4.25)

    c.Print('%s/plots/FeastEfficiency/FeastEfficiency.eps'%(the_path))

    # Iso-current plots
    c.Clear()
    leg = ROOT.TLegend(0.65,0.74,0.94,0.94)
    leg.SetNColumns(2)
    PlotUtils.SetStyleLegend(leg)
    # versus temperature now:
    for i,k in enumerate(['v01']) :
        for j,curr in enumerate([0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0]) :
            if not feast_data[k]['isoCurr'][curr]['x'] :
                continue
            graph = MakeGraph('FeastEfficiencyData_isoCurr_%0.1f'%(curr),
                              'I^{ }=^{ }%0.1f A'%(curr),'T [#circ^{}C]','FEAST efficiency [%]',
                              feast_data[k]['isoCurr'][curr]['x'],
                              feast_data[k]['isoCurr'][curr]['y'])

            graph.SetMarkerColor(PlotUtils.ColorGradient(j,8))
            graph.GetHistogram().GetYaxis().SetRangeUser(60,85)
            graph.GetHistogram().GetXaxis().SetRangeUser(-50,65)
            if k == 'v00' :
                graph.SetMarkerStyle(24)
            feast_data[k]['isoCurr'][curr]['graph'] = graph

        for j,curr in enumerate([0.5,2.5,1.0,3.0,1.5,3.5,2.0,4.0]) :
            if not feast_data[k]['isoCurr'][curr]['x'] :
                continue
            graph = feast_data[k]['isoCurr'][curr]['graph']
            graph.Draw('p' if (i+j) else 'ap')
            if k == 'v01' :
                leg.AddEntry(graph,graph.GetTitle(),'p')

    for j,func in enumerate([0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0]) :
        # tf1 = PoweringEfficiency.feast_func_fixedCurr[func]
        # tf1.SetLineColor(PlotUtils.ColorGradient(j,8))
        # tf1.Draw('same')
        tf1 = PoweringEfficiency.feast_func_fixedCurr_new[func]
        tf1.SetLineColor(PlotUtils.ColorGradient(j,8))
        tf1.Draw('same')

    dummy = ROOT.TGraph(1,array('d',[0]),array('d',[0]))
    dummy.SetLineWidth(2)
    dummy.SetTitle('Fit')
    leg.AddEntry(dummy,dummy.GetTitle(),'l')
    TAxisFunctions.SetXaxisRanges(c,-50,65)
    leg.Draw()
    c.Print('%s/plots/FeastEfficiency/FeastEfficiency_isoCurrent.eps'%(the_path))
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
