# coding: latin-1
'''
Intégrateur parfait II
'''
from brian import *

f=200*Hz
neurone=NeuronGroup(1,model='dv/dt=(.5+sin(2*pi*f*t))/(10*ms) : 1',threshold=1,reset=0)
M=StateMonitor(neurone,'v',record=True)
run(100*ms)
plot(M.times/ms,M[0])
xlabel('Time (ms)')
show()
