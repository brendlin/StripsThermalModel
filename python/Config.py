
import ROOT
import FluxAndTidParameterization
import TableUtils
import PlotUtils
import subprocess

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

    label = subprocess.check_output(["git", "describe",'--always']).replace('\n','')
    githash = GetStr('StripsThermalModel.GitHash',label,description='Git hash (for internal use)')

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

def GetBool(key,ValueIfNotInConfig=None,unit=None,description=None) :
    ProcessExtraDetails(key,ValueIfNotInConfig=ValueIfNotInConfig,unit=unit,description=description)
    EnsureDefined(key)
    return internal_config.GetValue(key,True)

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

def SaveSnapshot() :
    snapshot = dict()
    for i in range(internal_config.GetTable().GetSize()) :
        tenvrec = internal_config.GetTable().At(i)
        nm = tenvrec.GetName()
        snapshot[nm] = dict()
        snapshot[nm]['description'] = descriptions.get(nm,'--')
        snapshot[nm]['value'] = internal_config.GetValue(nm,'')
        snapshot[nm]['units'] = units.get(nm,'--')
    return snapshot

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
    ReloadPythonModule('python.FluxAndTidParameterization') # Config
    ReloadPythonModule('python.AbcTidBump'               ) # Config
    ReloadPythonModule('python.PoweringEfficiency'       ) # Config
    ReloadPythonModule('python.Layout'                   ) # Config
    ReloadPythonModule('python.SafetyFactors'            ) # Config
    ReloadPythonModule('python.CoolantTemperature'       ) # Config (GlobalSettings)
    ReloadPythonModule('python.SensorProperties'         ) # Config SafetyFactors
    ReloadPythonModule('python.ThermalImpedances'        ) # Config SafetyFactors
    ReloadPythonModule('python.OperationalProfiles'      ) # Config SafetyFactors (GlobalSettings)
    ReloadPythonModule('python.EOSComponents'            ) # SafetyFactors
    ReloadPythonModule('python.FrontEndComponents'       ) # SafetyFactors
    ReloadPythonModule('python.PlotUtils'                ) # SafetyFactors CoolantTemperature
    ReloadPythonModule('python.CableLosses'              ) # Config EOSComponents PlotUtils
    ReloadPythonModule('python.Temperatures'             ) # ThermalImpedances (GlobalSettings)
    ReloadPythonModule('python.ExtendedModelSummaryPlots') # CoolantTemperature PlotUtils CableLosses Layout PoweringEfficiency (GlobalSettings)
    ReloadPythonModule('python.SensorLeakage'            ) # SensorProperties OperationalProfiles (GlobalSettings)
    ReloadPythonModule('python.NominalPower'             ) # SensorProperties Config SafetyFactors Layout FrontEndComponents EOSComponents (GlobalSettings PoweringEfficiency AbcTidBump CableLosses)
    ReloadPythonModule('python.SensorTemperatureCalc'    ) # SensorProperties Config SafetyFactors Layout FrontEndComponents Temperatures NominalPower SensorLeakage OperationalProfiles CoolantTemperature PlotUtils (GlobalSettings PoweringEfficiency AbcTidBump)
    # do not need to reload TAxisFunctions, __init__, Config (maybe obviously)

    return
# --------------------------------
def AddConfigurationOptions(opt_parser) :
    opt_parser.add_option('--cooling',type='string',default=None,dest='cooling',help='Cooling scheme (\"-flat25\",\"-flat35\",\"ramp-25\",\"ramp-35\").')
    opt_parser.add_option('--safetyid',type='float',default=None,dest='safetyid',help='Current digital safety factor (default is 0.0)')
    opt_parser.add_option('--safetyia',type='float',default=None,dest='safetyia',help='Current analog safety factor (default is 0.0)')
    opt_parser.add_option('--safetyr',type='float' ,default=None,dest='safetyr',help='Thermal resistance safety factor (default is 0.0)')
    opt_parser.add_option('--safetyf',type='float' ,default=None,dest='safetyf',help='Flux safety factor (default is 0.0)')
    opt_parser.add_option('--tidpess',action='store_true',default=False,dest='tidpess',help='TID pessimistic scenario (optimistic is False)')
    opt_parser.add_option('--vbias'  ,type='float' ,default=None,dest='vbias'  ,help='Vbias (default is 500V)')
    opt_parser.add_option('--preirr' ,type='float' ,default=None,dest='preirr' ,help='Pre-irradiation (in MRad - default is 0)')
    opt_parser.add_option('--version_fluxtid',type='string' ,default=None,dest='version_fluxtid' ,help='Flux and TID version')
    return

# --------------------------------
def SetMissingConfigsUsingCommandLine(options,config='') :

    if not config and  options.config :
        config = options.config

    # If "key" is not defined in the config file, define it using the command-line argument
    value_to_set = {'cooling'                              : options.cooling,
                    'SafetyFactors.safetycurrentd'         : options.safetyid,
                    'SafetyFactors.safetycurrenta'         : options.safetyia,
                    'SafetyFactors.safetythermalimpedance' : options.safetyr,
                    'SafetyFactors.safetyfluence'          : options.safetyf,
                    'SafetyFactors.vbias'                  : options.vbias,
                    'SafetyFactors.TIDpessimistic'         : options.tidpess,
                    'OperationalProfiles.PreIrradiation'   : options.preirr,
                    'FluxAndTidParameterization.ModelVersion': options.version_fluxtid,
                    }

    for k in value_to_set.keys() :
        if not Defined(k) and (value_to_set[k] != None) :
            SetValue(k,value_to_set[k])

    if not Defined('OperationalProfiles.totalflux') :
        if GetStr('Layout.Detector') == 'Barrel' :
            SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetMaxFluxBarrel(config))
        elif GetStr('Layout.Detector') == 'Endcap' :
            SetValue('OperationalProfiles.totalflux',FluxAndTidParameterization.GetMaxFluxEndcap(config))

    if not Defined('OperationalProfiles.tid_in_3000fb') :
        if GetStr('Layout.Detector') == 'Barrel' :
            SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetMaxTIDBarrel(config))
        elif GetStr('Layout.Detector') == 'Endcap' :
            SetValue('OperationalProfiles.tid_in_3000fb',FluxAndTidParameterization.GetMaxTIDEndcap(config))

    return

# --------------------------------
def FancyPrintLatexTables(saved_configs,structure_names) :
    import Layout
    config_text = ''
    isEndcap = GetStr('Layout.Detector') == 'Endcap'

    config_list_general = []
    config_list_general.append(['Configurable Item','Description','Value','Unit'])
    config_list_ring_lay_specific = []
    rings_layers_header = ['R0','R1','R2','R3','R4','R5']
    if Layout.isBarrel :
        rings_layers_header = ['L0','L1','L2','L3']
    config_list_ring_lay_specific.append(['Configurable Item','Description']+rings_layers_header+['Unit'])
    config_text_modulespecific = ''
    for item in sorted(saved_configs[0].keys()) :
        module_specific_config = False in list(saved_configs[0][item]['value'] == saved_configs[i][item]['value'] for i in range(len(saved_configs)))
        ring_lay_specific_config = module_specific_config
        for ring_lay in range(Layout.nlayers_or_rings) :
            first_one = Layout.nmodules_or_disks*ring_lay
            range_to_compare = list(range(first_one+1,Layout.nmodules_or_disks*(ring_lay+1)))
            different_in_some_disk_or_modnumber = False in list(saved_configs[first_one][item]['value'] == saved_configs[i][item]['value'] for i in range_to_compare)
            ring_lay_specific_config = ring_lay_specific_config and not different_in_some_disk_or_modnumber

        if ring_lay_specific_config :
            config_list_ring_lay_specific.append([])
            config_list_ring_lay_specific[-1].append(item)
            config_list_ring_lay_specific[-1].append(saved_configs[0][item]['description'])
            for i in range(Layout.nlayers_or_disks) :
                config_list_ring_lay_specific[-1].append(saved_configs[i*Layout.nmodules_or_rings][item]['value'])
            config_list_ring_lay_specific[-1].append(saved_configs[0][item]['units'])

        elif module_specific_config :
            caption = '%s [%s]'%(saved_configs[0][item]['description'],saved_configs[0][item]['units'].replace('\t','\\t'))
            disk_ring_labels = '  & & \multicolumn{%d}{c|}{%s} \\\\\n\multirow{%d}{*}{%s}\n'%(Layout.nlayers_or_disks,
                                                                                             'Disk' if Layout.isEndcap else 'Layer',
                                                                                              Layout.nmodules_or_rings,
                                                                                             'Ring' if Layout.isEndcap else 'Module')
            the_list = []
            the_list.append(['',''] + range(Layout.nlayers_or_disks))
            for ring_mod in range(Layout.nmodules_or_rings-1,-1,-1) :
                the_list.append([])
                the_list[-1].append('')
                the_list[-1].append('%d'%(ring_mod))
                for disk_lay in range(Layout.nlayers_or_disks) :
                    index = PlotUtils.GetResultDictIndex(structure_names,ring_mod,disk_lay)
                    the_list[-1].append(saved_configs[index][item]['value'])
            table = TableUtils.PrintLatexTable(the_list,caption=caption)
            # insert special headers
            import re
            i_start_of_data = re.search("data_below\n",table).end()
            table = table[:i_start_of_data] + disk_ring_labels + table[i_start_of_data:]
            config_text_modulespecific += table

        else :
            config_list_general.append([])
            config_list_general[-1].append(item)
            config_list_general[-1].append(saved_configs[0][item]['description'])
            config_list_general[-1].append(saved_configs[0][item]['value'])
            config_list_general[-1].append(saved_configs[0][item]['units'])

    config_text += '\\subsection{Inputs, common to all %s modules}\n'%(Layout.detectorname)
    config_text += TableUtils.PrintLatexTable(config_list_general,justs='llrl')
    config_text += '\\subsection{Inputs, specific to %s}\n'%('endcap module type (R0, R1, etc.)' if Layout.isEndcap else 'barrel layer')
    config_text += TableUtils.PrintLatexTable(config_list_ring_lay_specific,justs='llrrrrrrl')
    config_text += '\n\\clearpage\n\n'
    config_text += '\\subsection{Inputs, specific to %s module position (%s)}\n'%(Layout.detectorname,'ring, disk' if Layout.isEndcap else 'layer, module 0-13')
    config_text += config_text_modulespecific

    return config_text
