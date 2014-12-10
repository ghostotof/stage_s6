# coding: latin-1
'''
Intégrateur parfait
'''
from brian import *

f=200*Hz
tau=20*ms
#neurone=NeuronGroup(2,model='dv/dt=(1+.5*sin(2*pi*f*t))/(20*ms) : 1',threshold=1,reset=0)
neurone=NeuronGroup(2,model='dv/dt=(1+.5*sin(2*pi*f*t))/tau+.1*tau**(-.5)*xi : 1',threshold=1,reset=0)
#neurone.v=[0,0.5]
M=StateMonitor(neurone,'v',record=True)
run(100*ms)
plot(M.times/ms,M[0],'r')
plot(M.times/ms,M[1],'b')
xlabel('Time (ms)')
show()
