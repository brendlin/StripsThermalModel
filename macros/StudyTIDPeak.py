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
    PlotUtils.ApplyGlobalStyle()
    
    tid_overall_data = open('%s/data/AbcTidBumpData.txt'%(the_path),'r')
    
    # x -> T, y -> d, z -> TID factor
    # Collect only points at T=-10C, T=-15 and T=-25 in separate arrays
    # Hardcoded for the moment, more elegant code later with fresh data
    data_m10 = {'y':[],'z':[]}
    data_m15 = {'y':[],'z':[]}
    data_m25 = {'y':[],'z':[]}
    data_all = {'x':[],'y':[],'z':[]}
    
    # Skip header row:
    lines = tid_overall_data.readlines()[1:]
    
    for row in lines:
        row = row.replace('\n','')
        datapoint = row.split()
        
        # T = -10 / -15 / -25
        if float(datapoint[0]) == -10 :
            data_m10['y'].append(float(datapoint[1]))
            data_m10['z'].append(float(datapoint[2]))
        elif float(datapoint[0]) == -15 :
            data_m15['y'].append(float(datapoint[1]))
            data_m15['z'].append(float(datapoint[2]))
        elif float(datapoint[0]) == -25 :   
            data_m25['y'].append(float(datapoint[1]))
            data_m25['z'].append(float(datapoint[2]))  
            
        # all points
        print "Datapoint %.2f, %.2f, %.2f" % (float(datapoint[0]), float(datapoint[1]), float(datapoint[2]))
        data_all['x'].append(float(datapoint[0]))
        data_all['y'].append(float(datapoint[1]))
        data_all['z'].append(float(datapoint[2]))
        
    #-------------------------
    # Projections for 3 Temps
    #-------------------------
    c = ROOT.TCanvas('tid_scale_overall_fit_function', 'TID Overall scale factor',500,500)
    
    # Caveat: hardcoded temp splits + need to plot T=-15 first 
    # 1D projection for data points T = -15
    AbcTidBump.tid_scale_overall_fit_function_Tm15.SetLineColor(8) # green
    AbcTidBump.tid_scale_overall_fit_function_Tm15.Draw()
    
    tid_overall_Tm15 = ROOT.TGraph(len(data_m15['y']),array('d',data_m15['y']),array('d',data_m15['z']))
    tid_overall_Tm15.SetMarkerSize(1)
    tid_overall_Tm15.SetMarkerStyle(20)
    tid_overall_Tm15.SetMarkerColor(8) # green
    tid_overall_Tm15.Draw('same p') 
    
    # 1D projection for data points T = -10
    AbcTidBump.tid_scale_overall_fit_function_Tm10.SetLineColor(96) # red
    AbcTidBump.tid_scale_overall_fit_function_Tm10.Draw('same')
    
    tid_overall_Tm10 = ROOT.TGraph(len(data_m10['y']),array('d',data_m10['y']),array('d',data_m10['z']))
    tid_overall_Tm10.SetMarkerSize(1)
    tid_overall_Tm10.SetMarkerStyle(20)
    tid_overall_Tm10.SetMarkerColor(2) # red
    tid_overall_Tm10.Draw('same p')

    # 1D projection for data points T = -25
    AbcTidBump.tid_scale_overall_fit_function_Tm25.SetLineColor(62) # blue
    AbcTidBump.tid_scale_overall_fit_function_Tm25.Draw('same')
    
    tid_overall_Tm25 = ROOT.TGraph(len(data_m25['y']),array('d',data_m25['y']),array('d',data_m25['z']))
    tid_overall_Tm25.SetMarkerSize(1)
    tid_overall_Tm25.SetMarkerStyle(20)
    tid_overall_Tm25.SetMarkerColor(60) # blue
    tid_overall_Tm25.Draw('same p')
    
        
    # Legending
    leg= ROOT.TLegend(0.4, 0.15, 0.9, 0.3)
    PlotUtils.SetStyleLegend(leg)
    leg.SetNColumns(2)
    #leg.AddEntry(tid_overall_Tm10, "Data points, T = -10 C", "p")
    #leg.AddEntry(AbcTidBump.tid_scale_overall_fit_function_Tm10,"Fit result,   T = -10 C","l")
    leg.AddEntry(tid_overall_Tm10, "Data", "p")
    leg.AddEntry(AbcTidBump.tid_scale_overall_fit_function_Tm10,"Fit result, T = -10 C","l")
    leg.AddEntry(tid_overall_Tm15, "Data", "p")
    leg.AddEntry(AbcTidBump.tid_scale_overall_fit_function_Tm15,"Fit result, T = -15 C","l") 
    leg.AddEntry(tid_overall_Tm25, "Data", "p")
    leg.AddEntry(AbcTidBump.tid_scale_overall_fit_function_Tm25,"Fit result, T = -25 C","l")
       
    leg.Draw()
    
    PlotUtils.SetStyleTitles(AbcTidBump.tid_scale_overall_fit_function_Tm15, "TID overall scale factor", "Dose rate [kRad/hr]", "TID scale factor")
    
    #c.Print('%s/plots/AbcTidBumpOverall_Tm10.eps'%(the_path))
    c.Print('%s/plots/AbcTidBumpOverall_factor_vs_d.eps'%(the_path))
    
    #c.SetLogx()
    #c.SetLogy()
    #c.Print('%s/plots/AbcTidBumpOverall_factor_vs_d_log.eps'%(the_path))
    
    # Let's remove that -15 point at d = 62
    AbcTidBump.tid_scale_overall_fit_function_Tm15.GetXaxis().SetRangeUser(0.,4.)
    c.Update()
    c.Print('%s/plots/AbcTidBumpOverall_factor_vs_d_restr.eps'%(the_path))
    
    #-------------------------
    # Overall 3D plot 
    #-------------------------
    c3 = ROOT.TCanvas("tid_scale_overall_fit_function","TID Overall scale factor",0,0,600,400);
    AbcTidBump.tid_scale_overall_fit_function.SetLineWidth(1)
    AbcTidBump.tid_scale_overall_fit_function.SetLineColor(12) # grey
    AbcTidBump.tid_scale_overall_fit_function.Draw("surf1")
        
    g2D = ROOT.TGraph2D(len(data_all['x']), array('d',data_all['x']), array('d',data_all['y']),array('d',data_all['z']))
    g2D.SetMarkerSize(1)
    g2D.SetMarkerStyle(20)
    g2D.SetMarkerColor(1)
    
    PlotUtils.Set2DStyleTitles(AbcTidBump.tid_scale_overall_fit_function, "TID overall scale factor", "T [#circ C]", "Dose rate [kRad/hr]", "TID scale factor")
    
    g2D.Draw('same p')
    
    c3.Print('%s/plots/AbcTidBumpOverall_all.eps'%(the_path))
    c3.Print('%s/plots/AbcTidBumpOverall_all.root'%(the_path))

    #-------------------------
    # Shape vs collected dose 
    #-------------------------
    c4 = ROOT.TCanvas('tid_scale_shape_at_D', 'TID shape scale factor',600,500)
    dose = []
    shapeArray = []
    for i in range(0, 10000, 10) :
        dose.append(float(i))
        shapeArray.append(AbcTidBump.tid_scale_shape(i))
    gShape = PlotUtils.MakeGraph('TIDShape','TID shape vs collected dose','Dose [kRad]','Scale factor',dose,shapeArray)
    gShape.SetLineColor(3)
    gShape.Draw('al')
    
    c4.Print('%s/plots/AbcTidBumpShape.eps'%(the_path))
 
    #-------------------------
    # Overall * shape => combined scale factor 
    #-------------------------   
    c5 = ROOT.TCanvas('tid_combined_1p1kRadhr', 'TID scaling for 1.1 kRad/hr',600,500)
    # Example Mathematica for d = 1.1 kRad/hr
    D = []
    fTm10 = []
    fTp10 = []
    for i in range(0,2200, 10) :
        D.append(i)
        fTm10.append(AbcTidBump.tid_scale_combined_factor(-10., 1.1, i))
        fTp10.append(AbcTidBump.tid_scale_combined_factor(10., 1.1, i))
    
    gCombm10 = PlotUtils.MakeGraph('TIDScaleCombined','TID scaling for 1.1 kRad/h','Dose [kRad]','Scale factor',D,fTm10)
    gCombm10.SetLineColor(4)
    gCombm10.SetMinimum(1.)
    gCombm10.GetXaxis().SetNdivisions(505)
    
    gCombp10 = PlotUtils.MakeGraph('TIDScaleCombined','TID scaling for 1.1 kRad/h','Dose [kRad]','Scale factor',D,fTp10)
    gCombp10.SetLineColor(3)
    
    gCombm10.Draw('al')
    gCombp10.Draw('l')
     
    leg5 = ROOT.TLegend(0.7,0.3,0.84,0.45)
    PlotUtils.SetStyleLegend(leg5)
    leg5.AddEntry(gCombm10, "T = -10 #circ C", "l")
    leg5.AddEntry(gCombp10, "T = +10 #circ C", "l")
    leg5.Draw()
    
    c5.Print('%s/plots/AbcTidBumpCombinedSF.eps'%(the_path))
    

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
