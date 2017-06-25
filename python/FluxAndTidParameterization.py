#
# Parameterization for the endcap
#
    
def GetFlux(ring,disk) :
    # return 2e14 + (1e15 - 2e14)*((5-ring) + disk)/10.
    
    # S1.9
    # Table has units of 10^14 cm^-2
    return [[ 5.03 , 5.12 , 5.38 , 5.67 , 6.25 , 7.74 ] ,
            [ 3.93 , 4.03 , 4.22 , 4.57 , 5.14 , 6.36 ] ,
            [ 3.31 , 3.41 , 3.62 , 3.95 , 4.47 , 5.47 ] ,
            [ 3.01 , 3.11 , 3.32 , 3.66 , 4.11 , 5.00 ] ,
            [ 2.53 , 2.65 , 2.85 , 3.12 , 3.56 , 4.25 ] ,
            [ 2.26 , 2.36 , 2.56 , 2.84 , 3.21 , 3.77 ] ][ring][disk] * 1.0e14

    # S1.7 ITk: Strip endcap
    # return [[ 5.08 , 5.17 , 5.46 , 5.78 , 6.42 , 7.88 ] ,
    #         [ 3.94 , 4.04 , 4.30 , 4.67 , 5.24 , 6.47 ] ,
    #         [ 3.34 , 3.46 , 3.71 , 4.06 , 4.57 , 5.57 ] ,
    #         [ 3.03 , 3.13 , 3.37 , 3.70 , 4.21 , 5.09 ] ,
    #         [ 2.56 , 2.67 , 2.89 , 3.18 , 3.63 , 4.32 ] ,
    #         [ 2.27 , 2.39 , 2.60 , 2.87 , 3.27 , 3.84 ]] [ring][disk] * 1.0e14

def GetTID(ring,disk) :
    # return 3e3 + (3e4 - 3e3)*(5-ring)/5.

    # S1.9 ITk: Strip endcap
    # table has units of MGy. 1 MGy = 0.1 MRad = 100 kRad = 100 000 Rad
    return [[ 0.227 , 0.239 , 0.248 , 0.268 , 0.291 , 0.311 ] ,
            [ 0.144 , 0.148 , 0.155 , 0.165 , 0.181 , 0.201 ] ,
            [ 0.110 , 0.113 , 0.114 , 0.121 , 0.128 , 0.143 ] ,
            [ 0.090 , 0.092 , 0.095 , 0.105 , 0.108 , 0.121 ] ,
            [ 0.062 , 0.067 , 0.067 , 0.072 , 0.079 , 0.089 ] ,
            [ 0.047 , 0.050 , 0.053 , 0.058 , 0.064 , 0.070 ]][ring][disk] * 100000.

    # S1.7 ITk: Strip endcap
    # return [[ 0.235 , 0.240 , 0.253 , 0.270 , 0.295 , 0.321 ] ,
    #         [ 0.142 , 0.148 , 0.159 , 0.167 , 0.181 , 0.206 ] ,
    #         [ 0.108 , 0.114 , 0.117 , 0.120 , 0.133 , 0.149 ] ,
    #         [ 0.086 , 0.088 , 0.098 , 0.101 , 0.109 , 0.123 ] ,
    #         [ 0.064 , 0.066 , 0.072 , 0.071 , 0.080 , 0.091 ] ,
    #         [ 0.048 , 0.050 , 0.055 , 0.059 , 0.063 , 0.074 ]][ring][disk] * 100000.

def GetMaxFlux(config_name) :
    try :
        ring = list('R%d'%(a) in config_name for a in [0,1,2,3,4,5]).index(True)
        return max(list(GetFlux(ring,i) for i in range(6)))
    except ValueError :
        print 'Error! Cannot find which endcap module you are. R0? R1? R2? %s'%(config_name)
        import sys; sys.exit()

def GetMaxTID(config_name) :
    try :
        ring = list('R%d'%(a) in config_name for a in [0,1,2,3,4,5]).index(True)
        return max(list(GetTID(ring,i) for i in range(6)))
    except ValueError :
        print 'Error! Cannot find which endcap module you are. R0? R1? R2? %s'%(config_name)
        import sys; sys.exit()
