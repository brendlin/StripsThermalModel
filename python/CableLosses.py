#
# CableLosses
#
import Config
import EOSComponents
import PlotUtils

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

def Resistance_LVType1and2() :
    return (LVType1ResistancePerMeter*Type1LengthOneWay*2 + LVType2ResistancePerMeter*Type2LengthOneWay*2)

def Resistance_LVType3and4() :
    return (LVType3ResistancePerMeter*Type3LengthOneWay*2 + LVType4ResistancePerMeter*Type4LengthOneWay*2)

# Vout_LV_pp2 is the return voltage to the pp2
# Ihalfsubstructure should be 'itapepetal' from ExtendedModelSummaryPlots.py
def Vout_LV_pp2(Ihalfsubstructure) :
    return EOSComponents.Veos + Ihalfsubstructure * Resistance_LVType1and2()

# "Round trip voltage drop"
def Vdrop_RoundTrip_type1and2(Ihalfsubstructure) :
    return Ihalfsubstructure * Resistance_LVType1and2()

def Ppp2_LV(Ihalfsubstructure) :
    return (1./float(PP2Efficiency) - 1.) * Ihalfsubstructure * Vout_LV_pp2(Ihalfsubstructure)

def ILVtype3andType4(Ihalfsubstructure) :
    return ( Vout_LV_pp2(Ihalfsubstructure)/float(PP2InputVoltage) ) * Ihalfsubstructure / float(PP2Efficiency)

def PlossCables(Ihalfsubstructure) :
    return (Ihalfsubstructure**2) * Resistance_LVType1and2() + (ILVtype3andType4(Ihalfsubstructure)**2) * Resistance_LVType3and4()

# Factor of 2 is for half-substructure -> full substructure
def PLVservicesFullSubstructure(Ihalfsubstructure) :
    return 2 * ( Ppp2_LV(Ihalfsubstructure) + PlossCables(Ihalfsubstructure) )

#
# High-voltage
#

RHVtape = 0 # Get from Graham?
RHV = 0 # What is this?

def Resistance_HVType1and2() :
    return (HVType1ResistancePerMeter*Type1LengthOneWay*2 + HVType2ResistancePerMeter*Type2LengthOneWay*2)

def Resistance_HVType3and4() :
    return (HVType3ResistancePerMeter*Type3LengthOneWay*2 + HVType4ResistancePerMeter*Type4LengthOneWay*2)

# separate HV lines will serve modules: R5, R4, R3 and R2, and R1 and R0.
def iSensors_HV_Type1Type2PP2_Petal(names,ring,disk,result_dicts,itime) :
    index = PlotUtils.GetResultDictIndex(names,ring,disk)
    isensors = result_dicts[index]['isensor'].GetY()[itime]

    if (ring == 0) or (ring == 2) :
        index = PlotUtils.GetResultDictIndex(names,ring+1,disk)
        isensors += result_dicts[index]['isensor'].GetY()[itime]

    if (ring == 1) or (ring == 3) :
        index = PlotUtils.GetResultDictIndex(names,ring-1,disk)
        isensors += result_dicts[index]['isensor'].GetY()[itime]

    return isensors

# For now assume that the multiplexing is the same as in Type1Type2PP2
def iSensors_HV_Type3Type4_Petal(names,ring,disk,result_dicts,itime) :
    return iSensors_HV_Type1Type2PP2_Petal(names,ring,disk,result_dicts,itime)

# separate HV lines will serve modules: R5, R4, R3 and R2, and R1 and R0.
# RHV is related to the EOS somehow... ?
def DeltaVHV_halfsubstructure_Type1Type2PP2(isensors_type12) :
    return isensors_type12 * (RHVtape + Resistance_HVType1and2() + PP2HVFilterResistance )

def DeltaVHV_halfsubstructure_Type3Type4(isensors_type34) :
    return isensors_type34 * Resistance_HVType3and4()

# Power of HV services, including tape, PP2, and cables. Excluding on-module resistors.
PHVservicesFullPetal = 0
