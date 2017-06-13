#
# Usage: python ConvertEndcapThermalData.py R0
#

import sys

files = ['FEA_T-20170906_S-2.dat', # abc
         'FEA_T-20170906_S-1.dat', # hcc
         'FEA_T-20170906_S-3.dat', # feast
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
    'ASIC':3, # feast
    'Sensor':4,
    'AMAC':5, # new
    'EoP':6, # new
    }

#print other_modules

outtext = ''
outtext += '{:>5} {:>5} {:>7} {:>6} {:>5} {:>7} {:>6}\n'.format('pabc','phcc','pfeast','prest','type','result','error')

for i,f in enumerate(files) :
    print '#',module,f
    a = open(f,'r')

    powers = [0.149*nabc[module] * (f == 'FEA_T-20170906_S-2.dat'),
              0.413*nhcc[module] * (f == 'FEA_T-20170906_S-1.dat'),
              1.5                * (f == 'FEA_T-20170906_S-3.dat')] # feast

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