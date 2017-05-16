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

import ROOT
import math

# Barrel I

def CalculateSensorTemperature(tc) :

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

        lhs = SensorLeakage.qrefb1[i]
        ts = 1 # dummy
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

#     f = ROOT.TF1("mine", "x*x - x", -10, 0.5 )
#     wf = ROOT.Math.WrappedTF1(f)
#     brf = ROOT.Math.BrentRootFinder()
#     brf.SetFunction( wf, -10, 0.5 )
#     brf.Solve()
#     print 'Root:',brf.Root()

        # (Dummy ts result)
        resultts = 1

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

        #
        # From here we can use actual temperatures
        #

        # Power per module (front-end + HV)
        pmoduleb1.append(NominalPower.ssPmod(tabcb1[-1],
                                             thccb1[-1],
                                             tfeastb1[-1],
                                             OperationalProfiles.doserateb1[i],
                                             OperationalProfiles.tidb1[i],
                                             Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias)
                                             + Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])
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
        pmhvb1.append(Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])
                      + NominalPower.Phv( Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias) )
                      )

        # Leakage current per module
        isb1.append( Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias) )

        # HV power per module due to serial resistors
        pmhvrb1.append( NominalPower.Prhv( Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias) ) )

        # HV per module due to parallel resistor
        pmhvmuxb1.append(NominalPower.Phvmux)

        # Stave power B1
        pstaveb1.append(NominalPower.ssPstave(tabcb1[-1],
                                              thccb1[-1],
                                              tfeastb1[-1],
                                              teosb1[-1],
                                              OperationalProfiles.doserateb1[i],
                                              OperationalProfiles.tidb1[i],
                                              Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias)
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
                                            Temperatures.unref(SensorLeakage.qrefb1[i],tsb1[-1])/float(SensorProperties.vbias)
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

    return
