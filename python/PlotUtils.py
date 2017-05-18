#!/usr/bin/env python

import ROOT
import os,sys

# To later defined gStyle common stuff for all plots


def SetStyleTitles(tobject, title, xtitle, ytitle) :
    
    print "Setting titles for plot: %s" % title
    
    #ROOT.gStyle.SetTitleOffset(1.2)
    
    tobject.SetTitle(title)
    tobject.GetXaxis().SetTitle(xtitle)
    tobject.GetXaxis().SetTitleOffset(1.3)
    tobject.GetYaxis().SetTitle(ytitle)
    tobject.GetYaxis().SetTitleOffset(1.3)
    
