#!/usr/bin/env python

import ROOT
import os,sys

# To later defined gStyle common stuff for all plots

# Does not seem to work...
def ApplyGlobalStyle() :
    mystyle = ROOT.TStyle("mystyle","mystyle")
    mystyle.SetMarkerStyle(20)
    mystyle.SetMarkerSize(1)
    mystyle.SetCanvasColor(0)
    mystyle.SetPadBorderMode(0)
    mystyle.SetCanvasBorderMode(0)
    mystyle.SetFrameBorderMode(0)
    mystyle.SetOptTitle(0)

    mystyle.SetPadTopMargin(0.05)
    mystyle.SetPadRightMargin(0.05)
    mystyle.SetPadBottomMargin(0.11)
    mystyle.SetPadLeftMargin(0.16)

    # all axes
    mystyle.SetTitleSize  (22   ,'xyz')
    mystyle.SetTitleFont  (43   ,'xyz')
    mystyle.SetLabelSize  (22   ,'xyz')
    mystyle.SetLabelFont  (43   ,'xyz')

    # x axis
    mystyle.SetTitleXOffset(1.0)
    mystyle.SetLabelOffset(0.003,'x')
    # y axis
    mystyle.SetTitleOffset(1.75 ,'y')
    mystyle.SetLabelOffset(0.003,'y')

    # line styles for the extended model
    mystyle.SetLineStyleString(10,'60 10');
    mystyle.SetLineStyleString(11,'50 10');
    mystyle.SetLineStyleString(12,'40 10');
    mystyle.SetLineStyleString(13,'30 10');
    mystyle.SetLineStyleString(14,'20 10');

    mystyle.SetLineStyleString(15,'30 10');
    mystyle.SetLineStyleString(16,'20 10');
    mystyle.SetLineStyleString(17,'10 10');
    mystyle.SetLineStyleString(18, '5 10');

    # For intermediate modules
    mystyle.SetLineStyleString(19, '5 5');

    ROOT.gROOT.SetStyle("mystyle")

def SetStyleTitles(tobject, title, xtitle, ytitle) :
    
    print "Setting titles for plot: %s" % title
    
    tobject.SetTitle(title)
    tobject.GetXaxis().SetTitle(xtitle)
    tobject.GetXaxis().SetTitleOffset(1.3)
    tobject.GetYaxis().SetTitle(ytitle)
    tobject.GetYaxis().SetTitleOffset(1.3)
    
# 2D objects (with z axis)
def Set2DStyleTitles(tobject, title, xtitle, ytitle, ztitle) :
    
    print "Setting titles for plot: %s" % title
    
    tobject.SetTitle(title)
    tobject.GetXaxis().SetTitle(xtitle)
    tobject.GetXaxis().SetTitleOffset(1.7)
    tobject.GetYaxis().SetTitle(ytitle)
    tobject.GetYaxis().SetTitleOffset(1.7)
    tobject.GetZaxis().SetTitle(ztitle)
    tobject.GetZaxis().SetTitleOffset(1.4)
    
    
def SetStyleLegend(leg) :
    
    leg.SetName('legend')
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)
    
def MakeGraph(name,title,xtitle,ytitle,xlist,ylist,xerrlist=None,yerrlist=None) :
    from array import array

    if (len(xlist) != len(ylist)) :
        print 'Error! List sizes are not correct for graph %s (%d vs %d)'%(name,len(xlist),len(ylist))
        import sys; sys.exit()
    if not xerrlist and not yerrlist :
        graph = ROOT.TGraph(len(xlist),array('d',xlist),array('d',ylist))
    else :
        graph = ROOT.TGraphErrors(len(xlist),array('d',xlist),array('d',ylist),array('d',xerrlist),array('d',yerrlist))
    graph.SetName(name)
    graph.SetTitle(title)
    graph.GetXaxis().SetTitle(xtitle)
    graph.GetYaxis().SetTitle(ytitle)
    graph.SetLineWidth(3)
    return graph

def GetCoolingOutputTag(cooling_option) :
    if 'flat' in cooling_option :
        return cooling_option.replace('flat','flat_').replace('-','m')
    if 'ramp' in cooling_option :
        return cooling_option.replace('ramp','ramp_').replace('-','m')
    return 'unknownScenario'

def GetCoolingScenarioLabel(cooling_option) :
    if 'flat' in cooling_option :
        temp = int(cooling_option.replace('flat',''))
        return ('Flat %s#circ cooling scenario'%(temp)).replace('-','#minus')
    if 'ramp' in cooling_option :
        temp = int(cooling_option.replace('ramp',''))
        return ('Ramp %s#circ cooling scenario'%(temp)).replace('-','#minus')
    return 'unknown cooling scenario'

def AddRunParameterLabels(legend,additionalinfo=[],wrap=False) :
    import SafetyFactors
    import CoolantTemperature
    layout,fluence,thermalimpedance,currenta,currentd,vbias = '','','','','',''

    if SafetyFactors.safetyfluence :
        fluence = 'flux_{ }#times^{ }%2.1f;  '%(SafetyFactors.safetyfluence + 1.0)
    if SafetyFactors.safetythermalimpedance :
        thermalimpedance = '^{}R_{thermal }#times^{ }%2.1f;  '%(SafetyFactors.safetythermalimpedance + 1.0)
    if SafetyFactors.safetycurrentd :
        currentd = 'I_{dig}#times%2.2f;  '%(SafetyFactors.safetycurrentd + 1.0)
    if SafetyFactors.safetycurrenta :
        currenta = '^{}I_{a }#times^{ }%2.2f;  '%(SafetyFactors.safetycurrenta + 1.0)
    if (SafetyFactors.vbias) != 500. :
        vbias = '^{}V_{bias}=^{ }%2.0f;  '%(SafetyFactors.vbias)

    #text = ('%s%s%s%s%s'%(layout,fluence,thermalimpedance,current,vbias)).rstrip('; ')
    sf1 = ('%s%s%s'    %(layout,fluence,thermalimpedance)).rstrip('; ')
    sf2 = ('%s%s%s'    %(                               currentd,currenta,vbias)).rstrip('; ')
    no_factors = ' none' if (not sf1 and not sf2) else ''

    nlines = 0
    if True :
        legend.AddEntry(0,GetCoolingScenarioLabel(CoolantTemperature.cooling),'')
        nlines += 1
    if True :
        legend.AddEntry(0,'Safety factors:%s'%(no_factors),'')
        nlines += 1
    if sf1 :
        legend.AddEntry(0,sf1,'')
        nlines += 1
    if sf2 :
        legend.AddEntry(0,sf2,'')
        nlines += 1
    for addinfo in additionalinfo :
        if not addinfo :
            continue

        add_label = [addinfo,'']
        if wrap :
            while(len(add_label[0]) > 28) :
                tmp = add_label[0].split(' ')
                add_label[0] = ' '.join(tmp[:-1])
                add_label[1] = ' '.join([tmp[-1],add_label[1]])

        legend.AddEntry(0,add_label[0],'')
        nlines += 1
        if add_label[1] :
            legend.AddEntry(0,add_label[1],'')
            nlines += 1

    while nlines < 5 :
        legend.AddEntry(0,'','')
        nlines += 1

    return

def ColorPalette() :
    from ROOT import kBlack,kRed,kBlue,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow
    return [kBlack+0,kRed+1,kAzure-2,kGreen-6,kMagenta-6,kCyan+1,kOrange+1
            ,kGray+1,kRed-6,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
            ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
            ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ]

def ColorGradient(i,ntotal) :
    import ROOT
    if ntotal == 1 :
        return ROOT.kBlack
    from array import array
    NCont = 255
    # Blue -> Green -> Red
#     NRGBs = 3
#     stops = array('d',[ 0.00, 0.50, 1.00 ])
#     red   = array('d',[ 0.00, 0.50, 1.00 ])
#     green = array('d',[ 0.00, 1.00, 0.00 ])
#     blue  = array('d',[ 1.00, 0.50, 0.00 ])
#     ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)

    # Some weird default
#     NRGBs = 5
#     stops = array('d',[  0.00, 0.34, 0.61, 0.84, 1.00 ])
#     red   = array('d',[  0.00, 0.00, 0.87, 1.00, 0.51 ])
#     green = array('d',[  0.00, 0.81, 1.00, 0.20, 0.00 ])
#     blue  = array('d',[  0.51, 1.00, 0.12, 0.00, 0.00 ])
#     ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)

    # Green -> Red
#     NRGBs = 2
#     stops = array('d',[ 0.00,1.00 ])
#     red   = array('d',[ 0.50,1.00 ])
#     green = array('d',[ 1.00,0.00 ])
#     blue  = array('d',[ 0.50,0.00 ])
#     ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)

    # Blue -> Red (but it doesn't go through white)
    NRGBs = 2
    stops = array('d',[ 0.00,1.00 ])
    red   = array('d',[ 0.10,0.90 ])
    green = array('d',[ 0.10,0.10 ])
    blue  = array('d',[ 1.00,0.10 ])
    ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)

    #ROOT.gStyle.SetPalette(ROOT.kThermometer)
    ROOT.gStyle.SetNumberContours(255)
    the_int = int(254*i/float(ntotal-1))
    return ROOT.gStyle.GetColorPalette(the_int)

def AddToStack(stack,leg,h) :
    h.SetFillColor(ColorPalette()[stack.GetNhists()+1])
    h.SetLineWidth(2)
    h.SetDrawOption('l')
    stack.Add(h)
    #leg.AddEntry(h,h.GetTitle().replace('power ','').replace('power',''),'f')
    return h

def MakePlotMinimumZero(plotname) :
    return plotname in ['tc_headroom','idig','ifeast','ifeast_in',
                        'phv_wleakage','phvr','phvmux','hv_power_resistors','pmodule_noHV',
                        'pmodule','powertotal','itape','itape_cumulative','itape_eos','ptape','ptape_cumulative','pstave',
                        'phvtotal','ppetal']

def GetPlotForcedMinimum(plotname) :
    return {'qsensor_headroom': 0.09}.get(plotname,None)

def GetOutputPath(modulename,options) :
    just_outside_git_repository = os.getcwd().split('/StripsThermalModel')[0]

    # Move output path outside code directory
    outputpath = '%s/plots/%s'%(just_outside_git_repository,modulename)

    # If a different output name is specified
    if hasattr(options,'outdir') :
        outputpath = '%s/plots/%s'%(just_outside_git_repository,options.outdir)

    if not os.path.exists(outputpath) :
        os.makedirs(outputpath)

    # print '%s output written to %s'%(modulename,outputpath)
    return outputpath

# A quick, useful helper function
def GetResultDictIndex(names,ring_mod,disk_layer) :
    try :
        index = names.index('R%dD%d'%(ring_mod,disk_layer))
    except ValueError :
        index = names.index('L%dM%d'%(disk_layer,ring_mod))
    return index

# A quick, useful helper function
def GetResultDictIndexInverted(names,ring_lay,disk_mod,isEndcap) :
    ring_mod   = ring_lay if isEndcap else disk_mod
    disk_layer = disk_mod if isEndcap else ring_lay
    try :
        index = names.index('R%dD%d'%(ring_mod,disk_layer))
    except ValueError :
        index = names.index('L%dM%d'%(disk_layer,ring_mod))
    return index
