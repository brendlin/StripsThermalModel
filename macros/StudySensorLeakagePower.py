#!/usr/bin/env python

import ROOT
import os,sys
from array import array

the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

# Dummy config must be loaded before loading any other module.
import python.Config as Config
Config.SetConfigFile('%s/data/%s'%(the_path,'Barrel_B1.config'),doprint=False)
TIDpessimistic = Config.GetBool('SafetyFactors.TIDpessimistic',False)

import python.SafetyFactors as SafetyFactors
import python.GlobalSettings as GlobalSettings
import python.SensorLeakage as SensorLeakage
import python.PlotUtils as PlotUtils


#-----------------------------------------------
def main(options,args) :

    PlotUtils.ApplyGlobalStyle()
    
    c = ROOT.TCanvas('SensorLeakage','Sensor Leakage',600,500)
    
    gr = dict()
    pts = dict()
    pts['fluence']  = []
    pts['700V']     = []
    pts['new500V']  = []
    pts['old500V']  = []
    
    timesMicroAmp = 1000000.
    
    for f in range(61) :
        f = f/10. # Step in 1/10 steps, to get features at low fluence
        # Output in microA/cm^2 
        pts['fluence'].append(f) # x axis = fluence in unit 10^14 neq/cm^2
        pts['700V'].append(timesMicroAmp* SensorLeakage.iref700(f*10**14))
        pts['new500V'].append(timesMicroAmp* SensorLeakage.iref(f*10**14))
        pts['old500V'].append(timesMicroAmp* SensorLeakage.oldiref(f*10**14))
    
    label = {'700V': '700 V','new500V': '500 V','old500V': 'old 500 V'}
    #colors = {'700V':ROOT.kGreen,'new500V':ROOT.kOrange,'old500V':ROOT.kBlue}
    leg = ROOT.TLegend(0.2,0.7,0.5,0.9)
    PlotUtils.SetStyleLegend(leg)
    
    firstPlot = True
    drawOption = 'al'
    
    for i,p in enumerate(['700V', 'new500V']) :
        gr[p] = PlotUtils.MakeGraph(p, 'Sensor Leakage Power', 'Fluence [10^{14} n_{eq} /cm^{2}]', 'I_{ref} [#muA/cm^{2}]', pts['fluence'], pts[p])
        gr[p].SetLineColor(PlotUtils.ColorPalette()[i])
        leg.AddEntry(gr[p], label[p], 'l')
        
        gr[p].Draw(drawOption)
        
        if firstPlot :
            firstPlot = False
            drawOption = 'l'
    
    leg.Draw()
    c.Print('%s/plots/SensorLeakage/SensorLeakagePower.eps'%(the_path))
    return

#-----------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    
    options,args = p.parse_args()
    
    main(options,args)
