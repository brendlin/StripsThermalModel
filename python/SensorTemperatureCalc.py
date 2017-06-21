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
    ts_vs_q_thermalbalance = [] # Thermal balance Q vs sensor temperature

    # Not sure whether nstep+1 is required...
    for i in range(GlobalSettings.nstep) :

        year = int((i+1)*GlobalSettings.step)
        month = ((i+1)*GlobalSettings.step % 1.)*12.

        # sensor temperature vs sensor leakage power stuff
        ts_sweep_list.append([])
        ts_vs_qref.append([])
        static_qref.append([])
        ts_vs_q.append([])
        ts_vs_q_thermalbalance.append([])

        # Solve for Tsensor (ts)
        tmp_ts_list = []
        qref_rootsolve_list = []

        y_gets_over_zero = False

        for ts_i,ts in enumerate(range(2*(-35),10*2)) :
            ts = ts/2.
            lhs = SensorLeakage.qref[i]
            rhs = Temperatures.Qref(ts,
                                    Temperatures.T0(NominalPower.eosP(teos[-1]),
                                                    NominalPower.Pmod(tabc[-1],
                                                                      thcc[-1],
                                                                      tfeast[-1],
                                                                      OperationalProfiles.doserate[i],
                                                                      OperationalProfiles.tid_dose[i],
                                                                      0 # Temperatures.unref(SensorLeakage.qref[i],ts)/float(SensorProperties.vbias)
                                                                      ),
                                                    CoolantTemperature.GetTimeStepTc()[i]
                                                    )
                                    )

            t0_noLeakage = Temperatures.T0(NominalPower.eosP(teos[-1]),
                                           NominalPower.Pmod(tabc[-1],
                                                             thcc[-1],
                                                             tfeast[-1],
                                                             OperationalProfiles.doserate[i],
                                                             OperationalProfiles.tid_dose[i],
                                                             0), # (assumed 0 HV current here)
                                           CoolantTemperature.GetTimeStepTc()[i]
                                           )

            # sensor temperature vs sensor leakage power stuff
            ts_sweep_list[-1].append(ts)
            ts_vs_qref[-1].append(rhs*1000./SensorProperties.area) # Qref vs sensor temperature in microW/mm^2
            static_qref[-1].append(lhs*1000./SensorProperties.area) # sensor leakage modeling
            ts_vs_q[-1].append(Temperatures.unref(SensorLeakage.qref[i],ts)) # Q(Ts) vs sensor temperature
            ts_vs_q_thermalbalance[-1].append(max(0,(ts-t0_noLeakage)/float(ThermalImpedances.Rt))) # Thermal balance Q vs sensor temperature

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
                           powertotal,phvtotal,pmhvmux,itape,idig,ifeast,efffeast,ptape,pstave] :
                i_list.append(i_list[-1])
            continue

        # interpolate using TGraph "Eval" function
        graph = ROOT.TGraph(len(tmp_ts_list),array('d',qref_rootsolve_list),array('d',tmp_ts_list))
        resultts = graph.Eval(0)

        # (solving step is done.)

        # Calculate temperatures in the system based on sensor temperature

        #  Sensor temperature
        tsensor.append(resultts)

        # Temperature of ABC
        tabc.append(Temperatures.Tabc(NominalPower.Pabc(tabc[-1],
                                                        OperationalProfiles.doserate[i],
                                                        OperationalProfiles.tid_dose[i]),
                                      NominalPower.eosP(teos[-1]),
                                      NominalPower.Pmod(tabc[-1],
                                                        thcc[-1],
                                                        tfeast[-1],
                                                        OperationalProfiles.doserate[i],
                                                        OperationalProfiles.tid_dose[i],
                                                        Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                                        ),
                                      Temperatures.unref(SensorLeakage.qref[i],resultts),
                                      CoolantTemperature.GetTimeStepTc()[i]
                                      )
                      )
        if (i == 0) :
            tabc.pop(0) # remove the initial value

        # Temperature of HCC
        thcc.append(Temperatures.Thcc(NominalPower.Phcc(thcc[-1],
                                                        OperationalProfiles.doserate[i],
                                                        OperationalProfiles.tid_dose[i]),
                                      NominalPower.eosP(teos[-1]),
                                      NominalPower.Pmod(tabc[-1],
                                                        thcc[-1],
                                                        tfeast[-1],
                                                        OperationalProfiles.doserate[i],
                                                        OperationalProfiles.tid_dose[i],
                                                        Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                                        ),
                                      Temperatures.unref(SensorLeakage.qref[i],resultts),
                                      CoolantTemperature.GetTimeStepTc()[i]
                                      )
                      )
        if (i == 0) :
            thcc.pop(0) # remove the initial value

        # Temperature of FEAST
        tfeast.append(Temperatures.Tfeast(NominalPower.Pfeast(tabc[-1],
                                                              thcc[-1],
                                                              tfeast[-1],
                                                              OperationalProfiles.doserate[i],
                                                              OperationalProfiles.tid_dose[i]),
                                          NominalPower.eosP(teos[-1]),
                                          NominalPower.Pmod(tabc[-1],
                                                            thcc[-1],
                                                            tfeast[-1],
                                                            OperationalProfiles.doserate[i],
                                                            OperationalProfiles.tid_dose[i],
                                                            Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                                            ),
                                          Temperatures.unref(SensorLeakage.qref[i],resultts),
                                          CoolantTemperature.GetTimeStepTc()[i]
                                          )
                      )
        if (i == 0) :
            tfeast.pop(0) # remove the initial value

        # Temperature of EOS
        teos.append(Temperatures.Teos(NominalPower.eosP(teos[-1]),
                                      NominalPower.Pmod(tabc[-1],
                                                        thcc[-1],
                                                        tfeast[-1],
                                                        OperationalProfiles.doserate[i],
                                                        OperationalProfiles.tid_dose[i],
                                                        Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                                        ),
                                      Temperatures.unref(SensorLeakage.qref[i],resultts),
                                      CoolantTemperature.GetTimeStepTc()[i]
                                      )
                    )
        if (i == 0) :
            teos.pop(0) # remove the initial value

        # ABC Power (all n ABCs)
        pabc.append(NominalPower.Pabc(tabc[-1],
                                      OperationalProfiles.doserate[i],
                                      OperationalProfiles.tid_dose[i])
                    )

        # HCC power (all n HCCs)
        phcc.append(NominalPower.Phcc(thcc[-1],
                                      OperationalProfiles.doserate[i],
                                      OperationalProfiles.tid_dose[i])
                    )

        # EOS Power
        peos.append(NominalPower.eosP(teos[-1]))

        # FEAST power
        pfeast.append(NominalPower.Pfeast(tabc[-1],
                                          thcc[-1],
                                          tfeast[-1],
                                          OperationalProfiles.doserate[i],
                                          OperationalProfiles.tid_dose[i])
                      )

        # FEAST power from ABC and HCC only
        pfeast_abchcc.append(NominalPower.Pfeast_ABC_HCC(tabc[-1],
                                                         thcc[-1],
                                                         tfeast[-1],
                                                         OperationalProfiles.doserate[i],
                                                         OperationalProfiles.tid_dose[i])
                             )

        #
        # From here we can use actual temperatures
        #

        # Power per module (front-end + HV)
        pmodule.append(NominalPower.Pmod(tabc[-1],
                                         thcc[-1],
                                         tfeast[-1],
                                         OperationalProfiles.doserate[i],
                                         OperationalProfiles.tid_dose[i],
                                         Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                         )
                       + Temperatures.unref(SensorLeakage.qref[i],resultts)
                       )

        # Power loss in tape per module
        pmtape.append(NominalPower.Ptape(tabc[-1],
                                         thcc[-1],
                                         tfeast[-1],
                                         OperationalProfiles.doserate[i],
                                         OperationalProfiles.tid_dose[i]
                                         )
                      )

        # HV power per module (leakage + resistors)
        pmhv.append(Temperatures.unref(SensorLeakage.qref[i],resultts)
                    + NominalPower.Phv( Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias) )
                    )

        # Leakage current per module
        isensor.append( Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias) )

        # HV power per module due to serial resistors
        pmhvr.append( NominalPower.Prhv( Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias) ) )

        # HV per module due to parallel resistor
        pmhvmux.append(NominalPower.Phvmux)

        # Stave power B1
        pstave.append(NominalPower.Pstave(tabc[-1],
                                          thcc[-1],
                                          tfeast[-1],
                                          teos[-1],
                                          OperationalProfiles.doserate[i],
                                          OperationalProfiles.tid_dose[i],
                                          Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                          )
                      )

        # Total power for layer
        # Extra factor of 2 is for 2 sides of the barrel, or 2 endcaps.
        powertotal.append( 2 * Layout.nstaves * (1 + SafetyFactors.safetylayout)
                           * NominalPower.Pstave(tabc[-1],
                                                 thcc[-1],
                                                 tfeast[-1],
                                                 teos[-1],
                                                 OperationalProfiles.doserate[i],
                                                 OperationalProfiles.tid_dose[i],
                                                 Temperatures.unref(SensorLeakage.qref[i],resultts)/float(SensorProperties.vbias)
                                                 )
                           / 1000.
                           )

        # Total HV power for layer
        # One factor of 2 is for 2 sides of the barrel, or 2 endcaps.
        # Antoher factor of 2 is for two sides of the module
        phvtotal.append( 2 * Layout.nstaves * (1 + SafetyFactors.safetylayout) * 2 * Layout.nmod * (pmhv[-1] + pmhvr[-1]) / 1000. )

        # Tape current per module
        itape.append(NominalPower.Itape(tabc[-1],
                                        thcc[-1],
                                        tfeast[-1],
                                        OperationalProfiles.doserate[i],
                                        OperationalProfiles.tid_dose[i]
                                        )
                     )

        # Tape power for one tape (half a stave)
        ptape.append(NominalPower.Pstavetape(tabc[-1],
                                             thcc[-1],
                                             tfeast[-1],
                                             OperationalProfiles.doserate[i],
                                             OperationalProfiles.tid_dose[i]
                                             )
                     )

        # Digital current per module
        idig.append(NominalPower.Idig(tabc[-1],
                                      thcc[-1],
                                      OperationalProfiles.doserate[i],
                                      OperationalProfiles.tid_dose[i]
                                      )
                    )

        # FEAST current PER FEAST (in case there is more than one feast)
        ifeast.append(NominalPower.Ifeast(tabc[-1],
                                          thcc[-1],
                                          OperationalProfiles.doserate[i],
                                          OperationalProfiles.tid_dose[i]
                                          ) / float(NominalPower.nfeast)
                      )

        # FEAST efficiency
        efffeast.append(PoweringEfficiency.feasteff(tfeast[-1],
                                                    NominalPower.Ifeast(tabc[-1],
                                                                        thcc[-1],
                                                                        OperationalProfiles.doserate[i],
                                                                        OperationalProfiles.tid_dose[i]
                                                                        )/float(NominalPower.nfeast)
                                                    )
                        )

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
    gr['isensor']    = MakeGraph('SensorCurrent'          ,'Sensor (leakage) current'                  ,xtitle,'I_{%s} [A]'%('sensor')        ,x,isensor   )
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

    dosave = (not hasattr(options,'save') or options.save)

    # Move output path outside code directory
    outputpath = '%s/plots/SensorTemperatureCalc'%(os.getcwd().split('/StripsThermalModel')[0])
    # If a different output name is specified
    if hasattr(options,'outdir') :
        outputpath = '%s/plots/%s'%(os.getcwd().split('/StripsThermalModel')[0],options.outdir)
    if dosave :
        if not os.path.exists(outputpath) :
            os.makedirs(outputpath)
        print 'SensorTemperatureCalc output written to %s'%(outputpath)

    # Write out to file
    if dosave :
        outfilename = '%s/%s.root'%(outputpath,'SensorTemperatureCalc')
        out = ROOT.TFile(outfilename,'recreate')
        for g in gr.keys() :
            gr[g].Write()
        out.Close()
        print 'Wrote file %s'%(outfilename)

    # Write plots
    c = ROOT.TCanvas('blah','blah',600,500)
    text = ROOT.TLegend(0.13,0.77,0.41,0.94) # a more flexible way to draw text.
    PlotUtils.SetStyleLegend(text)
    PlotUtils.AddRunParameterLabels(text)
    for g in gr.keys() :
        c.Clear()
        gr[g].Draw('al')
        text.Draw()
        taxisfunc.AutoFixYaxis(c)
        if dosave :
            c.Print('%s/%s.eps'%(outputpath,gr[g].GetName()))

    # Extra graphs that you may not want to save individually
    extr = dict()
    extr['pamac']         = MakeGraph('AMACPower'              ,'AMAC power'                                ,xtitle,'P_{%s} [W]'%('AMAC'  )        ,x,pamac     )
    extr['pabc']          = MakeGraph('ABCPower'               ,'ABC power'                                 ,xtitle,'P_{%s} [W]'%('ABC'   )        ,x,pabc      )
    extr['phcc']          = MakeGraph('HCCPower'               ,'HCC power'                                 ,xtitle,'P_{%s} [W]'%('HCC'   )        ,x,phcc      )
    extr['pfeast']        = MakeGraph('FeastPower'             ,'FEAST power'                               ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfeast    )
    extr['pfeast_abchcc'] = MakeGraph('FeastPower_ABC_HCC'     ,'FEAST power (HCC,ABC)'                     ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfeast_abchcc)
    extr['pfamac']        = MakeGraph('FeastPower_AMAC'        ,'FEAST power (AMAC)'                        ,xtitle,'P_{%s} [W]'%('FEAST' )        ,x,pfamac    )

    # Kurt, put any extra plots here

    #
    # Module power
    #
    c.Clear()
    # pmodule_noHV is (Power per module) minus (HV power + HV power due to serial resistors)
    pmodule_noHV  = list(pmodule[i] - (pmhv[i] + pmhvr[i]) for i in range(len(pmodule)))
    gr['pmodule_noHV'] = MakeGraph('ModulePower_noHV','Power without HV',xtitle,'P [W]',x,pmodule_noHV)
    pmodule_noHV_noTapeLoss = list(pmodule[i] - (pmhv[i] + pmhvr[i]) - pmtape[i] for i in range(len(pmodule)))
    gr['pmodule_noHV_noTapeLoss'] = MakeGraph('ModulePower_noHV_NoTapeLoss','Power w/o HV and w/o tape loss',xtitle,'P [W]',x,pmodule_noHV_noTapeLoss)
    colors = {'pmodule'                :ROOT.kGreen+1,
              'pmodule_noHV'           :ROOT.kBlue+1,
              'pmodule_noHV_noTapeLoss':ROOT.kRed+1
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmodule','pmodule_noHV','pmodule_noHV_noTapeLoss']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    taxisfunc.AutoFixYaxis(c,minzero=True)
    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'SummaryPowerPerModule'))

    #
    # Temperatures
    #
    c.Clear()
    gr['tcoolant'] = MakeGraph('CoolantTemperature','coolant temperature',xtitle,'T_{%s} [#circ^{}C]'%('coolant'),x,CoolantTemperature.GetTimeStepTc())
    colors = {'tabc'    :ROOT.kBlue+1,
              'thcc'    :ROOT.kRed+1,
              'tfeast'  :ROOT.kOrange+1,
              'teos'    :ROOT.kCyan+1,
              'tsensor' :ROOT.kGreen,
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
    PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pamac']))
    PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pabc']))
    PlotUtils.AddToStack(stack,leg,GraphToHist(extr['phcc']))
    PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pfeast_abchcc']))
    PlotUtils.AddToStack(stack,leg,GraphToHist(extr['pfamac']))
    PlotUtils.AddToStack(stack,leg,GraphToHist(gr['pmtape'])) # fix!!!
    PlotUtils.AddToStack(stack,leg,GraphToHist(gr['pmhv'])) # HV including the sensor leakage
    if max(peos) > 0 :
        PlotUtils.AddToStack(stack,leg,GraphToHist(gr['peos']))
    else :
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
        tmp_gr = MakeGraph('blah','blah','T_{S} [#circ^{}C]','Q [W]',xlist,ylist)

        ylist_1 = ts_vs_q[index]
        index_stop = len(ylist_1)
        too_high = list(ylist_1[i] > ylist[-1] for i in range(len(ylist_1)))
        if True in too_high :
            index_stop = too_high.index(True)
        tmp_gr_1 = MakeGraph('Q(thermal balance)','Q(thermal balance)','T_{S} [#circ^{}C]','Q [W]',xlist[:index_stop],ylist_1[:index_stop])

        tmp_gr  .SetLineColor(color)
        tmp_gr_1.SetLineColor(color)

        can.cd()
        drawopt = 'l' if (True in list(issubclass(type(a),ROOT.TGraph) for a in can.GetListOfPrimitives())) else 'al'
        tmp_gr.Draw(drawopt)
        tmp_gr_1.Draw('l')

        legend.AddEntry(tmp_gr,leg_label,'l')

        return tmp_gr,tmp_gr_1

    c.Clear()
    leg = ROOT.TLegend(0.61,0.80,0.93,0.93)
    PlotUtils.SetStyleLegend(leg)
    year1_index = int(1./float(GlobalSettings.step))
    print year1_index

    collection = []
    collection.append(PlotQGraph(c,leg,year1_index,PlotUtils.ColorPalette()[0],'t = 1 year'  ))
    collection.append(PlotQGraph(c,leg,tid_max_index,PlotUtils.ColorPalette()[1],'t = tid bump'))
    if thermal_runaway_index :
        collection.append(PlotQGraph(c,leg,thermal_runaway_index,PlotUtils.ColorPalette()[3],'t = thermal runaway'))
    else :
        collection.append(PlotQGraph(c,leg,-1           ,PlotUtils.ColorPalette()[2],'t = 0 years' ))
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

        x_max_i = xlist.index(max(xlist))

        # Trim top
        tmp_y = ylist
        while xlist[-1] < 0 :
            xlist.pop(-1)
            tmp_y.pop(-1)

        tmp_gr   = MakeGraph('blah','blah','q^{}_{ref} at  #minus15#circ^{}C [#mu^{}W/mm^{2}]','T_{S} [#circ^{}C]',xlist[:x_max_i],tmp_y[:x_max_i])
        tmp_gr_1 = MakeGraph('blah','blah','q^{}_{ref} at  #minus15#circ^{}C [#mu^{}W/mm^{2}]','T_{S} [#circ^{}C]',xlist[x_max_i-1:],tmp_y[x_max_i-1:])

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
        if static_qref[index][0] < max(xlist) :
            static_qref_ts = tmp_gr.Eval(static_qref[index][0])
        tmp_gr_2 = MakeGraph('blah','blah','','',[static_qref[index][0]],[static_qref_ts])
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
        collection.append(PlotQRefGraph(c,leg,thermal_runaway_index-1,PlotUtils.ColorPalette()[3],'t = thermal runaway'))
    else :
        collection.append(PlotQRefGraph(c,leg,-1           ,PlotUtils.ColorPalette()[2],'t = 14 years'))
    leg.Draw()

    taxisfunc.AutoFixYaxis(c)

    if dosave :
        c.Print('%s/%s.eps'%(outputpath,'QrefVersusTs'))

    # Kurt, put any extra plots here -- End.

    # Claire, put any extra plots here

    # Claire, put any extra plots here -- End.

    # return all the graphs
    return_items = gr

    return return_items
