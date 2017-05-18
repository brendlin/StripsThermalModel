#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.AbcTidBump as AbcTidBump
import python.PlotUtils as PlotUtils

#-----------------------------------------------
def main(options,args) :

    tid_overall_data = open('%s/data/AbcTidBumpData.txt'%(the_path),'r')
    
    # Collect only points at T=-10C
    # x -> d, y -> TID factor
    data_m10 = {'x':[],'y':[]}
    data_all = {'x':[],'y':[]}
    
    # Skip header row:
    lines = tid_overall_data.readlines()[1:]
    
    for row in lines:
        row = row.replace('\n','')
        datapoint = row.split()
        
        # T = -10 
        if float(datapoint[0]) == -10 :
            print "Datapoint %.2f, %.2f, %.2f" % (float(datapoint[0]), float(datapoint[1]), float(datapoint[2]))
            data_m10['x'].append(float(datapoint[1]))
            data_m10['y'].append(float(datapoint[2]))
            
        # all points
        data_all['x'].append(float(datapoint[1]))
        data_all['y'].append(float(datapoint[2]))
        
    # 1D projection for data points T = -10
    c = ROOT.TCanvas('tid_scale_overall_fit_function', 'TID Overall scale factor', 500,500)
    tid_overall_Tm10 = ROOT.TGraph(len(data_m10['x']),array('d',data_m10['x']),array('d',data_m10['y']))
    tid_overall_Tm10.SetMarkerSize(1)
    tid_overall_Tm10.SetMarkerStyle(20)
    
    AbcTidBump.tid_scale_overall_fit_function_Tm10.Draw()
    tid_overall_Tm10.Draw('same p')
    
    PlotUtils.SetStyleTitles(AbcTidBump.tid_scale_overall_fit_function_Tm10, "TID overall scale factor, T = -10 C", "Dose rate [kRad/hr]", "TID scale factor")
    
    c.Print('%s/plots/AbcTidBumpOverall_Tm10.eps'%(the_path))
      
    # Here 3D plot 
    # animation?
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
