
name='May22_2019'

for i in 35; do
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusBumpASICThermal         --safetyf 0.5 --safetyid 0.1 --safetyia 0.05 --safetyr 0.2 --tidpess
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusBumpASICThermalPreIrrad --safetyf 0.5 --safetyid 0.1 --safetyia 0.05 --safetyr 0.2 --tidpess --preirr 8
done

for j in newramp; do
    for i in 35; do
        echo python ExtendedRunModel.py --endcap --cooling ${j}-${i} --outdir ${name}_BasePlusBumpASICThermal         --safetyf 0.5 --safetyid 0.1 --safetyia 0.05 --safetyr 0.2 --tidpess
        echo python ExtendedRunModel.py --endcap --cooling ${j}-${i} --outdir ${name}_Base_assumptions                --safetyf 0.5
        echo python ExtendedRunModel.py --endcap --cooling ${j}-${i} --outdir ${name}_BasePlusBumpASICThermalPreIrrad --safetyf 0.5 --safetyid 0.1 --safetyia 0.05 --safetyr 0.2 --tidpess --preirr 8
        echo python ExtendedRunModel.py --endcap --cooling ${j}-${i} --outdir ${name}_Base_assumptionsPreIrrad        --safetyf 0.5                                                        --preirr 8
    done
done
k