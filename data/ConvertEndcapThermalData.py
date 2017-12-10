#
# Usage: python ConvertEndcapThermalData.py R0
# for i in {0..5}; do python ConvertEndcapThermalData.py R$i >& ThermalImpedances_R$i.txt; done
# DO NOT FORGET:
# python ConvertEndcapThermalData.py EoP
#

import sys

files = ['[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S2.dat', # abc
         '[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S1.dat', # hcc
         '[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S3.dat', # feast
         ]

nabc = {
    'R0' : 17,
    'R1' : 21,
    'R2' : 12,
    'R3' : 28,
    'R4' : 16,
    'R5' : 18,
    'EoP' : 18,
    }

nhcc = {
    'R0' : 2,
    'R1' : 2,
    'R2' : 2,
    'R3' : 4,
    'R4' : 2,
    'R5' : 2,
    'EoP' : 2,
    }

other_modules = ['R0','R1','R2','R3','R4','R5','EoP']
module = other_modules.pop(other_modules.index(sys.argv[1]))

name_type_rosetta = {
    'ABC':1,
    'HCC':2,
    'FEAST':3, # feast
    'Sensor':4,
    'AMAC':5, # new
    'EoP':6, # new
    'DCDC':7, # the EoP DCDC converter
    }

#print other_modules

outtext = ''
outtext += '{:>5} {:>5} {:>7} {:>6} {:>5} {:>7} {:>6}\n'.format('pabc','phcc','pfeast','prest','type','result','error')

print '# Types: 1 ABC, 2 HCC, 3 FEAST, 4 Sensor, 5 AMAC, 6 EoP'
for i,f in enumerate(files) :
    print '#',module,f
    a = open(f,'r')

    powers = [0.149*nabc[module] * (f == '[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S2.dat'),
              0.413*nhcc[module] * (f == '[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S1.dat'),
              1.5                * (f == '[FEA][20171207][-30.0C][0.0Wm2C][DP1][ALL]S3.dat')] # feast

    isCorrectModule = False

    for line in a :
        line = line.replace('\n','')
        datapoint = line.split()
        
        if not datapoint : continue
        if len(datapoint) < 3 : continue

        try :
            float(datapoint[2])
        except ValueError : 
            continue
        
        if len(datapoint) == 6 and datapoint[0] == module :
            isCorrectModule = True
            datapoint = datapoint[1:]
        if len(datapoint) == 6 and datapoint[0] in other_modules :
            isCorrectModule = False

        if not isCorrectModule :
            continue

        type = name_type_rosetta[datapoint[0]]
        outtext += '{:5.2f} {:5.2f} {:7.2f} {:6.2f} {:5d} {:7.2f} {:6.2f}\n'.format(powers[0],powers[1],powers[2],0,type,float(datapoint[1])+30,float(datapoint[2]))

print outtext
