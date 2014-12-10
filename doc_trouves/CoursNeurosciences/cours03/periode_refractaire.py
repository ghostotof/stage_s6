# coding: latin-1
'''
Fréquence de décharge d'un intègre-et-tire
'''
from brian import *

N=1000
tau=10*ms
vt=10*mV
v0=11*mV
eqs='''
dv/dt=(v0-v)/tau : volt
'''
group=NeuronGroup(N,model=eqs,threshold=vt,reset=0*mV,
                  refractory=5*ms)

M=StateMonitor(group,'v',record=True)

duration=100*ms
run(duration)
plot(M.times/ms,M[0]/mV)
xlabel('Temps (ms)')
ylabel('Vm (mV)')

show()
