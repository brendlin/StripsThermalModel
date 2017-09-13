
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


def SetEndcapLegendSpecial(leg,graphs,doDisks=True,doRings=True) :
    leg.Clear()
    if doDisks and doRings :
        leg.SetNColumns(2)
    leg.SetMargin(.5)

    dummy_graphs = []
    for i in range(6) :
        if doRings :
            # Rings
            dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
            dummy_graphs[-1].SetLineColor(colors['R%d'%(i)])
            dummy_graphs[-1].SetLineWidth(2)
            leg.AddEntry(dummy_graphs[-1],'Ring %d'%(i),'l')

        if doDisks :
            # Disks
            dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
            dummy_graphs[-1].SetLineStyle([1,10,11,12,13,14][i])
            if doRings :
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

    styles = {'D0':1,'D1':10,'D2':11,'D3':12,'D4':13,'D5':14}

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

    x = GlobalSettings.time_step_list[1:]

    #
    # Process stave / petal totals. One dict per petal -- a list of 6 dicts.
    #

    if options.endcap :
        result_dicts_petals = [] # endcap

        for disk in range(6) :
            result_dicts_petals.append(dict())
            ppetal,qsensorpetal,phvpetal,itapepetal,isensorpetal = [],[],[],[],[]

            for i in range(GlobalSettings.nstep) :
                ppetal.append(0); qsensorpetal.append(0); phvpetal.append(0); itapepetal.append(0); isensorpetal.append(0)
                for ring in range(6) :
                    index = names.index('R%dD%d'%(ring,disk))
                    ppetal[i] += result_dicts[index]['pmodule'].GetY()[i]
                    ppetal[i] += result_dicts[index]['peos'   ].GetY()[i] # peos should be 0 for R0-R4
                    qsensorpetal[i] += result_dicts[index]['qsensor'].GetY()[i]
                    phvpetal[i] += result_dicts[index]['phv_wleakage'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape_eos'].GetY()[i]
                    isensorpetal[i] += result_dicts[index]['isensor'].GetY()[i]

            result_dicts_petals[disk]['pmodulepetal']      = MakeGraph('PetalPowerDisk%d'  %(disk),'Total Power in petal (with EOS) (one side)',xtitle,'P_{%s} [W]'%('Petal'),x,ppetal)
            result_dicts_petals[disk]['qsensorpetal']      = MakeGraph('PetalSensorQDisk%d'%(disk),'Total Sensor Q in petal (one side)'        ,xtitle,'P [W]'               ,x,qsensorpetal)
            result_dicts_petals[disk]['phv_wleakagepetal'] = MakeGraph('PetalHVPowerDisk%d'%(disk),'HV Power in petal (one side)'              ,xtitle,'P [W]'               ,x,phvpetal)
            result_dicts_petals[disk]['itapepetal']        = MakeGraph('PetalTapeCurrentLVDisk%d'%(disk),'LV tape current in petal (with EOS) (one side)',xtitle,'I [A]'     ,x,itapepetal)
            result_dicts_petals[disk]['isensorpetal']      = MakeGraph('PetalSensorCurrentDisk%d'%(disk),'Total Sensor (leakage) current (one side)',xtitle,'I [mA]'         ,x,isensorpetal)

            # Append to result_dicts for further use in ProcessSummaryTables
            index = names.index('R%dD%d'%(0,disk))
            for i in ['pmodulepetal','qsensorpetal','phv_wleakagepetal','itapepetal','isensorpetal'] :
                result_dicts[index][i] = result_dicts_petals[disk][i]

        for plotname in result_dicts_petals[0].keys() :
            c.Clear()

            leg = ROOT.TLegend(0.74,0.69,0.91,0.93)
            PlotUtils.SetStyleLegend(leg)
            dummy_graphs = SetEndcapLegendSpecial(leg,graphs,doRings=False)

            for disk in range(6) :
                result_dicts_petals[disk][plotname].SetLineStyle(styles.get('D%d'%disk,1))
                result_dicts_petals[disk][plotname].Draw('l' if disk else 'al')
            text.Clear()
            PlotUtils.AddRunParameterLabels(text,additionalinfo=[result_dicts_petals[0][plotname].GetTitle()])
            text.Draw()
            leg.Draw()
            minzero = PlotUtils.MakePlotMinimumZero(plotname)
            forcemin = PlotUtils.GetPlotForcedMinimum(plotname)
            taxisfunc.AutoFixYaxis(c,minzero=minzero,forcemin=forcemin)
            c.Print('%s/%s%s.eps'%(outputpath,barrel_endcap,result_dicts_petals[0][plotname].GetName().replace('Disk0','')))

    #
    # Process Totals
    #

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
        powertotal[i] *= (nModuleSides * Layout.nmod * Layout.nstaves * nDetectors)
        phvtotal[i]   *= (nModuleSides * Layout.nmod * Layout.nstaves * nDetectors)

    gr = dict()
    gr['pmoduletotal']      = MakeGraph('TotalPower'  ,'Total Power in both %ss'%(structure_name)                   ,xtitle,'P_{%s} [W]'%('Total'),x,powertotal)
    gr['phv_wleakagetotal'] = MakeGraph('TotalHVPower','Total HV Power (sensor + resistors) in %ss'%(structure_name),xtitle,'P_{%s} [W]'%('HV')   ,x,phvtotal  )

    result_dicts[0]['pmoduletotal']      = gr['pmoduletotal']
    result_dicts[0]['phv_wleakagetotal'] = gr['phv_wleakagetotal']

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
    caption = '%s at {\\bf %s} %s.'%(result_dicts[0][quantity_name].GetTitle(),time_label,units)
    disk_label = '\multirow{2}{*}{%s} & & \multicolumn{6}{c|}{Disk} \\\\\n'%(units)
    ring_label = '\multirow{6}{*}{Ring}'
    the_lists = []

    if options.endcap :
        the_lists.append(['','','0','1','2','3','4','5'])
        endcap_total = None

        # EOS (if applicable)
        if quantity_name in ['pmodule','itape'] :
            caption = caption.replace('(no EOS)','')
            the_lists.append([])
            the_lists[-1].append('')
            the_lists[-1].append('EOS')
            for disk in range(6) :
                quantity_name_eos = {'pmodule':'peos',
                                     'itape':'itape_eos',
                                     }.get(quantity_name)
                index = structure_names.index('R%dD%d'%(5,disk))
                the_graph = result_dicts[index][quantity_name_eos]
                idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
                time_index = {'start':0,
                              'tid'  :idig.index(max(idig)),
                              'eol'  :the_graph.GetN()-1,
                              }.get(target_index)
                the_lists[-1].append(the_graph.GetY()[time_index])

        # Individual modules on rings / disks
        for ring in range(5,-1,-1) :
            the_lists.append([])
            the_lists[-1].append(ring_label if ring == 5 else '')
            the_lists[-1].append('%d'%(ring))
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                the_graph = result_dicts[index][quantity_name]
                idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
                time_index = {'start':0,
                              'tid'  :idig.index(max(idig)),
                              'eol'  :the_graph.GetN()-1,
                              }.get(target_index)
                the_lists[-1].append(the_graph.GetY()[time_index])

        # Petal totals
        if quantity_name in ['qsensor','pmodule','phv_wleakage','itape','isensor'] :
            caption += ' The ``petal total\'\' corresponds to one petal side.'
            the_lists.append([])
            the_lists[-1] += ['petal total','']
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(0,disk))
                the_graph = result_dicts[index][quantity_name+'petal']
                # For "tid" take max, or value at max petal power
                ppetal = list(result_dicts[index]['pmodulepetal'].GetY()[i] for i in range(result_dicts[index]['pmodulepetal'].GetN()))
                tid_index = ppetal.index(max(ppetal))

                if target_index == 'start' :
                    the_lists[-1].append(the_graph.GetY()[0])
                elif target_index == 'eol' :
                    the_lists[-1].append(the_graph.GetY()[the_graph.GetN()-1])
                else :
                    result_start = the_graph.GetY()[0]
                    result_max   = max(list(the_graph.GetY()[i] for i in range(the_graph.GetN())))
                    result_tid   = the_graph.GetY()[tid_index]
                    result_eol   = the_graph.GetY()[the_graph.GetN()-1]
                    if (result_max == result_start) or (result_max == result_eol) :
                        the_lists[-1].append(result_tid)
                    elif result_max != result_tid :
                        print 'Warning! Maximum does not correspond to maximum power! %.3g vs %.3g'%(result_max,result_tid)
                        the_lists[-1].append(result_max)
                    else :
                        the_lists[-1].append(result_tid)

        # Endcap system totals
        if quantity_name in ['pmodule','phv_wleakage'] :
            caption += ' The ``endcaps total\'\' corresponds to both petal sides, all petals, 2 endcaps.'
            the_lists.append([])
            the_lists[-1] += ['endcaps total','']
            the_lists[-1] += ['-','-','-','-','-','-'] # this is a placeholder
            the_graph = result_dicts[0][quantity_name+'total']
            # For "tid" take max, or value at max petal power
            ptotal = list(result_dicts[0]['pmoduletotal'].GetY()[i] for i in range(result_dicts[0]['pmoduletotal'].GetN()))
            tid_index = ptotal.index(max(ptotal))

            if target_index == 'start' :
                endcap_total = the_graph.GetY()[0]
            elif target_index == 'eol' :
                endcap_total = the_graph.GetY()[the_graph.GetN()-1]
            else :
                result_start = the_graph.GetY()[0]
                result_max   = max(list(the_graph.GetY()[i] for i in range(the_graph.GetN())))
                result_tid   = the_graph.GetY()[tid_index]
                result_eol   = the_graph.GetY()[the_graph.GetN()-1]
                if (result_max == result_start) or (result_max == result_eol) :
                    endcap_total = result_tid
                elif result_max != result_tid :
                    print 'Warning! Maximum does not correspond to maximum power! %.3g vs %.3g'%(result_max,result_tid)
                    endcap_total = result_max
                else :
                    endcap_total = result_tid

        table = TableUtils.PrintLatexTable(the_lists,caption=caption)
        # insert special headers
        import re
        i_start_of_data = re.search("data_below\n",table).end()
        table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
        # convert to multiline
        table = re.sub('\npetal total\s+&','\hline\n\multicolumn{2}{|l|}{petal total}',table)
        if endcap_total != None :
            table = re.sub('\nendcaps total\s+&','\hline\n\multicolumn{2}{|l|}{endcaps total}',table)
            table = re.sub('\s+-\s+&\s+-\s+&\s+-\s+&\s+-\s+&\s+-\s+&\s+-','\multicolumn{6}{l|}{%.3g}'%(endcap_total),table)

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
            the_lists[-1].append(the_graph.GetY()[time_index])

        table = TableUtils.PrintLatexTable(the_lists,caption=caption)

    outtext += table
    outtext += '\n'

    return outtext
