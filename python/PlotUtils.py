#!/usr/bin/env python

import ROOT
import os,sys

# To later defined gStyle common stuff for all plots

# Does not seem to work...
def ApplyGlobalStyle() :
    ROOT.gStyle.SetMarkerSize(20)
    ROOT.gStyle.SetMarkerSize(1)

def SetStyleTitles(tobject, title, xtitle, ytitle) :
    
    print "Setting titles for plot: %s" % title
    
    #ROOT.gStyle.SetTitleOffset(1.2)
    
    tobject.SetTitle(title)
    tobject.GetXaxis().SetTitle(xtitle)
    tobject.GetXaxis().SetTitleOffset(1.3)
    tobject.GetYaxis().SetTitle(ytitle)
    tobject.GetYaxis().SetTitleOffset(1.3)
    
def SetStyleLegend(leg) :
    
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)
    
