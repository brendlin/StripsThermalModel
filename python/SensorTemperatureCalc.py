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
    tabcb1     = [] # ???
    thccb1     = [] # ???
    tfeastb1   = [] # ???
    teosb1     = [] # ???
    pmoduleb1  = [] # ???
    pmtapeb1   = [] # ???
    pmhvb1     = [] # ???
    isb1       = [] # ???
    pmhvrb1    = [] # ???
    pb1        = [] # ???
    phvb1      = [] # ???
    pmhvmuxb1  = [] # ???
    itapeb1    = [] # ???
    idigb1     = [] # ???
    efffeastb1 = [] # ???
    ptapeb1    = [] # ???
    pstaveb1   = [] # ???

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
                                             + Temperatures.unref(SensorLeakage.qrefb1[i],resultts)
                                             )
                         )

        # Power in tape per module
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
                                            OperationalProfiles.doserateb1[-1],
                                            OperationalProfiles.tidb1[-1]
                                            )
                       )

        # Tape power for one tape (half a stave)
        ptapeb1.append(NominalPower.ssPstavetape(tabcb1[-1],
                                                 thccb1[-1],
                                                 tfeastb1[-1],
                                                 OperationalProfiles.doserateb1[-1],
                                                 OperationalProfiles.tidb1[-1]
                                                 )
                       )

        # Digital current per module
        idigb1.append(NominalPower.ssIdig(tabcb1[-1],
                                          thccb1[-1],
                                          OperationalProfiles.doserateb1[-1],
                                          OperationalProfiles.tidb1[-1]
                                          )
                      )

        # FEAST efficiency
        efffeastb1.append(PoweringEfficiency.feasteff(tfeastb1[-1],
                                                      NominalPower.ssIfeast(tabcb1[-1],
                                                                            thccb1[-1],
                                                                            OperationalProfiles.doserateb1[-1],
                                                                            OperationalProfiles.tidb1[-1]
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

    gr['tsb1']       = MakeGraph('SensorTemperature','sensor temperature' ,xtitle,'T_{%s} [#circ^{}C]'%('sensor'),x,tsb1      )
    gr['tabcb1']     = MakeGraph('AbcTemperature'   ,'ABC temperature'    ,xtitle,'T_{%s} [#circ^{}C]'%('ABC'   ),x,tabcb1    )
    gr['thccb1']     = MakeGraph('HCCTemperature'   ,'HCC temperature'    ,xtitle,'T_{%s} [#circ^{}C]'%('HCC'   ),x,thccb1    )
    gr['tfeastb1']   = MakeGraph('FEASTTemperature' ,'FEAST temperature'  ,xtitle,'T_{%s} [#circ^{}C]'%('FEAST' ),x,tfeastb1  )
    gr['teosb1']     = MakeGraph('EOSTemperature'   ,'EOS temperature'    ,xtitle,'T_{%s} [#circ^{}C]'%('EOS'   ),x,teosb1    )
    gr['pmoduleb1']  = MakeGraph('ModulePower'      ,'Module Power'       ,xtitle,'P_{%s} [W]'%('module')        ,x,pmoduleb1 )
    gr['pmtapeb1']   = MakeGraph('TapePower'        ,'Tape Power'         ,xtitle,'P_{%s} [W]'%('tape'  )        ,x,pmtapeb1  )
    gr['pmhvb1']     = MakeGraph('HVPower'          ,'HV Power per module',xtitle,'P_{%s} [W]'%('HV'    )        ,x,pmhvb1    )
    gr['isb1']       = MakeGraph('SensorCurrent'    ,'Sensor current'     ,xtitle,'I_{%s} [?]'%('sensor')        ,x,isb1      )
    gr['pmhvrb1']    = MakeGraph('pmhvrb1'          ,'pmhvrb1'            ,xtitle,'P_{%s} [W]'%('?')             ,x,pmhvrb1   )
    gr['pb1']        = MakeGraph('pb1'              ,'pb1'                ,xtitle,'P_{%s} [W]'%('?')             ,x,pb1       )
    gr['phvb1']      = MakeGraph('phvb1'            ,'phvb1'              ,xtitle,'P_{%s} [W]'%('?')             ,x,phvb1     )
    gr['pmhvmuxb1']  = MakeGraph('pmhvmuxb1'        ,'pmhvmuxb1'          ,xtitle,'P_{%s} [W]'%('?')             ,x,pmhvmuxb1 )
    gr['itapeb1']    = MakeGraph('itapeb1'          ,'itapeb1'            ,xtitle,'I_{%s} [?]'%('?')             ,x,itapeb1   )
    gr['idigb1']     = MakeGraph('idigb1'           ,'idigb1'             ,xtitle,'I_{%s} [?]'%('?')             ,x,idigb1    )
    gr['efffeastb1'] = MakeGraph('efffeastb1'       ,'efffeastb1'         ,xtitle,'Efficiency [%]'               ,x,efffeastb1)
    gr['ptapeb1']    = MakeGraph('ptapeb1'          ,'ptapeb1'            ,xtitle,'P_{%s} [W]'%('?')             ,x,ptapeb1   )
    gr['pstaveb1']   = MakeGraph('pstaveb1'         ,'pstaveb1'           ,xtitle,'P_{%s} [W]'%('?')             ,x,pstaveb1  )

    outputpath = '%s/plots/SensorTemperatureCalc'%(('/').join(os.getcwd().split('/')[:-1]))
    outputtag = {
        'flat-25':'flat_m25',
        'flat-35':'flat_m35',
        'ramp-25':'ramp_m25',
        'ramp-35':'ramp_m35'
        }.get(options.cooling,'unknownScenario')

    scenariolabel = {
        'flat-25':'Flat -25#circ cooling scenario',
        'flat-35':'Flat -35#circ cooling scenario',
        'ramp-25':'Ramp -25#circ cooling scenario',
        'ramp-35':'Ramp -35#circ cooling scenario',
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

    # Kurt, put any extra plots here -- End.

    # Claire, put any extra plots here

    # Claire, put any extra plots here -- End.

    return
