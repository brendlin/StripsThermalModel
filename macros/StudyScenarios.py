#!/usr/bin/env python

import os,sys
import re
import ROOT
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PlotUtils as PlotUtils
import python.TableUtils as TableUtils

if len(sys.argv) < 2 :
    print 'Usage: python StudyScenarios.py Wildcard'
    sys.exit()

wildcard = sys.argv[1]

options = None
inputpath  = PlotUtils.GetOutputPath('',options)
outputpath = PlotUtils.GetOutputPath(wildcard,options)

all_results = dict()
all_configs = dict()

def StringWithNSigFigs(the_float,nsigfig) :
    the_string = '%.*g'%(nsigfig,the_float)
    n = 1
    while len(the_string.lstrip('0').replace('.','')) < nsigfig :
        the_string = '%.*f'%(n,the_float)
        n += 1
    return the_string

scenarios = []
for s in os.listdir(inputpath) :
    if 'ExtendedModelEndcap' not in s :
        continue
    if wildcard not in s :
        continue
    scenarios.append(s)

# Want to explore ordering for solving sensor headroom issue
ordering = [
    'No_Safety',
    'Base_assumptionsPreIrrad',
    'BasePlusBumpASICThermalPreIrrad',
    'Base_assumptions',
    'BasePlusBumpParam',
    'BasePlusASIC',
    'BasePlusBias',
    'BasePlusThermal',
    'BasePlusBumpASICThermal',
    ]

for i in reversed(ordering) :
    scenarios.sort(key = lambda x: (i+'_' not in x))
for i in reversed(['_newramp_m35','flat_m35','flat_m30','flat_m25','flat_m20','flat_m15','_ramp_m35']) :
    scenarios.sort(key = lambda x: (i not in x))

# different ordering (used for "two main scenarios")
scenarios_o2 = list(a for a in scenarios)
for i in reversed(ordering) :
    scenarios_o2.sort(key = lambda x: (i+'_' not in x))

two_main_scenarios = []
find_two_main_scenarios = ['Base_assumptions','BasePlusBumpASICThermal']
#find_two_main_scenarios = ['No_Safety_','blah']
#find_two_main_scenarios = ['BasePlusBumpASICThermalBias_','blah']
#find_two_main_scenarios = ['BasePlusASICThermalBias','BasePlusBumpASICThermal']
for scenario in scenarios_o2 :
    print scenario
    if find_two_main_scenarios[0] in scenario :
        two_main_scenarios.append(scenario)
    if find_two_main_scenarios[1] in scenario :
        two_main_scenarios.append(scenario)

    # Load the saved numpy dictionary
    import numpy as np
    all_results[scenario] = np.load('%s/%s/Results.npy'%(inputpath,scenario), allow_pickle=True)
    all_configs[scenario] = np.load('%s/%s/Config.npy'%(inputpath,scenario),  allow_pickle=True).item()

if len(two_main_scenarios) < 2 :
    print 'Need the two main scenarios'
    sys.exit()

structure_names = []
for ring in range(6) :
    for disk in range(6) :
        structure_names.append('R%dD%d'%(ring,disk))

# output file
f = open('%s/Scenarios.txt'%(outputpath),'w')
f.write('\def\\arraystretch{1.05}\n')

def GetSixScenarioParamters(a_list) :
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.safetyfluence',''))
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.safetythermalimpedance',''))
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.safetycurrentd',''))
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.safetycurrenta',''))
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.TIDpessimistic','False'))
    a_list.append(all_configs[scenario].GetValue('OperationalProfiles.PreIrradiation','')+' MRad')
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.vbias',''))
    cooling = all_configs[scenario].GetValue('cooling','')
    if 'flat' in cooling :
        cooling = cooling.replace('flat','').replace('-','$-$')+' flat'
    elif 'newramp' in cooling :
        cooling = cooling.replace('newramp','').replace('-','$-$')+' newramp'
    elif 'ramp' in cooling :
        cooling = cooling.replace('ramp','').replace('-','$-$')+' ramp'
    a_list.append(cooling)
    return

#
# Automate hlines
#
hlines = [0]
scenario_last = scenarios[0]
for s,scenario in enumerate(scenarios) :
    cooling      = all_configs[scenario     ].GetValue('cooling','')
    cooling_last = all_configs[scenario_last].GetValue('cooling','')
    if cooling != cooling_last :
        hlines.append(s)
    scenario_last = scenario

def MaxTuple(tuple1,tuple2) :
    return sorted([tuple1,tuple2],key=lambda x: x[0],reverse=True)[0]

def MinTuple(tuple1,tuple2) :
    return sorted([tuple1,tuple2],key=lambda x: x[0],reverse=False)[0]


#
# Make Calculations for summary tables
#
for scenario in scenarios :
    tmp_dict = all_results[scenario][0]

    runaway = False
    if tmp_dict['thermal_runaway_yeartotal'] :
        RunawayText = '{\\bf Y%d}'%(tmp_dict['thermal_runaway_yeartotal'])
        runaway = True

    #
    # Calculate maximum total value (input to tables)
    #
    for quantity_name in ['pnoservices','pcoolingsys','pwallpower','pservice','phv_wleakage',
                          'plosslvcablest1','plosslvcablest2','plosslvcablest3','plosslvcablest4','plosslvpp2','plosslvPS'] :
        if runaway :
            tmp_dict['%s_maxTotal_str'%(quantity_name)] = RunawayText
            tmp_dict['%s_minTotal_str'%(quantity_name)] = RunawayText
            continue
        nstep = tmp_dict[quantity_name+'total'].GetN()

        # Find the maximum value AND store the index of this max.
        max_i,maxval = -1,-1
        for i in range(nstep) :
            tmp_val = tmp_dict[quantity_name+'total'].GetY()[i]
            if tmp_val > maxval :
                max_i,maxval = i,tmp_val

        minval = min(list(tmp_dict[quantity_name+'total'].GetY()[i] for i in range(nstep)))

        if quantity_name in ['pmodule','pnoservices','pcoolingsys','pwallpower','pservice','phv_wleakage',
                             'plosslvcablest1','plosslvcablest2','plosslvcablest3','plosslvcablest4','plosslvpp2','plosslvPS',
                             ] :
            maxval = maxval/1000.
            minval = minval/1000.

        tmp_dict['%s_maxTotal_str'%(quantity_name)] = StringWithNSigFigs(maxval,3)
        tmp_dict['%s_maxTotal_index'%(quantity_name)] = max_i
        tmp_dict['%s_maxTotal_index_str'%(quantity_name)] = '%d (y%d, m%d)'%(max_i,max_i/12,max_i%12)
        tmp_dict['%s_minTotal_str'%(quantity_name)] = StringWithNSigFigs(minval,3)

    #
    # Minimum / Maximum Module Value
    #
    for quantity_name in ['tfeast','isensor','qsensor_headroom','tsensor','tc_headroom','deltavhvservices'] :
        if runaway :
            tmp_dict['%s_minModule_str'%(quantity_name)] = (RunawayText,'')
            tmp_dict['%s_maxModule_str'%(quantity_name)] = (RunawayText,'')
            tmp_dict['%s_maxModuleY1_str' %(quantity_name)] = (RunawayText,'')
            tmp_dict['%s_maxModuleY14_str'%(quantity_name)] = (RunawayText,'')
            continue

        minval_endcap = (float('inf'),None)
        maxval_endcap = (None,None) # first is the value, 2nd is the corresponding ring
        max_y1_endcap = (None,None)
        max_y14_endcap = (None,None)

        for ring in range(6) :
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                graph = all_results[scenario][index][quantity_name]
                nstep = graph.GetN()

                # minval
                minval_module = (min(list(graph.GetY()[i] for i in range(nstep))),'R%d'%(ring))
                minval_endcap = MinTuple(minval_endcap,minval_module)

                # maxval
                maxval_module = (max(list(graph.GetY()[i] for i in range(nstep))),'R%d'%(ring))
                maxval_endcap = MaxTuple(maxval_endcap,maxval_module)

                # max in y1
                max_y1_module = (graph.GetY()[0],'R%d'%(ring))
                max_y1_endcap = MaxTuple(max_y1_endcap,max_y1_module)

                # max in y14
                max_y14_module = (graph.GetY()[nstep-1],'R%d'%(ring))
                max_y14_endcap = MaxTuple(max_y14_endcap,max_y14_module)

        tmp_dict['%s_minModule_str'%(quantity_name)] = (StringWithNSigFigs(minval_endcap[0],3),minval_endcap[1])
        tmp_dict['%s_maxModule_str'%(quantity_name)] = (StringWithNSigFigs(maxval_endcap[0],3),maxval_endcap[1])

        tmp_dict['%s_maxModuleY1_str' %(quantity_name)] = (StringWithNSigFigs(max_y1_endcap[0] ,3),max_y1_endcap[1])
        tmp_dict['%s_maxModuleY14_str'%(quantity_name)] = (StringWithNSigFigs(max_y14_endcap[0],3),max_y14_endcap[1])

    #
    # Maximum Petal Value
    #
    tmp_dict = all_results[scenario]
    for quantity_name in ['itapepetal','pmodulepetal','petalvoutlvpp2','vdrop_roundtrip','petaltapedeltav','petaltapepower'] :
        if runaway :
            all_results[scenario][0]['%s_maxPetal_str'%(quantity_name)] = RunawayText
            continue
        maxpetalval = None
        for disk in range(6) :
            index = structure_names.index('R%dD%d'%(0,disk))
            graph = tmp_dict[index][quantity_name]
            nstep = graph.GetN()
            maxval_thispetal = max(list(graph.GetY()[i] for i in range(nstep)))
            all_results[scenario][index]['%s_maxOfDiskNo_str'%(quantity_name)] = StringWithNSigFigs(maxval_thispetal,3)
            maxpetalval = max(maxpetalval,maxval_thispetal)

        all_results[scenario][0]['%s_maxPetal_str'%(quantity_name)] = StringWithNSigFigs(maxpetalval,3)


    #
    # Maximum of Ring type Rn
    #
    for quantity_name in ['phv_wleakage','tsensor','tfeast','qsensor_headroom','isensor','ifeast','pmodule','pmodule_noHV',
                          'ihybrid0','ihybrid1','ihybrid2','ihybrid3'] :
        for ring in range(6) :
            index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
            if runaway :
                all_results[scenario][index_rXd0]['%s_minOfRtype'%(quantity_name)] = RunawayText
                all_results[scenario][index_rXd0]['%s_maxOfRtype'%(quantity_name)] = RunawayText
                continue

            minval_ring = float('inf')
            maxval_ring = None

            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                graph = all_results[scenario][index][quantity_name]
                nstep = graph.GetN()

                minval_module = min(list(graph.GetY()[i] for i in range(nstep)))
                minval_ring = min(minval_ring,minval_module)

                maxval_module = max(list(graph.GetY()[i] for i in range(nstep)))
                maxval_ring = max(maxval_ring,maxval_module)

            all_results[scenario][index_rXd0]['%s_minOfRtype'%(quantity_name)] = StringWithNSigFigs(minval_ring,3)
            all_results[scenario][index_rXd0]['%s_maxOfRtype'%(quantity_name)] = StringWithNSigFigs(maxval_ring,3)

    #
    # Value at Maximum Wall Power, for disk-level quantities
    #
    for quantity_name in ['itapepetal'] :
        for disk in range(6) :
            index_r0dX = structure_names.index('R%dD%d'%(0,disk))
            tmp_dict = all_results[scenario][index_r0dX]
            max_i = all_results[scenario][0]['pwallpower_maxTotal_index']
            tmp_dict['%s_ValueAtMax_pwallpower'%(quantity_name)] = StringWithNSigFigs(tmp_dict[quantity_name].GetY()[max_i],3)

    #
    # Value at Maximum Wall Power, for detector-level quantities
    #
    for quantity_name in ['avgitapepetal','rmsitapepetal',
                          'plosslvcablest1total','plosslvcablest2total','plosslvcablest3total','plosslvcablest4total','plosslvpp2total','plosslvPStotal',
                          ] :
        max_i = all_results[scenario][0]['pwallpower_maxTotal_index']
        val = all_results[scenario][0][quantity_name].GetY()[max_i]
        if quantity_name in [
            'plosslvcablest1total','plosslvcablest2total','plosslvcablest3total','plosslvcablest4total',
            'plosslvpp2total','plosslvPStotal',
            ] :
            val = val/1000.
        all_results[scenario][0]['%s_ValueAtMax_pwallpower'%(quantity_name)] = StringWithNSigFigs(val,3)



def GetSafetyFactorHeaderRows(the_list,configs,scenarios) :
    the_list.append(['','Fluence'    ] + list(configs[scn].GetValue('SafetyFactors.safetyfluence','')          for scn in scenarios))
    the_list[-1][0] = '\multirow{6}{*}{Safety Factors}'
    the_list.append(['','$R_{T}$'    ] + list(configs[scn].GetValue('SafetyFactors.safetythermalimpedance','') for scn in scenarios))
    the_list.append(['','$I_D$'      ] + list(configs[scn].GetValue('SafetyFactors.safetycurrentd','')         for scn in scenarios))
    the_list.append(['','$I_A$'      ] + list(configs[scn].GetValue('SafetyFactors.safetycurrenta','')         for scn in scenarios))
    tmp_list = list(configs[scn].GetValue('SafetyFactors.TIDpessimistic','False') for scn in scenarios)
    tid_list = list(a.replace('False','nominal').replace('True','pessimistic') for a in tmp_list)
    the_list.append(['','TID parameterization'] + tid_list)
    the_list.append(['','Pre-irradiation [MRad]'] + list(configs[scn].GetValue('OperationalProfiles.PreIrradiation','0') for scn in scenarios))
    the_list.append(['','Voltage [V]'         ] + list(configs[scn].GetValue('SafetyFactors.vbias','')         for scn in scenarios))
    the_list[-1][0] = '\multirow{2}{*}{HV, Cooling}'
    the_list.append(['','Cooling [$^\circ$C]' ] + list(configs[scn].GetValue('cooling','').replace('-',' $-$') for scn in scenarios))
    return

# These values are calculated above...
def RowWithDetectorMinMax(label,quantity,results_dict,scenario_list) :
    row = ['',label]
    row += list('%s/%s'%(results_dict[scn][0]['%s_minTotal_str'%(quantity)],
                         results_dict[scn][0]['%s_maxTotal_str'%(quantity)]) for scn in scenario_list)
    return row

def RowWithDetectorVal(label,quantity,results_dict,scenario_list) :
    row = ['',label]
    row += list(results_dict[scn][0][quantity] for scn in scenario_list)
    return row

def RowWithDetectorMax(label,quantity,results_dict,scenario_list) :
    return RowWithDetectorVal(label,'%s_maxTotal_str'%(quantity),results_dict,scenario_list)

def RowWithPetalMax(label,quantity,results_dict,scenario_list) :
    row = ['',label]
    row += list(results_dict[scn][0]['%s_maxPetal_str'%(quantity)] for scn in scenario_list)
    return row

#
# Main Summary Table
#
#f.write('\\begin{landscape}\n')
#f.write('\subsubsection{Main Summary Table 2}\n')
olist = []
hlines_new = [5,7,12,13,16,22,28,34,40,46,59,66]
#
GetSafetyFactorHeaderRows(olist,all_configs,two_main_scenarios)
tmp_args = all_results,two_main_scenarios
olist.append( RowWithDetectorMinMax('Total LV+HV, no services','pnoservices',*tmp_args) )
olist.append( RowWithDetectorMinMax(' + type 1 cables (Cooling system power)','pcoolingsys',*tmp_args) )
olist.append( RowWithDetectorMinMax(' + all services and power supplies (Wall power)','pwallpower',*tmp_args) )
olist.append( RowWithDetectorMinMax('Service power only (cables,PP2,PS)','pservice',*tmp_args) )
olist.append( RowWithDetectorMax('Maximum $P_\text{HV}$ [kW]','phv_wleakage',*tmp_args) )
olist.append( RowWithPetalMax('Max petal power (LV+HV) [W]','pmodulepetal',*tmp_args) )
olist.append( RowWithPetalMax('Max LV tape power load (incl. tape losses) [W]','petaltapepower',*tmp_args) )
olist.append( RowWithPetalMax('Max $\Delta V_\text{tape}$ [V]','petaltapedeltav',*tmp_args) )
olist.append( RowWithPetalMax('Max $I_\text{tape}$ [A]','itapepetal',*tmp_args) )

#
# Fill in the leftmost labels:
#
olist[8][0] = '\multirow{3}{*}{Endcap System}'
olist[9][0] = '\multirow{3}{*}{Min/Max}'
olist[10][0] = '\multirow{3}{*}{Power [kW]}'
olist[13][0] = 'Petal-level'
olist[14][0] = '\multirow{3}{*}{Petal LV tape}'

def AddRingsDataMinMax(value,title) :
    for ring in range(6) :
        index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
        olist.append(['R%d'%(ring),''])
        olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['%s_minOfRtype'%(value)],
                                     all_results[scn][index_rXd0]['%s_maxOfRtype'%(value)]) for scn in two_main_scenarios)
        if not ring : olist[-1][1] = '\multirow{6}{*}{Min/Max %s}'%(title)

AddRingsDataMinMax('pmodule'     ,'(LV+HV) Power [W]')
AddRingsDataMinMax('pmodule_noHV','LV power [W]'     )
AddRingsDataMinMax('phv_wleakage','HV power [W]'     )
AddRingsDataMinMax('ifeast'      ,'Feast load [A]'   )
AddRingsDataMinMax('isensor'     ,'sensor leakage [A]')

for ring in range(6) :
    index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
    for hybrid in range(4) :
        name = 'R%dH%d'%(ring,hybrid)
        if name not in ['R0H0','R0H1','R1H0','R1H1','R2H0','R3H0','R3H1','R3H2','R3H3','R4H0','R4H1','R5H0','R5H1'] :
            continue
        olist.append([name,''])
        olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['ihybrid%d_minOfRtype'%(hybrid)],
                                     all_results[scn][index_rXd0]['ihybrid%d_maxOfRtype'%(hybrid)]) for scn in two_main_scenarios)
        if (not ring) and (not hybrid) :
            olist[-1][1] = '\multirow{13}{*}{Min/Max Hybrid Current [A]}'

# Sensor HV properties
olist.append(['','Max sensor $I_{HV}$ per module [mA]']); olist[-1] += list('%s (%s)'%all_results[scn][0]['isensor_maxModule_str'] for scn in two_main_scenarios)
# Sensor temperatures
olist.append(['','Max sensor T [$^\circ$C], Y1' ] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModuleY1_str' ] for scn in two_main_scenarios))
olist.append(['','Max sensor T [$^\circ$C], Y14'] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModuleY14_str'] for scn in two_main_scenarios))
olist.append(['','Max sensor T [$^\circ$C], Max'] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModule_str'   ] for scn in two_main_scenarios))
olist.append(['','Max $T_\text{Feast}$'         ] + list('%s (%s)'%all_results[scn][0]['tfeast_maxModule_str'    ] for scn in two_main_scenarios))
olist.append(['','Min $Q_{sensor}$ Headroom [$Q_{S,crit}/Q_{S}$]'] + list('%s (%s)'%all_results[scn][0]['qsensor_headroom_minModule_str'] for scn in two_main_scenarios))
olist.append(['','Min Coolant Temperature Headroom [$^\circ$C]'  ] + list('%s (%s)'%all_results[scn][0]['tc_headroom_minModule_str'     ] for scn in two_main_scenarios))

# Services
olist.append(['','Max $\Delta V_\text{HV}$ (filters, \sout{tape}, EOS, cables, PP2) [V]'] + list('%s (%s)'%all_results[scn][0]['deltavhvservices_maxModule_str'] for scn in two_main_scenarios))
olist.append(['','Max LV round-trip $\Delta V$ from PP2 (type I/II cables only) [V]'] + list(all_results[scn][0]['vdrop_roundtrip_maxPetal_str'] for scn in two_main_scenarios))
olist.append(['','Max LV $V_\text{out}$ at PP2 [V]'     ] + list(all_results[scn][0]['petalvoutlvpp2_maxPetal_str'] for scn in two_main_scenarios))

olist[-10][0] = '\multirow{6}{*}{Module-level}'
olist[ -9][0] = '\multirow{6}{*}{Components}'
olist[ -3][0] = '\multirow{3}{*}{Services}'

table = TableUtils.PrintLatexTable(olist,caption='Summary of nominal and worst-case safety factor scenarios.',hlines=hlines_new,justs=['l','l'])
f.write(table)
#f.write('\end{landscape}\n')

#
# Another summary table - this time of power estimates at the time of maximum total wall power
#

def AddDiskQuantity(rows,label,quantity,results_dict,scenario_list) :
    for disk in range(6) :
        row = ['Disk %d'%(disk),'']
        if not disk :
            row[1] = '\multirow{4}{*}{%s}'%(label)
        index_r0dX = structure_names.index('R%dD%d'%(0,disk))
        row += list('%s/%s'%(results_dict[scn][index_r0dX]['%s_maxOfDiskNo_str'%(quantity)],
                             results_dict[scn][index_r0dX]['%s_ValueAtMax_pwallpower'%(quantity)]) for scn in scenario_list)
        rows.append(row)
    return

def RowWithDetectorMaxAndAtMaxWallPower(label,quantity,results_dict,scenario_list) :
    row = ['',label]
    row += list('%s/%s'%(results_dict[scn][0]['%s_maxTotal_str'%(quantity)],
                         results_dict[scn][0]['%stotal_ValueAtMax_pwallpower'%(quantity)]) for scn in scenario_list)
    return row

the_list = []

GetSafetyFactorHeaderRows(the_list,all_configs,two_main_scenarios)
the_list.append( RowWithDetectorMinMax('\textbf{Wall power Min/Max}','pwallpower',*tmp_args) )
the_list.append( RowWithDetectorVal('\textbf{Month of max wall power}','pwallpower_maxTotal_index_str',*tmp_args) )
AddDiskQuantity(the_list,'Petal $I_{tape}$ [A]','itapepetal',*tmp_args)
the_list[-5][1] = '\multirow{4}{*}{%s}'%('(disk Max /')
the_list[-4][1] = '\multirow{4}{*}{%s}'%('~~~~~value at max wall power)')
the_list.append( RowWithDetectorVal('(at max wall power)','rmsitapepetal_ValueAtMax_pwallpower',*tmp_args) )
the_list[-1][0] = '\multicolumn{1}{|l}{%s}'%('RMS Petal $I_{tape}$ [A]')

the_list.append( RowWithDetectorMaxAndAtMaxWallPower('Type-1 LV cable','plosslvcablest1',*tmp_args) )
the_list.append( RowWithDetectorMaxAndAtMaxWallPower('Type-2 LV cable','plosslvcablest2',*tmp_args) )
the_list.append( RowWithDetectorMaxAndAtMaxWallPower('PP2 LV '        ,'plosslvpp2'     ,*tmp_args) )
the_list.append( RowWithDetectorMaxAndAtMaxWallPower('Type-3 LV cable','plosslvcablest3',*tmp_args) )
the_list.append( RowWithDetectorMaxAndAtMaxWallPower('Type-4 LV cable','plosslvcablest4',*tmp_args) )
the_list.append( RowWithDetectorMaxAndAtMaxWallPower('LV Power Supply (PS)','plosslvPS' ,*tmp_args) )
the_list[-6][0] = '\multirow{3}{*}{%s}'%('Cable / PP2 / PS')
the_list[-5][0] = '\multirow{3}{*}{%s}'%('power losses [kW]')
the_list[-4][0] = '\multirow{3}{*}{%s}'%('(Max / value at max')
the_list[-3][0] = '\multirow{3}{*}{%s}'%('~~~~~~~~~~~~~~~wall power)')

hlines = [5,7,9,15,16]
caption = 'Breakdown of power estimates at the time of max wall power.'
caption += ' The RMS current ($\sqrt{{1\over n}\Sigma i^2}$) is given instead of the average current in'
caption += ' order to be able to calculate the power losses properly.'
table = TableUtils.PrintLatexTable(the_list,caption=caption,hlines=hlines,justs=['l','l'])

f.write(table)
f.write('\clearpage\n')

#
# Breakdowns of different scenarios - power, HV power, sensor headroom, coolant headroom
#
safety_factor_list = ['Fluence','$R_{T}$','$I_D$','$I_A$','TID']
other_parameters = ['[MRad]','[V]','[$^\circ$C]']
header = '\n\multicolumn{%d}{|c|}{%s} & Pre-irradiation & $V_{bias}$ & Cooling & Endcaps max & Endcaps max & Min sensor & Min Coolant\\\\'%(len(safety_factor_list),'Safety factor')

the_lists = []
the_lists.append(list(a for a in safety_factor_list))
the_lists[-1] += list(a for a in other_parameters)
the_lists[-1] += list(a for a in ['\multicolumn{1}{l}{power (nos) [kW]}',
                                  '\multicolumn{1}{l}{HV [kW]}',
                                  '\multicolumn{1}{l}{headroom}', # [$Q_{s,crit}/Q_s$]
                                  '\multicolumn{1}{l|}{headroom [$^\circ$C]}',
                                  ])

f.write('\subsubsection{Main Summary Table}\n')
for scenario in scenarios :
    # all_configs[scenario].Print()

    the_lists.append([])
    GetSixScenarioParamters(the_lists[-1])

    tmp_dict = all_results[scenario][0]

    for quantity_name in ['pnoservices','phv_wleakage'] :
        the_lists[-1].append(tmp_dict['%s_maxTotal_str'%(quantity_name)])

    # maximum (or minimum) module value in full system
    for quantity_name in ['qsensor_headroom','tc_headroom'] :
        the_lists[-1].append(tmp_dict['%s_minModule_str'%(quantity_name)][0])

scenario0 = scenarios[0]
table = TableUtils.PrintLatexTable(the_lists,caption='Summary of all safety factor scenarios.',hlines=hlines)
i_start_of_data = re.search("data_below\n",table).end()
table = table[:i_start_of_data] + header + table[i_start_of_data:]
table = re.sub('\|l%s\|r\|r\|r\|r\|'%('\\|r'*(len(safety_factor_list)-1)),
               '|%s|ccc|rrrr|'%('c'*len(safety_factor_list)),table)
f.write(table)

#
# Units
#
units_dict = dict()
for quantity_name in all_results[scenario0][0].keys() :
    if not issubclass(type(all_results[scenario0][0][quantity_name]),ROOT.TGraph) :
        continue
    graph0  = all_results[scenario0][0][quantity_name]
    if '[' in graph0.GetYaxis().GetTitle() :
        units = graph0.GetYaxis().GetTitle().split('[')[1].split(']')[0]
        units = units.replace('#circ^{}','$^\circ$')
        units = units.replace('_{}Q_{S,crit}/Q_{S}','$Q_{S,crit}/Q_{S}$')
        units = '[%s]'%(units)
        units_dict[quantity_name] = units
    else :
        units_dict[quantity_name] = ''

#
# Petal-level Tables
#
f.write('\subsubsection{Petal Summaries}\n')
for quantity_name in ['pmodule','itape'] :
    the_lists = []
    the_lists.append(safety_factor_list + other_parameters)
    the_lists[-1] += ['disk 0','disk 1','disk 2','disk 3','disk 4','disk 5']
    for scenario in scenarios :
        the_lists.append([])
        GetSixScenarioParamters(the_lists[-1])
        for disk in range(6) :
            index = structure_names.index('R%dD%d'%(0,disk))
            if all_results[scenario][index]['thermal_runaway_yearpetal'] :
                the_lists[-1].append('{\\bf Y%d}'%(all_results[scenario][index]['thermal_runaway_yearpetal']))
                continue
            graph = all_results[scenario][index][quantity_name+'petal']
            nstep = graph.GetN()
            maxval_petal = max(list(graph.GetY()[i] for i in range(nstep)))
            the_lists[-1].append(maxval_petal)

    graph0  = all_results[scenario0][0][quantity_name]
    caption = 'Maximum %s'%(graph0.GetTitle())
    caption = caption.replace(' (one side)','')
    caption = caption.replace(' (no EOS)','')
    caption += ' for a full petal (1 side). Results are shown for a petal at each disk location.'
    caption = caption.replace(' due to items on module','')

    label_short = graph0.GetYaxis().GetTitle().split('[')[0]
    disk_label = '\multicolumn{%d}{|c|}{%s} & Pre-irradiation & $V_{bias}$ & Cooling & '%(len(safety_factor_list),'Safety factor')
    disk_label += '\multicolumn{6}{c|}{Max $%s$ for full petal (1 side) on disk $n$ %s} \\\\\n'%(label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|ccccc|ccc|rrrrrr|',table)
    f.write(table)

#
# Worst-case ring Tables
#
f.write('\clearpage\n')
f.write('\subsubsection{Worst-case ring modules}\n')
for quantity_name in ['phv_wleakage','tsensor','tfeast','qsensor_headroom','isensor'] :
    the_lists = []
    the_lists.append(safety_factor_list + other_parameters)
    the_lists[-1] += ['R0','R1','R2','R3','R4','R5']
    for scenario in scenarios :
        the_lists.append([])
        GetSixScenarioParamters(the_lists[-1])
        for ring in range(6) :
            index = structure_names.index('R%dD%d'%(ring,0))
            if all_results[scenario][index]['thermal_runaway_yearmodule'] :
                the_lists[-1].append('{\\bf Y%d}'%(all_results[scenario][index]['thermal_runaway_yearmodule']))
                continue
            maxval_ring = float('inf') if quantity_name in ['qsensor_headroom'] else None
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                graph = all_results[scenario][index][quantity_name]
                nstep = graph.GetN()
                if quantity_name in ['qsensor_headroom'] :
                    maxval_module = min(list(graph.GetY()[i] for i in range(nstep)))
                    maxval_ring = min(maxval_ring,maxval_module)
                else :
                    maxval_module = max(list(graph.GetY()[i] for i in range(nstep)))
                    maxval_ring = max(maxval_ring,maxval_module)
            the_lists[-1].append(maxval_ring)

    graph0  = all_results[scenario0][0][quantity_name]
    caption = 'Maximum module %s'%(graph0.GetTitle())
    caption = caption.replace(' Total','')
    caption = caption.replace(' (one side)','')
    caption = caption.replace(' (no EOS)','')
    caption += ' (1 side) for the worst-case module of a given type (typically located on Disk 5).'
    caption = caption.replace(' due to items on module','')

    label_short = graph0.GetYaxis().GetTitle().split('[')[0].rstrip()
    label_short = '$%s$'%(label_short)
    label_short = label_short.replace('$Power headroom factor$','headroom')
    disk_label = '\multicolumn{%d}{|c|}{%s} & Pre-irradiation & $V_{bias}$ & Cooling & '%(len(safety_factor_list),'Safety factor')
    disk_label += '\multicolumn{6}{c|}{Max %s for module of type R$n$ %s} \\\\\n'%(label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|ccccc|ccc|rrrrrr|',table)
    f.write(table)

f.close()

# make an auto-latex document
os.system('cat %s/latex/FrontMatter.tex > %s/Scenarios_%s.tex'%(the_path,outputpath,wildcard))
# os.system('echo "\section{Safety Factor Scenarios}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
os.system('cat %s/Scenarios.txt >> %s/Scenarios_%s.tex'%(outputpath,outputpath,wildcard))
os.system('echo "\end{document}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
PlotUtils.pdflatex(outputpath,'Scenarios_%s.tex'%(wildcard))

print 'done'
