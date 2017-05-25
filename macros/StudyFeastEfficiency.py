#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PoweringEfficiency as PoweringEfficiency
import python.PlotUtils as PlotUtils
from python.PlotUtils import MakeGraph

#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()

    c = ROOT.TCanvas('feast_fit_function','Feast Efficiency fit function',600,500)
    feast_data = open('%s/data/FeastEfficiencyData.txt'%(the_path),'r')

    # Collect data at T=10C and T=60C separately, for plotting.
    data_10 = {'x':[],'y':[]}
    data_60 = {'x':[],'y':[]}

    for line in feast_data :
        line = line.replace('\n','')
        datapoint = line.split()

        if not datapoint[1].isdigit() :
            continue
        
        # separate data collected at 10C and 60C
        if int(datapoint[1]) == 10 :
            data_10['x'].append(float(datapoint[0]))
            data_10['y'].append(float(datapoint[2]))
            
        # separate data collected at 10C and 60C
        if int(datapoint[1]) == 60 :
            data_60['x'].append(float(datapoint[0]))
            data_60['y'].append(float(datapoint[2]))
    
    
    # Drawing the fit 10 C + overlay data points:        
    feast_data_10 = MakeGraph('FeastEfficiency_Data_t10','Data, T=10#circ^{}C','I_{load} [A]','FEAST efficiency [%]',data_10['x'],data_10['y'])
    feast_data_10.SetMarkerColor(4)
    feast_data_10.Draw('ap')
    feast_data_10.GetHistogram().GetYaxis().SetRangeUser(58,82)

    PoweringEfficiency.feast_fit_function_T10.SetLineColor(62) # blue
    PoweringEfficiency.feast_fit_function_T10.Draw('same')

    # Drawing the fit 60 C + overlay data points:
    feast_data_60 = MakeGraph('FeastEfficiency_Data_t60','Data, T=60#circ^{}C','I_{load} [A]','FEAST efficiency [%]',data_60['x'],data_60['y'])
    feast_data_60.SetMarkerColor(2)
    feast_data_60.Draw('p')
    PoweringEfficiency.feast_fit_function_T60.SetLineColor(96)
    PoweringEfficiency.feast_fit_function_T60.Draw('same')
    
    # Legending
    leg= ROOT.TLegend(0.68,0.74,0.95,0.92)
    leg.AddEntry(feast_data_10,feast_data_10.GetTitle(), "p")
    leg.AddEntry(PoweringEfficiency.feast_fit_function_T10,"Fit, T=10#circ^{}C","l")
    leg.AddEntry(feast_data_60,feast_data_60.GetTitle(), "p")
    leg.AddEntry(PoweringEfficiency.feast_fit_function_T60,"Fit, T=60#circ^{}C","l")
    PlotUtils.SetStyleLegend(leg)
    leg.Draw()

    c.Print('%s/plots/FeastEfficiency/FeastEfficiency.eps'%(the_path))
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
