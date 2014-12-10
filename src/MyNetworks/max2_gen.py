#!/usr/bin/python2
# coding:utf-8
from brian import *

a = rand()
b = rand()
c = rand()

F = [(a*100) * Hz, (b*100) * Hz, (c*100) * Hz]

tau = 10 * ms
Vt  = 10 * mV
Vr  =  0 * mV
El  = Vr

we  = Vt
wi  = -2 * Vt

eqs = Equations("""
dV/dt = -(V-El)/tau : volt
""")

G1 = PoissonGroup(3, rates = F)
G2 = NeuronGroup(N = 3, model = eqs, threshold = Vt, reset = Vr)

C = Connection(G1, G2, 'V')
C[:,:] = wi
C[0,0] = we
C[1,1] = we
C[2,2] = we

Ci = Connection(G2, G2, 'V')
Ci[0,1] = wi
Ci[0,2] = wi
Ci[1,0] = wi
Ci[1,2] = wi
Ci[2,0] = wi
Ci[2,1] = wi

cpt1 = SpikeCounter(G1)
cpt2 = SpikeCounter(G2)

run(5 * second)

print "# spikes from 1st G1:", cpt1[0]
print "# spikes from 2nd G1:", cpt1[1]
print "# spikes from 3rd G1:", cpt1[2]
print ""
print "# spikes from 1st G2:", cpt2[0]
print "# spikes from 2nd G2:", cpt2[1]
print "# spikes from 3rd G2:", cpt2[2]
print ""
print "a =", a
print "b =", b
print "c =", c
