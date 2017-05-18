#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PoweringEfficiency as PoweringEfficiency
import python.PlotUtils as PlotUtils

#-----------------------------------------------
def main(options,args) :

    c = ROOT.TCanvas('feast_fit_function','Feast Efficiency fit function',500,500)
    feast_data = open('%s/data/FeastEfficiencyData.txt'%(the_path),'r')

    # Collect data at T=10C and T=60C separately, for plotting.
    data_10 = {'x':[],'y':[]}
    data_60 = {'x':[],'y':[]}

    for line in feast_data :
        line = line.replace('\n','')
        datapoint = line.split()

        if not datapoint[1].isdigit() :
            print 'blah:',datapoint[1]
            continue
        
        # separate data collected at 10C and 60C
        if int(datapoint[1]) == 10 :
            data_10['x'].append(float(datapoint[0]))
            data_10['y'].append(float(datapoint[2]))
            
        # separate data collected at 10C and 60C
        if int(datapoint[1]) == 60 :
            data_60['x'].append(float(datapoint[0]))
            data_60['y'].append(float(datapoint[2]))
            
    feast_data_10 = ROOT.TGraph(len(data_10['x']),array('d',data_10['x']),array('d',data_10['y']))
    feast_data_10.SetMarkerSize(1)
    feast_data_10.SetMarkerStyle(20)    

    feast_data_60 = ROOT.TGraph(len(data_60['x']),array('d',data_60['x']),array('d',data_60['y']))
    feast_data_60.SetMarkerSize(1)
    feast_data_60.SetMarkerStyle(20)

    PoweringEfficiency.feast_fit_function_T10.Draw()
    PoweringEfficiency.feast_fit_function_T60.Draw('sames')
    feast_data_10.Draw('p')
    feast_data_60.Draw('p')
    
    
    
    PlotUtils.SetStyleTitles(PoweringEfficiency.feast_fit_function_T10, "FEAST Efficiency fit", "I_{load} [A]", "FEAST Efficiency")

    c.Print('%s/plots/FeastEfficiency.eps'%(the_path))
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
