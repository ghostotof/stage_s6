'''
Reliability of spike timing.
Mainen & Sejnowski (1995)

R. Brette
'''
from brian import *

# The common noisy input
N=25
tau_input=5*ms
input=NeuronGroup(1,model='dx/dt=-x/tau_input+(2./tau_input)**.5*xi:1')
Min=StateMonitor(input,'x',record=True)

# The noisy neurons receiving the same input
tau=10*ms
sigma=.02
eqs_neurons='''
dx/dt=(1.1+.5*I-x)/tau+sigma*(2./tau)**.5*xi:1
I : 1
'''
neurons=NeuronGroup(N,model=eqs_neurons,threshold=1,reset=0,refractory=5*ms)
neurons.x=rand(N)
spikes=SpikeMonitor(neurons)

@network_operation
def inject():
    neurons.I=input.x[0]

run(500*ms)
subplot(211)
t=Min.times/ms
plot(t,Min[0])
plot(t,t*0-.1/.5,'r')
subplot(212)
raster_plot(spikes)
show()
