ITK Cooling Scheme
========================

To checkout, do:

 - git clone ssh://git@gitlab.cern.ch:7999/desy-atlas/itk/StripsThermalModel.git

To run, do :

 - cd macros
 - python RunModel.py --cooling -35


--------
The following submodules are defined in the python directory:

Submodules                                                        | Purpose                      | Assignee
------------------------------------------------------------------| ---------------------------- | ---------------------------------------
1. SafetyFactors             | Blah                                     | Kurt
2. Layout                    | Blah                                     | Claire
3. PoweringEfficiency        | FEAST efficiency, DCDC2 efficiency       | Kurt *
4. CableLosses               |                                          | Claire
(4.) FrontEndComponents      | Front-end components, before irradiation | (Claire)
5. EOSComponents             | (before irradiation)                     | Kurt
6. AbcTidBump                | Increase in digital current in ABC       | Claire *
7. SensorProperties          |                                          | Kurt
8. NominalPower              |                                          | Claire *
9. ThermalImpedances         |                                          | Kurt *
10. Temperatures             |                                          | Claire
11. OperationalProfiles      |                                          | Kurt *
12. SensorLeakage            |                                          | Claire *
13. SensorTemperatureCalc    | Sensor temperature calculation           | (Both)

Other info
-----

