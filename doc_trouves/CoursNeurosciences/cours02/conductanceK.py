# coding: latin-1
'''
Canal K+ voltage-dépendant.
'''
from brian import *

El=-70*mV
tau=20*ms
R=50*Mohm
C=tau/R # capacité
tauK=1*ms
va=-60*mV # demi-activation
k=3*mV # pente
#gK=1/R # conductance K+ maximale (ici = conductance de fuite)
EK=-90*mV # potentiel de réversion

eqs='''
dv/dt=(El-v)/tau + gK*m*(EK-v)/C : volt
#dv/dt=(El-v)/tau + gK*m*(EK-El)/C : volt
dm/dt=(minf-m)/tauK : 1 # ouverture du canal K+
minf=1/(1+exp((va-v)/k)) : 1
#minf=1/(1+exp((va-El)/k))+(v-El)* : 1
gK : siemens
'''

neurone=NeuronGroup(2,model=eqs)
neurone.v=El
neurone.m=neurone.minf
neurone.gK=[0/R,1/R]

run(50*ms)
Mv=StateMonitor(neurone,'v',record=True)
Mm=StateMonitor(neurone,'m',record=True)
run(10*ms)
neurone.v+=15*mV
run(50*ms)

subplot(211)
plot(Mv.times/ms,Mv[0]/mV,'r')
plot(Mv.times/ms,Mv[1]/mV,'b')
ylabel('Vm (mV)')
subplot(212)
plot(Mm.times/ms,Mm[1])
ylabel('m')
xlabel('Temps (ms)')
show()
