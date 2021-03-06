#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)
ROOT.gROOT.SetMacroPath(the_path)
ROOT.gROOT.SetBatch(True)

#-----------------------------------------------
def main(options,args) :

    # Dummy config must be loaded before loading any other module.
    import python.Config as Config
    Config.SetConfigFile('%s/data/%s'%(the_path,'Barrel_B0.config'),doprint=False)
    Config.SetValue('SafetyFactors.TIDpessimistic',options.pess)

    import python.AbcTidBump as AbcTidBump
    import python.PlotUtils as PlotUtils
    import python.TAxisFunctions as TAxisFunctions

    PlotUtils.ApplyGlobalStyle()
    PlotUtils.InitColorGradient()
    
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
        #print "Datapoint %.2f, %.2f, %.2f" % (float(datapoint[0]), float(datapoint[1]), float(datapoint[2]))
        data_all['x'].append(float(datapoint[0]))
        data_all['y'].append(float(datapoint[1]))
        data_all['z'].append(float(datapoint[2]))
        
    #-------------------------
    # Overall 3D plot 
    #-------------------------
    c3 = ROOT.TCanvas("tid_scalefactor_3d","TID Overall scale factor",0,0,600,400);
    AbcTidBump.tid_scalefactor_GeorgGraham_tf2.SetLineWidth(1)
    AbcTidBump.tid_scalefactor_GeorgGraham_tf2.SetLineColor(12) # grey
    AbcTidBump.tid_scalefactor_GeorgGraham_tf2.Draw("surf1")
        
    g2D = ROOT.TGraph2D(len(data_all['x']), array('d',data_all['x']), array('d',data_all['y']),array('d',data_all['z']))
    g2D.SetMarkerSize(1)
    g2D.SetMarkerStyle(20)
    g2D.SetMarkerColor(1)
    
    PlotUtils.Set2DStyleTitles(AbcTidBump.tid_scalefactor_GeorgGraham_tf2, "TID overall scale factor", "T [#circ C]", "Dose rate [kRad/hr]", "TID scale factor")
    
    g2D.Draw('same p')
    
    c3.Print('%s/plots/AbcTidBump/AbcTidBumpOverall_all.eps'%(the_path))

    #-------------------------
    # Shape vs collected dose 
    #-------------------------
    c4 = ROOT.TCanvas('tid_scale_shape_at_D', 'TID shape scale factor',600,500)
    dose = []
    shapeArray = []
    for i in range(0, 10000, 10) :
        dose.append(float(i))
        shapeArray.append(AbcTidBump.tid_shape_GeorgGraham(-999,-999,i,options.pess)) # no dependence on T or doserate
    gShape = PlotUtils.MakeGraph('TIDShape','TID shape vs collected dose','Dose [kRad]','Scale factor',dose,shapeArray)
    gShape.SetLineColor(3)
    gShape.Draw('al')
    
    c4.Print('%s/plots/AbcTidBump/AbcTidBumpShape.eps'%(the_path))
 
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
        fTm10.append(AbcTidBump.tid_scalePlusShape_GeorgGraham(-10., 1.1, i,options.pess))
        fTp10.append(AbcTidBump.tid_scalePlusShape_GeorgGraham( 10., 1.1, i,options.pess))
    
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
    
    c5.Print('%s/plots/AbcTidBump/AbcTidBumpCombinedSF.eps'%(the_path))

    ##
    # Overal * shape, temperature and doserate grid
    ##
    c5.Clear()
    time = []
    fT_and_DR = dict()
    # versions = ['v00','v01','v02','Apr2018']
    versions = ['Oct2017','Apr2018','Apr2018_nom','Apr2018_pess']
    temps = [-24,-18]
    rates = [1.,2.,3.]

    for v in versions :
        fT_and_DR[v] = dict()
        for temp in temps :
            fT_and_DR[v][temp] = dict()
            for rate in rates :
                fT_and_DR[v][temp][rate] = []

    for t,temp in enumerate(temps) :
        for r,rate in enumerate(rates) :
            #print 'Time     Dose     Rate     Temp'
            for i in range(300) :
                i = i/100.
                if not t+r :
                    time.append(i)
                Dose = float(i) # year
                Dose = Dose * (180. / 1.) * (24. / 1.) * (0.3) # hours = year * (d/y) * (h/d) * efficiency
                Dose = Dose * float(rate) # kRad = hours * (kRad/hr)
                #print '%8.1f %8.1f %8.1f %8.1f'%(i,Dose,rate,temp)
                fT_and_DR['Oct2017'][temp][rate].append(AbcTidBump.tid_scalePlusShape_Kyle_Oct2017(temp,rate,Dose,options.pess))
                fT_and_DR['Apr2018'][temp][rate].append(AbcTidBump.tid_scalePlusShape_Kyle_Apr2018(temp,rate,Dose,options.pess))

    dummy = dict()
    for j,rate in enumerate(rates) :
        gr = ROOT.TGraph(1,array('d',[0]),array('d',[0]))
        gr.SetTitle('D = %0.1f kRad/hr'%(rate))
        gr.SetLineStyle([1,15,16,17,18][j])
        gr.SetLineWidth(3)
        dummy[rate] = gr

    dummy_old = ROOT.TGraph(1,array('d',[0]),array('d',[0]))
    dummy_old.SetTitle('Oct2017 TID parameterization')
    dummy_old.SetLineWidth(1)

    ##
    ## Parameterization Comparison Plot
    ##
    gComb = dict()
    leg5 = ROOT.TLegend(0.47,0.70,0.84,0.94)
    leg5.SetNColumns(2)
    leg5.AddEntry('','^{ }'+('Pessimistic' if options.pess else 'Nominal') + ' scenarios','')
    leg5.AddEntry('','','')
    PlotUtils.SetStyleLegend(leg5)
    nominal = None
    temps_comparison = [-24]
    for v,version in enumerate(['Oct2017','Apr2018']) :
        gComb[version] = dict()
        for i,temp in enumerate(temps_comparison) :
            gComb[version][temp] = dict()
            for j,rate in enumerate(rates) :
                title = ('T = %3d#circ C'%(temp)).replace('-','#minus')
                gr = PlotUtils.MakeGraph('TIDScaleCombined',title,'Time [year]','Scale factor',time,fT_and_DR[version][temp][rate])
                gr.SetLineColor(PlotUtils.ColorGradient(i,len(temps_comparison)))
                gr.SetFillColor(PlotUtils.ColorGradient(i,len(temps_comparison)))
                gr.SetLineStyle([1,15,16,17,18][j])
                gr.SetLineWidth(2*v+1)
                gr.Draw('l' if i+j+v else 'al')

                # Add the "current" version to the plot
                if not j and not i and v :
                    # will be added later... see below.
                    nominal = gr

                # Add temperature and rate legend entries
                if (not j) and v :
                    # Temperature legend entries. Only one temperature at a time, or else too busy!
                    leg5.AddEntry('','^{ }'+gr.GetTitle(),'')
                    # Rate legend entries:
                    if i < len(rates) :
                        leg5.AddEntry(dummy[rates[i]],'^{ }'+dummy[rates[i]].GetTitle(), "l")
                gComb[version][temp][rate] = gr

    # Add additional legend items
    if len(temps_comparison) < len(rates) :
        for j,rate in enumerate(rates) :
            if j < len(temps_comparison) :
                continue
            leg5.AddEntry('','','')
            leg5.AddEntry(dummy[rates[j]],'^{ }'+dummy[rates[j]].GetTitle(), "l")

    # Add legend item for old function
    leg5.AddEntry(dummy_old,'^{ }'+dummy_old.GetTitle(),'l')
    leg5.AddEntry('','','')
    leg5.AddEntry(nominal,'^{ }Apr2018 TID parameterization','l')
    leg5.AddEntry('','','')
    leg5.Draw()
    TAxisFunctions.AutoFixYaxis(c5)

    c5.Print('%s/plots/AbcTidBump/AbcTidBumpVersionComparison_%s.eps'%(the_path,('Pessimistic' if options.pess else 'Nominal')))

    ##
    ## Different temperatures (one parameterization)
    ##
    gComb = dict()
    leg5 = ROOT.TLegend(0.47,0.74,0.84,0.94)
    leg5.SetNColumns(2)
    leg5.AddEntry('','^{ }'+('Pessimistic' if options.pess else 'Nominal') + ' scenarios','')
    leg5.AddEntry('','','')
    PlotUtils.SetStyleLegend(leg5)
    nominal = None
    for v,version in enumerate(['Apr2018']) :
        gComb[version] = dict()
        for i,temp in enumerate(temps) :
            gComb[version][temp] = dict()
            for j,rate in enumerate(rates) :
                title = ('T = %3d#circ C'%(temp)).replace('-','#minus')
                gr = PlotUtils.MakeGraph('TIDScaleCombined',title,'Time [year]','Scale factor',time,fT_and_DR[version][temp][rate])
                gr.SetLineColor(PlotUtils.ColorGradient(i,len(temps)))
                gr.SetFillColor(PlotUtils.ColorGradient(i,len(temps)))
                gr.SetLineStyle([1,15,16,17,18][j])
                gr.SetLineWidth(2)
                gr.Draw('l' if i+j+v else 'al')

                # Add temperature and rate legend entries
                if (not j) :
                    # Temperature legend entries
                    leg5.AddEntry(gr,'^{ }'+gr.GetTitle(), "f")
                    # Rate legend entries:
                    if i < len(rates) :
                        leg5.AddEntry(dummy[rates[i]],'^{ }'+dummy[rates[i]].GetTitle(), "l")
                gComb[version][temp][rate] = gr

    # Add additional legend items
    if len(temps) < len(rates) :
        for j,rate in enumerate(rates) :
            if j < len(temps) :
                continue
            leg5.AddEntry('','','')
            leg5.AddEntry(dummy[rates[j]],'^{ }'+dummy[rates[j]].GetTitle(), "l")

    # Add legend item for old function
    leg5.AddEntry('','^{ }Apr2018 TID parameterization','')
    leg5.AddEntry('','','')
    leg5.Draw()
    TAxisFunctions.AutoFixYaxis(c5)

    c5.Print('%s/plots/AbcTidBump/AbcTidBumpVersionRatesAndTemps_%s.eps'%(the_path,('Pessimistic' if options.pess else 'Nominal')))
    

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    p.add_option('--pess',action='store_true',default=False,dest='pess',help='Pessimistic?')
    options,args = p.parse_args()
    
    main(options,args)
