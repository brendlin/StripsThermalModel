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
    tsb1       = [] # Sensor temperature
    tabcb1     = [] # ABC temperature
    thccb1     = [] # HCC temperature
    tfeastb1   = [] # FEAST temperature
    teosb1     = [] # EOS temperature
    pmoduleb1  = [] # Power per module (front-end + HV)
    pmtapeb1   = [] # Power loss in tape per module
    pmhvb1     = [] # HV power per module (leakage + resistors)
    isb1       = [] # Sensor current (Leakage current per module)
    pmhvrb1    = [] # HV power per module due to serial resistors
    pb1        = [] # Total power in B1
    phvb1      = [] # Total HV Power (sensor+resistors) in B1
    pmhvmuxb1  = [] # HV Power parallel resistor
    itapeb1    = [] # Tape current per module
    idigb1     = [] # Digital current per module
    efffeastb1 = [] # FEAST efficiency
    ptapeb1    = [] # Power loss in complete tape B1
    pstaveb1   = [] # Stave Power in B1

    # "Initialize temperatures"

    nomT = GlobalSettings.nomsensorT

    # These are initial values. Saved slightly differently for simplicity.
    # defTeos
    teosb1.append(Temperatures.ssTeos( NominalPower.sseosP(nomT),
                                       NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, tc[0] ))
    # defTabc
    tabcb1.append(Temperatures.ssTabc( NominalPower.ssPabc(nomT, 1, 0),
                                       NominalPower.sseosP(nomT),
                                       NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, tc[0] ))
    # defThcc
    thccb1.append(Temperatures.ssThcc( NominalPower.ssPhcc(nomT, 1, 0), NominalPower.sseosP(nomT),
                                       NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, tc[0] ))
    # defTfeast
    tfeastb1.append(Temperatures.ssTfeast( NominalPower.ssPfeast(nomT, nomT, nomT, 1, 0),
                                           NominalPower.sseosP(nomT),
                                           NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                           0, tc[0] ))

    # Not sure whether nstep+1 is required...
    for i in range(GlobalSettings.nstep) :

        # Solve for Tsensor (ts)
        x_list = []
        y_list = []
        for ts_i,ts in enumerate(range(-35,100)) :
            lhs = SensorLeakage.qrefb1[i]
            rhs = Temperatures.Qref(ts,
                                    Temperatures.ssT0(NominalPower.sseosP(teosb1[-1]),
                                                      NominalPower.ssPmod(tabcb1[-1],
                                                                          thccb1[-1],
                                                                          tfeastb1[-1],
                                                                          OperationalProfiles.doserateb1[i],
                                                                          OperationalProfiles.tidb1[i],
                                                                          Temperatures.unref(SensorLeakage.qrefb1[i],ts)/float(SensorProperties.vbias)
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
        tsb1.append(resultts)

        # Temperature of ABC
        tabcb1.append(Temperatures.ssTabc(NominalPower.ssPabc(tabcb1[-1],
                                                              OperationalProfiles.doserateb1[i],
                                                              OperationalProfiles.tidb1[i]),
                                          NominalPower.sseosP(teosb1[-1]),
                                          NominalPower.ssPmod(tabcb1[-1],
                                                              thccb1[-1],
                                                              tfeastb1[-1],
                                                              OperationalProfiles.doserateb1[i],
                                                              OperationalProfiles.tidb1[i],
                                                              Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                                              ),
                                      Temperatures.unref(SensorLeakage.qrefb1[i],resultts), # ???
                                      tc[i] # ???
                                      )
                  )
        if (i == 0) :
            tabcb1.pop(0) # remove the initial value

        # Temperature of HCC
        thccb1.append(Temperatures.ssThcc(NominalPower.ssPhcc(thccb1[-1],
                                                              OperationalProfiles.doserateb1[i],
                                                              OperationalProfiles.tidb1[i]),
                                          NominalPower.sseosP(teosb1[-1]),
                                          NominalPower.ssPmod(tabcb1[-1],
                                                              thccb1[-1],
                                                              tfeastb1[-1],
                                                              OperationalProfiles.doserateb1[i],
                                                              OperationalProfiles.tidb1[i],
                                                              Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                                              ),
                                          Temperatures.unref(SensorLeakage.qrefb1[i],resultts), # ???
                                          tc[i] # ???
                                          )
                      )
        if (i == 0) :
            thccb1.pop(0) # remove the initial value

        # Temperature of FEAST
        tfeastb1.append(Temperatures.ssTfeast(NominalPower.ssPfeast(tabcb1[-1],
                                                                    thccb1[-1],
                                                                    tfeastb1[-1],
                                                                    OperationalProfiles.doserateb1[i],
                                                                    OperationalProfiles.tidb1[i]),
                                              NominalPower.sseosP(teosb1[-1]),
                                              NominalPower.ssPmod(tabcb1[-1],
                                                                  thccb1[-1],
                                                                  tfeastb1[-1],
                                                                  OperationalProfiles.doserateb1[i],
                                                                  OperationalProfiles.tidb1[i],
                                                                  Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                                                  ),
                                              Temperatures.unref(SensorLeakage.qrefb1[i],resultts), # ???
                                              tc[i] # ???
                                              )
                        )
        if (i == 0) :
            tfeastb1.pop(0) # remove the initial value

        # Temperature of EOS
        teosb1.append(Temperatures.ssTeos(NominalPower.sseosP(teosb1[-1]),
                                          NominalPower.ssPmod(tabcb1[-1],
                                                              thccb1[-1],
                                                              tfeastb1[-1],
                                                              OperationalProfiles.doserateb1[i],
                                                              OperationalProfiles.tidb1[i],
                                                              Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                                              ),
                                          Temperatures.unref(SensorLeakage.qrefb1[i],resultts), # ???
                                          tc[i] # ???
                                          )
                      )
        if (i == 0) :
            teosb1.pop(0) # remove the initial value

        #
        # From here we can use actual temperatures
        #

        # Power per module (front-end + HV)
        pmoduleb1.append(NominalPower.ssPmod(tabcb1[-1],
                                             thccb1[-1],
                                             tfeastb1[-1],
                                             OperationalProfiles.doserateb1[i],
                                             OperationalProfiles.tidb1[i],
                                             Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                             )
                         + Temperatures.unref(SensorLeakage.qrefb1[i],resultts)
                         )

        # Power loss in tape per module
        pmtapeb1.append(NominalPower.ssPtape(tabcb1[-1],
                                             thccb1[-1],
                                             tfeastb1[-1],
                                             OperationalProfiles.doserateb1[i],
                                             OperationalProfiles.tidb1[i]
                                             )
                        )

        # HV power per module (leakage + resistors)
        pmhvb1.append(Temperatures.unref(SensorLeakage.qrefb1[i],resultts)
                      + NominalPower.Phv( Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias) )
                      )

        # Leakage current per module
        isb1.append( Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias) )

        # HV power per module due to serial resistors
        pmhvrb1.append( NominalPower.Prhv( Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias) ) )

        # HV per module due to parallel resistor
        pmhvmuxb1.append(NominalPower.Phvmux)

        # Stave power B1
        pstaveb1.append(NominalPower.ssPstave(tabcb1[-1],
                                              thccb1[-1],
                                              tfeastb1[-1],
                                              teosb1[-1],
                                              OperationalProfiles.doserateb1[i],
                                              OperationalProfiles.tidb1[i],
                                              Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                              )
                        )

        # Total power for B1
        pb1.append( 2 * Layout.nstavesb1 * (1 + SafetyFactors.safetylayout)
                    * NominalPower.ssPstave(tabcb1[-1],
                                            thccb1[-1],
                                            tfeastb1[-1],
                                            teosb1[-1],
                                            OperationalProfiles.doserateb1[i],
                                            OperationalProfiles.tidb1[i],
                                            Temperatures.unref(SensorLeakage.qrefb1[i],resultts)/float(SensorProperties.vbias)
                                            )
                    / 1000.
                    )

        # Total HV power for B1
        phvb1.append( 2 * Layout.nstavesb1 * (1 + SafetyFactors.safetylayout) * 2 * Layout.nmod * (pmhvb1[-1] + pmhvrb1[-1]) / 1000. )

        # Tape current per module
        itapeb1.append(NominalPower.ssItape(tabcb1[-1],
                                            thccb1[-1],
                                            tfeastb1[-1],
                                            OperationalProfiles.doserateb1[i],
                                            OperationalProfiles.tidb1[i]
                                            )
                       )

        # Tape power for one tape (half a stave)
        ptapeb1.append(NominalPower.ssPstavetape(tabcb1[-1],
                                                 thccb1[-1],
                                                 tfeastb1[-1],
                                                 OperationalProfiles.doserateb1[i],
                                                 OperationalProfiles.tidb1[i]
                                                 )
                       )

        # Digital current per module
        idigb1.append(NominalPower.ssIdig(tabcb1[-1],
                                          thccb1[-1],
                                          OperationalProfiles.doserateb1[i],
                                          OperationalProfiles.tidb1[i]
                                          )
                      )

        # FEAST efficiency
        efffeastb1.append(PoweringEfficiency.feasteff(tfeastb1[-1],
                                                      NominalPower.ssIfeast(tabcb1[-1],
                                                                            thccb1[-1],
                                                                            OperationalProfiles.doserateb1[i],
                                                                            OperationalProfiles.tidb1[i]
                                                                            )
                                                      )
                          )

        if i and math.fabs(((i+1)*GlobalSettings.step) % 1.) < 0.000001 :
            print 'Calculated year %.0f'%( int((i+1)*GlobalSettings.step) )

        continue # end of loop

    x = GlobalSettings.time_step_list[1:]
    xtitle = 'Time [years]'

    # dictionary of graphs
    gr = dict()

    gr['tsb1']       = MakeGraph('SensorTemperature'      ,'sensor temperature'                     ,xtitle,'T_{%s} [#circ^{}C]'%('sensor'),x,tsb1      )
    gr['tabcb1']     = MakeGraph('AbcTemperature'         ,'ABC temperature'                        ,xtitle,'T_{%s} [#circ^{}C]'%('ABC'   ),x,tabcb1    )
    gr['thccb1']     = MakeGraph('HCCTemperature'         ,'HCC temperature'                        ,xtitle,'T_{%s} [#circ^{}C]'%('HCC'   ),x,thccb1    )
    gr['tfeastb1']   = MakeGraph('FEASTTemperature'       ,'FEAST temperature'                      ,xtitle,'T_{%s} [#circ^{}C]'%('FEAST' ),x,tfeastb1  )
    gr['teosb1']     = MakeGraph('EOSTemperature'         ,'EOS temperature'                        ,xtitle,'T_{%s} [#circ^{}C]'%('EOS'   ),x,teosb1    )
    gr['pmoduleb1']  = MakeGraph('ModulePower'            ,'Module Power'                           ,xtitle,'P_{%s} [W]'%('module')        ,x,pmoduleb1 )
    gr['pmtapeb1']   = MakeGraph('TapePower'              ,'Tape Power Loss'                        ,xtitle,'P_{%s} [W]'%('tape'  )        ,x,pmtapeb1  )
    gr['pmhvb1']     = MakeGraph('HVPower'                ,'HV Power per module'                    ,xtitle,'P_{%s} [W]'%('HV'    )        ,x,pmhvb1    )
    gr['isb1']       = MakeGraph('SensorCurrent'          ,'Sensor (leakage) current'               ,xtitle,'I_{%s} [A]'%('sensor')        ,x,isb1      )
    gr['pmhvrb1']    = MakeGraph('HVPowerSerialResistors' ,'HV Power serial resistors'              ,xtitle,'P_{%s} [W]'%('HV,Rseries')    ,x,pmhvrb1   )
    gr['pb1']        = MakeGraph('SummaryTotalPower'      ,'Total Power in B1'                      ,xtitle,'P_{%s} [kW]'%('B1')           ,x,pb1       )
    gr['phvb1']      = MakeGraph('SummaryTotalHVPower'    ,'Total HV Power (sensor+resistors) in B1',xtitle,'P_{%s} [kW]'%('HV')           ,x,phvb1     )
    gr['pmhvmuxb1']  = MakeGraph('HVPowerParallelResistor','HV Power parallel resistor'             ,xtitle,'P_{%s} [W]'%('HV,Rparallel')  ,x,pmhvmuxb1 )
    gr['itapeb1']    = MakeGraph('TapeCurrent'            ,'Tape current per module'                ,xtitle,'I_{%s} [A]'%('tape')          ,x,itapeb1   )
    gr['idigb1']     = MakeGraph('DigitalCurrent'         ,'ABC and HCC digital current'            ,xtitle,'I_{%s} [A]'%('digital')       ,x,idigb1    )
    gr['efffeastb1'] = MakeGraph('FeastEfficiency'        ,'Feast efficiency'                       ,xtitle,'Efficiency [%]'               ,x,efffeastb1)
    gr['ptapeb1']    = MakeGraph('TotalPowerLossTapeB1'   ,'Power loss in complete tape B1'         ,xtitle,'P_{%s} [W]'%('tape')          ,x,ptapeb1   )
    gr['pstaveb1']   = MakeGraph('TotalStavePowerB1'      ,'Stave Power in B1'                      ,xtitle,'P_{%s} [W]'%('stave')         ,x,pstaveb1  )

    outputpath = '%s/plots/SensorTemperatureCalc'%(('/').join(os.getcwd().split('/')[:-1]))
    outputtag = {
        'flat-25':'flat_m25',
        'flat-35':'flat_m35',
        'ramp-25':'ramp_m25',
        'ramp-35':'ramp_m35'
        }.get(options.cooling,'unknownScenario')

    scenariolabel = {
        'flat-25':'Flat #minus25#circ cooling scenario',
        'flat-35':'Flat #minus35#circ cooling scenario',
        'ramp-25':'Ramp #minus25#circ cooling scenario',
        'ramp-35':'Ramp #minus35#circ cooling scenario',
        }.get(options.cooling,'unknown cooling scenario')

    # Write out to file
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
        c.Print('%s/%s_%s.eps'%(outputpath,gr[g].GetName(),outputtag))

    # Kurt, put any extra plots here

    #
    # Module power
    #
    c.Clear()
    # pmoduleb1_noHV is (Power per module) minus (HV power + HV power due to serial resistors)
    pmoduleb1_noHV  = list(pmoduleb1[i] - (pmhvb1[i] + pmhvrb1[i]) for i in range(len(pmoduleb1)))
    gr['pmoduleb1_noHV'] = MakeGraph('ModulePower_noHV','Power without HV',xtitle,'P [W]',x,pmoduleb1_noHV)
    pmoduleb1_noHV_noTapeLoss = list(pmoduleb1[i] - (pmhvb1[i] + pmhvrb1[i]) - pmtapeb1[i] for i in range(len(pmoduleb1)))
    gr['pmoduleb1_noHV_noTapeLoss'] = MakeGraph('ModulePower_noHV_NoTapeLoss','Power w/o HV and w/o tape loss',xtitle,'P [W]',x,pmoduleb1_noHV_noTapeLoss)
    colors = {'pmoduleb1'                :ROOT.kGreen+1,
              'pmoduleb1_noHV'           :ROOT.kBlue+1,
              'pmoduleb1_noHV_noTapeLoss':ROOT.kRed+1
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmoduleb1','pmoduleb1_noHV','pmoduleb1_noHV_noTapeLoss']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        gr[key].GetHistogram().GetYaxis().SetRangeUser(0,15)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    c.Print('%s/%s_%s.eps'%(outputpath,'SummaryPowerPerModule',outputtag))

    #
    # Temperatures
    #
    c.Clear()
    gr['tcoolant'] = MakeGraph('CoolantTemperature','coolant temperature',xtitle,'T_{%s} [#circ^{}C]',x,tc)
    colors = {'tabcb1'  :ROOT.kBlue+1,
              'thccb1'  :ROOT.kRed+1,
              'tfeastb1':ROOT.kOrange+1,
              'teosb1'  :ROOT.kCyan+1,
              'tsb1'    :ROOT.kGreen,
              'tcoolant':ROOT.kMagenta+1,
              }
    leg = ROOT.TLegend(0.52,0.69,0.80,0.93)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['tabcb1','thccb1','tfeastb1','teosb1','tsb1','tcoolant']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        gr[key].GetHistogram().GetYaxis().SetRangeUser(-40,100)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    c.Print('%s/%s_%s.eps'%(outputpath,'SummaryTemperature',outputtag))

    #
    # HV power summary
    #
    c.Clear()
    gr['pmoduleb1'].SetTitle('Total HV power per module')
    hv_power_resistors = list(pmhvrb1[i] + pmhvmuxb1[i] for i in range(len(pmhvb1)))
    gr['hv_power_resistors'] = MakeGraph('HVPowerResistors','HV power contributions all resistors',xtitle,'P [W]',x,hv_power_resistors)
    gr['pmhvmuxb1'].SetTitle('HV power contribution parallel resistor')
    colors = {'pmhvb1'            :ROOT.kBlue+1,
              'hv_power_resistors':ROOT.kGreen+1,
              'pmhvmuxb1'         :ROOT.kRed+1,
              }
    leg = ROOT.TLegend(0.50,0.81,0.78,0.94)
    PlotUtils.SetStyleLegend(leg)
    for i,key in enumerate(['pmhvb1','hv_power_resistors','pmhvmuxb1']) :
        gr[key].SetLineColor(colors.get(key))
        gr[key].Draw('l' if i else 'al')
        gr[key].GetHistogram().GetYaxis().SetRangeUser(0,2)
        leg.AddEntry(gr[key],gr[key].GetTitle(),'l')
    leg.Draw()
    text.Draw()
    c.Print('%s/%s_%s.eps'%(outputpath,'SummaryHVPower',outputtag))

    # Kurt, put any extra plots here -- End.

    # Claire, put any extra plots here

    # Claire, put any extra plots here -- End.

    return
