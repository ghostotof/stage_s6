# coding: latin-1
'''
Un intègre-et-tire avec des entrées régulières
'''
from brian import *

tau = 10*ms
R = 50*Mohm
gl = 1/R
C=tau/R
taus = 3*ms
El = -70*mV
Vr = -70*mV
Vt = -55*mV
Es = 0*mV

eqs='''
dV/dt = (gl*(El-V)+gs*(Es-V))/C : volt
dgs/dt = -gs/taus : siemens
'''

G = NeuronGroup(1,model=eqs,
                threshold=Vt,reset=Vr)

spikes = linspace(10*ms,150*ms,20)
input = MultipleSpikeGeneratorGroup([spikes])

C = Connection(input,G,'gs')
C[0,0] = 13*nS

M = StateMonitor(G,'V',record=True)

G.V =Vr
run(200*ms)
plot(M.times/ms,M[0]/mV)
xlabel('Time (ms)')
ylabel('V (mV)')
show()
