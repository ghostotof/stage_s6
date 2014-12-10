'''
Accrochage de phase: escalier du diable
'''
from brian import *

#defaultclock.dt=0.01*ms
tau=5*ms
N=10
f=50*Hz
a=.2

eqs='''
dv/dt=(v0-v+a*(sin(2*pi*f*t)+sin(4*pi*f*t)))/tau : 1
v0 : 1
'''

neurons=NeuronGroup(N,model=eqs,threshold=1,reset=0)
neurons.v0=1.45
neurons.v=rand(N)

run(1*second)
S=SpikeMonitor(neurons)
run(100*ms)
raster_plot(S)
show()
