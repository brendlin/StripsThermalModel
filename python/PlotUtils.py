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
    
