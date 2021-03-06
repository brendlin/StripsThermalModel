ITK Cooling Scheme
========================
This is an analytical model of the thermal model, based off of the analytical barrel model from
Georg Viehhauser.

More information is available in the twiki https://wiki-zeuthen.desy.de/ATLAS/ThermalModelForPetal

Checking Out and Running
--------
To checkout, do:

    git clone ssh://git@gitlab.cern.ch:7999/desy-atlas/itk/StripsThermalModel.git

To run, do :

    cd macros
    python RunModel.py --cooling -35

Submodules
--------
The following submodules are defined in the python directory (modules with a * are fairly large) :

Submodules                   | Purpose                                          | Assignee   | Status
-----------------------------|--------------------------------------------------|------------|------------
0. GlobalSettings            | Settings for the analysis: nyears, nstep, step.. | Kurt       | Done
1. SafetyFactors             | for layout, fluence, thermal impedance, I, vbias | Kurt       | Done
2. Layout                    | Number of staves per end                         | Claire     | Done
3. PoweringEfficiency        | FEAST efficiency, DCDC2 efficiency               | Kurt *     | Done
4. CableLosses               | Service modules and outer cables                 | Claire     | Done
(4.) FrontEndComponents      | Front-end components, before irradiation         | (Claire)   | Done
5. EOSComponents             | lpbt, gbtia, gbld (before irradiation)           | Kurt       | Done
6. AbcTidBump                | Increase in digital current in ABC               | Claire *   | Done
7. SensorProperties          | Sensor area, bias volate, resistors              | Kurt       | Done
8. NominalPower              | Expressions for the power in each element        | Claire *   | Done
9. ThermalImpedances         | Fit for impedances (R) given simulated points    | Kurt *     | Done
10. Temperatures             | Activation, barrel LS and SS                     | Claire     | Done
11. OperationalProfiles      | Luminosity (inst, int), efficiency (?)           | Kurt *     | Done
12. SensorLeakage            | Leakage current as a function of flux (A/cm^2)   | Claire *   | Done
13. SensorTemperatureCalc    | Sensor temperature calculation                   | (Both)     | Done, debugged w/B1

Plotting/Checks/Investigations
-----------
Topic                        | Purpose                                          | Assignee   | Status
-----------------------------|--------------------------------------------------|------------|------------
Sensor power                 | Plotting to check correct implementation         | Claire     | Done plotting
TID bump                     | Plot to check and investigate the modelling      | Claire     | Done plotting
Feast efficiency             | Plot to check and investigate the modelling      | Kurt       | Done
Operating profiles           | Reproducing plots from Graham and Georg          | Kurt       | Done
SensorTemperatureCalc tsensor    | Sensor temperature                           | Kurt       | Done
SensorTemperatureCalc tabc       | ABC temperature                              | Kurt       | Done
SensorTemperatureCalc thcc       | HCC temperature                              | Kurt       | Done
SensorTemperatureCalc tfeast     | FEAST temperature                            | Kurt       | Done
SensorTemperatureCalc teos       | EOS temperature                              | Kurt       | Done
SensorTemperatureCalc pmodule    | Power per module (front-end + HV)            | Kurt       | Done
SensorTemperatureCalc pmtape     | Power loss in tape per module                | Kurt       | Done
SensorTemperatureCalc pmhv       | HV power per module (leakage + resistors)    | Kurt       | Done
SensorTemperatureCalc isensor    | Sensor current                               | Kurt       | Done
SensorTemperatureCalc pmhvr      | HV power per module due to serial resistors  | Kurt       | Done
SensorTemperatureCalc powertotal | Total power in layer                         | Kurt       | Done
SensorTemperatureCalc phvtotal   | Total HV Power (sensor+resistors) in layer   | Kurt       | Done
SensorTemperatureCalc pmhvmux    | HV Power parallel resistor                   | Kurt       | Done
SensorTemperatureCalc itape      | Tape current per module                      | Kurt       | Done
SensorTemperatureCalc idig       | Digital current per module                   | Kurt       | Done
SensorTemperatureCalc efffeast   | FEAST efficiency                             | Kurt       | Done
SensorTemperatureCalc ptape      | Power loss in complete tape in layer         | Kurt       | Done
SensorTemperatureCalc pstave     | Stave Power in layer                         | Kurt       | Done

More plots -- plotting and debugging (focus on flat-35 scenario)
-----------
Topic                                 | Notes                                                                              | Assignee   | Status
--------------------------------------|------------------------------------------------------------------------------------|------------|------------
Sensor temperature                    | p. 11 in https://indico.cern.ch/event/625365                                       | Kurt       | Done, debugged
Power summary plot                    | p. 11 of slides; total power, w/o HV, w/o tape loss                                | Kurt       | Done, debugged
Total HV power per module             | p. 11 of slides                                                                    | Kurt       | Done, debugged
Temperature summary of all components | p. 12 of slides                                                                    | Kurt       | Done, debugged
Total power in B1                     | p. 12 of slides                                                                    | Kurt       | Done, debugged

Simple numbers that need to be switched from barrel to endcap values:
-----
 - **Fluences/Total ionizing dose for the petal**. Later, extend this to include dependence on eta and
radius (or equivalent parameterization).
 - **Layout**: change the number of staves with the different petal sensors..

Data / fits that we need
-----
 - **FEAST efficiency** (vs temperature, current): Georg et al have an initial fit based on some data,
but the fit could be improved and more precise data could be pushed for.
 - **Thermal impedances**: These are currently based on thermal simulations from the the barrel, and
need to be rederived using endcap thermal simulations.
 - **Losses**: no value for losses in tapes? 

Questions
-----
 - **Sensor leakage**: line 28 
 - Document (v2.1): Eq. 15a has I instead of I^2 ?
 - **Operational profiles**: Figures 11 and 12 of report v2.3 are not matching associated plots in Mathematica file
(Section 11) E.g. second plateau Year 8 of B1 is around 15000 kRad in the document, but 20000 kRad in Mathematica's plot.
Was there an update in between? 


Other info
-----
 - Data files are kept in the "data" directory -- an example of the format is FeastEfficiencyData.txt.


Mathematica-to-python Quick-guide
-----
 - "./x -> y" means replace all "x" with "y"
 - "x[y_] := 2y": set delay, evaluated at call. Python analog: def x(y) : return 2y
 - "x = 2y": set, meaning x is set immediately to 2y, whatever y is at the time. Python analog: x = 2y
 - Log in mathematica is natural logarithm (base e)
