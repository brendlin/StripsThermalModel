#!/usr/bin/env python

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
    data_rcm = {'x':[],'y':[]}
    
    # Individual datapoints
    power_keys = ['ABC','HCC','FEAST','Tape','HVMUX','R_{HV}']
    measured_keys = ['ABC','HCC','FEAST','Sensor']

    poweredby_tempmeas = dict()
    for p in power_keys :
        poweredby_tempmeas[p] = dict()
        for t in measured_keys :
            if t == p : 
                continue
            poweredby_tempmeas[p][t] = {'x':[],'y':[]}

    max_x = 0

    for line in feast_data :
        line = line.replace('\n','')
        datapoint = line.split()
        if not datapoint : continue

        try :
            float(datapoint[0])
        except ValueError : 
            continue

        for i in range(6) :
            datapoint[i] = float(datapoint[i])
        datapoint[4] = int(datapoint[4])

        # Rcm
        if datapoint[4] == 1 and datapoint[0] != 0 :
            continue
        if datapoint[4] == 2 and datapoint[1] != 0 :
            continue
        if datapoint[4] == 3 and datapoint[2] != 0 :
            continue
        # datapoint[4] == 4 is the measured sensor temperature

        # Turn off AMAC for now
        if datapoint[4] == 5 :
            continue

        data_rcm['x'].append(max(datapoint[0],datapoint[1],datapoint[2],datapoint[3]))
        data_rcm['y'].append(datapoint[5])

        is_on = list(x > 0 for x in datapoint[:4])
        data_power_source = power_keys[is_on.index(True)]
        if data_power_source == 'Tape' and datapoint[3] == 0.25 : data_power_source = 'HVMUX'
        if data_power_source == 'Tape' and datapoint[3] == 0.01 : data_power_source = 'R_{HV}'

        data_measured_item = measured_keys[datapoint[4]-1]
        
        # print data_power_source,data_measured_item,datapoint

        poweredby_tempmeas[data_power_source][data_measured_item]['x'].append(data_rcm['x'][-1])
        poweredby_tempmeas[data_power_source][data_measured_item]['y'].append(data_rcm['y'][-1])

        max_x = max(max_x,data_rcm['x'][-1])
        
    data_rcm_graph = MakeGraph('data_rcm_graph','Power vs temperature','Power delivered [W]','Temperature [#circ^{}C]',data_rcm['x'],data_rcm['y'])
    #data_rcm_graph.Draw('ap')
    the_fit = ROOT.TF1('Fit for Rcm','[0]*x',0,1.1*max_x)
    data_rcm_graph.Fit(the_fit)
    the_fit.Draw()
    the_fit.GetHistogram().GetXaxis().SetTitle('Power delivered [W]')
    the_fit.GetHistogram().GetYaxis().SetTitle('T_{meas} #minus T_{C} [#circ^{}C]')

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
              }

    gr = []
    for p in power_keys :
        for t in measured_keys :
            if t == p : 
                continue
            if not poweredby_tempmeas[p][t]['x'] or not poweredby_tempmeas[p][t]['x'] :
                print 'Warning: point Power: %s Temp: %s seems to be missing:'%(p,t),
                print poweredby_tempmeas[p][t]['x'],poweredby_tempmeas[p][t]['y']
                continue
            try :
                gr.append(MakeGraph('%s_%s'%(p,t),'%s_%s'%(p,t),'Power delivered [W]','Temperature [#circ^{}C]',poweredby_tempmeas[p][t]['x'],poweredby_tempmeas[p][t]['y']))
                gr[-1].SetMarkerStyle(styles[p])
                if gr[-1].GetMarkerStyle() in [29,33] :
                    gr[-1].SetMarkerSize(1.3)
                gr[-1].SetMarkerColor(colors[t])
                gr[-1].Draw('p')
            except KeyError :
                print p,t,'does not have a datapoint...?'

    def MakeDummy(color,style) :
        ret = ROOT.TGraph(1,array('d',[1]),array('d',[1]))
        ret.SetMarkerColor(color)
        ret.SetMarkerStyle(style)
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
    
    leg = ROOT.TLegend(0.60,0.16,0.87,0.41)
    for k in power_keys :
        leg.AddEntry(dummy_powered[k],"%s power source"%(k),"p")
    PlotUtils.SetStyleLegend(leg)
    leg.SetMargin(.15)

    leg2 = ROOT.TLegend(0.20,0.75,0.47,0.91)
    for k in measured_keys :
        leg2.AddEntry(dummy_measured[k],"%s measured temperature"%(k),"p")
    PlotUtils.SetStyleLegend(leg2)
    leg2.SetMargin(.15)

    text = ROOT.TLegend(0.21,0.70,0.34,0.75)
    PlotUtils.SetStyleLegend(text)
    text.AddEntry(0,'T(P)=P#times^{}R_{cm}; Fit result: ^{}R_{cm}=%2.3f'%(the_fit.GetParameter(0)),'')

    leg.Draw()
    leg2.Draw()
    text.Draw()

    taxisfunc.AutoFixYaxis(c,minzero=True,ignorelegend=True)

    outputpath = '%s/plots/ThermalImpedances'%(the_path)
    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    outfiletag = options.data.replace('ThermalImpedances_','').replace('.txt','')
    c.Print('%s/ThermalImpedanceFit_%s_Rcm.eps'%(outputpath,outfiletag))
    
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--data',type='string',default='ThermalImpedances_ShortStripEOS.txt',dest='data',help='Input data')

    options,args = p.parse_args()
    
    main(options,args)
