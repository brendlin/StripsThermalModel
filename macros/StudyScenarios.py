#!/usr/bin/env python

import os,sys
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

scenarios = ['FullMatrix_No_Safety_flat_m30',
             'FullMatrix_Base_assumptions_flat_m30',
             'FullMatrix_BasePlusASICOldCurrent_flat_m30',
             'FullMatrix_BasePlusASIC_flat_m30',
             'FullMatrix_BasePlusThermal_flat_m30',
             'FullMatrix_BasePlusThermalTight_flat_m30',
             'FullMatrix_BasePlusBias_flat_m30',
             'FullMatrix_BasePlusASICPlusBiasPlusThermal_flat_m30',
             'FullMatrix_BasePlusASICPlusBiasPlusThermalTight_flat_m30',
             ]
scenarios = list('ExtendedModelEndcap_'+i for i in scenarios)

#for scenario in os.listdir(inputpath) :
for scenario in scenarios :
    if 'ExtendedModelEndcap' not in scenario :
        continue
    if wildcard not in scenario :
        continue
    
    print scenario

    # Load the saved numpy dictionary
    import numpy as np
    all_results[scenario] = np.load('%s/%s/Results.npy'%(inputpath,scenario))
    all_configs[scenario] = np.load('%s/%s/Config.npy'%(inputpath,scenario)).item()

the_lists = []
the_lists.append(['Fluence','$R_{T}$','$I_D$','$I_A$','$V_{bias}$','Cooling'     ,'Endcaps max ','Endcaps max'])
the_lists.append([''       ,''       ,''     ,''     ,''          ,'[$^\circ$C]' ,'power [W]'   ,'HV [W]'     ])

structure_names = []
for ring in range(6) :
    for disk in range(6) :
        structure_names.append('R%dD%d'%(ring,disk))

# output file
f = open('%s/Scenarios.txt'%(outputpath),'w')

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
        cooling = cooling.replace('flat','').replace('-','$-$')+' ramp'
    the_lists[-1].append(cooling)
    return

for scenario in scenarios :
    all_configs[scenario].Print()

    the_lists.append([])
    GetSixScenarioParamters(the_lists[-1])
    
    for quantity_name in ['pmodule','phv_wleakage'] :
        nstep = all_results[scenario][0][quantity_name+'total'].GetN()
        maxval = max(list(all_results[scenario][0][quantity_name+'total'].GetY()[i] for i in range(nstep)))
        the_lists[-1].append(maxval)

scenario0 = scenarios[0]
f.write(TableUtils.PrintLatexTable(the_lists,caption='Summary of all safety factor scenarios.'))

for quantity_name in ['pmodule','itape','phv_wleakage'] :
    the_lists = []
    the_lists.append(['Fluence','$R_{T}$','$I_D$','$I_A$','$V_{bias}$','Cooling [$^\circ C$]',
                     '0','1','2','3','4','5'])
    for scenario in scenarios :
        the_lists.append([])
        GetSixScenarioParamters(the_lists[-1])
        for disk in range(6) :
            index = structure_names.index('R%dD%d'%(0,disk))
            nstep = all_results[scenario][index][quantity_name+'petal'].GetN()
            maxval_petal = max(list(all_results[scenario][index][quantity_name+'petal'].GetY()[i] for i in range(nstep)))
            the_lists[-1].append(maxval_petal)

    graph0  = all_results[scenario0][0][quantity_name]
    caption = all_results[scenario0][0][quantity_name+'caption']
    units = ''
    if '[' in graph0.GetYaxis().GetTitle() :
        units = graph0.GetYaxis().GetTitle().split('[')[1].split(']')[0]
        units = units.replace('#circ^{}','$^\circ$')
        units = units.replace('_{}Q_{S,crit}/Q_{S}','$Q_{S,crit}/Q_{S}$')
        units = '[%s]'%(units)
    label_short = graph0.GetYaxis().GetTitle().split('[')[0]
    disk_label = '\multicolumn{6}{|c|}{%s} & \multicolumn{6}{c|}{$%s$ for Disk $n$ %s} \\\\\n'%('Scenario',label_short,units)
    table = TableUtils.PrintLatexTable(the_lists,caption=caption)
    # insert special headers
    import re
    i_start_of_data = re.search("data_below\n",table).end()
    table = table[:i_start_of_data] + disk_label + table[i_start_of_data:]
    f.write(table)

f.close()

# make an auto-latex document
os.system('cat %s/latex/FrontMatter.tex > %s/Scenarios.tex'%(the_path,outputpath))
os.system('echo "\section{Model Results}\n" >> %s/Scenarios.tex'%(outputpath))
os.system('cat %s/Scenarios.txt >> %s/Scenarios.tex'%(outputpath,outputpath))
os.system('echo "\end{document}\n" >> %s/Scenarios.tex'%(outputpath))
os.system('cd %s && pdflatex Scenarios.tex'%(outputpath))

print 'done'
