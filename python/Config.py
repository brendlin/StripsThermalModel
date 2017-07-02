
import ROOT
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

    print TableUtils.PrintLatexTable(the_lists,justs='llrl')
    return

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
