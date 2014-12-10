#!/usr/bin/python2
# coding:utf-8
from brian import *

a = rand()
b = rand()
c = rand()

tau = 10   * ms
Vt  = 10   * mV
Vr  =  0   * mV
El  =  0   * mV
ws  =  5.5 * mV

eqs = Equations("""
dV/dt = -(V-El)/tau : volt
""")

spiketimes = []

if a > b:
    spiketimes.append((0, 1 * ms))

if a > c:
    spiketimes.append((1, 1 * ms))

if b > a:
    spiketimes.append((2, 1 * ms))

if b > c:
    spiketimes.append((3, 1 * ms))

if c > a:
    spiketimes.append((4, 1 * ms))

if c > b:
    spiketimes.append((5, 1 * ms))

G1 = SpikeGeneratorGroup(6, spiketimes)
G2 = NeuronGroup(N = 3, model = eqs, threshold = Vt, reset = Vr)

C1 = Connection(G1, G2, 'V')
C1[0,0] = ws
C1[1,0] = ws
C1[2,1] = ws
C1[3,1] = ws
C1[4,2] = ws
C1[5,2] = ws

M = StateMonitor(G2, 'V', record = True)
cpt = SpikeCounter(G2)

run(2 * ms)

print "Nb spike from G2[0] :", cpt[0]
print "Nb spike from G2[1] :", cpt[1]
print "Nb spike from G2[2] :", cpt[2]
print ""
print "a =", a
print "b =", b
print "c =", c
plot(M.times, M[0])
plot(M.times, M[1])
plot(M.times, M[2])
legend(('a','b','c'), 'upper right')
show()
