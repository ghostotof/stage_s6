# coding: latin-1
'''
Fréquence de décharge d'un intègre-et-tire
'''
from brian import *

N=1000
tau=10*ms
vt=10*mV
eqs='''
dv/dt=(v0-v)/tau : volt
v0 : volt
'''
group=NeuronGroup(N,model=eqs,threshold=vt,reset=0*mV)
group.v0=linspace(0*mV,25*mV,N)

counter=SpikeCounter(group)

duration=5*second
run(duration)
plot(group.v0/mV,counter.count/duration,'b')
# Théorie (intégrateur parfait avec v remplacé par vt/2)
plot(group.v0/mV,(group.v0-vt*.5)/vt/tau/Hz,'g')
xlabel('RI (mV)')
ylabel('F (Hz)')
axis([0,25,-10,200])

show()
