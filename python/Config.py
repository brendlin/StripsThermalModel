
import ROOT

internal_config = ROOT.TEnv()
confname = ['None']

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

def EnsureDefined(key) :
    if not internal_config.Defined(key) :
        print 'Error! \"%s\" is not defined in %s! Exiting.'%(key,internal_config.GetName())
        import sys; sys.exit()

def GetDouble(key) :
    EnsureDefined(key)
    return internal_config.GetValue(key,-99.9)

def GetInt(key) :
    EnsureDefined(key)
    return internal_config.GetValue(key,1)

def GetStr(key) :
    EnsureDefined(key)
    return internal_config.GetValue(key,'none')

def SetValue(name,value) :
    internal_config.SetValue(name,value)
    return

def Print() :
    internal_config.Print()
    return

# For reloading python module, in case e.g. the config file changed.
def ReloadPythonModule(module) :
    import imp
    imp.reload(module)
    #print 'Reloaded %s'%(module.__name__)

def ReloadAllPythonModules() :
    import sys
    for i in sys.modules.keys() :
        if not sys.modules[i] :
            continue
        if hasattr(sys.modules[i],'__file__') and 'StripsThermalModel' in sys.modules[i].__file__ :
            if '__init__' in sys.modules[i].__file__ :
                continue
            if 'Config.py' in sys.modules[i].__file__ :
                continue
            ReloadPythonModule(sys.modules[i])

    return
