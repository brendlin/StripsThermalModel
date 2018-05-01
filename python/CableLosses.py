#
# CableLosses
#
import Config
import EOSComponents
import PlotUtils

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

# Round-trip resistance
def Resistance_LVType1and2() :
    return (LVType1ResistancePerMeter*Type1LengthOneWay*2 + LVType2ResistancePerMeter*Type2LengthOneWay*2)

# Round-trip resistance
def Resistance_LVType3and4() :
    return (LVType3ResistancePerMeter*Type3LengthOneWay*2 + LVType4ResistancePerMeter*Type4LengthOneWay*2)

# Vout_LV_pp2 is the return voltage to the pp2
# Ihalfsubstructure should be 'itapepetal' from ExtendedModelSummaryPlots.py
# vdrop_tape_r5 should be the vdrop_tape from R5 (which includes VfeastMin)
def Vout_LV_pp2(Ihalfsubstructure,vdrop_tape_r5) :
    return vdrop_tape_r5 + Ihalfsubstructure * Resistance_LVType1and2()

# "Round trip voltage drop" meaning due to the Type 1 and Type 2 cables
def VdropLV_RoundTrip_type1and2(Ihalfsubstructure) :
    return Ihalfsubstructure * Resistance_LVType1and2()

def Ppp2_LV(Ihalfsubstructure,vdrop_tape_r5) :
    return (1./float(PP2Efficiency) - 1.) * Ihalfsubstructure * Vout_LV_pp2(Ihalfsubstructure,vdrop_tape_r5)

def ILVtype3andType4(Ihalfsubstructure,vdrop_tape_r5) :
    return ( Vout_LV_pp2(Ihalfsubstructure,vdrop_tape_r5)/float(PP2InputVoltage) ) * Ihalfsubstructure / float(PP2Efficiency)

def PlossLVCablesType1and2(Ihalfsubstructure) :
    return (Ihalfsubstructure**2) * Resistance_LVType1and2()

def PlossLVCablesType3and4(Ihalfsubstructure,vdrop_tape_r5) :
    return (ILVtype3andType4(Ihalfsubstructure,vdrop_tape_r5)**2) * Resistance_LVType3and4()

# Factor of 2 is for half-substructure -> full substructure
def PLVservicesFullSubstructure(Ihalfsubstructure,vdrop_tape_r5) :
    return 2 * ( Ppp2_LV(Ihalfsubstructure,vdrop_tape_r5) + PlossLVCablesType1and2(Ihalfsubstructure) + PlossLVCablesType3and4(Ihalfsubstructure,vdrop_tape_r5) )

#
# High-voltage
#

# Barrel: Tape resistance calculated for the longest HV trace: 8.3 Ohms (SS), 8.3 Ohms (LS)
RHVtape = 0 # Get from Graham?
RHV = 0 # This is the series resistor! Fix!

def Resistance_HVType1and2() :
    return (HVType1ResistancePerMeter*Type1LengthOneWay*2 + HVType2ResistancePerMeter*Type2LengthOneWay*2)

def Resistance_HVType3and4() :
    return (HVType3ResistancePerMeter*Type3LengthOneWay*2 + HVType4ResistancePerMeter*Type4LengthOneWay*2)

# Type I and II HV current
# separate HV lines will serve modules: R5, R4, R3 and R2, and R1 and R0.
# Millivolts!
def iSensors_HV_Type1Type2PP2_Petal(names,ring,disk,result_dicts,itime) :

    isensors = 0

    if ring in [0,1] :

        for iring in [0,1] :
            index = PlotUtils.GetResultDictIndex(names,iring,disk)
            isensors += result_dicts[index]['isensor'].GetY()[itime]

    if ring in [2,3] :

        for iring in [2,3] :
            index = PlotUtils.GetResultDictIndex(names,iring,disk)
            isensors += result_dicts[index]['isensor'].GetY()[itime]

    if ring in [4,5] :

        index = PlotUtils.GetResultDictIndex(names,ring,disk)
        isensors += result_dicts[index]['isensor'].GetY()[itime]

    return isensors

# Type III and IV HV current
# For now assume that the multiplexing is the same as in Type1Type2PP2
# Millivolts!
def iSensors_HV_Type3Type4_Petal(names,ring,disk,result_dicts,itime) :

    isensors = 0

    if ring in [0,1,2,3] :

        for iring in [0,1,2,3] :
            index = PlotUtils.GetResultDictIndex(names,iring,disk)
            isensors += result_dicts[index]['isensor'].GetY()[itime]

    if ring in [4,5] :

        for iring in [4,5] :
            index = PlotUtils.GetResultDictIndex(names,iring,disk)
            isensors += result_dicts[index]['isensor'].GetY()[itime]

    return isensors

# HV Delta V for a given module, from PP2 (including PP2) to just before the sensor.
# Separate HV lines will serve modules: R5, R4, R3 and R2, and R1 and R0.
# RHV will need to be taken separately from the module, for each module.
def DeltaVHV_halfsubstructure_Type1Type2PP2(names,ring,disk,result_dicts,itime) :

    # current in type-I/II-multiplexed cables
    isensors_type12 = 0.001 * iSensors_HV_Type1Type2PP2_Petal(names,ring,disk,result_dicts,itime)

    return isensors_type12 * (RHVtape + Resistance_HVType1and2() + PP2HVFilterResistance )


# HV Delta V for a given module, PP4 to just before PP2
def DeltaVHV_halfsubstructure_Type3Type4(names,ring,disk,result_dicts,itime) :

    # current in type-I/II-multiplexed cables
    isensors_type34 = 0.001 * iSensors_HV_Type3Type4_Petal(names,ring,disk,result_dicts,itime)

    return isensors_type34 * Resistance_HVType3and4()


# For power calculations
def SumCurrentSquared_Type1Type2(names,disk,result_dicts,itime) :
    # Sum(i^2)
    sumi2 = 0

    # (0,1), (2,3), (4), (5) Type1Type2PP2 multiplexing
    for ring in [0,2,4,5] :
        itmp = 0.001 * iSensors_HV_Type1Type2PP2_Petal(names,ring,disk,result_dicts,itime)
        sumi2 += (itmp*itmp)

    return sumi2


def SumCurrentSquared_Type3Type4(names,disk,result_dicts,itime) :
    # Sum(i^2)
    sumi2 = 0

    # (0,1,2,3), (4,5) multiplexing for Type3Type4
    for ring in [0,4] :
        itmp = 0.001 * iSensors_HV_Type3Type4_Petal(names,ring,disk,result_dicts,itime)
        sumi2 += (itmp*itmp)

    return sumi2


def PtapeHV(names,disk,result_dicts,itime) :
    return 0

def Ppp2_HV(names,disk,result_dicts,itime) :
    return PP2HVFilterResistance * SumCurrentSquared_Type1Type2(names,disk,result_dicts,itime)

def PlossHVCablesType1and2(names,disk,result_dicts,itime) :
    return Resistance_HVType1and2() * SumCurrentSquared_Type1Type2(names,disk,result_dicts,itime)

def PlossHVCablesType3and4(names,disk,result_dicts,itime) :
    return Resistance_HVType3and4() * SumCurrentSquared_Type3Type4(names,disk,result_dicts,itime)

# Power of HV services, including tape, PP2, and cables. Excluding on-module resistors.
def PHVservicesFullPetal(names,disk,result_dicts,itime) :
    output = 0
    output += PtapeHV(names,disk,result_dicts,itime)
    output += PlossHVCablesType1and2(names,disk,result_dicts,itime)
    output += Ppp2_HV(names,disk,result_dicts,itime)
    output += PlossHVCablesType3and4(names,disk,result_dicts,itime)

    # Extra factor of 2 for two halves of the petal
    return 2 * output
