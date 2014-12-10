# coding: latin-1
'''
Intégrateur parfait contre intégrateur à fuite
'''
from brian import *

tau=10*ms
vt=10*mV
v0=15*mV
a=2*mV
f=200*Hz
eqs='''
dv/dt=(v0+a*sin(2*pi*f*t)-u*v+(u-1)*.5*vt)/tau : volt
u:1
'''
group=NeuronGroup(2,model=eqs,threshold=vt,reset=0*mV)
group.u=[0,1]
M=StateMonitor(group,'v',record=True)

duration=200*ms
run(duration)
plot(M.times/ms,M[0]/mV,'b')
plot(M.times/ms,M[1]/mV,'r')
xlabel('Temps (ms)')
#ylabel('F (Hz)')

show()
