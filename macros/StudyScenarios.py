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
    while len(the_string.replace('.','')) < 3 :
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

ordering = [
    'No_Safety',
    'Base_assumptions',
    'BasePlusASICOldCurrent',
    'BasePlusASIC',
    'BasePlusThermal',
    'BasePlusThermalTight',
    'BasePlusBias',
    'BasePlusASICPlusBiasPlusThermal',
    'BasePlusASICPlusBiasPlusThermalTight',
    ]

for i in reversed(ordering) :
    scenarios.sort(key = lambda x: (i+'_' not in x))
for i in reversed(['flat_m35','flat_m30','flat_m25','flat_m20','flat_m15','ramp_m35']) :
    scenarios.sort(key = lambda x: (i not in x))

# scenarios = [
#     'Official_No_Safety_flat_m30',
#     'Official_Base_assumptions_flat_m30',
#     'Official_BasePlusASICOldCurrent_flat_m30',
#     'Official_BasePlusASIC_flat_m30',
#     'Official_BasePlusThermal_flat_m30',
#     'Official_BasePlusThermalTight_flat_m30',
#     'Official_BasePlusBias_flat_m30',
#     'Official_BasePlusASICPlusBiasPlusThermal_flat_m30',
#     'Official_BasePlusASICPlusBiasPlusThermalTight_flat_m30',
#     ]
# scenarios = list('ExtendedModelEndcap_'+i for i in scenarios)

for scenario in scenarios :
    print scenario
    # Load the saved numpy dictionary
    import numpy as np
    all_results[scenario] = np.load('%s/%s/Results.npy'%(inputpath,scenario))
    all_configs[scenario] = np.load('%s/%s/Config.npy'%(inputpath,scenario)).item()

header = '\n\multicolumn{4}{|c|}{%s} & $V_{bias}$ & Cooling & Endcaps max & Endcaps max & Min sensor \\\\'%('Safety factor')

the_lists = []
the_lists.append(['Fluence','$R_{T}$','$I_D$','$I_A$',
                  '[V]',
                  '[$^\circ$C]',
                  '\multicolumn{1}{l}{power [kW]}',
                  '\multicolumn{1}{l}{HV [kW]}',
                  '\multicolumn{1}{l|}{headroom}',
                  ])

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
    a_list.append(all_configs[scenario].GetValue('SafetyFactors.vbias',''))
    cooling = all_configs[scenario].GetValue('cooling','')
    if 'flat' in cooling :
        cooling = cooling.replace('flat','').replace('-','$-$')+' flat'
    if 'ramp' in cooling :
        cooling = cooling.replace('ramp','').replace('-','$-$')+' ramp'
    the_lists[-1].append(cooling)
    return

#
# Automate hlines
#
hlines = []
scenario_last = scenarios[0]
for s,scenario in enumerate(scenarios) :
    cooling      = all_configs[scenario     ].GetValue('cooling','')
    cooling_last = all_configs[scenario_last].GetValue('cooling','')
    if cooling != cooling_last :
        hlines.append(s)
    scenario_last = scenario

#
# Main Summary Table
#
f.write('\subsubsection{Main Summary Table}\n')
for scenario in scenarios :
    # all_configs[scenario].Print()

    the_lists.append([])
    GetSixScenarioParamters(the_lists[-1])

    for quantity_name in ['pmodule','phv_wleakage'] :
        if all_results[scenario][0]['thermal_runaway_yeartotal'] :
            the_lists[-1].append('{\\bf Year %d}'%(all_results[scenario][0]['thermal_runaway_yeartotal']))
            continue
        nstep = all_results[scenario][0][quantity_name+'total'].GetN()
        maxval = max(list(all_results[scenario][0][quantity_name+'total'].GetY()[i] for i in range(nstep)))
        if quantity_name in ['pmodule','phv_wleakage'] :
            maxval = maxval/1000.
        the_lists[-1].append(StringWithNSigFigs(maxval,3))

    # maximum (or minimum) module value in full system
    for quantity_name in ['qsensor_headroom'] :
        if all_results[scenario][0]['thermal_runaway_yeartotal'] :
            the_lists[-1].append('{\\bf Year %d}'%(all_results[scenario][0]['thermal_runaway_yeartotal']))
            continue
        maxval_endcap = float('inf') if quantity_name in ['qsensor_headroom'] else None
        for ring in range(6) :
            for disk in range(6) :
                index = structure_names.index('R%dD%d'%(ring,disk))
                graph = all_results[scenario][index][quantity_name]
                nstep = graph.GetN()
                if quantity_name in ['qsensor_headroom'] :
                    maxval_module = min(list(graph.GetY()[i] for i in range(nstep)))
                    maxval_endcap = min(maxval_endcap,maxval_module)
                else :
                    maxval_module = max(list(graph.GetY()[i] for i in range(nstep)))
                    maxval_endcap = max(maxval_endcap,maxval_module)
        the_lists[-1].append(StringWithNSigFigs(maxval_endcap,3))

scenario0 = scenarios[0]
table = TableUtils.PrintLatexTable(the_lists,caption='Summary of all safety factor scenarios.',hlines=hlines)
i_start_of_data = re.search("data_below\n",table).end()
table = table[:i_start_of_data] + header + table[i_start_of_data:]
table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|','|cccc|cc|rrr|',table)
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
    the_lists.append(['Fluence','$R_{T}$','$I_D$','$I_A$','[V]','[$^\circ$C]',
                      'disk 0','disk 1','disk 2','disk 3','disk 4','disk 5'])
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
    disk_label = '\multicolumn{4}{|c|}{%s} & $V_{bias}$ & Cooling & \multicolumn{6}{c|}{Max $%s$ for full petal (1 side) on disk $n$ %s} \\\\\n'%('Safety factor',label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|cccc|cc|rrrrrr|',table)
    f.write(table)

#
# Worst-case ring Tables
#
f.write('\clearpage\n')
f.write('\subsubsection{Worst-case ring modules}\n')
for quantity_name in ['phv_wleakage','tsensor','tfeast','qsensor_headroom'] :
    the_lists = []
    the_lists.append(['Fluence','$R_{T}$','$I_D$','$I_A$','[V]','[$^\circ$C]',
                      'R0','R1','R2','R3','R4','R5'])
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

    label_short = graph0.GetYaxis().GetTitle().split('[')[0]
    disk_label = '\multicolumn{4}{|c|}{%s} & $V_{bias}$ & Cooling & \multicolumn{6}{c|}{Max $%s$ for module of type R$n$ %s} \\\\\n'%('Safety factor',label_short,units_dict[quantity_name])
    table = TableUtils.PrintLatexTable(the_lists,caption=caption,hlines=hlines)
    # insert special headers
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    table = re.sub('\|l\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|r\|','|cccc|cc|rrrrrr|',table)
    f.write(table)

f.close()

# make an auto-latex document
os.system('cat %s/latex/FrontMatter.tex > %s/Scenarios_%s.tex'%(the_path,outputpath,wildcard))
os.system('echo "\section{Safety Factor Scenarios}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
os.system('cat %s/Scenarios.txt >> %s/Scenarios_%s.tex'%(outputpath,outputpath,wildcard))
os.system('echo "\end{document}\n" >> %s/Scenarios_%s.tex'%(outputpath,wildcard))
os.system('cd %s && pdflatex Scenarios_%s.tex'%(outputpath,wildcard))

print 'done'
