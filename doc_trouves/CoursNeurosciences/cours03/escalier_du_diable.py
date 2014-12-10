'''
Accrochage de phase: escalier du diable
'''
from brian import *

tau=5*ms
N=1000
f=50*Hz
a=.2
duration=5*second

eqs='''
dv/dt=(v0-v+a*(sin(2*pi*f*t)+sin(4*pi*f*t)))/tau : 1
v0 : 1
'''

neurons=NeuronGroup(N,model=eqs,threshold=1,reset=0)
neurons.v0=linspace(.9,1.5,N)
counter=SpikeCounter(neurons)

run(duration)
plot(neurons.v0,counter.count/duration,'b')
#plot(neurons.v0,(neurons.v0-.5)/tau,'r')
axis([neurons.v0[0],neurons.v0[-1],0,max(counter.count/duration)])
xlabel('Moyenne')
ylabel('F (Hz)')
show()
