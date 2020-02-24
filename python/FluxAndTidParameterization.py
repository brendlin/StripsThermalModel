#
# Parameterization for the endcap
#

def GetFluxEndcap(ring,disk) :
    # return 2e14 + (1e15 - 2e14)*((5-ring) + disk)/10.

    # S3.1Q6 -- 4000 fb-1 - corrected below!
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsStep3X
    # Table has units of 10^14 cm^-2
    return [[ 7.57 , 7.86 , 8.24 , 8.80 , 9.58 , 10.96 ] ,
            [ 5.82 , 6.07 , 6.45 , 6.90 , 7.62 ,  8.66 ] ,
            [ 4.90 , 5.15 , 5.49 , 5.95 , 6.52 ,  7.40 ] ,
            [ 4.45 , 4.67 , 4.96 , 5.40 , 5.96 ,  6.71 ] ,
            [ 3.74 , 3.92 , 4.21 , 4.60 , 5.07 ,  5.70 ] ,
            [ 3.31 , 3.48 , 3.73 , 4.11 , 4.55 ,  5.11 ] ][ring][disk] * 1.0e14 * 3./4.


    # S2.2D -- 4000 fb-1 - corrected below!
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsStep2X
    # Table has units of 10^14 cm^-2
    # return [[ 6.72 , 6.85 , 7.13 , 7.66 , 8.45 ,10.57 ] ,
    #         [ 5.26 , 5.40 , 5.70 , 6.16 , 6.95 , 8.67 ] ,
    #         [ 4.47 , 4.62 , 4.93 , 5.39 , 6.08 , 7.53 ] ,
    #         [ 4.07 , 4.24 , 4.47 , 4.97 , 5.65 , 6.86 ] ,
    #         [ 3.42 , 3.57 , 3.86 , 4.26 , 4.87 , 5.84 ] ,
    #         [ 3.06 , 3.20 , 3.48 , 3.86 , 4.40 , 5.17 ] ][ring][disk] * 1.0e14 * 3./4.

    # S1.9 -- 3000 fb-1
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsFullyInclinedAt4
    # Table has units of 10^14 cm^-2
    # return [[ 5.03 , 5.12 , 5.38 , 5.67 , 6.25 , 7.74 ] ,
    #         [ 3.93 , 4.03 , 4.22 , 4.57 , 5.14 , 6.36 ] ,
    #         [ 3.31 , 3.41 , 3.62 , 3.95 , 4.47 , 5.47 ] ,
    #         [ 3.01 , 3.11 , 3.32 , 3.66 , 4.11 , 5.00 ] ,
    #         [ 2.53 , 2.65 , 2.85 , 3.12 , 3.56 , 4.25 ] ,
    #         [ 2.26 , 2.36 , 2.56 , 2.84 , 3.21 , 3.77 ] ][ring][disk] * 1.0e14

    # S1.7 ITk: Strip endcap -- 3000 fb-1
    # return [[ 5.08 , 5.17 , 5.46 , 5.78 , 6.42 , 7.88 ] ,
    #         [ 3.94 , 4.04 , 4.30 , 4.67 , 5.24 , 6.47 ] ,
    #         [ 3.34 , 3.46 , 3.71 , 4.06 , 4.57 , 5.57 ] ,
    #         [ 3.03 , 3.13 , 3.37 , 3.70 , 4.21 , 5.09 ] ,
    #         [ 2.56 , 2.67 , 2.89 , 3.18 , 3.63 , 4.32 ] ,
    #         [ 2.27 , 2.39 , 2.60 , 2.87 , 3.27 , 3.84 ]] [ring][disk] * 1.0e14

def GetTIDEndcap(ring,disk) :
    # return 3e3 + (3e4 - 3e3)*(5-ring)/5.
    # Output is in kRad

    # S3.1Q6 -- 4000 fb-1 - corrected below!
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsStep3X
    return [[ 0.343 , 0.360 , 0.384 , 0.418 , 0.474 , 0.532 ] ,
            [ 0.201 , 0.217 , 0.231 , 0.251 , 0.277 , 0.297 ] ,
            [ 0.153 , 0.167 , 0.173 , 0.184 , 0.194 , 0.216 ] ,
            [ 0.122 , 0.132 , 0.137 , 0.153 , 0.165 , 0.173 ] ,
            [ 0.091 , 0.096 , 0.099 , 0.104 , 0.115 , 0.127 ] ,
            [ 0.067 , 0.071 , 0.077 , 0.086 , 0.091 , 0.101 ]][ring][disk] * 100000. * 3./4. # value in kRad


    # S2.2D -- 4000 fb-1 - corrected below!
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsStep2X
    # return [[ 0.313 , 0.325 , 0.338 , 0.367 , 0.405 , 0.438 ] ,
    #         [ 0.193 , 0.198 , 0.217 , 0.224 , 0.247 , 0.282 ] ,
    #         [ 0.145 , 0.154 , 0.160 , 0.163 , 0.176 , 0.199 ] ,
    #         [ 0.119 , 0.120 , 0.128 , 0.139 , 0.149 , 0.164 ] ,
    #         [ 0.084 , 0.087 , 0.094 , 0.098 , 0.108 , 0.121 ] ,
    #         [ 0.065 , 0.067 , 0.071 , 0.077 , 0.087 , 0.098 ]][ring][disk] * 100000. * 3./4. # value in kRad

    # S1.9 ITk: Strip endcap -- 3000 fb-1
    # https://twiki.cern.ch/twiki/bin/view/Atlas/RadiationBackgroundSimulationsFullyInclinedAt4
    # table has units of MGy. 1 MGy = 0.1 MRad = 100 kRad = 100 000 Rad
    # return [[ 0.227 , 0.239 , 0.248 , 0.268 , 0.291 , 0.311 ] ,
    #         [ 0.144 , 0.148 , 0.155 , 0.165 , 0.181 , 0.201 ] ,
    #         [ 0.110 , 0.113 , 0.114 , 0.121 , 0.128 , 0.143 ] ,
    #         [ 0.090 , 0.092 , 0.095 , 0.105 , 0.108 , 0.121 ] ,
    #         [ 0.062 , 0.067 , 0.067 , 0.072 , 0.079 , 0.089 ] ,
    #         [ 0.047 , 0.050 , 0.053 , 0.058 , 0.064 , 0.070 ]][ring][disk] * 100000.

    # S1.7 ITk: Strip endcap -- 3000 fb-1
    # return [[ 0.235 , 0.240 , 0.253 , 0.270 , 0.295 , 0.321 ] ,
    #         [ 0.142 , 0.148 , 0.159 , 0.167 , 0.181 , 0.206 ] ,
    #         [ 0.108 , 0.114 , 0.117 , 0.120 , 0.133 , 0.149 ] ,
    #         [ 0.086 , 0.088 , 0.098 , 0.101 , 0.109 , 0.123 ] ,
    #         [ 0.064 , 0.066 , 0.072 , 0.071 , 0.080 , 0.091 ] ,
    #         [ 0.048 , 0.050 , 0.055 , 0.059 , 0.063 , 0.074 ]][ring][disk] * 100000.

def GetMaxFluxEndcap(config_name) :
    try :
        ring = list('R%d'%(a) in config_name for a in [0,1,2,3,4,5]).index(True)
        return max(list(GetFluxEndcap(ring,i) for i in range(6)))
    except ValueError :
        print 'Error! Cannot find which endcap module you are. R0? R1? R2? %s'%(config_name)
        import sys; sys.exit()

def GetMaxTIDEndcap(config_name) :
    try :
        ring = list('R%d'%(a) in config_name for a in [0,1,2,3,4,5]).index(True)
        return max(list(GetTIDEndcap(ring,i) for i in range(6)))
    except ValueError :
        print 'Error! Cannot find which endcap module you are. R0? R1? R2? %s'%(config_name)
        import sys; sys.exit()


#
# Parameterization for the barrel
#
def GetFluxBarrel(module,layer) :

    # S1.9 ITk: Strip barrel
    # Table has units of 10^14 cm^-2
    return [[ 3.86 , 2.74 , 2.05 , 1.54 ] ,
            [ 3.90 , 2.76 , 2.04 , 1.55 ] ,
            [ 3.95 , 2.79 , 2.04 , 1.56 ] ,
            [ 4.03 , 2.82 , 2.08 , 1.56 ] ,
            [ 4.11 , 2.86 , 2.09 , 1.59 ] ,
            [ 4.17 , 2.90 , 2.14 , 1.60 ] ,
            [ 4.27 , 2.97 , 2.19 , 1.63 ] ,
            [ 4.34 , 3.04 , 2.23 , 1.67 ] ,
            [ 4.45 , 3.09 , 2.29 , 1.77 ] ,
            [ 4.51 , 3.17 , 2.31 , 1.81 ] ,
            [ 4.58 , 3.23 , 2.38 , 1.84 ] ,
            [ 4.64 , 3.29 , 2.41 , 1.89 ] ,
            [ 4.71 , 3.33 , 2.48 , 1.92 ] ,
            [ 4.79 , 3.39 , 2.53 , 1.96 ] ][module][layer] * 1.0e14


def GetTIDBarrel(module,layer) :
    # Output is in kRad

    # S1.9 ITk: Strip barrel
    # table has units of MGy. 1 MGy = 0.1 MRad = 100 kRad = 100 000 Rad FALSE FALSE FALSE
    # table has units of MGy. 1 MGy = 100 MRad = 100,000 kRad
    return [[ 0.171 , 0.095 , 0.0550 , 0.0300 ] ,
            [ 0.162 , 0.097 , 0.0564 , 0.0295 ] ,
            [ 0.169 , 0.098 , 0.0552 , 0.0296 ] ,
            [ 0.172 , 0.098 , 0.0562 , 0.0308 ] ,
            [ 0.176 , 0.099 , 0.0558 , 0.0304 ] ,
            [ 0.178 , 0.100 , 0.0568 , 0.0310 ] ,
            [ 0.182 , 0.103 , 0.0578 , 0.0308 ] ,
            [ 0.187 , 0.106 , 0.0591 , 0.0317 ] ,
            [ 0.190 , 0.110 , 0.0594 , 0.0325 ] ,
            [ 0.195 , 0.111 , 0.0590 , 0.0325 ] ,
            [ 0.204 , 0.112 , 0.0624 , 0.0340 ] ,
            [ 0.209 , 0.111 , 0.0638 , 0.0340 ] ,
            [ 0.215 , 0.117 , 0.0645 , 0.0349 ] ,
            [ 0.216 , 0.116 , 0.0656 , 0.0357 ] ][module][layer] * 100000. # value in kRad


# Here we want max flux for a given module in a layer, instead of the max flux of RX across disks
def GetMaxFluxBarrel(config_name) :
    try :
        layer = list('B%d'%(a) in config_name for a in [0,1,2,3]).index(True)
        return max(list(GetFluxBarrel(i,layer) for i in range(14)))
    except ValueError :
        print 'Error! Cannot find which barrel module you are. B0? B1? B2? %s'%(config_name)
        import sys; sys.exit()

def GetMaxTIDBarrel(config_name) :
    try :
        layer = list('B%d'%(a) in config_name for a in [0,1,2,3]).index(True)
        return max(list(GetTIDBarrel(i,layer) for i in range(14)))
    except ValueError :
        print 'Error! Cannot find which barrel module you are. B0? B1? B2? %s'%(config_name)
        import sys; sys.exit()

#
# Helper functions
#
def GetFlux(ring_mod,disk_layer,isEndcap) :
    if isEndcap :
        return GetFluxEndcap(ring_mod,disk_layer)
    return GetFluxBarrel(ring_mod,disk_layer)

def GetTID(ring_mod,disk_layer,isEndcap) :
    if isEndcap :
        return GetTIDEndcap(ring_mod,disk_layer)
    return GetTIDBarrel(ring_mod,disk_layer)
