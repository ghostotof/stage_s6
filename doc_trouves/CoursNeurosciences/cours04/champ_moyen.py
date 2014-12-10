# coding: latin-1
'''
Champ moyen
'''
from brian import *

tau=10*ms
taus=5*ms # constante de temps synaptique
w=.22

eqs='''
dv/dt=(i-v)/tau : 1
di/dt=-i/taus : 1
'''

F_entree=10*Hz
N_entree=100
duree=1*second
entree=PoissonGroup(N_entree,F_entree)
neurone=NeuronGroup(1,model=eqs,threshold=1,reset=0)
synapse=Connection(entree,neurone,'i',weight=w)

M=StateMonitor(neurone,'i',record=True)
S_entree=SpikeMonitor(entree)
S=SpikeMonitor(neurone,record=False)

run(duree)
print "Fréquence observée:",S.nspikes/duree
I=w*taus*F_entree*N_entree # entrée moyenne
print "Entrée moyenne:",I
if I>1:
    print "Fréquence prédite (intégrateur à fuite):",1/(tau*log(I/(I-1)))
else:
    print "Fréquence prédite (intégrateur à fuite): 0 Hz"
print "Fréquence prédite (intégrateur parfait):",clip((I-.5)/tau,0,Inf)*Hz

subplot(211)
raster_plot(S_entree)
subplot(212)
plot(M.times/ms,M[0])
plot(M.times/ms,ones(len(M.times))*1,'r') # seuil
xlabel('Temps (ms)')
ylabel('I')
show()
