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

    # Collect data at T=10C and T=60C separately, for plotting.
    for k in feast_data.keys() :
        feast_data[k]['vsCurrent'] = dict()
        feast_data[k]['vsCurrent'][10] = {'x':[],'y':[]}
        feast_data[k]['vsCurrent'][60] = {'x':[],'y':[]}

    for k in feast_data.keys() :
        for line in feast_data[k]['data'] :
            line = line.replace('\n','')
            datapoint = line.split()

            if not isFloat(datapoint[0]) :
                continue

            # separate data collected at 10C and 60C
            if math.fabs(float(datapoint[1]) - 10) < 1.0 :
                feast_data[k]['vsCurrent'][10]['x'].append(float(datapoint[0]))
                feast_data[k]['vsCurrent'][10]['y'].append(float(datapoint[2]))

            # separate data collected at 10C and 60C
            if math.fabs(float(datapoint[1]) - 60) < 10.0 :
                feast_data[k]['vsCurrent'][60]['x'].append(float(datapoint[0]))
                feast_data[k]['vsCurrent'][60]['y'].append(float(datapoint[2]))

    c = ROOT.TCanvas('feast_fit_function','Feast Efficiency fit function',600,500)
    
    # Drawing the fit 10 C + overlay data points:        
    for i,k in enumerate(feast_data.keys()) :
        for j,temp in enumerate([10,60]) :
            graph = MakeGraph('FeastEfficiency_Data_t10',
                              '%s, T=%d#circ C'%(k,temp),'I_{load} [A]','FEAST efficiency [%]',
                              feast_data[k]['vsCurrent'][temp]['x'],
                              feast_data[k]['vsCurrent'][temp]['y'])
            graph.SetMarkerColor(ROOT.kBlue)
            if temp == 60 :
                graph.SetMarkerColor(ROOT.kOrange+8)
            graph.GetHistogram().GetYaxis().SetRangeUser(58,82)
            graph.GetHistogram().GetXaxis().SetRangeUser(0.25,4.25)
            if k == 'v01' :
                graph.SetMarkerStyle(24)
            graph.Draw('p' if (i+j) else 'ap')
            feast_data[k]['vsCurrent'][temp]['graph'] = graph

    for func in PoweringEfficiency.feast_func_fixedTemp.keys() :
        PoweringEfficiency.feast_func_fixedTemp[func].SetLineColor(ROOT.kGray)
        if func == 10 :
            PoweringEfficiency.feast_func_fixedTemp[func].SetLineColor(ROOT.kBlue)
        if func == 60 :
            PoweringEfficiency.feast_func_fixedTemp[func].SetLineColor(ROOT.kOrange+8)
        PoweringEfficiency.feast_func_fixedTemp[func].Draw('same')

    for i,k in enumerate(feast_data.keys()) :
        for j,temp in enumerate([10,60]) :
            feast_data[k]['vsCurrent'][temp]['graph'].Draw('p')

    # Legending
    leg= ROOT.TLegend(0.68,0.74,0.95,0.92)
    for k in feast_data.keys() :
        for t in [10,60] :
            gr = feast_data[k]['vsCurrent'][t]['graph']
            leg.AddEntry(gr,gr.GetTitle(),'p')
    for func in PoweringEfficiency.feast_func_fixedTemp.keys() :
        if func not in [10,60] :
            continue
        gr = PoweringEfficiency.feast_func_fixedTemp[func]
        leg.AddEntry(gr,"Fit, T = %d#circ C"%(func),"l")
    PlotUtils.SetStyleLegend(leg)
    leg.Draw()
    TAxisFunctions.SetXaxisRanges(c,0.25,4.25)

    c.Print('%s/plots/FeastEfficiency/FeastEfficiency.eps'%(the_path))
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
