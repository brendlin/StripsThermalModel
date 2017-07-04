
import ROOT
import FluxAndTidParameterization
import TableUtils

internal_config = ROOT.TEnv()
confname = ['None']
units = dict()
descriptions = dict()
is_default = dict()

def GetName() :
    return confname[0]

def SetConfigFile(filepath,doprint=True) :
    configname = filepath.split('/')[-1]
    confname[0] = configname

    # Reset TEnv
    if internal_config.GetTable() :
        print 'Info: Resetting config file'
        internal_config.GetTable().Clear()

    # Load the new file
    loaded = internal_config.ReadFile(filepath,ROOT.kEnvGlobal)
    if loaded != 0 :
        print 'Error! Failed to load config file %s -- Exiting.'%(configname)
        import sys; sys.exit()

    if doprint :
        print 'Loaded config file %s:'%(configname)
        internal_config.Print()
    else :
        print 'Loaded config file %s.'%(configname)

    return

def Defined(key) :
    if not internal_config.Defined(key) :
        return False
    return True

def EnsureDefined(key) :
    if not internal_config.Defined(key) :
        print 'Error! \"%s\" is not defined in %s! Exiting.'%(key,internal_config.GetName())
        import sys; sys.exit()

def ProcessExtraDetails(key,ValueIfNotInConfig=None,unit=None,description=None) :
    if description != None :
        descriptions[key] = description
    if unit != None :
        units[key] = unit
    if (ValueIfNotInConfig != None) and (not Defined(key)) :
        SetValue(key,ValueIfNotInConfig)
        is_default[key] = True
    return

def GetDouble(key,ValueIfNotInConfig=None,unit=None,description=None) :
    ProcessExtraDetails(key,ValueIfNotInConfig=ValueIfNotInConfig,unit=unit,description=description)
    EnsureDefined(key)
    return internal_config.GetValue(key,-99.9)

def GetInt(key,ValueIfNotInConfig=None,unit=None,description=None) :
    ProcessExtraDetails(key,ValueIfNotInConfig=ValueIfNotInConfig,unit=unit,description=description)
    EnsureDefined(key)
    return internal_config.GetValue(key,1)

def GetStr(key,ValueIfNotInConfig=None,unit=None,description=None) :
    ProcessExtraDetails(key,ValueIfNotInConfig=ValueIfNotInConfig,unit=unit,description=description)
    EnsureDefined(key)
    return internal_config.GetValue(key,'none')

def SetValue(name,value) :
    internal_config.SetValue(name,str(value))
    return

def Print() :
    #internal_config.Print()
    the_lists = []
    the_lists.append(['Configurable Item','Description','Value','Unit'])

    the_configs_default = []
    the_configs_set = []
    for i in range(internal_config.GetTable().GetSize()) :
        tenvrec = internal_config.GetTable().At(i)
        nm = tenvrec.GetName()
        if nm in is_default.keys() and is_default[nm] :
            the_configs_default.append(nm)
        else :
            the_configs_set.append(nm)

    for nm in sorted(the_configs_set) + sorted(the_configs_default) :
        the_lists.append([])
        value = internal_config.GetValue(nm,'')
        the_lists[-1].append(nm)
        the_lists[-1].append(descriptions.get(nm,'--'))
        the_lists[-1].append(value)
        the_lists[-1].append(units.get(nm,'--'))

    table = TableUtils.PrintLatexTable(the_lists,justs='llrl')
    return table

# For reloading python module, in case e.g. the config file changed.
def ReloadPythonModule(name) :
    import sys,imp
    if name in sys.modules.keys() :
        module = sys.modules[name]
        imp.reload(module)
        #print 'Reloaded %s'%(module.__name__)
    else :
        #print 'Skipping module %s because it does not exist.'%(name)
        pass
    return

def ReloadAllPythonModules() :
    #                   Module                               Dependencies
    ReloadPythonModule('python.GlobalSettings'           ) # none
    ReloadPythonModule('python.AbcTidBump'               ) # none
    ReloadPythonModule('python.CableLosses'              ) # none
    ReloadPythonModule('python.PoweringEfficiency'       ) # none
    ReloadPythonModule('python.Layout'                   ) # Config
    ReloadPythonModule('python.SafetyFactors'            ) # Config
    ReloadPythonModule('python.CoolantTemperature'       ) # Config (GlobalSettings)
    ReloadPythonModule('python.SensorProperties'         ) # Config SafetyFactors
    ReloadPythonModule('python.ThermalImpedances'        ) # Config SafetyFactors
    ReloadPythonModule('python.OperationalProfiles'      ) # Config SafetyFactors (GlobalSettings)
    ReloadPythonModule('python.EOSComponents'            ) # SafetyFactors
    ReloadPythonModule('python.FrontEndComponents'       ) # SafetyFactors
    ReloadPythonModule('python.PlotUtils'                ) # SafetyFactors CoolantTemperature
    ReloadPythonModule('python.Temperatures'             ) # ThermalImpedances (GlobalSettings)
    ReloadPythonModule('python.ExtendedModelSummaryPlots') # CoolantTemperature PlotUtils (GlobalSettings)
    ReloadPythonModule('python.SensorLeakage'            ) # SensorProperties OperationalProfiles (GlobalSettings)
    ReloadPythonModule('python.NominalPower'             ) # SensorProperties Config SafetyFactors Layout FrontEndComponents EOSComponents (GlobalSettings PoweringEfficiency AbcTidBump CableLosses)
    ReloadPythonModule('python.SensorTemperatureCalc'    ) # SensorProperties Config SafetyFactors Layout Temperatures NominalPower SensorLeakage OperationalProfiles CoolantTemperature PlotUtils (GlobalSettings PoweringEfficiency AbcTidBump)
    # do not need to reload TAxisFunctions, __init__, Config (maybe obviously)

    return
# --------------------------------
def AddConfigurationOptions(opt_parser) :
    opt_parser.add_option('--cooling',type='string',default=None,dest='cooling',help='Cooling scheme (\"-flat25\",\"-flat35\",\"ramp-25\",\"ramp-35\").')
    opt_parser.add_option('--safetyi',type='float' ,default=None,dest='safetyi',help='Current safety factor (default is 0.0)')
    opt_parser.add_option('--safetyr',type='float' ,default=None,dest='safetyr',help='Thermal resistance safety factor (default is 0.0)')
    opt_parser.add_option('--safetyf',type='float' ,default=None,dest='safetyf',help='Flux safety factor (default is 0.0)')
    return

# --------------------------------
def SetMissingConfigsUsingCommandLine(options,config='') :

    if not config and  options.config :
        config = options.config

    # If "key" is not defined in the config file, define it using the command-line argument
    value_to_set = {'cooling'                          : options.cooling,
                    'SafetyFactors.safetycurrent'          : options.safetyi,
                    'SafetyFactors.safetythermalimpedance' : options.safetyr,
                    'SafetyFactors.safetyfluence'          : options.safetyf,
                    }

    for k in value_to_set.keys() :
        if not Defined(k) and (value_to_set[k] != None) :
            SetValue(k,value_to_set[k])

    if not Defined('OperationalProfiles.totalflux') :
        SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetMaxFlux(config))

    if not Defined('OperationalProfiles.tid_in_3000fb') :
        SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetMaxTID(config))

    return
