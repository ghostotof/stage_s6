'''
Olfactory processing.
Each olfactory object corresponds to 25 chemical components with common fluctuations.
There are 50 receptors as leaky integrate-and-fire neurons, each for each chemical component.
Then 4 detectors are defined, receiving inputs from receptors:
1-25
26-50
even receptors
odd receptors
In the first half, two objects are presented: 1-25 and 26-50.
In the second half two objects are presented: even and odd components.
Thus in both cases all receptors are equally active, but synchronous fluctuations create
cooperative groups.
'''
from brian import *

# Two olfactory objects with their own fluctuations
tau_odour=5*ms
fluctuations=NeuronGroup(2,model="dx/dt=-x/tau_odour+(2./tau_odour)**.5*xi:1")

# Receptors
tau=5*ms
eqs='''
dv/dt=(1.5*x-v)/tau + .1*(2./tau)**.5*xi : 1
x:1
'''
receptors=NeuronGroup(50,model=eqs,threshold=1,reset=0,refractory=5*ms)
groupA=receptors[0:25]
groupB=receptors[25:50]

@network_operation
def olfactory_input(clock):
    if clock.t<1000*ms:
        groupA.x=fluctuations.x[0]
        groupB.x=fluctuations.x[1]
    else:
        receptors.x[0:50:2]=fluctuations.x[0]
        receptors.x[1:51:2]=fluctuations.x[1]
        
spikes=SpikeMonitor(receptors)

# Detectors
detectors=NeuronGroup(40,model='dv/dt=-v/tau + .05*(2./tau)**.5*xi : 1',threshold=1,reset=0,\
                      refractory=5*ms)
C=Connection(receptors,detectors,'v')
w=.05
C.connect_full(groupA,detectors[0:10],weight=w)
C.connect_full(groupB,detectors[10:20],weight=w)
for i in range(len(receptors)):
    if i%2==0:
        C.connect_full(receptors[i],detectors[20:30],weight=w)
    else:
        C.connect_full(receptors[i],detectors[30:40],weight=w)

spikes_detectors=SpikeMonitor(detectors)

run(2000*ms)
subplot(211)
raster_plot(spikes)
subplot(212)
raster_plot(spikes_detectors)
show()
