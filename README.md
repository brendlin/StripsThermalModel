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
2. Layout                    |                                                  | Claire     |
3. PoweringEfficiency        | FEAST efficiency, DCDC2 efficiency               | Kurt *     | Done
4. CableLosses               |                                                  | Claire     |
(4.) FrontEndComponents      | Front-end components, before irradiation         | (Claire)   |
5. EOSComponents             | lpbt, gbtia, gbld (before irradiation)           | Kurt       | Done
6. AbcTidBump                | Increase in digital current in ABC               | Claire *   |
7. SensorProperties          | Sensor area, bias volate, resistors              | Kurt       | Done
8. NominalPower              |                                                  | Claire *   | In Progress
9. ThermalImpedances         | Fit for impedances (R) given simulated points    | Kurt *     | Done
10. Temperatures             |                                                  | Claire     | In Progress
11. OperationalProfiles      | Luminosity (inst, int), efficiency (?)           | Kurt *     | Done
12. SensorLeakage            | Leakage current as a function of flux (A/cm^2)   | Claire *   | In Progress
13. SensorTemperatureCalc    | Sensor temperature calculation                   | (Both)     |

Simple numbers that need to be switched from barrel to endcap values:
-----
 - **Fluences/Total ionizing dose for the petal**. Later, extend this to include dependence on eta and
radius (or equivalent parameterization).
 - (more...)

Data / fits that we need
-----
 - **FEAST efficiency** (vs temperature, current): Georg et al have an initial fit based on some data,
but the fit could be improved and more precise data could be pushed for.
 - **Thermal impedances**: These are currently based on thermal simulations from the the barrel, and
need to be rederived using endcap thermal simulations.


Other info
-----
 - Data files are kept in the "data" directory -- an example of the format is FeastEfficiencyData.txt.


Mathematica-to-python Quick-guide
-----
 - "./x -> y" means replace all "x" with "y"
 - "x[y_] := 2y": set delay, evaluated at call. Python analog: def x(y) : return 2y
 - "x = 2y": set, meaning x is set immediately to 2y, whatever y is at the time. Python analog: x = 2y
