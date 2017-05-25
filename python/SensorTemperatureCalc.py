#
# SensorTemperatureCalc
#
import GlobalSettings
import Temperatures
import NominalPower
import SensorLeakage
import OperationalProfiles
import SensorProperties
import Layout
import SafetyFactors
import PoweringEfficiency
import PlotUtils
from PlotUtils import MakeGraph

import ROOT
import math
from array import array
import os

# Barrel I

def CalculateSensorTemperature(tc,options) :

    # "Initialize lists"
    # Lists of quantities vs time
    tsensor    = [] # Sensor temperature
    tabc       = [] # ABC temperature
    thcc       = [] # HCC temperature
    tfeast     = [] # FEAST temperature
    teos       = [] # EOS temperature
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
    efffeast   = [] # FEAST efficiency
    ptape      = [] # Power loss in complete tape layer
    pstave     = [] # Stave Power in layer

    # "Initialize temperatures"

    nomT = GlobalSettings.nomsensorT

    # These are initial values. Saved slightly differently for simplicity.
    # defTeos
    teos.append(Temperatures.Teos( NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] ))
    # defTabc
    tabc.append(Temperatures.Tabc( NominalPower.Pabc(nomT, 1, 0),
                                   NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] ))
    # defThcc
    thcc.append(Temperatures.Thcc( NominalPower.Phcc(nomT, 1, 0), NominalPower.eosP(nomT),
                                   NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] ))
    # defTfeast
    tfeast.append(Temperatures.Tfeast( NominalPower.Pfeast(nomT, nomT, nomT, 1, 0),
                                       NominalPower.eosP(nomT),
                                       NominalPower.Pmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, tc[0] ))

    # Not sure whether nstep+1 is required...
    for i in range(GlobalSettings.nstep) :

        # Solve for Tsensor (ts)
        x_list = []
        y_list = []
        for ts_i,ts in enumerate(range(-35,100)) :
            lhs = SensorLeakage.qref[i]
            rhs = Temperatures.Qref(ts,
                                    Temperatures.T0(NominalPower.eosP(teos[-1]),
                                                    NominalPower.Pmod(tabc[-1],
                                                                      thcc[-1],
                                                                      tfeast[-1],
                                                                      OperationalProfiles.doserate[i],
                                                                      OperationalProfiles.tid_dose[i],
                                                                      Temperatures.unref(SensorLeakage.qref[i],ts)/float(SensorProperties.vbias)
                                                                      ),
                                                    tc[i]
                                                    )
                                    )

            y = rhs - lhs
            if len(y_list) and y < y_list[-1] :
                break
            if (ts_i == 0) and y > 0 :
                print 'Error! In year %2.1f, y starts greater than 0. Exiting.'%(i*GlobalSettings.step)
                import sys; sys.exit()
            if y < -5 :
                continue

            x_list.append(ts)
            y_list.append(y)

        # interpolate using TGraph "Eval" function
        graph = ROOT.TGraph(len(x_list),array('d',y_list),array('d',x_list))
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
                                      tc[i]
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
                                      tc[i]
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
                                          tc[i]
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
                                      tc[i]
                                      )
                    )
        if (i == 0) :
            teos.pop(0) # remove the initial value

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

        # FEAST efficiency
        efffeast.append(PoweringEfficiency.feasteff(tfeast[-1],
                                                    NominalPower.Ifeast(tabc[-1],
                                                                        thcc[-1],
                                                                        OperationalProfiles.doserate[i],
                                                                        OperationalProfiles.tid_dose[i]
                                                                        )
                                                    )
                        )

        # if i and math.fabs(((i+1)*GlobalSettings.step) % 1.) < 0.000001 :
        #     print 'Calculated year %.0f'%( int((i+1)*GlobalSettings.step) )

        continue # end of loop

    x = GlobalSettings.time_step_list[1:]
    xtitle = 'Time [years]'

    # dictionary of graphs
    gr = dict()

    gr['tsensor']    = MakeGraph('SensorTemperature'      ,'sensor temperature'                        ,xtitle,'T_{%s} [#circ^{}C]'%('sensor'),x,tsensor   )
    gr['tabc']       = MakeGraph('AbcTemperature'         ,'ABC temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('ABC'   ),x,tabc      )
    gr['thcc']       = MakeGraph('HCCTemperature'         ,'HCC temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('HCC'   ),x,thcc      )
    gr['tfeast']     = MakeGraph('FEASTTemperature'       ,'FEAST temperature'                         ,xtitle,'T_{%s} [#circ^{}C]'%('FEAST' ),x,tfeast    )
    gr['teos']       = MakeGraph('EOSTemperature'         ,'EOS temperature'                           ,xtitle,'T_{%s} [#circ^{}C]'%('EOS'   ),x,teos      )
    gr['pmodule']    = MakeGraph('ModulePower'            ,'Module Power'                              ,xtitle,'P_{%s} [W]'%('module')        ,x,pmodule   )
    gr['pmtape']     = MakeGraph('TapePower'              ,'Tape Power Loss'                           ,xtitle,'P_{%s} [W]'%('tape'  )        ,x,pmtape    )
    gr['pmhv']       = MakeGraph('HVPower'                ,'HV Power per module'                       ,xtitle,'P_{%s} [W]'%('HV'    )        ,x,pmhv      )
    gr['isensor']    = MakeGraph('SensorCurrent'          ,'Sensor (leakage) current'                  ,xtitle,'I_{%s} [A]'%('sensor')        ,x,isensor   )
    gr['pmhvr']      = MakeGraph('HVPowerSerialResistors' ,'HV Power serial resistors'                 ,xtitle,'P_{%s} [W]'%('HV,Rseries')    ,x,pmhvr     )
    gr['powertotal'] = MakeGraph('SummaryTotalPower'      ,'Total Power in layer'                      ,xtitle,'P [kW]'                       ,x,powertotal)
    gr['phvtotal']   = MakeGraph('SummaryTotalHVPower'    ,'Total HV Power (sensor+resistors) in layer',xtitle,'P_{%s} [kW]'%('HV')           ,x,phvtotal  )
    gr['pmhvmux']    = MakeGraph('HVPowerParallelResistor','HV Power parallel resistor'                ,xtitle,'P_{%s} [W]'%('HV,Rparallel')  ,x,pmhvmux   )
    gr['itape']      = MakeGraph('TapeCurrent'            ,'Tape current per module'                   ,xtitle,'I_{%s} [A]'%('tape')          ,x,itape     )
    gr['idig']       = MakeGraph('DigitalCurrent'         ,'ABC and HCC digital current'               ,xtitle,'I_{%s} [A]'%('digital')       ,x,idig      )
    gr['efffeast']   = MakeGraph('FeastEfficiency'        ,'Feast efficiency'                          ,xtitle,'Efficiency [%]'               ,x,efffeast  )
    gr['ptape']      = MakeGraph('TotalPowerLossTape'     ,'Power loss in complete tape in layer'      ,xtitle,'P_{%s} [W]'%('tape')          ,x,ptape     )
    gr['pstave']     = MakeGraph('TotalStavePower'        ,'Stave Power in layer'                      ,xtitle,'P_{%s} [W]'%('stave')         ,x,pstave    )

    outputpath = '%s/plots/SensorTemperatureCalc'%(('/').join(os.getcwd().split('/')[:-1]))

    outputtag = PlotUtils.GetCoolingOutputTag(options.cooling)
    scenariolabel = PlotUtils.GetCoolingScenarioLabel(options.cooling)

    dosave = (not hasattr(options,'save') or options.save)

    # Write out to file
    if dosave :
        outfilename = '%s/%s_%s.root'%(outputpath,'SensorTemperatureCalc',outputtag)
        out = ROOT.TFile(outfilename,'recreate')
        for g in gr.keys() :
            gr[g].Write()
        out.Close()
        print 'Wrote file %s'%(outfilename)

    # Write plots
    c = ROOT.TCanvas('blah','blah',600,500)
    text = ROOT.TLegend(0.13,0.89,0.41,0.94) # a more flexible way to draw text.
    PlotUtils.SetStyleLegend(text)
    text.AddEntry(0,scenariolabel,'')
    for g in gr.keys() :
        c.Clear()
        gr[g].Draw('al')
        text.Draw()
        if dosave :
            c.Print('%s/%s_%s.eps'%(outputpath,gr[g].GetName(),outputtag))

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
        gr[key].GetHistogram().GetYaxis().SetRangeUser(0,15)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    if dosave :
        c.Print('%s/%s_%s.eps'%(outputpath,'SummaryPowerPerModule',outputtag))

    #
    # Temperatures
    #
    c.Clear()
    gr['tcoolant'] = MakeGraph('CoolantTemperature','coolant temperature',xtitle,'T_{%s} [#circ^{}C]',x,tc)
    colors = {'tabc'    :ROOT.kBlue+1,
              'thcc'    :ROOT.kRed+1,
              'tfeast'  :ROOT.kOrange+1,
              'teos'    :ROOT.kCyan+1,
              'tsensor' :ROOT.kGreen,
              'tcoolant':ROOT.kMagenta+1,
              }
    leg = ROOT.TLegend(0.52,0.69,0.80,0.93)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['tabc','thcc','tfeast','teos','tsensor','tcoolant']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        gr[key].GetHistogram().GetYaxis().SetRangeUser(-40,100)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    if dosave :
        c.Print('%s/%s_%s.eps'%(outputpath,'SummaryTemperature',outputtag))

    #
    # HV power summary
    #
    c.Clear()
    gr['pmodule'].SetTitle('Total HV power per module')
    hv_power_resistors = list(pmhvr[i] + pmhvmux[i] for i in range(len(pmhv)))
    gr['hv_power_resistors'] = MakeGraph('HVPowerResistors','HV power contributions all resistors',xtitle,'P [W]',x,hv_power_resistors)
    gr['pmhvmux'].SetTitle('HV power contribution parallel resistor')
    colors = {'pmhv'              :ROOT.kBlue+1,
              'hv_power_resistors':ROOT.kGreen+1,
              'pmhvmux'           :ROOT.kRed+1,
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmhv','hv_power_resistors','pmhvmux']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        gr[key].GetHistogram().GetYaxis().SetRangeUser(0,2)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    if dosave :
        c.Print('%s/%s_%s.eps'%(outputpath,'SummaryHVPower',outputtag))

    # Kurt, put any extra plots here -- End.

    # Claire, put any extra plots here

    # Claire, put any extra plots here -- End.

    return_items = dict()
    return_items['powertotal'] = powertotal
    return_items['pmodule'] = pmodule

    return return_items
