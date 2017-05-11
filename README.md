ITK Cooling Scheme
========================

To checkout, do:

    git clone ssh://git@gitlab.cern.ch:7999/desy-atlas/itk/StripsThermalModel.git

To run, do :

    cd macros
    python RunModel.py --cooling -35


--------
The following submodules are defined in the python directory (modules with a * are fairly large) :

Submodules                   | Purpose                                  | Assignee   | Status
-----------------------------|------------------------------------------|------------|----------------------------------------
1. SafetyFactors             | Blah                                     | Kurt       | Done
2. Layout                    | Blah                                     | Claire     |
3. PoweringEfficiency        | FEAST efficiency, DCDC2 efficiency       | Kurt *     | In Progress
4. CableLosses               |                                          | Claire     |
(4.) FrontEndComponents      | Front-end components, before irradiation | (Claire)   |
5. EOSComponents             | (before irradiation)                     | Kurt       | Done
6. AbcTidBump                | Increase in digital current in ABC       | Claire *   |
7. SensorProperties          |                                          | Kurt       | Done
8. NominalPower              |                                          | Claire *   |
9. ThermalImpedances         |                                          | Kurt *     |
10. Temperatures             |                                          | Claire     |
11. OperationalProfiles      |                                          | Kurt *     |
12. SensorLeakage            |                                          | Claire *   |
13. SensorTemperatureCalc    | Sensor temperature calculation           | (Both)     |

Other info
-----

