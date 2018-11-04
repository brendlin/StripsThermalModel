
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
import PoweringEfficiency
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
                    leg.AddEntry(dummy_graphs[-1],'Ring %d/%d'%(i,i+1),'l')
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
    # We put this here in order to print out the plot.
    for disk_layer in range(Layout.nlayers_or_disks) :
        if not full_system :
            continue
        for ring_mod in range(Layout.nmodules_or_rings) :
            deltavhvservices = []
            for i in range(GlobalSettings.nstep) :
                index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)

                # Get the multiplexed deltavhv
                # tape, type I+II cables, PP2
                deltavhv_type12pp2 = CableLosses.DeltaVHV_halfsubstructure_Type1Type2PP2(names,ring_mod,disk_layer,result_dicts,i)
                # type III+IV cables
                deltavhv_type34    = CableLosses.DeltaVHV_halfsubstructure_Type3Type4   (names,ring_mod,disk_layer,result_dicts,i)

                # Add vhvr too
                deltavhvservices.append(deltavhv_type12pp2 + deltavhv_type34 + result_dicts[index]['vhvr'].GetY()[i])

            result_dicts[index]['deltavhvservices'] = MakeGraph('HVDeltaVServices','HV #Delta^{}V of HV filter, tape, cables, PP2 (one petal side)',xtitle,'V',x,deltavhvservices)


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

        taxisfunc.FixXaxisRanges(c)
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
            petalhvservices = []
            petalvoutlvpp2,vdrop_roundtrip,pserviceslvfullpetal = [],[],[]
            plosslvcablest1,plosslvcablest2,plosslvcablest34,plosslvpp2 = [],[],[],[]
            plosshvcablest1,plosshvcablest2,plosshvcablest34,plosshvpp2,ptapehv = [],[],[],[],[]
            petaltapedeltav,petaltapepower = [],[]

            for i in range(GlobalSettings.nstep) :
                ppetal.append(0); qsensorpetal.append(0); phvpetal.append(0); itapepetal.append(0); isensorpetal.append(0)
                petaltapepower.append(0);
                for ring_mod in range(Layout.nmodules_or_rings) :
                    index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
                    ppetal[i] += result_dicts[index]['pmodule'].GetY()[i]
                    ppetal[i] += result_dicts[index]['peos'   ].GetY()[i] # peos should be 0 for R0-R4
                    qsensorpetal[i] += result_dicts[index]['qsensor'].GetY()[i]
                    phvpetal[i] += result_dicts[index]['phv_wleakage'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape'].GetY()[i]
                    itapepetal[i] += result_dicts[index]['itape_eos'].GetY()[i]
                    isensorpetal[i] += result_dicts[index]['isensor'].GetY()[i]

                    # Module LV power (including module, tape)
                    # This one is quite important actually!
                    petaltapepower[i] += result_dicts[index]['pmodule_noHV'].GetY()[i]

                # Five power components (0,1), (2,3), (4), (5), EOS
                petalhvservices.append(CableLosses.PHVservicesFullPetal(names,disk_layer,result_dicts,i))

                # Get the tape voltage drop, power in R5
                LastModule = (5 if options.endcap else 13)
                index_R5 = PlotUtils.GetResultDictIndex(names,LastModule,disk_layer)
                tape_voltage_drop_r5 = result_dicts[index_R5]['vdrop_tape'].GetY()[i]
                petaltapedeltav.append(tape_voltage_drop_r5 - PoweringEfficiency.VfeastMin)

                # Other services - LV
                petalvoutlvpp2.append(CableLosses.Vout_LV_pp2(itapepetal[i],tape_voltage_drop_r5))
                vdrop_roundtrip.append(CableLosses.VdropLV_RoundTrip_type1and2(itapepetal[i]))
                pserviceslvfullpetal.append(CableLosses.PLVservicesFullSubstructure(itapepetal[i],tape_voltage_drop_r5))
                plosslvcablest1.append(CableLosses.PlossLVCablesType1(itapepetal[i]))
                plosslvcablest2.append(CableLosses.PlossLVCablesType2(itapepetal[i]))
                plosslvcablest34.append(CableLosses.PlossLVCablesType3and4(itapepetal[i],tape_voltage_drop_r5))
                plosslvpp2.append(CableLosses.Ppp2_LV(itapepetal[i],tape_voltage_drop_r5))

                # Other services - HV
                plosshvcablest1.append(CableLosses.PlossHVCablesType1(names,disk_layer,result_dicts,i))
                plosshvcablest2.append(CableLosses.PlossHVCablesType2(names,disk_layer,result_dicts,i))
                plosshvcablest34.append(CableLosses.PlossHVCablesType3and4(names,disk_layer,result_dicts,i))
                plosshvpp2.append(CableLosses.Ppp2_HV(names,disk_layer,result_dicts,i))
                ptapehv.append(CableLosses.PtapeHV(names,disk_layer,result_dicts,i))


            str_pet_stv = 'petal' if Layout.isEndcap else 'stave'
            aa,bb,cc = ['Petal','Disk',disk_layer] if Layout.isEndcap else ['Stave','Layer',disk_layer]
            result_dicts_petals[disk_layer]['pmodulepetal']      = MakeGraph('%sPower%s%d'  %(aa,bb,cc),'Total power in %s (with EOS) (one side)'%(str_pet_stv),xtitle,'P_{%s} [W]'%(str_pet_stv),x,ppetal)
            result_dicts_petals[disk_layer]['qsensorpetal']      = MakeGraph('%sSensorQ%s%d'%(aa,bb,cc),'Total sensor Q in %s (one side)'        %(str_pet_stv),xtitle,'P [W]'              ,x,qsensorpetal)
            result_dicts_petals[disk_layer]['phv_wleakagepetal'] = MakeGraph('%sHVPower%s%d'%(aa,bb,cc),'HV power in %s (one side)'              %(str_pet_stv),xtitle,'P [W]'              ,x,phvpetal)
            result_dicts_petals[disk_layer]['itapepetal']        = MakeGraph('%sTapeCurrentLV%s%d'%(aa,bb,cc),'LV tape current in %s (with EOS) (one side)'%(str_pet_stv),xtitle,'I [A]'    ,x,itapepetal)
            result_dicts_petals[disk_layer]['isensorpetal']      = MakeGraph('%sSensorCurrent%s%d'%(aa,bb,cc),'Total sensor (leakage) current in %s (one side)'%(str_pet_stv),xtitle,'I [mA]',x,isensorpetal)

            result_dicts_petals[disk_layer]['petalhvservices']   = MakeGraph('%sHVServicesPowerLossFullPetal%s%d'%(aa,bb,cc),'HV Services power loss, %s (both sides)'%(str_pet_stv),xtitle,'P [W]',x,petalhvservices)
            result_dicts_petals[disk_layer]['petalvoutlvpp2']    = MakeGraph('%sVoutLVPP2%s%d'%(aa,bb,cc),'Vout at PP2 (servicing one %s side)'%(str_pet_stv),xtitle,'V',x,petalvoutlvpp2)
            result_dicts_petals[disk_layer]['vdrop_roundtrip']   = MakeGraph('%sVdropLVRoundTripType1and2%s%d'%(aa,bb,cc),'Round-trip Vdrop of Type 1 and 2 cables (servicing one %s side)'%(str_pet_stv),xtitle,'V',x,vdrop_roundtrip)
            result_dicts_petals[disk_layer]['pserviceslvfullpetal'] = MakeGraph('%sLVServicesPowerLossFullPetal%s%d'%(aa,bb,cc),'LV Services (cables + PP2) power loss for a full %s (both sides)'%(str_pet_stv),xtitle,'P [W]',x,pserviceslvfullpetal)
            result_dicts_petals[disk_layer]['plosslvcablest1']   = MakeGraph('%sLVPowerLossCablesType1%s%d'%(aa,bb,cc),'LV cables power loss, type I (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosslvcablest1)
            result_dicts_petals[disk_layer]['plosslvcablest2']   = MakeGraph('%sLVPowerLossCablesType2%s%d'%(aa,bb,cc),'LV cables power loss, type II (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosslvcablest2)
            result_dicts_petals[disk_layer]['plosslvcablest34']  = MakeGraph('%sLVPowerLossCablesType34%s%d'%(aa,bb,cc),'LV cables power loss, type III/IV (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosslvcablest34)
            result_dicts_petals[disk_layer]['plosslvpp2']        = MakeGraph('%sLVPowerLossPP2%s%d'%(aa,bb,cc),'LV PP2 power loss, (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosslvpp2)
            result_dicts_petals[disk_layer]['petaltapedeltav']  = MakeGraph('%sLVTapeVoltageDrop%s%d'%(aa,bb,cc),'LV tape voltage drop (one %s side)'%(str_pet_stv),xtitle,'#Delta^{}V [V]',x,petaltapedeltav)
            result_dicts_petals[disk_layer]['petaltapepower']    = MakeGraph('%sLVTapePower%s%d'%(aa,bb,cc),'LV tape power (one side), %s'%(str_pet_stv),xtitle,'P [W]',x,petaltapepower)

            result_dicts_petals[disk_layer]['plosshvcablest1']  = MakeGraph('%sHVPowerLossCablesType1%s%d'%(aa,bb,cc),'HV cables power loss, type I (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosshvcablest1)
            result_dicts_petals[disk_layer]['plosshvcablest2']  = MakeGraph('%sHVPowerLossCablesType2%s%d'%(aa,bb,cc),'HV cables power loss, type II (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosshvcablest2)
            result_dicts_petals[disk_layer]['plosshvcablest34']  = MakeGraph('%sHVPowerLossCablesType12%s%d'%(aa,bb,cc),'HV cables power loss, type III/IV (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosshvcablest34)
            result_dicts_petals[disk_layer]['plosshvpp2']        = MakeGraph('%sHVPowerLossPP2%s%d'%(aa,bb,cc),'HV PP2 power loss, (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,plosshvpp2)
            result_dicts_petals[disk_layer]['ptapehv']           = MakeGraph('%sHVPowerLossTape%s%d'%(aa,bb,cc),'HV tape power loss, (one %s side)'%(str_pet_stv),xtitle,'P [W]',x,ptapehv)

            thermal_runaway_yearpetal = 999
            for ring_mod in range(Layout.nmodules_or_rings) :
                index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
                if result_dicts[index]['thermal_runaway_year'] :
                    thermal_runaway_yearpetal = min(thermal_runaway_yearpetal,result_dicts[index]['thermal_runaway_year'])
            if thermal_runaway_yearpetal == 999 :
                thermal_runaway_yearpetal = 0

            # Append to result_dicts for further use in ProcessSummaryTables
            index = PlotUtils.GetResultDictIndex(names,0,disk_layer)
            for i in ['pmodulepetal','qsensorpetal','phv_wleakagepetal','itapepetal','isensorpetal',
                      'petalhvservices','petalvoutlvpp2','vdrop_roundtrip','pserviceslvfullpetal',
                      'plosslvcablest1','plosslvcablest2',
                      'plosslvcablest34','plosslvpp2','petaltapedeltav','petaltapepower',
                      'plosshvcablest1','plosshvcablest2','plosshvcablest34','plosshvpp2','ptapehv'] :
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
    pnoservicestotal = [] # Power in both endcaps (LV+HV), excluding services (e.g. excluding cables, patch-panels)
    pcoolingsystotal = [] # Power in both endcaps, adding type-1 cables and PP1 losses
    pwallpowertotal  = [] # Including everything else
    phvtotal   = [] # Total HV Power (sensor+resistors) in full endcap or barrel (both sides)
    pservice   = [] # Service power only (opposite of noservices)
    nModuleSides = 2.
    nDetectors = 2. # 2 barrel sides; 2 endcaps
    for i in range(GlobalSettings.nstep) :
        pnoservicestotal.append(0)
        pcoolingsystotal.append(0)
        pwallpowertotal.append(0)
        phvtotal.append(0)
        pservice.append(0)

        for disk_layer in range(Layout.nlayers_or_disks) :
            index = PlotUtils.GetResultDictIndex(names,0,disk_layer)

            # HV only
            phvtotal[i] += result_dicts[index]['phv_wleakagepetal'].GetY()[i]

            # Nominal module power (Module LV + HV + HV resistors + leakage + EOS + LV tape)
            list_noservices = ['pmodulepetal']
            list_cooling = ['plosslvcablest1','plosshvcablest1','ptapehv']
            list_pp2andlater = ['plosslvcablest2' ,'plosshvcablest2',
                                'plosslvcablest34','plosshvcablest34','plosslvpp2','plosshvpp2']

            for value in list_noservices :
                pnoservicestotal[i] += result_dicts[index][value].GetY()[i]

            for value in list_noservices + list_cooling :
                pcoolingsystotal[i] += result_dicts[index][value].GetY()[i]

            for value in list_noservices + list_cooling + list_pp2andlater :
                pwallpowertotal[i]  += result_dicts[index][value].GetY()[i]

            for value in list_cooling + list_pp2andlater :
                pservice[i] += result_dicts[index][value].GetY()[i]

        # endcap                2              npetals/ring            nEndcaps (2)
        # barrel                2              nstaves/side            nSides (2)
        pnoservicestotal[i] *= (nModuleSides * Layout.nstaves_petals * nDetectors)
        pcoolingsystotal[i] *= (nModuleSides * Layout.nstaves_petals * nDetectors)
        pwallpowertotal[i]  *= (nModuleSides * Layout.nstaves_petals * nDetectors)
        phvtotal[i]         *= (nModuleSides * Layout.nstaves_petals * nDetectors)
        pservice[i]         *= (nModuleSides * Layout.nstaves_petals * nDetectors)

    gr = dict()
    gr['pnoservicestotal']  = MakeGraph('TotalPowerNoServices'  ,'Total power in both %ss (no services)'%(structure_name),xtitle,'P_{%s} [W]'%('Total'),x,pnoservicestotal)
    gr['pcoolingsystotal']  = MakeGraph('TotalPowerCoolingSys'  ,'Total power in both %ss (cooling system power)'%(structure_name),xtitle,'P_{%s} [W]'%('Total'),x,pcoolingsystotal)
    gr['pwallpowertotal' ]  = MakeGraph('TotalWallPower'        ,'Total power in both %ss (wall power)'%(structure_name),xtitle,'P_{%s} [W]'%('Total'),x,pwallpowertotal)
    gr['phv_wleakagetotal'] = MakeGraph('TotalHVPower','Total HV power (sensor + resistors) in both %ss'%(structure_name),xtitle,'P_{%s} [W]'%('HV')   ,x,phvtotal  )
    gr['pservicetotal']     = MakeGraph('TotalServicePower','Total service power in both %ss'%(structure_name),xtitle,'P_{%s} [W]'%('Total')   ,x,pservice  )

    thermal_runaway_yeartotal = 999
    for disk_layer in range(Layout.nlayers_or_disks) :
        for ring_mod in range(Layout.nmodules_or_rings) :
            index = PlotUtils.GetResultDictIndex(names,ring_mod,disk_layer)
            if result_dicts[index]['thermal_runaway_year'] :
                thermal_runaway_yeartotal = min(thermal_runaway_yeartotal,result_dicts[index]['thermal_runaway_year'])
    if thermal_runaway_yeartotal == 999 :
        thermal_runaway_yeartotal = 0

    for i in ['pnoservicestotal','pcoolingsystotal','pwallpowertotal','phv_wleakagetotal','pservicetotal'] :
        result_dicts[0][i] = gr[i]

    # For summary tables in ProcessSummaryTables
    result_dicts[0]['pmoduletotal'] = result_dicts[0]['pnoservicestotal']

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
            caption += ' The ``%ss total\'\' corresponds to both %s sides, all %ss, 2 %ss (no services loss)'%(str_ec_barrel,str_petal_stave,str_petal_stave,str_ec_barrel)
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
