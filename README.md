ITK Cooling Scheme
========================

To checkout, do:

    git clone ssh://git@gitlab.cern.ch:7999/desy-atlas/itk/StripsThermalModel.git

To run, do :

    cd macros
    python RunModel.py --cooling -35

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
8. NominalPower              |                                                  | Claire *   |
9. ThermalImpedances         | Fit for impedances (R) given simulated points    | Kurt *     | Done
10. Temperatures             |                                                  | Claire     |
11. OperationalProfiles      | Luminosity (inst, int), efficiency (?)           | Kurt *     | Done
12. SensorLeakage            |                                                  | Claire *   |
13. SensorTemperatureCalc    | Sensor temperature calculation                   | (Both)     |

Other info
-----
 - Data files are kept in the "data" directory -- an example of the format is FeastEfficiencyData.txt.
