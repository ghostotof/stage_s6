# coding: latin-1
'''
Un intègre-et-tire avec des entrées régulières
'''
from brian import *

tau = 10*ms
Vr = -70*mV
Vt = -55*mV

G = NeuronGroup(1,model="dV/dt = -(V-Vr)/tau : volt",
                threshold=Vt,reset=Vr)

spikes = linspace(10*ms,100*ms,25)
input = MultipleSpikeGeneratorGroup([spikes])

C = Connection(input,G)
C[0,0] = 5*mV

M = StateMonitor(G,'V',record=True)

G.V =Vr
run(100*ms)
plot(M.times/ms,M[0]/mV)
show()
