
name='ItkWeek1711_v2'


for i in {30,35,25,20,15}; do
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_No_Safety                              
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_Base_assumptions            --safetyf 0.5
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusBumpParam           --safetyf 0.5                                                          --tidpess
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusASIC                --safetyf 0.5 --safetyid 0.2 --safetyia 0.05
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusThermal             --safetyf 0.5                                --safetyr 0.2
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusBias                --safetyf 0.5                                              --vbias 700
    echo python ExtendedRunModel.py --endcap --cooling flat-${i} --outdir ${name}_BasePlusBumpASICThermalBias --safetyf 0.5 --safetyid 0.2 --safetyia 0.05 --safetyr 0.2 --vbias 700 --tidpess
done

for i in 35; do
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_No_Safety                              
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_Base_assumptions            --safetyf 0.5
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_BasePlusBumpParam           --safetyf 0.5                                                          --tidpess
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_BasePlusASIC                --safetyf 0.5 --safetyid 0.2 --safetyia 0.05
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_BasePlusThermal             --safetyf 0.5                                --safetyr 0.2
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_BasePlusBias                --safetyf 0.5                                              --vbias 700
    echo python ExtendedRunModel.py --endcap --cooling ramp-${i} --outdir ${name}_BasePlusBumpASICThermalBias --safetyf 0.5 --safetyid 0.2 --safetyia 0.05 --safetyr 0.2 --vbias 700 --tidpess
done

# echo 'Order:'
# for i in {35,30,25,20,15}; do
#     echo ${name}_No_Safety_flat_m${i}
#     echo ${name}_Base_assumptions_flat_m${i}
#     echo ${name}_BasePlusASICOldCurrent_flat_m${i}
#     echo ${name}_BasePlusASIC_flat_m${i}
#     echo ${name}_BasePlusThermal_flat_m${i}
#     echo ${name}_BasePlusThermalTight_flat_m${i}
#     echo ${name}_BasePlusBias_flat_m${i}
#     echo ${name}_BasePlusASICPlusBiasPlusThermal_flat_m${i}
#     echo ${name}_BasePlusASICPlusBiasPlusThermalTight_flat_m${i}
# #     echo ${name}_BasePlusASICPlusThermal_flat_m${i}
# #     echo ${name}_BasePlusASICPlusThermalTight_flat_m${i}
# #     echo ${name}_BasePlusASICPlusThermal_flat_m${i}
# #     echo ${name}_BasePlusASICPlusThermalTight_flat_m${i}
# done
