
import os
import ROOT
import PlotUtils
from PlotUtils import MakeGraph
import TAxisFunctions as taxisfunc
import GlobalSettings
import CoolantTemperature
import TableUtils
import Layout
import CableLosses
from array import array

colors = {'L0':ROOT.kGreen,
          'L1':ROOT.kBlue+1,
          'L2':ROOT.kRed+1,
          'L3':ROOT.kCyan+1,
          'R0':ROOT.kGreen,
          'R1':ROOT.kBlue+1,
          'R2':ROOT.kRed+1,
          'R3':ROOT.kCyan+1,
          'R4':ROOT.kMagenta+1,
          'R5':ROOT.kOrange+1,
          }


def SetEndcapLegendSpecial(leg,graphs,doDisks=True,doRings=True,multiplexedhv=False) :
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
            if multiplexedhv :
                if i == 1 or i == 3 :
                    leg.AddEntry(dummy_graphs[-1],'Ring%d/%d'%(i,i+1),'l')
                elif i == 0 or i == 2 :
                    leg.AddEntry(0,' ','')
                else :
                    leg.AddEntry(dummy_graphs[-1],'Ring %d'%(i),'l')
            else :
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

def SetBarrelLegendSpecial(leg,graphs,doLayers=True,doModules=True) :
    leg.Clear()
    if doLayers and doModules :
        leg.SetNColumns(2)
    leg.SetMargin(.3)

    dummy_graphs = []
    for i in range(Layout.nlayers_or_disks) :
        if doLayers :
            # Rings
            dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
            dummy_graphs[-1].SetLineColor(colors['R%d'%(i)])
            dummy_graphs[-1].SetLineWidth(2)
            leg.AddEntry(dummy_graphs[-1],'^{ }Layer %d'%(i),'l')

        if doModules and (i < 3) :
            dummy_graphs.append(ROOT.TGraph(1,array('d',[1]),array('d',[1])))
            dummy_graphs[-1].SetLineWidth(2)
            dummy_graphs[-1].SetLineStyle([1,19,14][i])
            if doLayers :
                dummy_graphs[-1].SetLineColor(ROOT.kGray+1)
            if i == 0 :
                leg.AddEntry(dummy_graphs[-1],'^{ }Module 0','l')
            if i == 1 :
                leg.AddEntry(dummy_graphs[-1],'^{ }Modules 1-12','l')
            if i == 2 :
                leg.AddEntry(dummy_graphs[-1],'^{ }Module 13','l')

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
        structure_name = 'barrel side'  if options.barrel else 'endcap'
        barrel_endcap  = 'Barrel_' if options.barrel else 'Endcap_'

    full_system = hasattr(options,'endcap') or hasattr(options,'barrel')

    if not hasattr(options,'endcap') :
        options.endcap = False

    if not hasattr(options,'barrel') :
        options.barrel = False
    
    # Write plots
    c = ROOT.TCanvas('ExtendedModelSummaryPlotsCanvas','blah',600,500)

    xtitle = 'Time [years]'
    x = GlobalSettings.time_step_list[1:]

    styles = {'D0':1,'D1':10,'D2':11,'D3':12,'D4':13,'D5':14,
              'M0':1,'M13':14}

    # One-per-module items that nonetheless need to know about the other modules.
    for disk_layer in range(Layout.nlayers_or_disks) :
        for ring_mod in range(Layout.nmodules_or_rings) :
            deltavhvservices = []
            for i in range(GlobalSettings.nstep) :
                index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)

                # Get the multiplexed deltavhv
                deltav_RHV = 0
                if ('R5' in names[index]) or ('M13' in names[index]) :
                    deltav_RHV = result_dicts[index]['isensor'].GetY()[i] * CableLosses.RHV

                isensors_type12 = CableLosses.iSensors_HV_Type1Type2PP2_Petal(names,ring_mod,disk_layer,result_dicts,i)
                isensors_type34 = CableLosses.iSensors_HV_Type3Type4_Petal(names,ring_mod,disk_layer,result_dicts,i)
                deltavhv_type12pp2 = CableLosses.DeltaVHV_halfsubstructure_Type1Type2PP2(isensors_type12)
                deltavhv_type34    = CableLosses.DeltaVHV_halfsubstructure_Type3Type4   (isensors_type34)
                # milliVolts -> Volts
                deltavhvservices.append((deltav_RHV + deltavhv_type12pp2 + deltavhv_type34)/1000.)

            result_dicts[index]['deltavhvservices'] = MakeGraph('HVDeltaVServices','HV cable HV #Delta^{}V (one petal side)',xtitle,'V',x,deltavhvservices)


    list_of_plots = list(result_dicts[0].keys())

    for plotname in list_of_plots :

        if not issubclass(type(result_dicts[0][plotname]),ROOT.TGraph) :
            continue

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
        if options.barrel :
            leg = ROOT.TLegend(0.57,0.69,0.95,0.93)

        PlotUtils.SetStyleLegend(leg)
        for i,g in enumerate(graphs) :
            if i :
                g.SetName('%s_%d'%(g.GetName(),i))
            g.SetLineColor(colors.get(names[i][:2],PlotUtils.ColorPalette()[i]))
            if options.endcap :
                g.SetLineStyle(styles.get(names[i][2:],1))
            if options.barrel :
                g.SetLineStyle(styles.get(names[i][2:],19))
            g.SetLineWidth(2)
            g.Draw('l' if i else 'al')
            leg.AddEntry(g,names[i],'l')

        # special legend for endcap
        if speciallegend :
            if options.endcap :
                # save dummy graphs so they do not go out of scope
                dummy_graphs = SetEndcapLegendSpecial(leg,graphs,multiplexedhv = (plotname == 'deltavhvservices'))
            elif options.barrel :
                dummy_graphs = SetBarrelLegendSpecial(leg,graphs)

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
    if not full_system :
        return

    if True :
        result_dicts_petals = [] # endcap

        for disk_layer in range(Layout.nlayers_or_disks) :
            result_dicts_petals.append(dict())
            ppetal,qsensorpetal,phvpetal,itapepetal,isensorpetal = [],[],[],[],[]
            petalvoutlvpp2,vdrop_roundtrip,pserviceslvfullpetal,plosscables = [],[],[],[]

            for i in range(GlobalSettings.nstep) :
                ppetal.append(0); qsensorpetal.append(0); phvpetal.append(0); itapepetal.append(0); isensorpetal.append(0)
                for ring_mod in range(Layout.nmodules_or_rings) :
                    index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
                    ppetal[i] += result_dicts[index]['pmodule'].GetY()[i]
                    ppetal[i] += result_dicts[index]['peos'   ].GetY()[i] # peos should be 0 for R0-R4
                    qsensorpetal[i] += result_dicts[index]['qsensor'].GetY()[i]
                    phvpetal[i] += result_dicts[index]['phv_wleakage'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape_eos'].GetY()[i]
                    isensorpetal[i] += result_dicts[index]['isensor'].GetY()[i]

                petalvoutlvpp2.append(CableLosses.Vout_LV_pp2(itapepetal[i]))
                vdrop_roundtrip.append(CableLosses.Vdrop_RoundTrip_type1and2(itapepetal[i]))
                pserviceslvfullpetal.append(CableLosses.PLVservicesFullSubstructure(itapepetal[i]))
                plosscables.append(CableLosses.PlossCables(itapepetal[i]))

            str_pet_stv = 'petal' if Layout.isEndcap else 'stave'
            aa,bb,cc = ['Petal','Disk',disk_layer] if Layout.isEndcap else ['Stave','Layer',disk_layer]
            result_dicts_petals[disk_layer]['pmodulepetal']      = MakeGraph('%sPower%s%d'  %(aa,bb,cc),'Total power in %s (with EOS) (one side)'%(str_pet_stv),xtitle,'P_{%s} [W]'%(str_pet_stv),x,ppetal)
            result_dicts_petals[disk_layer]['qsensorpetal']      = MakeGraph('%sSensorQ%s%d'%(aa,bb,cc),'Total sensor Q in %s (one side)'        %(str_pet_stv),xtitle,'P [W]'              ,x,qsensorpetal)
            result_dicts_petals[disk_layer]['phv_wleakagepetal'] = MakeGraph('%sHVPower%s%d'%(aa,bb,cc),'HV power in %s (one side)'              %(str_pet_stv),xtitle,'P [W]'              ,x,phvpetal)
            result_dicts_petals[disk_layer]['itapepetal']        = MakeGraph('%sTapeCurrentLV%s%d'%(aa,bb,cc),'LV tape current in %s (with EOS) (one side)'%(str_pet_stv),xtitle,'I [A]'    ,x,itapepetal)
            result_dicts_petals[disk_layer]['isensorpetal']      = MakeGraph('%sSensorCurrent%s%d'%(aa,bb,cc),'Total sensor (leakage) current in %s (one side)'%(str_pet_stv),xtitle,'I [mA]',x,isensorpetal)

            result_dicts_petals[disk_layer]['petalvoutlvpp2']    = MakeGraph('%sVoutLVPP2%s%d'%(aa,bb,cc),'Vout at PP2, %s (servicing one petal side)'%(str_pet_stv),xtitle,'V',x,petalvoutlvpp2)
            result_dicts_petals[disk_layer]['vdrop_roundtrip']   = MakeGraph('%sVdropLVRoundTripType1and2%s%d'%(aa,bb,cc),'Round-trip Vdrop of Type 1 and 2, %s (servicing one petal side)'%(str_pet_stv),xtitle,'V',x,vdrop_roundtrip)
            result_dicts_petals[disk_layer]['pserviceslvfullpetal'] = MakeGraph('%sLVServicesPowerLossFullPetal%s%d'%(aa,bb,cc),'LV Services power for a full petal (both sides), %s (includes both sides)'%(str_pet_stv),xtitle,'P [W]',x,pserviceslvfullpetal)
            result_dicts_petals[disk_layer]['plosscables']       = MakeGraph('%sLVPowerLossAllCables%s%d'%(aa,bb,cc),'LV cable power loss (one petal side), %s'%(str_pet_stv),xtitle,'P [W]',x,plosscables)

            thermal_runaway_yearpetal = 999
            for ring_mod in range(Layout.nmodules_or_rings) :
                index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
                if result_dicts[index]['thermal_runaway_year'] :
                    thermal_runaway_yearpetal = min(thermal_runaway_yearpetal,result_dicts[index]['thermal_runaway_year'])
            if thermal_runaway_yearpetal == 999 :
                thermal_runaway_yearpetal = 0

            # Append to result_dicts for further use in ProcessSummaryTables
            index = PlotUtils.GetResultDictIndex(names,0,disk_layer)
            for i in ['pmodulepetal','qsensorpetal','phv_wleakagepetal','itapepetal','isensorpetal','petalvoutlvpp2','vdrop_roundtrip','pserviceslvfullpetal','plosscables'] :
                result_dicts[index][i] = result_dicts_petals[disk_layer][i]
            result_dicts[index]['thermal_runaway_yearpetal'] = thermal_runaway_yearpetal

        for plotname in result_dicts_petals[0].keys() :
            c.Clear()

            leg = ROOT.TLegend(0.74,0.69,0.91,0.93)
            PlotUtils.SetStyleLegend(leg)
            if options.endcap :
                dummy_graphs = SetEndcapLegendSpecial(leg,graphs,doRings=False)
            else :
                dummy_graphs = SetBarrelLegendSpecial(leg,graphs,doModules=False)

            for disk_layer in range(Layout.nlayers_or_disks) :
                if options.endcap :
                    result_dicts_petals[disk_layer][plotname].SetLineStyle(styles.get('D%d'%disk_layer,1))
                else :
                    result_dicts_petals[disk_layer][plotname].SetLineColor(colors.get('L%d'%disk_layer,1))
                result_dicts_petals[disk_layer][plotname].Draw('l' if disk_layer else 'al')
            text.Clear()
            PlotUtils.AddRunParameterLabels(text,additionalinfo=[result_dicts_petals[0][plotname].GetTitle()])
            text.Draw()
            leg.Draw()
            minzero = PlotUtils.MakePlotMinimumZero(plotname)
            forcemin = PlotUtils.GetPlotForcedMinimum(plotname)
            taxisfunc.AutoFixYaxis(c,minzero=minzero,forcemin=forcemin)
            c.Print('%s/%s%s.eps'%(outputpath,barrel_endcap,result_dicts_petals[0][plotname].GetName().replace('Disk0','').replace('Layer0','')))

        # Endcap totals, if necessary.
        for ring_mod in range(Layout.nmodules_or_rings) :
            thermal_runaway_yearmodule = 999
            for disk_layer in range(Layout.nlayers_or_disks) :
                index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
                if result_dicts[index]['thermal_runaway_year'] :
                    thermal_runaway_yearmodule = min(thermal_runaway_yearmodule,result_dicts[index]['thermal_runaway_year'])
            if thermal_runaway_yearmodule == 999 :
                thermal_runaway_yearmodule = 0

            index = PlotUtils.GetResultDictIndex(names,ring_mod,0)
            result_dicts[index]['thermal_runaway_yearmodule'] = thermal_runaway_yearmodule

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

        # endcap          2              npetals/ring     nEndcaps (2)
        # barrel          2              nstaves/side     nSides (2)
        powertotal[i] *= (nModuleSides * Layout.nstaves_petals * nDetectors * (1+CableLosses.losstype1) * (1+CableLosses.lossouter))
        phvtotal[i]   *= (nModuleSides * Layout.nstaves_petals * nDetectors)

    gr = dict()
    gr['pmoduletotal']      = MakeGraph('TotalPower'  ,'Total power in both %ss (including cable losses)'%(structure_name),xtitle,'P_{%s} [W]'%('Total'),x,powertotal)
    gr['phv_wleakagetotal'] = MakeGraph('TotalHVPower','Total HV power (sensor + resistors) in both %ss'%(structure_name),xtitle,'P_{%s} [W]'%('HV')   ,x,phvtotal  )

    thermal_runaway_yeartotal = 999
    for disk_layer in range(Layout.nlayers_or_disks) :
        for ring_mod in range(Layout.nmodules_or_rings) :
            index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
            if result_dicts[index]['thermal_runaway_year'] :
                thermal_runaway_yeartotal = min(thermal_runaway_yeartotal,result_dicts[index]['thermal_runaway_year'])
    if thermal_runaway_yeartotal == 999 :
        thermal_runaway_yeartotal = 0

    result_dicts[0]['pmoduletotal']      = gr['pmoduletotal']
    result_dicts[0]['phv_wleakagetotal'] = gr['phv_wleakagetotal']
    result_dicts[0]['thermal_runaway_yeartotal'] = thermal_runaway_yeartotal

    for g in gr.keys() :
        c.Clear()
        gr[g].Draw('al')
        text.Clear()
        PlotUtils.AddRunParameterLabels(text,additionalinfo=[gr[g].GetTitle()])
        text.Draw()
        taxisfunc.AutoFixYaxis(c,minzero=True,forcemin=False)
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

    units = ''
    if '[' in result_dicts[0][quantity_name].GetYaxis().GetTitle() :
        units = result_dicts[0][quantity_name].GetYaxis().GetTitle().split('[')[1].split(']')[0]
        units = units.replace('#circ^{}','$^\circ$')
        units = units.replace('_{}Q_{S,crit}/Q_{S}','$Q_{S,crit}/Q_{S}$')
        units = '[%s]'%(units)
    caption = '%s at {\\bf %s} %s.'%(result_dicts[0][quantity_name].GetTitle(),time_label,units)
    column_label = '\multirow{2}{*}{%s} & & \multicolumn{%d}{c|}{%s} \\\\\n'%(units,
                                                                              Layout.nlayers_or_disks,
                                                                              'Disk' if Layout.isEndcap else 'Layer')
    row_label = '\multirow{%d}{*}{%s}'%(Layout.nmodules_or_rings,'Ring' if Layout.isEndcap else 'Module')
    the_lists = []

    # used to be for endcap only :
    if True :
        the_lists.append(['',''] + list('%d'%(i) for i in range(Layout.nlayers_or_disks)))
        endcap_total = None

        # EOS (if applicable)
        if quantity_name in ['pmodule','itape'] :
            caption = caption.replace('(no EOS)','')
            the_lists.append([])
            the_lists[-1].append('')
            the_lists[-1].append('EOS')
            for disk_layer in range(Layout.nlayers_or_disks) :
                quantity_name_eos = {'pmodule':'peos',
                                     'itape':'itape_eos',
                                     }.get(quantity_name)
                index = PlotUtils.GetResultDictIndex(structure_names,Layout.nmodules_or_rings-1,disk_layer)
                the_graph = result_dicts[index][quantity_name_eos]
                idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
                time_index = {'start':0,
                              'tid'  :idig.index(max(idig)),
                              'eol'  :the_graph.GetN()-1,
                              }.get(target_index)
                the_lists[-1].append(the_graph.GetY()[time_index])

        # Individual modules on rings / disks
        for ring_mod in range(Layout.nmodules_or_rings-1,-1,-1) :
            the_lists.append([])
            the_lists[-1].append(row_label if ring_mod == Layout.nmodules_or_rings-1 else '')
            the_lists[-1].append('%d'%(ring_mod))
            for disk_layer in range(Layout.nlayers_or_disks) :
                index = PlotUtils.GetResultDictIndex(structure_names,ring_mod,disk_layer)
                if result_dicts[index]['thermal_runaway_year'] :
                    the_lists[-1].append('{\\bf Y%d}'%(result_dicts[index]['thermal_runaway_year']))
                    continue
                the_graph = result_dicts[index][quantity_name]
                idig = list(result_dicts[index]['idig'].GetY()[i] for i in range(result_dicts[index]['idig'].GetN()))
                time_index = {'start':0,
                              'tid'  :idig.index(max(idig)),
                              'eol'  :the_graph.GetN()-1,
                              }.get(target_index)
                the_lists[-1].append(the_graph.GetY()[time_index])

        # Petal / stave totals
        str_petal_stave = 'petal' if Layout.isEndcap else 'stave'
        if quantity_name in ['qsensor','pmodule','phv_wleakage','itape','isensor'] :
            caption += ' The ``%s total\'\' corresponds to one %s side.'%(str_petal_stave,str_petal_stave)
            the_lists.append([])
            the_lists[-1] += ['%s total'%(str_petal_stave),'']
            for disk_layer in range(Layout.nlayers_or_disks) :
                index = PlotUtils.GetResultDictIndex(structure_names,0,disk_layer)
                if result_dicts[index]['thermal_runaway_yearpetal'] :
                    the_lists[-1].append('{\\bf Y%d}'%(result_dicts[index]['thermal_runaway_yearpetal']))
                    continue
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
                        print 'Warning! Maximum does not correspond to maximum power! %.3g vs %.3g %0.1f%%'%(result_max,result_tid,100*(result_max-result_tid)/float(result_max))
                        the_lists[-1].append(result_max)
                    else :
                        the_lists[-1].append(result_tid)

        # Endcap / barrel system totals
        str_ec_barrel = 'endcap' if Layout.isEndcap else 'barrel side'
        if quantity_name in ['pmodule','phv_wleakage'] :
            caption += ' The ``%ss total\'\' corresponds to both %s sides, all %ss, 2 %ss.'%(str_ec_barrel,str_petal_stave,str_petal_stave,str_ec_barrel)
            the_lists.append([])
            the_lists[-1] += ['%ss total'%(str_ec_barrel),'']
            the_lists[-1] += ['-']*Layout.nlayers_or_disks # this is a placeholder
            if result_dicts[0]['thermal_runaway_yeartotal'] :
                endcap_total = '{\\\\bf Y%d}'%(result_dicts[0]['thermal_runaway_yeartotal'])

            else :
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
        result_dicts[0][quantity_name+'caption'] = caption
        # insert special headers
        import re
        i_start_of_data = re.search("data_below\n",table).end()
        table = table[:i_start_of_data] + column_label + table[i_start_of_data:]
        # convert to multiline
        table = re.sub('\n%s total\s+&'%(str_petal_stave),'\hline\n\multicolumn{2}{|l|}{%s total}'%(str_petal_stave),table)
        if endcap_total != None :
            if type(endcap_total) == type(1.1) :
                endcap_total = '%.3g'%(endcap_total)
            table = re.sub('\n%ss total\s+&'%(str_ec_barrel),'\hline\n\multicolumn{2}{|l|}{%ss total}'%(str_ec_barrel),table)
            table = re.sub(('\s+-\s+&'*Layout.nlayers_or_disks).rstrip('&'),'\multicolumn{%d}{l|}{%s}'%(Layout.nlayers_or_disks,endcap_total),table)

    outtext += table
    outtext += '\n'

    return outtext
