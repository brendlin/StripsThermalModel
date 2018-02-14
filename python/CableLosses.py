#
# CableLosses
#
import Config
import EOSComponents

# Loss factors in cables
# in tapes (no value?)
losstype1_descr = 'Cable losses from service modules'
losstype1 = Config.GetDouble('CableLosses.losstype1',0.05,description=losstype1_descr)
lossouter_descr = 'Cable losses from PP1 to USA15'
lossouter = Config.GetDouble('CableLosses.lossouter',0.05,description=lossouter_descr)

#
# NEW cabling prescription
#
# From Alex Grillo: "There are two parameters that have changed just recently.
# Mike Dawson has re-measured the resistance of the Type I cable and the length of those cables.
# So those two parameters are now 21 mOhms/m and 2.44 m long."

descr = 'Type %d LV cable resistance per meter'

LVType1ResistancePerMeter = Config.GetDouble('CableLosses.LVType1ResistancePerMeter',0.025438,unit='$\Omega$/m',description=descr%(1))
LVType2ResistancePerMeter = Config.GetDouble('CableLosses.LVType2ResistancePerMeter',0.0148  ,unit='$\Omega$/m',description=descr%(2))
LVType3ResistancePerMeter = Config.GetDouble('CableLosses.LVType3ResistancePerMeter',0.0095  ,unit='$\Omega$/m',description=descr%(3))
LVType4ResistancePerMeter = Config.GetDouble('CableLosses.LVType4ResistancePerMeter',0.00127 ,unit='$\Omega$/m',description=descr%(4))

descr = 'Type %d LV/HV cable one-way length'

# (Have to multiply by two to get the round-trip length.)
Type1LengthOneWay = Config.GetDouble('CableLosses.Type1LengthOneWay',2.6,unit='m',description=descr%(1))
Type2LengthOneWay = Config.GetDouble('CableLosses.Type2LengthOneWay',15.,unit='m',description=descr%(2))
Type3LengthOneWay = Config.GetDouble('CableLosses.Type3LengthOneWay',32.,unit='m',description=descr%(3))
Type4LengthOneWay = Config.GetDouble('CableLosses.Type4LengthOneWay',70.,unit='m',description=descr%(4))

PP2InputVoltage = Config.GetDouble('CableLosses.PP2InputVoltage',48.0,unit='V',description='PP2 input voltage')
PP2Efficiency   = Config.GetDouble('CableLosses.PP2Efficiency'  ,0.85,unit='' ,description='PP2 Efficiency'   )
PP2HVFilterResistance = Config.GetDouble('CableLosses.PP2HVFilterResistance',100.,unit='$\Omega$' ,description='PP2 Efficiency')

PowerSuppliesEfficency = Config.GetDouble('CableLosses.PowerSuppliesEfficency',0.80,unit='',description='Power supplies efficiency')

descr = 'Type %d HV cable resistance per meter'

HVType1ResistancePerMeter = Config.GetDouble('CableLosses.HVType1ResistancePerMeter',0.213  ,unit='$\Omega$/m',description=descr%(1))
HVType2ResistancePerMeter = Config.GetDouble('CableLosses.HVType2ResistancePerMeter',0.213  ,unit='$\Omega$/m',description=descr%(2))
HVType3ResistancePerMeter = Config.GetDouble('CableLosses.HVType3ResistancePerMeter',0.139  ,unit='$\Omega$/m',description=descr%(3))
HVType4ResistancePerMeter = Config.GetDouble('CableLosses.HVType4ResistancePerMeter',0.14286,unit='$\Omega$/m',description=descr%(4))

# Vout_LV_pp2 is the return voltage to the pp2
# Ihalfsubstructure should be 'itapepetal' from ExtendedModelSummaryPlots.py
def Vout_LV_pp2(Ihalfsubstructure) :
    tmp_type12_R = (LVType1ResistancePerMeter*Type1LengthOneWay*2 + LVType2ResistancePerMeter*Type2LengthOneWay*2)
    return EOSComponents.Veos + Ihalfsubstructure * tmp_type12_R

def Ppp2_LV(Ihalfsubstructure) :
    return (1./float(PP2Efficiency) - 1.) * Ihalfsubstructure * Vout_LV_pp2(Ihalfsubstructure)

def ILVtype3andType4(Ihalfsubstructure) :
    return ( Vout_LV_pp2(Ihalfsubstructure)/float(PP2InputVoltage) ) * Ihalfsubstructure / float(PP2Efficiency)

# Factor of 2 is for half-substructure -> full substructure
def PLVservicesFullSubstructure(Ihalfsubstructure) :
    tmp_type34_R = (LVType3ResistancePerMeter*Type3LengthOneWay*2 + LVType4ResistancePerMeter*Type4LengthOneWay*2)
    return 2 * ( Ppp2_LV(Ihalfsubstructure) + (Ihalfsubstructure**2) * tmp_type12_R + (ILVtype3andType4**2) * tmp_type34_R )

# High-voltage
def DeltaVHV_halfsubstructure_Services() :
    return 0

# Power of HV services, including tape, PP2, and cables. Excluding on-module resistors.
PHV_Services = 0
