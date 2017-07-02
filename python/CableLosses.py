#
# CableLosses
#
import Config

# Loss factors in cables
# in tapes (no value?)
losstype1_descr = 'Cable losses from service modules'
losstype1 = Config.GetDouble('CableLosses.losstype1',0.05,description=losstype1_descr)
lossouter_descr = 'Cable losses from PP1 to USA15'
lossouter = Config.GetDouble('CableLosses.lossouter',0.05,description=lossouter_descr)
