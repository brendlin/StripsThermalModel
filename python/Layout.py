#
# Layout
#
import Config

if Config.GetStr('Layout.Detector') == 'Barrel' :
    nstaves = Config.GetInt('Layout.nstaves') # Number of staves per end
    nmod = 14 # number of modules per stave per side

elif Config.GetStr('Layout.Detector') == 'Endcap' :
    nstaves = Config.GetInt('Layout.npetals') # re-use the variable "nstaves" for npetals
    nmod = 1 # number of modules per petal of type R0, R1, ... etc.

else :
    print 'Error! Layout.Detector not defined in configuration'
    import sys; sys.exit()
