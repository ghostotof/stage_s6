'''
Accrochage de phase: escalier du diable
'''
from brian import *

defaultclock.dt=0.01*ms
tau=5*ms
N=300
f=50*Hz
a=.2

eqs='''
dv/dt=(v0-v+a*(sin(2*pi*f*t)+sin(4*pi*f*t)))/tau : 1
v0 : 1
'''

neurons=NeuronGroup(N,model=eqs,threshold=1,reset=0)
neurons.v0=linspace(.9,1.5,N)
neurons.v=rand(N)

run(1*second)
S=SpikeMonitor(neurons)
run(200*ms)
indexes=array([i for i,t in S.spikes])
phases=array([t % (1/f) for i,t in S.spikes])*f
plot(neurons.v0[indexes],phases,'.')
xlabel('Moyenne')
ylabel('Phase')
axis([.9,1.5,0,1])
show()
