#
# OperationalProfiles
#
import math

# Luminosity profile
# Luminosity per year in fb^-1/y for 14 y of operation
luminosity = [ 61, 163, 203, 203, 0, 305, 400, 400, 0, 440, 440, 440, 440, 440 ]

# days per year of operation
daysperyear = [ 80, 160, 160, 160, 1, 200, 200, 200, 1, 220, 220, 220, 220, 220]

# Efficiency (?)
eff = [ 0.294, 0.294, 0.294, 0.294, 0.294, 0.294,
        0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308 ]

# luminosity ramp
def lumiramp(step,nyears) :
    # step is number of steps per year
    ret = []
    nstep = int(nyears/float(step))
    ret.append(0)
    for i in range(nstep) :
        # print math.floor(i*step)
        ret.append(ret[-1] + step*luminosity[int(math.floor(i*step))] )
    return ret

# luminosity = {
#    {300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 
#     300}
#   };
# luminosity = {
#    {61, 163, 203, 203, 0, 305, 400, 400, 0, 440, 440, 440, 440, 440}
#   };
# lumi = Accumulate[luminosity[[1]]];
# lumiramp = List[];
# For[i = 1, i <= nstep, i++,
#  If[i <= 12, lumiramp = Append[lumiramp, N[lumi[[1]]*step*i]], 
#    If[i == nstep, lumiramp = Append[lumiramp, N[lumi[[nyears]]]], 
#     lumiramp = 
#      Append[lumiramp, 
#       N[lumi[[IntegerPart[
#           i*step]]] + (lumi[[IntegerPart[i*step] + 1]] - 
#            lumi[[IntegerPart[i*step]]])*(i*step - 
#            IntegerPart[i*step])]]]];
#  ]
# totallumi = Last[lumiramp];
# lumiplot = 
#   ListPlot[luminosity, AxesLabel -> {"Year", ""}, Ticks -> Automatic, 
#    plotformat];
# intlumiplot = 
#  ListLinePlot[lumiramp, 
#   AxesLabel -> {"Year", 
#     "integrated luminosity [\!\(\*SuperscriptBox[\(fb\), \(-1\)]\)]"},
#    plotformat]
# daysperyear = {
#    {120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 
#     120}
#   };
# daysperyear = {
#    {80, 160, 160, 160, 1, 200, 200, 200, 1, 220, 220, 220, 220, 220}
#   };
# eff = {
#    {0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 
#     0.5}
#   };
# eff = {
#    {0.294, 0.294, 0.294, 0.294, 0.294, 0.294, 0.308, 0.308, 0.308, 
#     0.308, 0.308, 0.308, 0.308, 0.308}
#   };
# dpyplot = 
#   ListPlot[daysperyear, AxesLabel -> {"Year", "days"}, 
#    Ticks -> Automatic, PlotStyle -> {Blue, Thickness[0.005]}, 
#    plotformat];
# effplot = 
#   ListPlot[100*eff, AxesLabel -> {"Year", "days"}, Ticks -> Automatic,
#     PlotStyle -> {Red, Thickness[0.005]}, plotformat];
# inputplot = TwoAxisPlot
# Legended[Show[lumiplot, dpyplot, effplot], 
#  Placed[LineLegend[{Green, Blue, Red}, { 
#     Style["Luminosity per year [\!\(\*SuperscriptBox[\(fb\), \
# \(-1\)]\)/y]", 16, Bold], Style["Days per year", 16, Bold], 
#     Style["Efficiency [%]", 16, Bold]}, 
#    LegendFunction -> Framed], {{0.98, 0.4}, {1, 1}}]]
