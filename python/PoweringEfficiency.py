#
# PoweringEfficiency
#

import ROOT

# Fit function used: a+b Subscript[i, load]+c Subsuperscript[i, load, 2]+d Subsuperscript[i, load, 3]-(2 T)/25, with the coefficients:
# a=58.0448, b=29.6715, c=-12.4747, d=1.40142

# x is load current
# y is temperature
feast_fit_function = ROOT.TF2("feast_fit_function","[0] + [1]*x + [2]*x*x - (2/25)*y",0,5,5,65);
feast_fit_function.SetParameter(0, 58.0448)
feast_fit_function.SetParameter(1, 29.6715)
feast_fit_function.SetParameter(2,-12.4747)
feast_fit_function.SetParameter(3,  1.40142)

Vfeast = 10.5 # Feast input voltage
DCDC2eff = 0.88 # DCDC2 efficiency

# Clear[i]
# feasteffdata = {{0.5, 60, 66.2}, {1, 60, 73}, {1.5, 60, 75.1}, {2, 60,
#      74.3}, {2.5, 60, 71.1}, {3, 60, 67.8}, {4, 60, 63}, {0.5, 10, 
#     67.9}, {1, 10, 75.1}, {1.5, 10, 77.6}, {2, 10, 77.3}, {2.5, 10, 
#     75.5}, {3, 10, 72.1}, {4, 10, 65}};
# Text[Row[{"Data (\!\(\*SubscriptBox[\(I\), \(load\)]\)[A], \
# \!\(\*SubscriptBox[\(T\), \(sensor\)]\)[degC], efficiency): ", 
#    TraditionalForm[feasteffdata]}]]
# feasteff1[x1_, x2_, x3_, x4_, iload_, tsensor_] := 
#  x1 + x2*iload + x3*iload^2 + x4*iload^3 - 2/25*tsensor
# feastfit = 
#   FindFit[feasteffdata, 
#    feasteff1[a, b, c, d, il, t], {a, b, c, d}, {il, t}];
# feastfitconstants = {a, b, c, d} /. feastfit;
# feasteff[tsensor_, iload_] := 
#  feastfitconstants[[1]] + feastfitconstants[[2]]*iload + 
#   feastfitconstants[[3]]*iload^2 + feastfitconstants[[4]]*iload^3 - 
#   2/25*tsensor
# animation = 
#   Table[Show[
#     Plot3D[feasteff[y, x], {x, 0, 4}, {y, 9, 61}, 
#      PlotRange -> {{0, 4}, {9, 61}, {60, 80}}, 
#      ViewPoint -> {2, 1.5 - 1.2*Sin[2*Pi*(i/30 - 1)], 0.3}, 
#      ImageSize -> 600, AxesEdge -> {{1, -1}, {1, -1}, {-1, 1}}, 
#      AxesStyle -> {Directive[18, Bold], Directive[18, Bold], 
#        Directive[18, Bold]}], 
#     ListPointPlot3D[feasteffdata, PlotStyle -> PointSize[0.02]], 
#     AxesLabel -> {"\!\(\*SubscriptBox[\(I\), \(load\)]\)[A]", 
#       "T \!\(\*SuperscriptBox[\([\), \(o\)]\)C]", 
#       "Efficiency [%]"}], {i, 0, 30}];
# animation[[1]]
# SetDirectory[NotebookDirectory[]];
# Export["FEAST eff.gif", animation, "GIF", "DisplayDurations" -> 0.2];
# Text[Row[{"Fit function used: ", 
#    TraditionalForm[feasteff1[a, b, c, d, Subscript[i, load], T]], 
#    ", with the coefficients: a=", 
#    TraditionalForm[feastfitconstants[[1]]], ", b=", 
#    TraditionalForm[feastfitconstants[[2]]], ", c=", 
#    TraditionalForm[feastfitconstants[[3]]], ", d=", 
#    TraditionalForm[feastfitconstants[[4]]]}]]

