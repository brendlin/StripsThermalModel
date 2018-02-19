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
    'Base_assumptions',
    'BasePlusBumpParam',
    'BasePlusASIC',
    'BasePlusBias',
    'BasePlusThermal',
    'BasePlusBumpASICThermalBias',
    ]

for i in reversed(ordering) :
    scenarios.sort(key = lambda x: (i+'_' not in x))
for i in reversed(['flat_m35','flat_m30','flat_m25','flat_m20','flat_m15','ramp_m35']) :
    scenarios.sort(key = lambda x: (i not in x))

# different ordering (used for "two main scenarios")
scenarios_o2 = list(a for a in scenarios)
for i in reversed(ordering) :
    scenarios_o2.sort(key = lambda x: (i+'_' not in x))

two_main_scenarios = []
find_two_main_scenarios = ['No_Safety_','BasePlusBumpASICThermalBias_']
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
    all_results[scenario] = np.load('%s/%s/Results.npy'%(inputpath,scenario))
    all_configs[scenario] = np.load('%s/%s/Config.npy'%(inputpath,scenario)).item()

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
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.vbias',''))
    cooling = all_configs[scenario].GetValue('cooling','')
    if 'flat' in cooling :
        cooling = cooling.replace('flat','').replace('-','$-$')+' flat'
    if 'ramp' in cooling :
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
    for quantity_name in ['pmodule','phv_wleakage'] :
        if runaway :
            tmp_dict['%s_maxval_str'%(quantity_name)] = RunawayText
            tmp_dict['%s_minval_str'%(quantity_name)] = RunawayText
            continue
        nstep = tmp_dict[quantity_name+'total'].GetN()

        maxval = max(list(tmp_dict[quantity_name+'total'].GetY()[i] for i in range(nstep)))
        minval = min(list(tmp_dict[quantity_name+'total'].GetY()[i] for i in range(nstep)))

        if quantity_name in ['pmodule','phv_wleakage'] :
            maxval = maxval/1000.
            minval = minval/1000.

        tmp_dict['%s_maxval_str'%(quantity_name)] = StringWithNSigFigs(maxval,3)
        tmp_dict['%s_minval_str'%(quantity_name)] = StringWithNSigFigs(minval,3)

    #
    # Minimum / Maximum Module Value
    #
    for quantity_name in ['tfeast','isensor','qsensor_headroom','tsensor','tc_headroom'] :
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
    for quantity_name in ['itapepetal','pmodulepetal','petalvoutlvpp2'] :
        if runaway :
            all_results[scenario][0]['%s_maxPetal_str'%(quantity_name)] = RunawayText
            continue
        maxpetalval = None
        for disk in range(6) :
            index = structure_names.index('R%dD%d'%(0,disk))
            graph = tmp_dict[index][quantity_name]
            nstep = graph.GetN()
            maxval_thispetal = max(list(graph.GetY()[i] for i in range(nstep)))
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
# Main Summary Table
#
#f.write('\\begin{landscape}\n')
#f.write('\subsubsection{Main Summary Table 2}\n')
olist = []
hlines_new = [4,6,10,13,19,25,31,37,50]
#
olist.append(['','Fluence'    ] + list(all_configs[scn].GetValue('SafetyFactors.safetyfluence','')          for scn in two_main_scenarios))
olist.append(['','$R_{T}$'    ] + list(all_configs[scn].GetValue('SafetyFactors.safetythermalimpedance','') for scn in two_main_scenarios))
olist.append(['','$I_D$'      ] + list(all_configs[scn].GetValue('SafetyFactors.safetycurrentd','')         for scn in two_main_scenarios))
olist.append(['','$I_A$'      ] + list(all_configs[scn].GetValue('SafetyFactors.safetycurrenta','')         for scn in two_main_scenarios))
olist.append(['','TID parameterization'] + list(all_configs[scn].GetValue('SafetyFactors.TIDpessimistic','False').replace('False','nominal').replace('True','pessimistic') for scn in two_main_scenarios))
olist.append(['','Voltage [V]'         ] + list(all_configs[scn].GetValue('SafetyFactors.vbias','')         for scn in two_main_scenarios))
olist.append(['','Cooling [$^\circ$C]' ] + list(all_configs[scn].GetValue('cooling','').replace('-',' $-$') for scn in two_main_scenarios))
olist.append(['','Min/Max Power (LV+HV, no services) [kW]'] + list('%s/%s'%(all_results[scn][0]['pmodule_minval_str'],
                                                                            all_results[scn][0]['pmodule_maxval_str']) for scn in two_main_scenarios))
olist.append(['','\phantom{Min/Max Power} (w/type 1 cooling system) [kW]'] + list('%s/%s'%('???','???') for scn in two_main_scenarios))
olist.append(['','\phantom{Min/Max Power} (w/all services +PS, e.g. wall power) [kW]'] + list('%s/%s'%('???','???') for scn in two_main_scenarios))
olist.append(['','Maximum $P_\text{HV}$ [kW]'      ] + list(all_results[scn][0]['phv_wleakage_maxval_str']     for scn in two_main_scenarios))
olist.append(['','Max petal LV $I_\text{tape}$ [A]'] + list(all_results[scn][0]['itapepetal_maxPetal_str']     for scn in two_main_scenarios))
olist.append(['','Max petal power (LV+HV) [W]'     ] + list(all_results[scn][0]['pmodulepetal_maxPetal_str']   for scn in two_main_scenarios))
olist.append(['','Max LV $V_\text{out}$ at PP2'    ] + list(all_results[scn][0]['petalvoutlvpp2_maxPetal_str'] for scn in two_main_scenarios))
#
# Fill in the leftmost labels:
#
olist[0][0] = '\multirow{5}{*}{Safety Factors}'
olist[5][0] = '\multirow{2}{*}{HV, Cooling}'
olist[7][0] = '\multirow{2}{*}{Endcap System}'
olist[8][0] = '\multirow{2}{*}{Min/Max}'
olist[9][0] = '\multirow{2}{*}{Power [kW]}'
olist[11][0] = '\multirow{3}{*}{Petal-level}'

#
for ring in range(6) :
    index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
    olist.append(['R%d'%(ring),''])
    olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['pmodule_minOfRtype'],
                                     all_results[scn][index_rXd0]['pmodule_maxOfRtype']) for scn in two_main_scenarios)
    if not ring : olist[-1][1] = '\multirow{6}{*}{Min/Max (LV+HV) Power [W]}'
#
for ring in range(6) :
    index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
    olist.append(['R%d'%(ring),''])
    olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['pmodule_noHV_minOfRtype'],
                                     all_results[scn][index_rXd0]['pmodule_noHV_maxOfRtype']) for scn in two_main_scenarios)
    if not ring : olist[-1][1] = '\multirow{6}{*}{Min/Max LV power [W]}'
#
for ring in range(6) :
    index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
    olist.append(['R%d'%(ring),''])
    olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['phv_wleakage_minOfRtype'],
                                     all_results[scn][index_rXd0]['phv_wleakage_maxOfRtype']) for scn in two_main_scenarios)
    if not ring : olist[-1][1] = '\multirow{6}{*}{Min/Max HV power [W]}'
#
for ring in range(6) :
    index_rXd0 = structure_names.index('R%dD%d'%(ring,0))
    olist.append(['R%d'%(ring),''])
    olist[-1] += list('%s / %s'%(all_results[scn][index_rXd0]['ifeast_minOfRtype'],
                                 all_results[scn][index_rXd0]['ifeast_maxOfRtype']) for scn in two_main_scenarios)
    if not ring : olist[-1][1] = '\multirow{6}{*}{Min/Max Feast load [A]}'
#
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
#
olist.append(['','Max $I_{HV}$ per module [mA]']); olist[-1] += list('%s (%s)'%all_results[scn][0]['isensor_maxModule_str'] for scn in two_main_scenarios)
olist[-1][0] = '\multirow{7}{*}{Components}'
# Sensor temperatures
olist.append(['','Max sensor T [$^\circ$C], Y1' ] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModuleY1_str' ] for scn in two_main_scenarios))
olist.append(['','Max sensor T [$^\circ$C], Y14'] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModuleY14_str'] for scn in two_main_scenarios))
olist.append(['','Max sensor T [$^\circ$C], Max'] + list('%s (%s)'%all_results[scn][0]['tsensor_maxModule_str'   ] for scn in two_main_scenarios))
olist.append(['','Max $T_\text{Feast}$'         ] + list('%s (%s)'%all_results[scn][0]['tfeast_maxModule_str'    ] for scn in two_main_scenarios))
olist.append(['','Min $Q_{sensor}$ Headroom [$Q_{S,crit}/Q_{S}$]'] + list('%s (%s)'%all_results[scn][0]['qsensor_headroom_minModule_str'] for scn in two_main_scenarios))
olist.append(['','Min Coolant Temperature Headroom [$^\circ$C]'  ] + list('%s (%s)'%all_results[scn][0]['tc_headroom_minModule_str'     ] for scn in two_main_scenarios))
table = TableUtils.PrintLatexTable(olist,caption='Summary of nominal and worst-case safety factor scenarios.',hlines=hlines_new,justs=['l','l'])
f.write(table)
#f.write('\end{landscape}\n')

#
# Main Summary Table
#
safety_factor_list = ['Fluence','$R_{T}$','$I_D$','$I_A$','TID']
other_parameters = ['[V]','[$^\circ$C]']
header = '\n\multicolumn{%d}{|c|}{%s} & $V_{bias}$ & Cooling & Endcaps max & Endcaps max & Min sensor & Min Coolant\\\\'%(len(safety_factor_list),'Safety factor')

the_lists = []
the_lists.append(list(a for a in safety_factor_list))
the_lists[-1] += list(a for a in other_parameters)
the_lists[-1] += list(a for a in ['\multicolumn{1}{l}{power [kW]}',
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

    for quantity_name in ['pmodule','phv_wleakage'] :
        the_lists[-1].append(tmp_dict['%s_maxval_str'%(quantity_name)])

    # maximum (or minimum) module value in full system
    for quantity_name in ['qsensor_headroom','tc_headroom'] :
        the_lists[-1].append(tmp_dict['%s_minModule_str'%(quantity_name)][0])

scenario0 = scenarios[0]
table = TableUtils.PrintLatexTable(the_lists,caption='Summary of all safety factor scenarios.',hlines=hlines)
i_start_of_data = re.search("data_below\n",table).end()
table = table[:i_start_of_data] + header + table[i_start_of_data:]
table = re.sub('\|l%s\|r\|r\|r\|r\|'%('\\|r'*(len(safety_factor_list)-1)),
               '|%s|cc|rrrr|'%('c'*len(safety_factor_list)),table)
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
    disk_label = '\multicolumn{%d}{|c|}{%s} & $V_{bias}$ & Cooling & '%(len(safety_factor_list),'Safety factor')
    disk_label += '\multicolumn{6}{c|}{Max $%s$ for full petal (1 side) on disk $n$ %s} \\\\\n'%(label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|ccccc|cc|rrrrrr|',table)
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
    disk_label = '\multicolumn{%d}{|c|}{%s} & $V_{bias}$ & Cooling & '%(len(safety_factor_list),'Safety factor')
    disk_label += '\multicolumn{6}{c|}{Max %s for module of type R$n$ %s} \\\\\n'%(label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|ccccc|cc|rrrrrr|',table)
    f.write(table)

f.close()

# make an auto-latex document
os.system('cat %s/latex/FrontMatter.tex > %s/Scenarios_%s.tex'%(the_path,outputpath,wildcard))
os.system('echo "\section{Safety Factor Scenarios}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
os.system('cat %s/Scenarios.txt >> %s/Scenarios_%s.tex'%(outputpath,outputpath,wildcard))
os.system('echo "\end{document}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
PlotUtils.pdflatex(outputpath,'Scenarios_%s.tex'%(wildcard))

print 'done'
