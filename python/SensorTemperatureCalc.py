#
# SensorTemperatureCalc
#
import GlobalSettings
import Config
import Temperatures
import NominalPower
import SensorLeakage
import OperationalProfiles
import SensorProperties
import Layout
import SafetyFactors
import PoweringEfficiency
import CoolantTemperature
import ThermalImpedances
import AbcTidBump
import PlotUtils
from PlotUtils import MakeGraph
import TAxisFunctions as taxisfunc

import ROOT
import math
from array import array
import os

n_runaway_errors = [0]

def GraphToHist(gr) :
    name = gr.GetName()+'_Hist'
    i = 1
    while ROOT.gDirectory.Get(name) :
        name = '%s_Hist_%d'%(gr.GetName(),i)
        i += 1
    h = ROOT.TH1F(name,gr.GetTitle(),gr.GetN(),0,GlobalSettings.nyears+GlobalSettings.step)
    for i in range(gr.GetN()) :
        h.SetBinContent(h.FindBin(gr.GetX()[i]),gr.GetY()[i])
    return h

def CalculateSensorTemperature(options) :

    # "Initialize lists"
    # Lists of quantities vs time
    tsensor    = [] # Sensor temperature
    tabc       = [] # ABC temperature
    thcc       = [] # HCC temperature
    tfeast     = [] # FEAST temperature
    teos       = [] # EOS temperature
    pabc       = [] # ABC power
    phcc       = [] # HCC power
    pamac      = list(NominalPower.Pamac for i in range(GlobalSettings.nstep))
    peos       = [] # EOS power
    pfeast     = [] # FEAST power
    pfeast_abchcc = [] # FEAST power, abc and hcc specific
    pfamac     = list(NominalPower.Pfamac for i in range(GlobalSettings.nstep))
    pmodule    = [] # Power per module (front-end + HV)
    pmtape     = [] # Power loss in tape per module
    pmhv       = [] # HV power per module (leakage + resistors)
    isensor    = [] # Sensor current (Leakage current per module)
    pmhvr      = [] # HV power per module due to serial resistors
    powertotal = [] # Total power in layer
    phvtotal   = [] # Total HV Power (sensor+resistors) in layer
    pmhvmux    = [] # HV Power parallel resistor
    itape      = [] # Tape current per module
    idig       = [] # Digital current per module
    ifeast     = [] # FEAST current
    efffeast   = [] # FEAST efficiency
    ptape      = [] # Power loss in complete tape layer
    pstave     = [] # Stave Power in layer
    qsensor    = [] # sensor Q
    qsensor_headroom = [] # Sensor Qleakage headroom factor
    tc_crit = [] # Critical coolant temperature
    tid_sf_abc = [] # scale factor vs time (ABC)
    tid_sf_hcc = [] # scale factor vs time (HCC)
    tid_bump_abc = [] # TID bump vs time (ABC)
    tid_bump_hcc = [] # TID bump vs time (HCC)
    tid_shape = [] # TID shape vs time (ABC)
    # if you add a list here, then be sure to add it to the "if thermal_runaway" list

    # "Initialize temperatures"

    nomT = GlobalSettings.nomsensorT

    # These are initial values. Saved slightly differently for simplicity.
    # defTeos
    teos.append(Temperatures.Teos( NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, CoolantTemperature.GetTimeStepTc()[0] ))
    # defTabc
    tabc.append(Temperatures.Tabc( NominalPower.Pabc(nomT, 1, 0),
                                   NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, CoolantTemperature.GetTimeStepTc()[0] ))
    # defThcc
    thcc.append(Temperatures.Thcc( NominalPower.Phcc(nomT, 1, 0), NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, CoolantTemperature.GetTimeStepTc()[0] ))
    # defTfeast
    tfeast.append(Temperatures.Tfeast( NominalPower.Pfeast(nomT, nomT, nomT, 1, 0),
                                       NominalPower.eosP(nomT),
                                       NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, CoolantTemperature.GetTimeStepTc()[0] ))

    thermal_runaway = False
    thermal_runaway_index = 0

    ts_sweep_list = []          # Ts sweep lists as a companion to the lists below
    ts_vs_qref = []             # Qref vs sensor temperature in microW/mm^2
    static_qref = []            # corresponds to "lhs"
    ts_vs_q = []                # Q(Ts) vs sensor temperature
    ts_vs_q_at_crit = []        # Propaganda plot
    ts_vs_q_thermalbalance = [] # Thermal balance Q vs sensor temperature
    q_minus_qthermalbalance = [] # Needed for Tcoolant headroom

    # Not sure whether nstep+1 is required...
    for i in range(GlobalSettings.nstep) :

        year = int((i+1)*GlobalSettings.step)
        month = ((i+1)*GlobalSettings.step % 1.)*12.

        # sensor temperature vs sensor leakage power stuff
        ts_sweep_list.append([])
        ts_vs_qref.append([])
        ts_vs_q.append([])
        ts_vs_q_at_crit.append([])
        ts_vs_q_thermalbalance.append([])
        q_minus_qthermalbalance.append([])

        # Solve for Tsensor (ts)
        tmp_ts_list = []
        qref_rootsolve_list = []

        y_gets_over_zero = False

        doserate_i = OperationalProfiles.doserate[i]
        tid_dose_i = OperationalProfiles.tid_dose[i]
        Tcoolant_i = CoolantTemperature.GetTimeStepTc()[i]

        lhs = SensorLeakage.qref[i]
        static_qref.append(lhs*1000./SensorProperties.area) # sensor leakage modeling

        for ts_i,ts in enumerate(range(GlobalSettings.ts_step*(-35),GlobalSettings.ts_step*60)) :
            ts = ts/float(GlobalSettings.ts_step)

            # sensor current at this temperature ts
            isensor_i = Temperatures.unref(SensorLeakage.qref[i],ts)/float(SensorProperties.vbias)

            # T0 temperature, which depends (via HV resistors) on ts at a given step.
            t0_noLeakage_ts_i = Temperatures.T0(NominalPower.eosP(teos[-1]),
                                                NominalPower.Pmod(tabc[-1],thcc[-1],tfeast[-1],
                                                                  doserate_i,tid_dose_i,
                                                                  isensor_i), # You need the current here to get the heat from the HV resistors
                                                Tcoolant_i
                                                )

            # Module temperature, excluding the sensor power
            RcQh = t0_noLeakage_ts_i - Tcoolant_i

            rhs = Temperatures.Qref(ts,t0_noLeakage_ts_i)

            # sensor temperature vs sensor leakage power stuff
            ts_sweep_list[-1].append(ts)
            ts_vs_qref[-1].append(rhs*1000./SensorProperties.area) # Qref vs sensor temperature in microW/mm^2
            ts_vs_q[-1].append(Temperatures.unref(SensorLeakage.qref[i],ts)) # Q(Ts) vs sensor temperature
            ts_vs_q_thermalbalance[-1].append(max(0,(ts-t0_noLeakage_ts_i)/float(ThermalImpedances.Rt))) # Thermal balance Q vs sensor temperature
            if (len(ts_vs_q_thermalbalance[-1]) > 2) and ts_vs_q_thermalbalance[-1][-1] < ts_vs_q_thermalbalance[-1][-2] :
                ts_vs_q_thermalbalance[-1].pop(-1)

            y = rhs - lhs

            if y > 0 :
                y_gets_over_zero = True

            # thermal runaway
            if len(qref_rootsolve_list) and y < qref_rootsolve_list[-1] and (not y_gets_over_zero) :
                if thermal_runaway == False :
                    thermal_runaway_index = i
                thermal_runaway = True
                if n_runaway_errors[0] <= 5 :
                    print 'WARNING! Probably hit thermal runaway! Year %d Month %2.0f'%(year,month)
                if n_runaway_errors[0] == 5 :
                    print '(Suppressing additional thermal runaway efficiency errors)'
                n_runaway_errors[0] += 1
                continue

            # bad starting point
            if (ts_i == 0) and y > 0 :
                print 'Error! In year %2.1f, y starts greater than 0 (%2.2f). Exiting.'%(i*GlobalSettings.step,y)
                import sys; sys.exit()

            # unimportant region
            if y < -5 :
                continue

            # only fill solving lists if y is increasing
            if (not len(qref_rootsolve_list)) or (y > qref_rootsolve_list[-1]) :
                tmp_ts_list.append(ts)
                qref_rootsolve_list.append(y)

        if thermal_runaway :
            for i_list in [tsensor,tabc,thcc,tfeast,teos,pabc,phcc,peos,pfeast,pfeast_abchcc,pmodule,pmtape,pmhv,isensor,pmhvr,
                           powertotal,phvtotal,pmhvmux,itape,idig,ifeast,efffeast,ptape,pstave,qsensor,
                           tid_sf_abc,tid_sf_hcc,tid_bump_abc,tid_bump_hcc,tid_shape] :
                i_list.append(i_list[-1])
            qsensor_headroom.append(0.1)
            tc_crit.append(Tcoolant_i)
            continue

        # interpolate using TGraph "Eval" function
        graph = ROOT.TGraph(len(tmp_ts_list),array('d',qref_rootsolve_list),array('d',tmp_ts_list))
        resultts = graph.Eval(0)
        resultqsensor = Temperatures.unref(SensorLeakage.qref[i],resultts)

        # (solving step is done.)

        qsensor.append(resultqsensor)

        # Leakage current per module
        isensor.append( resultqsensor /float(SensorProperties.vbias) )

        # Calculate temperatures in the system based on sensor temperature

        #  Sensor temperature
        tsensor.append(resultts)

        # Critical Temperature Coolant calculation
        tmp_graph = ROOT.TGraph(len(ts_vs_q_thermalbalance[-1]),array('d',ts_vs_q_thermalbalance[-1]),array('d',ts_sweep_list[-1][:len(ts_vs_q_thermalbalance[-1])]))
        tmp_headroom_list = [-1]
        for x in range(len(ts_vs_q[-1])) :
            if ts_vs_q[-1][x] > ts_vs_q_thermalbalance[-1][-1] :
                continue
            if ts_vs_q[-1][x] == 0 :
                continue
            tmp_headroom_list.append( ts_sweep_list[-1][x] - tmp_graph.Eval(ts_vs_q[-1][x]) )

        tc_crit.append( Tcoolant_i + max(tmp_headroom_list) )
        if len(tc_crit) == 2 :
            tc_crit[0] = tc_crit[1]

        # Sensor Qleakage headroom factor
        qref_crit = max(ts_vs_qref[-1]) # Critical qref -- maximum of qref list
        qsensor_headroom.append( 1 if (not static_qref[-1]) else qref_crit/float(static_qref[-1]))
        if len(qsensor_headroom) == 2 :
            qsensor_headroom[0] = qsensor_headroom[1]

        # propaganda: Ts vs Q at critical point (multiplied by headroom factor)
        for ts_i,ts in enumerate(range(GlobalSettings.ts_step*(-35),GlobalSettings.ts_step*60)) :
            ts = ts/float(GlobalSettings.ts_step)
            ts_vs_q_at_crit[-1].append(Temperatures.unref(SensorLeakage.qref[i]*qsensor_headroom[-1],ts))

        # Stuff that is useful for later on

        # module power: no leakage power, but power from hvmux and rhv is included here.
        pmodule_noLeakagePow_lastStep = NominalPower.Pmod(tabc[i-1],thcc[i-1],tfeast[i-1],
                                                          doserate_i,tid_dose_i,isensor[i])

        # Temperature of ABC
        tabc.append(Temperatures.Tabc(NominalPower.Pabc(tabc[i-1],doserate_i,tid_dose_i),
                                      NominalPower.eosP(teos[i-1]),
                                      pmodule_noLeakagePow_lastStep,resultqsensor,Tcoolant_i)
                    )
        if (i == 0) :
            tabc.pop(0) # remove the initial value

        # Temperature of HCC
        thcc.append(Temperatures.Thcc(NominalPower.Phcc(thcc[i-1],doserate_i,tid_dose_i),
                                      NominalPower.eosP(teos[i-1]),
                                      pmodule_noLeakagePow_lastStep,resultqsensor,Tcoolant_i)
                      )
        if (i == 0) :
            thcc.pop(0) # remove the initial value

        # Temperature of FEAST
        tfeast.append(Temperatures.Tfeast(NominalPower.Pfeast(tabc[i],thcc[i],tfeast[i-1],
                                                              doserate_i,tid_dose_i),
                                          NominalPower.eosP(teos[i-1]),
                                          pmodule_noLeakagePow_lastStep,resultqsensor,Tcoolant_i)
                      )
        if (i == 0) :
            tfeast.pop(0) # remove the initial value

        # Temperature of EOS
        teos.append(Temperatures.Teos(NominalPower.eosP(teos[i-1]),
                                      pmodule_noLeakagePow_lastStep,resultqsensor,Tcoolant_i)
                    )
        if (i == 0) :
            teos.pop(0) # remove the initial value

        #
        # From here we can use actual temperatures
        #

        pmodule_noLeakagePow_thisStep = NominalPower.Pmod(tabc[i],thcc[i],tfeast[i],
                                                          doserate_i,tid_dose_i,isensor[i])

        # ABC Power (all n ABCs)
        pabc.append(NominalPower.Pabc(tabc[i],doserate_i,tid_dose_i))
        tid_sf_abc.append(AbcTidBump.tid_scale_overall_fit_function.Eval(tabc[i],doserate_i))
        tid_bump_abc.append(AbcTidBump.tid_scale_combined_factor(tabc[i],doserate_i,tid_dose_i))
        tid_shape.append(1+AbcTidBump.tid_scale_shape(tid_dose_i)*0.45)

        # HCC power (all n HCCs)
        phcc.append(NominalPower.Phcc(thcc[i],doserate_i,tid_dose_i))
        tid_sf_hcc.append(AbcTidBump.tid_scale_overall_fit_function.Eval(thcc[i],doserate_i))
        tid_bump_hcc.append(AbcTidBump.tid_scale_combined_factor(thcc[i],doserate_i,tid_dose_i))

        # EOS Power
        peos.append(NominalPower.eosP(teos[i]))

        # FEAST power
        pfeast.append(NominalPower.Pfeast(tabc[i],thcc[i],tfeast[i],doserate_i,tid_dose_i))

        # FEAST power from ABC and HCC only
        pfeast_abchcc.append(NominalPower.Pfeast_ABC_HCC(tabc[i],thcc[i],tfeast[i],doserate_i,tid_dose_i))

        # Power per module (front-end + HV)
        pmodule.append(pmodule_noLeakagePow_thisStep + resultqsensor)

        # Power loss in tape per module
        pmtape.append(NominalPower.Ptape(tabc[i],thcc[i],tfeast[i],doserate_i,tid_dose_i))

        # HV power per module (leakage + resistors)
        pmhv.append(resultqsensor + NominalPower.Phv( isensor[i] ) )

        # HV power per module due to serial resistors
        pmhvr.append( NominalPower.Prhv( isensor[i] ) )

        # HV per module due to parallel resistor
        pmhvmux.append(NominalPower.Phvmux)

        # Stave power B1
        pstave.append(NominalPower.Pstave(tabc[i],thcc[i],tfeast[i],teos[i],doserate_i,tid_dose_i,isensor[i]))

        # Total power for layer
        # Extra factor of 2 is for 2 sides of the barrel, or 2 endcaps.
        powertotal.append( 2 * Layout.nstaves * (1 + SafetyFactors.safetylayout) * pstave[i] / 1000.)

        # Total HV power for layer
        # One factor of 2 is for 2 sides of the barrel, or 2 endcaps.
        # Antoher factor of 2 is for two sides of the module
        phvtotal.append( 2 * Layout.nstaves * (1 + SafetyFactors.safetylayout) * 2 * Layout.nmod * (pmhv[i] + pmhvr[i]) / 1000. )

        # Tape current per module
        itape.append(NominalPower.Itape(tabc[i],thcc[i],tfeast[i],doserate_i,tid_dose_i))

        # Tape power for one tape (half a stave)
        ptape.append(NominalPower.Pstavetape(tabc[i],thcc[i],tfeast[i],doserate_i,tid_dose_i))

        # Digital current per module
        idig.append(NominalPower.Idig(tabc[i],thcc[i],doserate_i,tid_dose_i))

        # FEAST current PER FEAST (in case there is more than one feast)
        ifeast.append(NominalPower.Ifeast(tabc[i],thcc[i],doserate_i,tid_dose_i) / float(NominalPower.nfeast))

        # FEAST efficiency
        efffeast.append(PoweringEfficiency.feasteff(tfeast[i],ifeast[i]))

        # if i and math.fabs(((i+1)*GlobalSettings.step) % 1.) < 0.000001 :
        #     print 'Calculated year %.0f'%( int((i+1)*GlobalSettings.step) )

        continue # end of loop

    x = GlobalSettings.time_step_list[1:]
    xtitle = 'Time [years]'
    tid_max_index = idig.index(max(idig))

    # dictionary of graphs
    gr = dict()

    structure_name = Config.GetStr('Layout.Detector')
    substructure_name = {'Barrel':'layer (both sides)',
                         'Endcap':'ring (both endcaps)'}.get(structure_name)
    layer_or_ring = {'Barrel':'layer',
                     'Endcap':'-----'}.get(structure_name)

    gr['tsensor']    = MakeGraph('SensorTemperature'      ,'sensor temperature'                        ,xtitle,'T_{%s} [#circ^{}C]'%('sensor'),x,tsensor   )
    gr['tabc']       = MakeGraph('AbcTemperature'         ,'ABC temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('ABC'   ),x,tabc      )
    gr['thcc']       = MakeGraph('HCCTemperature'         ,'HCC temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('HCC'   ),x,thcc      )
    gr['tfeast']     = MakeGraph('FEASTTemperature'       ,'FEAST temperature'                         ,xtitle,'T_{%s} [#circ^{}C]'%('FEAST' ),x,tfeast    )
    gr['teos']       = MakeGraph('EOSTemperature'         ,'EOS temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('EOS'   ),x,teos      )
    gr['peos']       = MakeGraph('EOSPower'               ,'EOS power'                                 ,xtitle,'P_{%s} [W]'%('EOS'   )        ,x,peos      )
    gr['pmodule']    = MakeGraph('ModulePower'            ,'Module Power'                              ,xtitle,'P_{%s} [W]'%('module')        ,x,pmodule   )
    gr['pmtape']     = MakeGraph('TapePower'              ,'Tape power loss'                           ,xtitle,'P_{%s} [W]'%('tape'  )        ,x,pmtape    )
    gr['pmhv']       = MakeGraph('HVPower'                ,'Total HV power'                            ,xtitle,'P_{%s} [W]'%('HV'    )        ,x,pmhv      )
    gr['isensor']    = MakeGraph('SensorCurrent'          ,'Sensor (leakage) current'                  ,xtitle,'I_{%s} [mA]'%('sensor')       ,x,list(isensor[a]*1000. for a in range(len(isensor))))
    gr['pmhvr']      = MakeGraph('HVPowerSerialResistors' ,'HV Power serial resistors'                 ,xtitle,'P_{%s} [W]'%('HV,Rseries')    ,x,pmhvr     )
    gr['powertotal'] = MakeGraph('SummaryTotalPower'      ,'Total Power in %s'%(substructure_name)     ,xtitle,'P_{%s} [kW]'%('Total')        ,x,powertotal)
    gr['phvtotal']   = MakeGraph('SummaryTotalHVPower'    ,'Total HV Power (sensor + resistors) in %s'%(substructure_name),xtitle,'P_{%s} [kW]'%('HV'),x,phvtotal)
    gr['pmhvmux']    = MakeGraph('HVPowerParallelResistor','HV Power parallel resistor'                ,xtitle,'P_{%s} [W]'%('HV,Rparallel')  ,x,pmhvmux   )
    gr['itape']      = MakeGraph('TapeCurrent'            ,'Tape current per module'                   ,xtitle,'I_{%s} [A]'%('tape')          ,x,itape     )
    gr['idig']       = MakeGraph('DigitalCurrent'         ,'ABC and HCC digital current'               ,xtitle,'I_{%s} [A]'%('digital')       ,x,idig      )
    gr['ifeast']     = MakeGraph('FeastCurrent'           ,'FEAST current'                             ,xtitle,'I_{%s} [A]'%('FEAST')         ,x,ifeast    )
    gr['efffeast']   = MakeGraph('FeastEfficiency'        ,'Feast efficiency'                          ,xtitle,'Efficiency [%]'               ,x,efffeast  )
    gr['ptape']      = MakeGraph('TotalPowerLossTape'     ,'Power loss in complete tape in %s'%(layer_or_ring),xtitle,'P_{%s} [W]'%('tape')   ,x,ptape     )
    gr['pstave']     = MakeGraph('TotalStavePower'        ,'Stave Power'                               ,xtitle,'P_{%s} [W]'%('stave')         ,x,pstave    )
    gr['qsensor_headroom'] = MakeGraph('SensorQHeadroom'  ,'Sensor Q Headroom factor'                  ,xtitle,'Power headroom factor, _{}Q_{S,crit}/Q_{S}',x,qsensor_headroom)
    gr['tcoolant']   = MakeGraph('CoolantTemperature'     ,'coolant temperature'                       ,xtitle,'T_{%s} [#circ^{}C]'%('coolant'),x,CoolantTemperature.GetTimeStepTc())
    gr['tid_sf_abc'] = MakeGraph('ABCTidBumpScaleFactor'  ,'ABC TID bump scale factor'                 ,xtitle,'scale factor'                 ,x,tid_sf_abc)
    gr['tid_sf_hcc'] = MakeGraph('HCCTidBumpScaleFactor'  ,'HCC TID bump scale factor'                 ,xtitle,'scale factor'                 ,x,tid_sf_hcc)
    gr['tid_bump_abc'] = MakeGraph('ABCTidBump'           ,'ABC TID bump'                              ,xtitle,'scale factor #times shape'    ,x,tid_bump_abc)
    gr['tid_bump_hcc'] = MakeGraph('HCCTidBump'           ,'HCC TID bump'                              ,xtitle,'scale factor #times shape'    ,x,tid_bump_hcc)

    dosave = (not hasattr(options,'save') or options.save)

    # Write out to file
    if dosave :
        outputpath = PlotUtils.GetOutputPath('SensorTemperatureCalc',options)
        outfilename = '%s/%s.root'%(outputpath,'SensorTemperatureCalc')
        out = ROOT.TFile(outfilename,'recreate')
        for g in gr.keys() :
            gr[g].Write()
        out.Close()
        print 'Wrote file %s'%(outfilename)

    # Write plots
    c = ROOT.gROOT.FindObject('SensorTemperatureCalcCanvas')
    if not c :
        c = ROOT.TCanvas('SensorTemperatureCalcCanvas','blah',600,500)
    c.Clear()

    text = ROOT.TLegend(0.13,0.77,0.41,0.94) # a more flexible way to draw text.
    PlotUtils.SetStyleLegend(text)
    PlotUtils.AddRunParameterLabels(text)
    for g in gr.keys() :
        c.Clear()
        gr[g].Draw('al')
        text.Draw()
        minzero = PlotUtils.MakePlotMinimumZero(g)
        forcemin = PlotUtils.GetPlotForcedMinimum(g)
        if g == 'qsensor_headroom' :
            c.SetLogy(True)
        taxisfunc.AutoFixYaxis(c,minzero=minzero,forcemin=forcemin)
        if dosave :
            c.Print('%s/%s.eps'%(outputpath,gr[g].GetName()))
        if g == 'qsensor_headroom' :
            c.SetLogy(False)

    # Extra graphs that you may not want to save individually
    extr = dict()
    extr['pamac']         = MakeGraph('AMACPower'              ,'AMAC power'                                ,xtitle,'P_{%s} [W]'%('AMAC'  )        ,x,pamac     )
    extr['pabc']          = MakeGraph('ABCPower'               ,'ABC power'                                 ,xtitle,'P_{%s} [W]'%('ABC'   )        ,x,pabc      )
    extr['phcc']          = MakeGraph('HCCPower'               ,'HCC power'                                 ,xtitle,'P_{%s} [W]'%('HCC'   )        ,x,phcc      )
    extr['pfeast']        = MakeGraph('FeastPower'             ,'FEAST power'                               ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfeast    )
    extr['pfeast_abchcc'] = MakeGraph('FeastPower_ABC_HCC'     ,'FEAST power (HCC,ABC)'                     ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfeast_abchcc)
    extr['pfamac']        = MakeGraph('FeastPower_AMAC'        ,'FEAST power (AMAC)'                        ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfamac    )
    extr['tid_shape']     = MakeGraph('TID_Shape'              ,'TID shape #times 1.45'                     ,xtitle,'shape'                        ,x,tid_shape )

    # Kurt, put any extra plots here

    #
    # Module power
    #
    c.Clear()
    # pmodule_noHV is (Power per module) minus (HV power + HV power due to serial resistors)
    pmodule_noHV  = list(pmodule[i] - (pmhv[i] + pmhvr[i]) for i in range(len(pmodule)))
    gr['pmodule_noHV'] = MakeGraph('ModulePower_noHV','Power without HV',xtitle,'P [W]',x,pmodule_noHV)
    pmodule_noHV_noTapeLoss = list(pmodule[i] - (pmhv[i] + pmhvr[i]) - pmtape[i] for i in range(len(pmodule)))
    gr_pmodule_noHV_noTapeLoss = MakeGraph('ModulePower_noHV_NoTapeLoss','Power w/o HV and w/o tape loss',xtitle,'P [W]',x,pmodule_noHV_noTapeLoss)
    colors = {'pmodule'                :ROOT.kGreen+1,
              'pmodule_noHV'           :ROOT.kBlue+1,
              'pmodule_noHV_noTapeLoss':ROOT.kRed+1
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmodule','pmodule_noHV']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    gr_pmodule_noHV_noTapeLoss.SetLineColor(colors.get('pmodule_noHV_noTapeLoss'))
    gr_pmodule_noHV_noTapeLoss.Draw('l')
    leg.AddEntry(gr_pmodule_noHV_noTapeLoss,gr_pmodule_noHV_noTapeLoss.GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c,minzero=True)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'SummaryPowerPerModule'))

    #
    # Temperatures
    #
    c.Clear()
    colors = {'tabc'    :ROOT.kBlue+1,
              'thcc'    :ROOT.kRed+1,
              'tfeast'  :ROOT.kOrange+1,
              'teos'    :ROOT.kCyan+1,
              'tsensor' :ROOT.kGreen+1,
              'tcoolant':ROOT.kMagenta+1,
              }
    leg = ROOT.TLegend(0.52,0.69,0.80,0.93)
    PlotUtils.SetStyleLegend(leg)
    tabc_clone = gr['tabc'].Clone()
    tabc_clone.GetYaxis().SetTitle('T [#circ^{}C]')
    tabc_clone.Draw('al')
    leg.AddEntry(tabc_clone,tabc_clone.GetTitle(),'l')
    for i,key in enumerate(['thcc','tfeast','teos','tsensor','tcoolant']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l')
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'SummaryTemperature'))

    #
    # Temperature headroom
    #
    c.Clear()
    leg = ROOT.TLegend(0.57,0.86,0.80,0.93)
    PlotUtils.SetStyleLegend(leg)
    gr_tc_crit = MakeGraph('TcCrit','Critical Tc',xtitle,'T_{coolant} [C]',x,tc_crit)
    tc_headroom = list(tc_crit[a] - CoolantTemperature.GetTimeStepTc()[a] for a in range(len(tc_crit)))
    gr['tc_headroom'] = MakeGraph('CoolantTemperatureHeadroom','Coolant Headroom',xtitle,'Headroom T_{C} [C]',x,tc_headroom)
    gr['tcoolant'].Draw('al')
    gr_tc_crit.Draw('l')
    leg.AddEntry(gr['tcoolant'],gr['tcoolant'].GetTitle(),'l')
    leg.AddEntry(gr_tc_crit,gr_tc_crit.GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c,ignorelegend=False)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'TemperatureHeadroom'))

    #
    # HV power summary
    #
    c.Clear()
    hv_power_resistors = list(pmhvr[i] + pmhvmux[i] for i in range(len(pmhv)))
    gr['hv_power_resistors'] = MakeGraph('HVPowerResistors','Contribution from all resistors',xtitle,'P [W]',x,hv_power_resistors)
    gr['pmhvmux'].SetTitle('Contribution from parallel resistor')
    colors = {'pmhv'              :ROOT.kBlue+1,
              'hv_power_resistors':ROOT.kGreen+1,
              'pmhvmux'           :ROOT.kRed+1,
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmhv','hv_power_resistors','pmhvmux']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c,minzero=True)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'SummaryHVPower'))

    #
    # Total power plot
    #
    c.Clear()
    hists = dict()
    stack = ROOT.THStack('stack','stack')
    # pmod = pabc + phcc + pamac + pfeast + ptape + phv
    leg = ROOT.TLegend(0.61,0.63,0.86,0.93)
    leg.SetName('legend')
    PlotUtils.SetStyleLegend(leg)
    hists = []
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pamac'])))
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pabc'])))
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(extr['phcc'])))
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pfeast_abchcc'])))
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pfamac'])))
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(gr['pmtape']))) # fix!!!
    phvresistors  = list(pmhvmux[i] + pmhvr[i] for i in range(len(pmhvmux)))
    gr_phvresistors = MakeGraph('ModulePower_HVResistors','Power of HV resistors',xtitle,'P [W]',x,phvresistors)
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(gr_phvresistors))) # HV resistors
    gr_qsensor = MakeGraph('Qsensor','Sensor Q',xtitle,'P [W]',x,qsensor)
    hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(gr_qsensor))) # qsensor
    if max(peos) > 0 :
        hists.insert(0,PlotUtils.AddToStack(stack,leg,GraphToHist(gr['peos'])))

    for h in hists :
        leg.AddEntry(h,h.GetTitle().replace('power ','').replace('power',''),'f')
    if max(peos) == 0 :
        leg.AddEntry(0,'','')

    stack.Draw('l')
    leg.Draw()
    text.Draw()
    stack.GetHistogram().GetXaxis().SetTitle(xtitle)
    stack.GetHistogram().GetYaxis().SetTitle('P [W]')
    taxisfunc.AutoFixYaxis(c,ignorelegend=False,minzero=True)
    #taxisfunc.SetYaxisRanges(c,0,20)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'PowerStackPlot'))

    #
    # Thermal balance curve
    #
    def PlotQGraph(can,legend,index,color,leg_label) :
        xlist = ts_sweep_list[index]
        ylist = ts_vs_q_thermalbalance[index]

        max_coolantT = max(CoolantTemperature.GetTimeStepTc())
        xlist = xlist[:xlist.index(max_coolantT + 45.)]
        ylist = ylist[:len(xlist)]

        xlist_2 = xlist[:len(ylist)]
        tmp_gr = MakeGraph('blah','blah','T_{S} [#circ^{}C]','Q [W]',xlist_2,ylist)

        # Now do the ts vs q plot
        ylist_1 = ts_vs_q[index]
        ylist_1 = ylist_1[:len(xlist)]

        index_stop = len(ylist_1)
        #too_high = list(ylist_1[i] > ylist[-1] for i in range(len(ylist_1)))
        too_high = list(ylist_1[i] > 40 for i in range(len(ylist_1)))
        if True in too_high :
            index_stop = too_high.index(True)
        tmp_gr_1 = MakeGraph('Q(thermal balance)','Q(thermal balance)','T_{S} [#circ^{}C]','Q [W]',xlist[:index_stop],ylist_1[:index_stop])

        tmp_gr  .SetLineColor(color)
        tmp_gr_1.SetLineColor(color)
        tmp_gr_1.SetLineStyle(7)

        can.cd()
        drawopt = 'l' if (True in list(issubclass(type(a),ROOT.TGraph) for a in can.GetListOfPrimitives())) else 'al'
        tmp_gr.Draw(drawopt)
        tmp_gr_1.Draw('l')

#         ylist_2 = ts_vs_q_at_crit[index]
#         index_stop = len(ylist_2)
#         too_high = list(ylist_2[i] > 40 for i in range(len(ylist_2)))
#         if True in too_high :
#             index_stop = too_high.index(True)
#         tmp_gr_2 = MakeGraph('q_crit','q crit','T_{S} [#circ^{}C]','Q [W]',xlist[:index_stop],ylist_2[:index_stop])
#         tmp_gr_2.SetLineColor(color)
#         tmp_gr_2.Draw('l')

        legend.AddEntry(tmp_gr,leg_label,'l')

        return tmp_gr,tmp_gr_1#,tmp_gr_2

    c.Clear()
    leg = ROOT.TLegend(0.61,0.80,0.93,0.93)
    PlotUtils.SetStyleLegend(leg)
    year1_index = int(1./float(GlobalSettings.step))

    collection = []
    collection.append(PlotQGraph(c,leg,year1_index,PlotUtils.ColorPalette()[0],'t = 1 year'  ))
    collection.append(PlotQGraph(c,leg,tid_max_index,PlotUtils.ColorPalette()[1],'t = tid bump'))
    if thermal_runaway_index :
        collection.append(PlotQGraph(c,leg,thermal_runaway_index,PlotUtils.ColorPalette()[3],'t = thermal runaway'))
    else :
        collection.append(PlotQGraph(c,leg,-1           ,PlotUtils.ColorPalette()[2],'t = 14 years' ))
    leg.Draw()

    taxisfunc.AutoFixYaxis(c)

    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'QVersusTs'))

    #
    # Sensor temperature vs sensor leakage power
    #
    def PlotQRefGraph(can,legend,index,color,leg_label) :
        xlist = ts_vs_qref[index]
        ylist = ts_sweep_list[index]

        max_coolantT = max(CoolantTemperature.GetTimeStepTc())
        ylist = ylist[:ylist.index(max_coolantT + 45.)]
        xlist = xlist[:len(ylist)]

        x_max_i = xlist.index(max(xlist))

        # Trim top
        tmp_y = ylist
        while xlist[-1] < 0 :
            xlist.pop(-1)
            tmp_y.pop(-1)

        tmp_gr   = MakeGraph('blah','blah','q^{}_{ref} at  #minus15#circ^{}C [#mu^{}W/mm^{2}]','T_{S} [#circ^{}C]',xlist[:x_max_i+1],tmp_y[:x_max_i+1])
        tmp_gr_1 = MakeGraph('blah','blah','q^{}_{ref} at  #minus15#circ^{}C [#mu^{}W/mm^{2}]','T_{S} [#circ^{}C]',xlist[x_max_i:],tmp_y[x_max_i:])

        tmp_gr  .SetLineColor(color)
        tmp_gr_1.SetLineColor(color)
        tmp_gr_1.SetLineStyle(7)

         # Set 0 point
        tmp_gr.SetPoint(0,0,tmp_gr.Eval(0))
        while tmp_gr.GetX()[1] < 0 :
            tmp_gr.RemovePoint(1)

        can.cd()
        drawopt = 'l' if (True in list(issubclass(type(a),ROOT.TGraph) for a in can.GetListOfPrimitives())) else 'al'
        tmp_gr.Draw(drawopt)
        tmp_gr_1.Draw('l')

        static_qref_ts = ylist[xlist.index(max(xlist))]
        if static_qref[index] < max(xlist) :
            static_qref_ts = tmp_gr.Eval(static_qref[index])
        tmp_gr_2 = MakeGraph('blah','blah','','',[static_qref[index]],[static_qref_ts])
        tmp_gr_2.SetMarkerColor(color)
        tmp_gr_2.Draw('p')

        legend.AddEntry(tmp_gr,leg_label,'l')
        tmp_gr.GetXaxis().SetTitle('q^{}_{ref} at  #minus15#circ^{}C [#mu^{}W/mm^{2}]')
        tmp_gr.GetYaxis().SetTitle('T_{S} [#circ^{}C]')
        return tmp_gr,tmp_gr_1,tmp_gr_2

    c.Clear()
    leg = ROOT.TLegend(0.61,0.80,0.93,0.93)
    PlotUtils.SetStyleLegend(leg)
    collection = []
    collection.append(PlotQRefGraph(c,leg,year1_index  ,PlotUtils.ColorPalette()[0],'t = 1 year'))
    collection.append(PlotQRefGraph(c,leg,tid_max_index,PlotUtils.ColorPalette()[1],'t = tid bump'))
    if thermal_runaway_index :
        collection.append(PlotQRefGraph(c,leg,thermal_runaway_index,PlotUtils.ColorPalette()[3],'t = thermal runaway'))
    else :
        collection.append(PlotQRefGraph(c,leg,-1           ,PlotUtils.ColorPalette()[2],'t = 14 years'))
    leg.Draw()

    taxisfunc.AutoFixYaxis(c)
    taxisfunc.FixXaxisRanges(c)

    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'QrefVersusTs'))

    #
    # TID Characterization vs time
    #
    c.Clear()
    leg = ROOT.TLegend(0.52,0.76,0.84,0.93)
    PlotUtils.SetStyleLegend(leg)
    extr['tid_shape'].Draw('al')
    leg.AddEntry(extr['tid_shape'],extr['tid_shape'].GetTitle(),'l')
    for i,g in enumerate(['tid_bump_abc','tid_bump_hcc','tid_sf_abc','tid_sf_hcc']) :
        gr[g].SetLineColor(PlotUtils.ColorPalette()[i%2+1])
        if i > 1 :
            gr[g].SetLineStyle(7)
        gr[g].Draw('l')
        leg.AddEntry(gr[g],gr[g].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'TIDBumpCharacterization'))

    #
    # TID Characterization vs dose
    #
    c.Clear()
    leg = ROOT.TLegend(0.52,0.76,0.84,0.93)
    PlotUtils.SetStyleLegend(leg)
    gr_vdose = dict()
    xtitle_dose = 'Integrated dose [MRad]'
    x_dose = list(a/1000. for a in OperationalProfiles.tid_dose[1:])
    gr_vdose['tid_shape']    = MakeGraph('TID_ShapeVsDose'            ,'TID shape #times 1.45'    ,xtitle_dose,'shape',x_dose,tid_shape)
    gr_vdose['tid_sf_abc']   = MakeGraph('ABCTidBumpScaleFactorVsDose','ABC TID bump scale factor',xtitle_dose,'shape',x_dose,tid_sf_abc)
    gr_vdose['tid_sf_hcc']   = MakeGraph('HCCTidBumpScaleFactorVsDose','HCC TID bump scale factor',xtitle_dose,'shape',x_dose,tid_sf_hcc)
    gr_vdose['tid_bump_abc'] = MakeGraph('ABCTidBumpVsDose'           ,'ABC TID bump'             ,xtitle_dose,'shape',x_dose,tid_bump_abc)
    gr_vdose['tid_bump_hcc'] = MakeGraph('HCCTidBumpVsDose'           ,'HCC TID bump'             ,xtitle_dose,'shape',x_dose,tid_bump_hcc)
    gr_vdose['tid_shape'].Draw('al')
    leg.AddEntry(extr['tid_shape'],extr['tid_shape'].GetTitle(),'l')
    for i,g in enumerate(['tid_bump_abc','tid_bump_hcc','tid_sf_abc','tid_sf_hcc']) :
        gr_vdose[g].SetLineColor(PlotUtils.ColorPalette()[i%2+1])
        if i > 1 :
            gr_vdose[g].SetLineStyle(7)
        gr_vdose[g].Draw('l')
        leg.AddEntry(gr_vdose[g],gr_vdose[g].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'TIDBumpCharacterizationVsDose'))

    # Kurt, put any extra plots here -- End.

    # Claire, put any extra plots here

    # Claire, put any extra plots here -- End.

    # return all the graphs
    return_items = gr

    return return_items
