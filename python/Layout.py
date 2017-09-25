#
# Layout
#
import Config

if Config.GetStr('Layout.Detector',description='barrel or endcap geometry') == 'Barrel' :
    detectorname = 'barrel'
    isEndcap = False
    isBarrel = True
    nstaves_petals = Config.GetInt('Layout.nstaves',description='Number of staves per end')
    nlayers_or_disks  =  4
    nlayers_or_rings  =  4
    nmodules_or_rings = 14
    nmodules_or_disks = 14

elif Config.GetStr('Layout.Detector') == 'Endcap' :
    detectorname = 'endcap'
    isEndcap = True
    isBarrel = False
    # re-use the variable "nstaves" for npetals
    nstaves_petals = Config.GetInt('Layout.npetals',description='Number of petals per ring')
    nlayers_or_disks  = 6
    nmodules_or_disks = 6
    nmodules_or_rings = 6
    nlayers_or_rings  = 6

else :
    print 'Error! Layout.Detector not defined in configuration'
    import sys; sys.exit()
