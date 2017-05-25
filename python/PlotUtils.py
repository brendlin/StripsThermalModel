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
    
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)
    
def MakeGraph(name,title,xtitle,ytitle,xlist,ylist) :
    from array import array

    if (len(xlist) != len(ylist)) :
        print 'Error! List sizes are not correct for graph %s (%d vs %d)'%(name,len(xlist),len(ylist))
        import sys; sys.exit()
    graph = ROOT.TGraph(len(xlist),array('d',xlist),array('d',ylist))
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
