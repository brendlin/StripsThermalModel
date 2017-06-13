#!/usr/bin/env python

# Usage:
# for i in $(ls ../data/ | grep ThermalImpedances_R); do echo $i; python StudyThermalImpedances.py --data $i; done;
#

import ROOT
import os,sys
from array import array

ROOT.gROOT.SetBatch(True)

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

import python.PoweringEfficiency as PoweringEfficiency
import python.PlotUtils as PlotUtils
from python.PlotUtils import MakeGraph
import python.TAxisFunctions as taxisfunc

#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()

    c = ROOT.TCanvas('blah','blah',600,500)
    feast_data = open('%s/data/%s'%(the_path,options.data),'r')

    # Collect datapoints for Rcm calculation
    data_rcm = {'x':[],'y':[],'xerr':[],'yerr':[]}

    # For EoS
    data_rc  = {'x':[],'y':[],'xerr':[],'yerr':[]}

    # power numbers
    diagonal_power_numbers = dict()
    diagonal_temp_numbers = dict()
    
    # Individual datapoints
    power_keys = ['ABC','HCC','FEAST','Tape','HVMUX','R_{HV}']
    measured_keys = ['ABC','HCC','FEAST','Sensor','AMAC','EoS']

    poweredby_tempmeas = dict()
    for p in power_keys :
        poweredby_tempmeas[p] = dict()
        for t in measured_keys :
            if t == p : 
                continue
            poweredby_tempmeas[p][t] = {'x':[],'y':[],'xerr':[],'yerr':[]}

    max_x = 0
    has_amac = False
    has_eos  = False

    for line in feast_data :
        line = line.replace('\n','')
        datapoint = line.split()
        if not datapoint : continue

        try :
            float(datapoint[0])
        except ValueError : 
            continue

        for i in range(len(datapoint)) :
            datapoint[i] = float(datapoint[i])
        datapoint[4] = int(datapoint[4])

        # find power source
        is_on = list(x > 0 for x in datapoint[:4])
        data_power_source = power_keys[is_on.index(True)]
        if data_power_source == 'Tape' and datapoint[3] == 0.25 : data_power_source = 'HVMUX'
        if data_power_source == 'Tape' and datapoint[3] == 0.01 : data_power_source = 'R_{HV}'

        # find measured item
        data_measured_item = measured_keys[datapoint[4]-1]

        # Rcm
        if data_measured_item == 'ABC' and data_power_source == 'ABC' :
            diagonal_power_numbers['ABC'] = datapoint[0]
            diagonal_temp_numbers['ABC'] = datapoint[5]
            continue
        if data_measured_item == 'HCC' and data_power_source == 'HCC' :
            diagonal_power_numbers['HCC'] = datapoint[1]
            diagonal_temp_numbers['HCC'] = datapoint[5]
            continue
        if data_measured_item == 'FEAST' and data_power_source == 'FEAST' :
            diagonal_power_numbers['FEAST'] = datapoint[2]
            diagonal_temp_numbers['FEAST'] = datapoint[5]
            continue
        # datapoint[4] == 4 is the measured sensor temperature

        # Turn off AMAC for now
        if data_measured_item == 'AMAC' :
            # has_amac = True
            continue

        xval = max(datapoint[0],datapoint[1],datapoint[2],datapoint[3])

        if data_measured_item == 'EoS' :
            has_eos = True
            data_rc['x'].append(xval)
            data_rc['xerr'].append(xval)
            data_rc['y'].append(datapoint[5])
            data_rc['yerr'].append(datapoint[6])
            continue

        data_rcm['x'].append(xval)
        data_rcm['xerr'].append(0)
        data_rcm['y'].append(datapoint[5])
        if len(datapoint) >= 7 :
            data_rcm['yerr'].append(datapoint[6])
        else :
            data_rcm['yerr'].append(0)

        # print data_power_source,data_measured_item,datapoint

        # x offset is just so the points don't overlap. Does not affect any fit result.
        offset = (datapoint[4]-3)*0.01

        poweredby_tempmeas[data_power_source][data_measured_item]['x'   ].append(data_rcm['x'   ][-1]+offset)
        poweredby_tempmeas[data_power_source][data_measured_item]['xerr'].append(data_rcm['xerr'][-1])
        poweredby_tempmeas[data_power_source][data_measured_item]['y'   ].append(data_rcm['y'   ][-1])
        poweredby_tempmeas[data_power_source][data_measured_item]['yerr'].append(data_rcm['yerr'][-1])

        max_x = max(max_x,data_rcm['x'][-1])
        
    data_rcm_graph = MakeGraph('data_rcm_graph','Power vs temperature','Power delivered [W]','Temperature [#circ^{}C]',data_rcm['x'],data_rcm['y'])
    #data_rcm_graph.Draw('ap')
    the_fit = ROOT.TF1('Fit for Rcm','[0]*x',0,1.1*max_x)
    data_rcm_graph.Fit(the_fit,'Q')
    the_fit_error = ROOT.TGraphErrors(2,array('d',[0,1.1*max_x]),
                                      array('d',[0,the_fit.Eval(1.1*max_x)]),
                                      array('d',[0,0]),
                                      array('d',[0,the_fit.Eval(1.1*max_x)*0.2])
                                      )
    the_fit_error.SetFillColor(ROOT.kBlue-10)
    the_fit_error.SetLineColor(ROOT.kBlack)
    the_fit_error.SetLineWidth(0)
    the_fit_error.Draw('ae3')
    the_fit.SetLineWidth(2)
    the_fit.Draw('lsames')
    the_fit_error.GetHistogram().GetXaxis().SetTitle('Power delivered [W]')
    the_fit_error.GetHistogram().GetYaxis().SetTitle('T_{meas} #minus T_{C} [#circ^{}C]')

    styles = {'ABC'   :20,
              'HCC'   :34,
              'FEAST' :22,
              'Tape'  :23,
              'HVMUX' :29,
              'R_{HV}':33,
              }

    colors = {'ABC'   :ROOT.kRed   +1,
              'HCC'   :ROOT.kBlue  +1,
              'FEAST' :ROOT.kGreen +1,
              'Sensor':ROOT.kOrange+1,
              'AMAC'  :ROOT.kCyan  +1,
              'EoS'   :ROOT.kMagenta+1,
              }

    gr = []
    for p in power_keys :
        for t in measured_keys :
            if t == p : 
                continue
            if not poweredby_tempmeas[p][t]['x'] or not poweredby_tempmeas[p][t]['x'] :
                #print 'Warning: point Power: %s Temp: %s seems to be missing:'%(p,t),
                #print poweredby_tempmeas[p][t]['x'],poweredby_tempmeas[p][t]['y']
                continue
            try :
                gr.append(MakeGraph('%s_%s'%(p,t),'%s_%s'%(p,t),
                                    'Power delivered [W]',
                                    'Temperature [#circ^{}C]',
                                    poweredby_tempmeas[p][t]['x'],
                                    poweredby_tempmeas[p][t]['y'],
                                    poweredby_tempmeas[p][t]['xerr'],
                                    poweredby_tempmeas[p][t]['yerr']
                                    ))
                gr[-1].SetMarkerStyle(styles[p])
                gr[-1].SetLineWidth(2)
                if gr[-1].GetMarkerStyle() in [29,33] :
                    gr[-1].SetMarkerSize(1.3)
                gr[-1].SetMarkerColor(colors[t])
                gr[-1].SetLineColor(colors[t])
                gr[-1].Draw('p')
            except KeyError :
                print p,t,'does not have a datapoint...?'

    def MakeDummy(color,style) :
        ret = ROOT.TGraph(1,array('d',[1]),array('d',[1]))
        ret.SetMarkerColor(color)
        ret.SetFillColor(color)
        ret.SetMarkerStyle(style)
        ret.SetLineWidth(0)
        if ret.GetMarkerStyle() in [29,33,21] :
            ret.SetMarkerSize(1.3)

        return ret

    dummy_powered = dict()
    dummy_powered['ABC']    = MakeDummy(ROOT.kGray+1,styles['ABC']   )
    dummy_powered['HCC']    = MakeDummy(ROOT.kGray+1,styles['HCC']   )
    dummy_powered['FEAST']  = MakeDummy(ROOT.kGray+1,styles['FEAST'] )
    dummy_powered['Tape']   = MakeDummy(ROOT.kGray+1,styles['Tape']  )
    dummy_powered['HVMUX']  = MakeDummy(ROOT.kGray+1,styles['HVMUX'] )
    dummy_powered['R_{HV}'] = MakeDummy(ROOT.kGray+1,styles['R_{HV}'])

    dummy_measured = dict()
    dummy_measured['ABC']    = MakeDummy(colors['ABC']   ,21)
    dummy_measured['HCC']    = MakeDummy(colors['HCC']   ,21)
    dummy_measured['FEAST']  = MakeDummy(colors['FEAST'] ,21)
    dummy_measured['Sensor'] = MakeDummy(colors['Sensor'],21)

    if has_amac :
        dummy_measured['AMAC'] = MakeDummy(colors['AMAC']  ,21)
    else :
        measured_keys.pop(measured_keys.index('AMAC'))

    # Skip EoS in plot
    measured_keys.pop(measured_keys.index('EoS'))

    leg = ROOT.TLegend(0.60,0.16,0.87,0.41)
    for k in power_keys :
        leg.AddEntry(dummy_powered[k],"%s power source"%(k),"p")
    PlotUtils.SetStyleLegend(leg)
    leg.SetMargin(.15)

    leg2 = ROOT.TLegend(0.20,0.70,0.47,0.91)
    for k in measured_keys :
        leg2.AddEntry(dummy_measured[k],"%s measured temperature"%(k),"f")
    PlotUtils.SetStyleLegend(leg2)
    leg2.SetMargin(.12)
    leg2.AddEntry(the_fit,'T(P)=P#times^{}R_{cm}; Fit result: ^{}R_{cm}=%2.3f'%(the_fit.GetParameter(0)),'l')
    leg2.AddEntry(the_fit_error,'#pm^{}20%','f')

    leg.Draw()
    leg2.Draw()

    taxisfunc.AutoFixYaxis(c,minzero=True,ignorelegend=True)

    outputpath = '%s/plots/ThermalImpedances'%(the_path)
    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    outfiletag = options.data.replace('ThermalImpedances_','').replace('.txt','')
    c.Print('%s/ThermalImpedanceFit_%s_Rcm.eps'%(outputpath,outfiletag))

    Rc = 0
    if has_eos :
        c.Clear()
        data_rc_graph = MakeGraph('data_rc_graph','Power vs temperature','Power delivered [W]','Temperature [#circ^{}C]',data_rc['x'],data_rc['y'])
        the_rc_fit = ROOT.TF1('Fit for Rc','[0]*x',0,1.1*max_x)
        data_rc_graph.Fit(the_rc_fit,'Q')
        Rc = the_rc_fit.GetParameter(0)
        the_rc_fit.Draw()
        data_rc_graph.Draw('p')
        taxisfunc.AutoFixYaxis(c,minzero=True,ignorelegend=True)
        c.Print('%s/ThermalImpedanceFit_%s_EoS.eps'%(outputpath,outfiletag))

    # Calculate Rhcc, Rabc, Rfeast
    Rcm = the_fit.GetParameter(0)
    for component in ['ABC','HCC','FEAST'] :
        R_component = diagonal_temp_numbers[component]/float(diagonal_power_numbers[component]) - Rcm
        print 'ThermalImpedances.r%s: %2.3f'%(component.lower(),R_component)
    print 'ThermalImpedances.rc: %2.3f'%(    Rc)
    print '# Rc is 0 ( no EoS anyway) except in R5, where it is calculated using the EoS.'
    print 'ThermalImpedances.rm: %2.3f'%(Rcm-Rc)
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--data',type='string',default='ThermalImpedances_ShortStripEOS.txt',dest='data',help='Input data')

    options,args = p.parse_args()
    
    main(options,args)
