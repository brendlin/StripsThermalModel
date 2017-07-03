#
# Global settings
#

# Step size for calculation
step = 1/12.
nyears = 14
nstep = int(nyears/float(step))

# Step size for temperature (determines roughly the granularity of reported sensor temperatures)
ts_step = 5 # steps per degree

# time_step_list is a list of each step through the years, for plotting purposes maybe.
# It is size nstep+1
time_step_list = []
time_step_list.append(0)
for i in range(nstep) :
    time_step_list.append( time_step_list[-1] + step )

# Used to live in NominalPower
nomsensorT = 0

# Temperature kelvin / celsius conversion
def kelvin(celsius) :
    return 273.15 + celsius
