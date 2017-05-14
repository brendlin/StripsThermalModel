#
# SensorTemperatureCalc
#
import GlobalSettings
import Temperatures
import NominalPower

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

    defTeos = Temperatures.ssTeos( NominalPower.sseosP(nomT),
                                   NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] )
    defTabc = Temperatures.ssTabc( NominalPower.ssPabc(nomT, 1, 0),
                                   NominalPower.sseosP(nomT),
                                   NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] )
    defThcc = Temperatures.ssThcc( NominalPower.ssPhcc(nomT, 1, 0), NominalPower.sseosP(nomT),
                                   NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                   0, tc[0] )
    defTfeast = Temperatures.ssTfeast( NominalPower.ssPfeast(nomT, nomT, nomT, 1, 0),
                                       NominalPower.sseosP(nomT),
                                       NominalPower.ssPmod(nomT, nomT, nomT, 1, 0, 0),
                                       0, tc[0] )

    # (*calculate temperatures, powers etc.*)
    # For[i = 1, i <= nstep, i++,
    #  sol = FindInstance[
    #    (*solve for qref (with 2 solutions)*)

    #    qrefb1[[i]] == 
    #     Qref[ts, 
    #      ssT0[sseosP[If[i == 1, defTeos, teosb1[[i - 1]]]], 
    #       ssPmod[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #        If[i == 1, defThcc, thccb1[[i - 1]]], 
    #        If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #        tidb1[[i]], unref[qrefb1[[i]], ts]/vbias], tc[[i]]]],
    #    ts, Reals, 2];
    #  resultts = ts /. sol;(*Print[i,resultts]*);
    #  (*select correct solution*) 
    #  If[Length[resultts] == 1, index = 1, 
    #   If[resultts[[1]] > resultts[[2]], index = 2, index = 1]];
    #  (*calculate temperatures in the system based on sensor temperature*)
    # \
    #  (*sensor temperature*)tsb1 = Append[tsb1, resultts[[index]]];
    #  (*temperature of ABC*)
    #  tabcb1 = Append[tabcb1, 
    #    ssTabc[ssPabc[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      doserateb1[[i]], tidb1[[i]]], 
    #     sseosP[If[i == 1, defTeos, teosb1[[i - 1]]]], 
    #     ssPmod[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #      tidb1[[i]], unref[qrefb1[[i]], resultts[[index]]]/vbias], 
    #     unref[qrefb1[[i]], resultts[[index]]], tc[[i]]]];
    #  (*temperature of HCC*)

    #  thccb1 = Append[thccb1, 
    #    ssThcc[ssPhcc[If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      doserateb1[[i]], tidb1[[i]]], 
    #     sseosP[If[i == 1, defTeos, teosb1[[i - 1]]]], 
    #     ssPmod[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #      tidb1[[i]], unref[qrefb1[[i]], resultts[[index]]]/vbias], 
    #     unref[qrefb1[[i]], resultts[[index]]], tc[[i]]]];
    #  (*temperature of FEAST*)

    #  tfeastb1 = 
    #   Append[tfeastb1, 
    #    ssTfeast[
    #     ssPfeast[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #      tidb1[[i]]], sseosP[If[i == 1, defTeos, teosb1[[i - 1]]]], 
    #     ssPmod[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #      tidb1[[i]], unref[qrefb1[[i]], resultts[[index]]]/vbias], 
    #     unref[qrefb1[[i]], resultts[[index]]], tc[[i]]]];
    #  (*temperature of EOS*)

    #  teosb1 = Append[teosb1, 
    #    ssTeos[sseosP[If[i == 1, defTeos, teosb1[[i - 1]]]], 
    #     ssPmod[If[i == 1, defTabc, tabcb1[[i - 1]]], 
    #      If[i == 1, defThcc, thccb1[[i - 1]]], 
    #      If[i == 1, defTfeast, tfeastb1[[i - 1]]], doserateb1[[i]], 
    #      tidb1[[i]], unref[qrefb1[[i]], resultts[[index]]]/vbias], 
    #     unref[qrefb1[[i]], resultts[[index]]], tc[[i]]]];
    #  (*from here we can use actual temperatures*)
    #  (*power per module \
    # (front-end + HV)*)

    #  pmoduleb1 = 
    #   Append[pmoduleb1, 
    #    ssPmod[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], doserateb1[[i]], 
    #      tidb1[[i]], unref[qrefb1[[i]], tsb1[[i]]]/vbias] + 
    #     unref[qrefb1[[i]], tsb1[[i]]]];
    #  (*power in tape per module*)

    #  pmtapeb1 = 
    #   Append[pmtapeb1, 
    #    ssPtape[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], doserateb1[[i]], 
    #     tidb1[[i]]]];
    #  (*HV power per module (leakage + resistors*)

    #  pmhvb1 = Append[pmhvb1, 
    #    unref[qrefb1[[i]], tsb1[[i]]] + 
    #     Phv[unref[qrefb1[[i]], tsb1[[i]]]/vbias]];
    #  (*leakage current per module*)

    #  isb1 = Append[isb1, unref[qrefb1[[i]], tsb1[[i]]]/vbias];
    #  (*HV power per module due to serial resistors*)

    #  pmhvrb1 = 
    #   Append[pmhvrb1, Prhv[unref[qrefb1[[i]], tsb1[[i]]]/vbias]];
    #  (*HV per module due to parallel resistor*)

    #  pmhvmuxb1 = Append[pmhvmuxb1, Phvmux];
    #  (*stave power B1*)

    #  pstaveb1 = 
    #   Append[pstaveb1, 
    #    ssPstave[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], teosb1[[i]], 
    #     doserateb1[[i]], tidb1[[i]], unref[qrefb1[[i]], tsb1[[i]]]/vbias]];
    #  (*total power for B1*)

    #  pb1 = Append[pb1, 
    #    2*nstavesb1*(1 + safetylayout)/1000*
    #     ssPstave[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], teosb1[[i]], 
    #      doserateb1[[i]], tidb1[[i]], 
    #      unref[qrefb1[[i]], tsb1[[i]]]/vbias]];
    #  (*total HV power for B1*)

    #  phvb1 = Append[phvb1, 
    #    2*nstavesb1*(1 + safetylayout)/1000*2*
    #     nmod*(pmhvb1[[i]] + pmhvrb1[[i]])];
    #  (*tape current per module*)

    #  itapeb1 = 
    #   Append[itapeb1, 
    #    ssItape[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], doserateb1[[i]], 
    #     tidb1[[i]]]];
    #  (*tape power for one tape (half a stave)*)

    #  ptapeb1 = 
    #   Append[ptapeb1, 
    #    ssPstavetape[tabcb1[[i]], thccb1[[i]], tfeastb1[[i]], 
    #     doserateb1[[i]], tidb1[[i]]]];
    #  (*digital current per module*)

    #  idigb1 = Append[idigb1, 
    #    ssIdig[tabcb1[[i]], thccb1[[i]], doserateb1[[i]], tidb1[[i]]]];
    #  (*FEAST efficiency*)

    #  efffeastb1 = 
    #   Append[efffeastb1, 
    #    feasteff[tfeastb1[[i]], 
    #     ssIfeast[tabcb1[[i]], thccb1[[i]], doserateb1[[i]], 
    #      tidb1[[i]]]]];
    #  (*done*)

    #  If[i*step == IntegerPart[i*step], 
    #   Print["calculated year ", i*step]];
    #  ]
