
import os
import ROOT
import PlotUtils
from PlotUtils import MakeGraph
import GlobalSettings
from array import array

def ProcessSummaryPlots(result_dicts,names,options) :
    # result_dicts: a list of dictionaries with results that we saved from CalculateSensorTemperature
    # names: a list of the corresponding names for result_dicts

    # Move output path outside code directory
    outputpath = '%s/plots/SensorTemperatureCalc'%(os.getcwd().split('/StripsThermalModel')[0])
    # If a different output name is specified
    if hasattr(options,'outdir') :
        outputpath = '%s/%s'%(outputpath,options.outdir)
    print 'ExtendedModelSummaryPlots output written to %s'%(outputpath)

    outputtag = PlotUtils.GetCoolingOutputTag(options.cooling)
    scenariolabel = PlotUtils.GetCoolingScenarioLabel(options.cooling)

    barrel_endcap = 'Barrel' if options.barrel else 'Endcap'
    
    # Write plots
    c = ROOT.TCanvas('blah','blah',600,500)

    xtitle = 'Time [years]'
    x = GlobalSettings.time_step_list[1:]

    colors = {'B1':ROOT.kGreen,
              'B2':ROOT.kBlue+1,
              'B3':ROOT.kRed+1,
              'B4':ROOT.kCyan+1,
              'R0':ROOT.kGreen,
              'R1':ROOT.kBlue+1,
              'R2':ROOT.kRed+1,
              'R3':ROOT.kCyan+1,
              'R4':ROOT.kMagenta+1,
              'R5':ROOT.kOrange+1,
              }

    styles = {'D0':1,
              'D1':10,
              'D2':11,
              'D3':12,
              'D4':13,
              'D5':14
              }

    #
    # Power per module
    #
    gr = dict()
    gr['pmodule'] = []
    average = [0]*len(result_dicts[0]['pmodule'])
    for i,name in enumerate(names) :
        gr['pmodule'].append(MakeGraph('PowerPerModule_%s'%(name),name,xtitle,'P [W]',x,result_dicts[i]['pmodule']))
        for j in range(len(result_dicts[i]['pmodule'])) :
            average[j] += result_dicts[i]['pmodule'][j]
        
    average = list(average[i]/float(len(result_dicts)) for i in range(len(average)))
    gr_average = MakeGraph('AveragePowerPerModule','average',xtitle,'P [W]',x,average)
    gr_average.SetLineWidth(4)

    if options.barrel :
        text = ROOT.TLegend(0.13,0.89,0.41,0.94)
        PlotUtils.SetStyleLegend(text)
        text.AddEntry(0,scenariolabel,'')

        leg = ROOT.TLegend(0.72,0.75,0.91,0.90)
        PlotUtils.SetStyleLegend(leg)
        for i,g in enumerate(gr['pmodule']) :
            g.SetLineColor(colors.get(names[i]))
            leg.AddEntry(g,g.GetTitle(),'l')
            g.Draw('l' if i else 'al')
            g.GetHistogram().GetYaxis().SetRangeUser(0,15)
    
    if options.endcap :
        text1 = ROOT.TLegend(0.11,0.83,0.46,0.92)
        PlotUtils.SetStyleLegend(text1)
        text1.AddEntry(0,'Power per module','')
        text1.AddEntry(0,scenariolabel,'')

        text = ROOT.TLegend(0.32,0.53,0.67,0.77)
        PlotUtils.SetStyleLegend(text)
        text.AddEntry(0,'DUMMY VALUES - NOT REAL NUMBERS','')

        dummy_graphs = []
        for i in range(6) :
            dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
            #dummy_graphs[-1].SetLineStyle([1,10,9,7,2,3][i])
            dummy_graphs[-1].SetLineStyle([1,10,11,12,13,14][i])
            dummy_graphs[-1].SetLineColor(ROOT.kGray+1)
            dummy_graphs[-1].SetLineWidth(2)

        leg = ROOT.TLegend(0.57,0.69,0.91,0.93)
        PlotUtils.SetStyleLegend(leg)
        leg.SetMargin(.5)
        leg.SetNColumns(2)
        for i,g in enumerate(gr['pmodule']) :
            g.SetLineColor(colors.get(names[i][:2]))
            g.SetLineStyle(styles.get(names[i][2:]))
            g.SetLineWidth(2)
            g.Draw('l' if i else 'al')
            g.GetHistogram().GetYaxis().SetRangeUser(7,15)
        
        for i,nm in enumerate(['R0D0','R1D0','R2D0','R3D0','R4D0','R5D0']) :
            leg.AddEntry(gr['pmodule'][names.index(nm)],nm[:2],'l')
            leg.AddEntry(dummy_graphs[i],'Disk %d'%(i),'l')
            
        # gr_average.Draw('l')
        # leg.AddEntry(gr_average,'Average','l')

        text1.Draw()

    leg.Draw()
    text.Draw()

    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    c.Print('%s/%s_%s_%s.eps'%(outputpath,barrel_endcap,'PowerPerModule',outputtag))
    return
