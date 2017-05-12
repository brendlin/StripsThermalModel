#
# Global settings
#

# Step size for calculation
step = 1/12.
nyears = 14
nstep = int(nyears/float(step))

# time_step_list is a list of each step through the years, for plotting purposes maybe.
time_step_list = []
time_step_list.append(0)
for i in range(nstep) :
    time_step_list.append( time_step_list[-1] + step )
