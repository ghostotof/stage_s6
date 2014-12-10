# coding:latin-1
# Régularité de la décharge d'un intègre-et-tire
from brian import *

N=100
tau=10*ms
taus=3*ms
duree=10*second
eqs='''
dv/dt=(i0+sigma*i-v)/tau : 1
di/dt=-i/taus+(2/taus)**.5*xi : 1
i0 : 1
sigma : 1
'''

P=NeuronGroup(N,model=eqs,threshold=1,reset=0)
P.i0[:N/2]=linspace(.7,1.5,N/2)
P.i0[N/2:]=P.i0[:N/2]
P.sigma[:N/2]=.2
P.sigma[N/2:]=.5
spikes=SpikeMonitor(P)
run(duree,report='text')

cv=zeros(N)
F=zeros(N)
for i in range(N):
    cv[i]=CV(spikes[i])
    F[i]=firing_rate(spikes[i])
    
#subplot(211)
#plot(P.i0,F)
#subplot(212)
plot(P.i0[:N/2],cv[:N/2],'b')
plot(P.i0[N/2:],cv[N/2:],'r')
ylabel('CV')
xlabel('I')
show()
