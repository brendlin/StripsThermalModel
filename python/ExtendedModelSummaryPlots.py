
import os
import ROOT
import PlotUtils
from PlotUtils import MakeGraph
import TAxisFunctions as taxisfunc
import GlobalSettings
import CoolantTemperature
import TableUtils
import Layout
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

    outputpath = PlotUtils.GetOutputPath('ExtendedModelSummaryPlots',options)

    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    scenariolabel = PlotUtils.GetCoolingScenarioLabel(CoolantTemperature.cooling)

    barrel_endcap = ''
    if hasattr(options,'barrel') :
        structure_name = 'Barrel'  if options.barrel else 'Endcap'
        barrel_endcap  = 'Barrel_' if options.barrel else 'Endcap_'

    if not hasattr(options,'endcap') :
        options.endcap = False
    
    # Write plots
    c = ROOT.TCanvas('ExtendedModelSummaryPlotsCanvas','blah',600,500)

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
            if i :
                g.SetName('%s_%d'%(g.GetName(),i))
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
        PlotUtils.AddRunParameterLabels(text,[graphs[0].GetTitle()],wrap=True)
        text.Draw()

        if False :
            text_endcap_warning = ROOT.TLegend(0.32,0.63,0.67,0.69)
            PlotUtils.SetStyleLegend(text_endcap_warning)
            text_endcap_warning.AddEntry(0,'DUMMY VALUES - NOT REAL NUMBERS','')
            text_endcap_warning.Draw()

        minzero = PlotUtils.MakePlotMinimumZero(plotname)
        forcemin = PlotUtils.GetPlotForcedMinimum(plotname)

        if plotname in ['qsensor_headroom'] :
            c.SetLogy(True)

        taxisfunc.AutoFixYaxis(c,minzero=minzero,forcemin=forcemin)

        c.Print('%s/%s%s.eps'%(outputpath,barrel_endcap,graphs[0].GetName()))

        if plotname in ['qsensor_headroom'] :
            c.SetLogy(False)

    #
    # Process Totals
    #
    substructure_name = {'Barrel':'layer (both sides)',
                         'Endcap':'ring (both endcaps)'}.get(structure_name)
#     layer_or_ring = {'Barrel':'layer',
#                      'Endcap':'-----'}.get(structure_name)

    x = GlobalSettings.time_step_list[1:]
    powertotal = [] # Total power in full endcap or barrel (both sides)
    phvtotal   = [] # Total HV Power (sensor+resistors) in full endcap or barrel (both sides)
    nModuleSides = 2.
    nDetectors = 2. # 2 barrel sides; 2 endcaps
    for i in range(GlobalSettings.nstep) :
        powertotal.append(0)
        phvtotal.append(0)
        for result_dict in result_dicts :
            powertotal[i] += result_dict['pmodule'].GetY()[i]
            powertotal[i] += result_dict['peos'   ].GetY()[i] # peos should be 0 for R0-R4

            phvtotal[i] += result_dict['phv_wleakage' ].GetY()[i]

        # endcap          2              1/petal       npetals/ring     nEndcaps (2)
        # barrel          2              14/stave      nstaves/side     nSides (2)
        powertotal[i] *= (nModuleSides * Layout.nmod * Layout.nstaves * nDetectors / 1000.)
        phvtotal[i]   *= (nModuleSides * Layout.nmod * Layout.nstaves * nDetectors / 1000.)

    gr = dict()
    gr['powertotal'] = MakeGraph('TotalPower'  ,'Total Power in both %ss'%(structure_name)                   ,xtitle,'P_{%s} [kW]'%('Total'),x,powertotal)
    gr['phvtotal']   = MakeGraph('TotalHVPower','Total HV Power (sensor + resistors) in %ss'%(structure_name),xtitle,'P_{%s} [kW]'%('HV')   ,x,phvtotal  )

    for g in gr.keys() :
        c.Clear()
        gr[g].Draw('al')
        text.Clear()
        PlotUtils.AddRunParameterLabels(text,additionalinfo=[gr[g].GetTitle()])
        text.Draw()
        minzero = PlotUtils.MakePlotMinimumZero(g)
        forcemin = PlotUtils.GetPlotForcedMinimum(g)
        taxisfunc.AutoFixYaxis(c,minzero=minzero,forcemin=forcemin)
        c.Print('%s/%s%s.eps'%(outputpath,barrel_endcap,gr[g].GetName()))

    return

#--------------------------------------------
def ProcessSummaryTables(quantity_name,result_dicts,structure_names,options,target_index='tid') :
    # Target indices are 'start', 'tid', 'eol'

    outtext = ''

    time_label = {'tid'  :'TID bump',
                  'start':'Year 0',
                  'eol':'Year %d'%(GlobalSettings.nyears),
                  }.get(target_index)

    ncolumns = 8 if options.endcap else 2
    units = ''
    if '[' in result_dicts[0][quantity_name].GetYaxis().GetTitle() :
        units = result_dicts[0][quantity_name].GetYaxis().GetTitle().split('[')[1].split(']')[0]
        units = units.replace('#circ^{}','$^\circ$')
        units = '[%s]'%(units)
    header = '\multicolumn{%d}{|c|}{%s at %s %s}\\\\ \hline'%(ncolumns,result_dicts[0][quantity_name].GetTitle(),time_label,units)
    disk_ring_labels = '  & & \multicolumn{6}{c|}{Disk} \\\\\n\multirow{6}{*}{Ring}'
    the_lists = []

    if options.endcap :
        the_lists.append(['','','0','1','2','3','4','5'])
        for ring in range(5,-1,-1) :
            the_lists.append([])
            the_lists[-1].append('')
            the_lists[-1].append('%d'%(ring))
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                the_graph = result_dicts[index][quantity_name]
                idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
                time_index = {'start':0,
                              'tid'  :idig.index(max(idig)),
                              'eol'  :the_graph.GetN()-1,
                              }.get(target_index)
                result_double = the_graph.GetY()[time_index]
                the_lists[-1].append(result_double)

        table = TableUtils.PrintLatexTable(the_lists)
        table = table[:table.index('\n')+1] + disk_ring_labels + table[table.index('\n'):]
        table = table[:table.index('\n')+1] + header + table[table.index('\n'):]

    if options.barrel :
        for layer in range(4,0,-1) :
            the_lists.append([])
            the_lists[-1].append('B%d'%(layer))
            index = structure_names.index('B%d'%(layer))
            the_graph = result_dicts[index][quantity_name]
            idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
            time_index = {'start':0,
                          'tid'  :idig.index(max(idig)),
                          'eol'  :the_graph.GetN()-1,
                          }.get(target_index)
            result_double = the_graph.GetY()[time_index]
            the_lists[-1].append(result_double)

        table = TableUtils.PrintLatexTable(the_lists)
        table = table[:table.index('\n')+1] + header + table[table.index('\n'):]

    print table
    outtext += table
    outtext += '\n'
    outtext += '\\vspace{4mm}\n'

    return outtext
