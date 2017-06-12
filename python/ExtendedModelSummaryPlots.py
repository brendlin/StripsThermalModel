
import os
import ROOT
import PlotUtils
from PlotUtils import MakeGraph
import TAxisFunctions as taxisfunc
import GlobalSettings
import CoolantTemperature
from array import array

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


def SetEndcapLegendSpecial(leg,graphs) :
    leg.Clear()
    leg.SetNColumns(2)
    leg.SetMargin(.5)

    dummy_graphs = []
    for i in range(6) :
        # Rings
        dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
        dummy_graphs[-1].SetLineColor(colors['R%d'%(i)])
        dummy_graphs[-1].SetLineWidth(2)
        leg.AddEntry(dummy_graphs[-1],'Ring %d'%(i),'l')

        # Disks
        dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
        dummy_graphs[-1].SetLineStyle([1,10,11,12,13,14][i])
        dummy_graphs[-1].SetLineColor(ROOT.kGray+1)
        dummy_graphs[-1].SetLineWidth(2)
        leg.AddEntry(dummy_graphs[-1],'Disk %d'%(i),'l')

    return dummy_graphs


def ProcessSummaryPlots(result_dicts,names,options,plotaverage=True,speciallegend=False) :
    # result_dicts: a list of dictionaries with results that we saved from CalculateSensorTemperature
    # names: a list of the corresponding names for result_dicts

    # Move output path outside code directory
    outputpath = '%s/plots/ExtendedModelSummaryPlots'%(os.getcwd().split('/StripsThermalModel')[0])
    # If a different output name is specified
    if hasattr(options,'outdir') :
        outputpath = '%s/plots/%s'%(os.getcwd().split('/StripsThermalModel')[0],options.outdir)
    print 'ExtendedModelSummaryPlots output written to %s'%(outputpath)

    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    scenariolabel = PlotUtils.GetCoolingScenarioLabel(CoolantTemperature.cooling)

    barrel_endcap = ''
    if hasattr(options,'barrel') :
        barrel_endcap = 'Barrel_' if options.barrel else 'Endcap_'

    if not hasattr(options,'endcap') :
        options.endcap = False
    
    # Write plots
    c = ROOT.TCanvas('blah','blah',600,500)

    xtitle = 'Time [years]'
    x = GlobalSettings.time_step_list[1:]

    styles = {'D0':1,
              'D1':10,
              'D2':11,
              'D3':12,
              'D4':13,
              'D5':14
              }

    list_of_plots = list(result_dicts[0].keys())

    for plotname in list_of_plots :

        # collect all the graphs
        graphs = list(a[plotname] for a in result_dicts)

        # For the average plot
        average = [0]*result_dicts[0][plotname].GetN()

        for i,name in enumerate(names) :
            for j in range(result_dicts[i][plotname].GetN()) :
                average[j] += result_dicts[i][plotname].GetY()[j]

        average = list(average[i]/float(len(result_dicts)) for i in range(len(average)))
        gr_average = MakeGraph('Average_%s'%(plotname),'average',xtitle,'P [W]',x,average)
        gr_average.SetLineWidth(4)

        leg = ROOT.TLegend(0.57,0.69,0.91,0.93)
        PlotUtils.SetStyleLegend(leg)
        for i,g in enumerate(graphs) :
            g.SetLineColor(colors.get(names[i][:2],PlotUtils.ColorPalette()[i]))
            if options.endcap :
                g.SetLineStyle(styles.get(names[i][2:],1))
            g.SetLineWidth(2)
            g.Draw('l' if i else 'al')
            leg.AddEntry(g,names[i],'l')

        # special legend for endcap
        if speciallegend :
            # save dummy graphs so they do not go out of scope
            dummy_graphs = SetEndcapLegendSpecial(leg,graphs)

        if plotaverage :
            gr_average.Draw('l')
            leg.AddEntry(gr_average,'Average','l')

        # make sure there are at least 5 entries in legend (spacing)
        for i in range(5 - len(graphs) - plotaverage) :
            leg.AddEntry(0,'','')

        leg.Draw()

        #
        # Descriptive text
        #
        text = ROOT.TLegend(0.11,0.70,0.46,0.92)
        PlotUtils.SetStyleLegend(text)
        add_label = [graphs[0].GetTitle(),'']
        while(len(add_label[0]) > 28) :
            tmp = add_label[0].split(' ')
            add_label[0] = ' '.join(tmp[:-1])
            add_label[1] = ' '.join([tmp[-1],add_label[1]])
        PlotUtils.AddRunParameterLabels(text,add_label)

        text.Draw()

        if options.endcap :
            text_endcap_warning = ROOT.TLegend(0.32,0.63,0.67,0.69)
            PlotUtils.SetStyleLegend(text_endcap_warning)
            text_endcap_warning.AddEntry(0,'DUMMY VALUES - NOT REAL NUMBERS','')
            text_endcap_warning.Draw()

        taxisfunc.AutoFixYaxis(c)

        c.Print('%s/%s%s.eps'%(outputpath,barrel_endcap,graphs[0].GetName()))

    return
