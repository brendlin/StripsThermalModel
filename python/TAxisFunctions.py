
def AutoFixYaxis(can,ignorelegend=False,forcemin=None,minzero=False) :
    #
    # Makes space for text as well!
    #
    can.Update()
    import ROOT
    import math
    # maxy_frac is the fractional maximum of the y-axis stuff.
    maxy_frac = 1
    #
    # Now we make space for any text we drew on the canvas, and
    # also the Legend
    #
    plots_exist = False
    tframe_height = 1-can.GetTopMargin()-can.GetBottomMargin()
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),ROOT.TH1) :
            plots_exist = True
        if issubclass(type(i),ROOT.TF1) :
            plots_exist = True
        if issubclass(type(i),ROOT.TGraph) :
            plots_exist = True
        if (ignorelegend) and ('legend' in i.GetName()) :
            continue
        if type(i) == type(ROOT.TFrame()) :
            continue
        if hasattr(i,'GetY1NDC') :
            maxy_frac = min(maxy_frac,i.GetY1NDC())
        if hasattr(i,'GetY') :
            maxy_frac = min(maxy_frac,i.GetY())
    if not plots_exist :
        print 'Your plot %s has nothing in it. AutoFixYaxis() is Doing nothing.'%(can.GetName())
        return
    (miny,maxy) = GetYaxisRanges(can,check_all=True)
    # print 'AutoFixAxes0',miny,maxy
    if miny == 0 and maxy == 0 :
        return
    miny = (0.95*miny) if (miny>0) else (1.05*miny)
    maxy = (1.05*maxy) if (maxy>0) else (0.95*maxy)
    maxy_frac = maxy_frac-can.GetBottomMargin()

    if maxy_frac < 0 :
        print 'Error in AutoFixAxes - somehow there is no more room for your plot.'
        print '(Bad legend placement?)'
        return

    if can.GetLogy() :
        # special treatment for log plots
        miny = 0.85*MinimumForLog(can)
        # some orders of magnitude *above* miny, making room for text
        orderofmagnitude_span = math.log(maxy/miny)/math.log(10)
        orderofmagnitude_span = 1.1*orderofmagnitude_span*tframe_height/maxy_frac
        maxy = miny*math.pow(10,orderofmagnitude_span)
    else :
        # scale to make space for text
        maxy_frac = maxy_frac-.02
        maxy = tframe_height*(maxy-miny)/float(maxy_frac)+miny
        # round y axis to nice round numbers
        (miny,maxy) = NearestNiceNumber(miny,maxy)
    # print 'AutoFixAxes',miny,maxy
#     if symmetrize :
#         (miny,maxy) = -max(math.fabs(miny),math.fabs(maxy)),max(math.fabs(miny),math.fabs(maxy))
    if minzero == True :
        miny = 0
    if forcemin :
        miny = forcemin
    SetYaxisRanges(can,miny,maxy)
    return miny,maxy

##
## Snap to base-ten-centric numbers
##
def NearestNiceNumber(miny,maxy) :
    import math
    round_number = 10 # or 5 perhaps
    smallest_increment = pow(10,math.floor(math.log((maxy-miny))/math.log(10))-2)
    if miny > 0 :
        newminy = round_number*smallest_increment*       int(miny/(round_number*smallest_increment))
    else :
        newminy = round_number*smallest_increment*math.floor(miny/(round_number*smallest_increment))
    newmaxy     = round_number*smallest_increment*math.ceil (maxy/(round_number*smallest_increment))
    # print 'NearestNiceNumber',newminy,newmaxy
    return newminy,newmaxy

##
## Find the non-zero y-axis minimum of plot content.
##
def MinimumForLog(can) :
    from ROOT import TGraph,TH1,TMath,THStack
    ymin = 999999999
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            for ii in range(i.GetN()) :
                y = i.GetY()[ii]
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),TH1) :
            for bin in range(i.GetNbinsX()) :
                y = i.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
        if issubclass(type(i),THStack) :
            j = i.GetHists()[0]
            for bin in range(j.GetNbinsX()) :
                y = j.GetBinContent(bin+1)
                if y <= 0 :
                    y = ymin
                ymin = min(ymin,y)
    # print 'MinimumForLog',ymin
    return ymin

##
## Set the x-axis ranges of a canvas
##
def SetYaxisRanges(can,ymin,ymax) :
    if can.GetPrimitive('pad_top') :
        SetYaxisRanges(can.GetPrimitive('pad_top'),ymin,ymax)
    from ROOT import TGraph,TH1,THStack
    yaxis = 0
    for i in can.GetListOfPrimitives() :
        if issubclass(type(i),TGraph) :
            # print 'SetYaxisRanges',ymin,ymax
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis :
                yaxis = i.GetHistogram().GetYaxis()
        if issubclass(type(i),TH1) :
            # print 'SetYaxisRanges',ymin,ymax
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis: 
                yaxis = i.GetYaxis()
        if issubclass(type(i),THStack) :
            # print 'SetYaxisRanges',ymin,ymax
            i.SetMinimum(ymin)
            i.SetMaximum(ymax)
            if not yaxis :
                yaxis = i.GetHistogram().GetYaxis()
    if not yaxis :
        print 'Warning: SetYaxisRange had no effect. Check that your canvas has plots in it.'
        return
    
    yaxis.SetRangeUser(ymin,ymax)
    can.Modified()
    #can.Update()
    return

def SetNdivisions(can,a,b,c) :
    for i in can.GetListOfPrimitives() :
        if hasattr(i,'GetXaxis') :
            i.GetXaxis().SetNdivisions(a,b,c)
    can.Modified()
    #can.Update()
    return
    

##
## Returns the y-range of the first plotted histogram.
## If you specify "check_all=True", returns the maximal y-range of all the plots in the canvas
##
def GetYaxisRanges(can,check_all=False) :
    #
    # check_all is if you want to check the maximum extent of all the histograms you plotted.
    #
    import ROOT
    ymin = 999999999
    ymax = -999999999
    
    primitives = list(can.GetListOfPrimitives())
    if can.GetPrimitive('stack') :
        the_stack = list(can.GetPrimitive('stack').GetHists())
        primitives += the_stack

    for i in primitives :
        if issubclass(type(i),ROOT.TGraph) :
            tmp_ymin = None
            tmp_ymax = None
            for j in range(i.GetN()) :
                eyl = 0
                eyh = 0
                if issubclass(type(i),ROOT.TGraphAsymmErrors) :
                    eyl = i.GetEYlow()[j]
                    eyh = i.GetEYhigh()[j]
                elif issubclass(type(i),ROOT.TGraphErrors) :
                    eyl = i.GetEY()[j]
                    eyh = i.GetEY()[j]
                if tmp_ymin == None :
                    tmp_ymin = i.GetY()[j]-eyl
                    tmp_ymax = i.GetY()[j]+eyh
                    continue
                tmp_ymin = min(tmp_ymin,i.GetY()[j]-eyl)
                tmp_ymax = max(tmp_ymax,i.GetY()[j]+eyh)
            ymin = min(ymin,tmp_ymin)
            ymax = max(ymax,tmp_ymax)
            if not check_all :
                return ymin,ymax
        if issubclass(type(i),ROOT.TH1) :
            for bin in range(i.GetNbinsX()) :
                if bin+1 < i.GetXaxis().GetFirst() : continue # X-axis SetRange should be done first
                if bin+1 > i.GetXaxis().GetLast() : continue # X-axis SetRange should be done first
                y = i.GetBinContent(bin+1)
                yel = i.GetBinErrorLow(bin+1)
                yeu = i.GetBinErrorUp(bin+1)
                ymin = min(ymin,y-yel)
                ymax = max(ymax,y+yeu)
            if not check_all :
                return ymin,ymax
        if issubclass(type(i),ROOT.TF1) :
            ymin = min(ymin,i.GetMinimum())
            ymax = max(ymax,i.GetMaximum())
            if not check_all :
                return ymin,ymax            
        if issubclass(type(i),ROOT.THStack) :
            ymin = min(ymin,i.GetMinimum())
            ymax = max(ymax,i.GetMaximum())
            if not check_all :
                return ymin,ymax

    # print 'GetYaxisRanges',ymin,ymax
    return ymin,ymax
