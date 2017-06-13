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
    outputtag = {
        'flat-25':'flat_m25',
        'flat-35':'flat_m35',
        'ramp-25':'ramp_m25',
        'ramp-35':'ramp_m35'
        }.get(cooling_option,'unknownScenario')
    return outputtag

def GetCoolingScenarioLabel(cooling_option) :
    scenariolabel = {
        'flat-25':'Flat #minus25#circ cooling scenario',
        'flat-35':'Flat #minus35#circ cooling scenario',
        'ramp-25':'Ramp #minus25#circ cooling scenario',
        'ramp-35':'Ramp #minus35#circ cooling scenario',
        }.get(cooling_option,'unknown cooling scenario')
    return scenariolabel

def AddRunParameterLabels(legend,additionalinfo=[]) :
    import SafetyFactors
    import CoolantTemperature
    layout,fluence,thermalimpedance,current,vbias = '','','','',''

    if SafetyFactors.safetylayout :
        layout = 'SF{#font[52]{Layout}}=%2.1f;  '%(SafetyFactors.safetylayout + 1.0)
    if SafetyFactors.safetyfluence :
        fluence = 'SF_{#font[52]{flux}}=%2.1f;  '%(SafetyFactors.safetyfluence + 1.0)
    if SafetyFactors.safetythermalimpedance :
        thermalimpedance = 'SF_{#font[52]{RThermal}}=%2.1f;  '%(SafetyFactors.safetythermalimpedance + 1.0)
    if SafetyFactors.safetycurrent :
        current = 'SF_{#font[52]{current}}=%2.1f;  '%(SafetyFactors.safetycurrent + 1.0)
    if (SafetyFactors.vbiasscale - 1.) != 0 :
        vbias = 'SF_{#font[52]{Impedance}}=%2.1f;  '%(SafetyFactors.vbiasscale)

    #text = ('%s%s%s%s%s'%(layout,fluence,thermalimpedance,current,vbias)).rstrip('; ')
    sf1 = ('%s%s%s'    %(layout,fluence,thermalimpedance)).rstrip('; ')
    sf2 = ('%s%s'      %(                                current,vbias)).rstrip('; ')
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
        legend.AddEntry(0,addinfo,'')
        nlines += 1

    while nlines < 5 :
        legend.AddEntry(0,'','')
        nlines += 1

    return

def ColorPalette() :
    from ROOT import kBlack,kRed,kBlue,kAzure,kGreen,kMagenta,kCyan,kOrange,kGray,kYellow
    return [kBlack+0,kRed+1,kAzure-2,kGreen+1,kMagenta+1,kCyan+1,kOrange+1
            ,kGray+1,kRed+3,kBlue+3,kGreen+3,kMagenta+3,kCyan+3,kOrange+3
            ,kGray,kRed-7,kBlue-7,kGreen-7,kMagenta-7,kCyan-7,kOrange-7
            ,kYellow+2,kRed-5,kBlue-5,kGreen-5,kMagenta-5,kCyan-5,kOrange-5
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ,21,22,23,24,25,26,27,28,29,30
            ]

def AddToStack(stack,leg,h) :
    h.SetFillColor(ColorPalette()[stack.GetNhists()+1])
    h.SetLineWidth(2)
    h.SetDrawOption('l')
    stack.Add(h)
    leg.AddEntry(h,h.GetTitle().replace('power ','').replace('power',''),'f')
