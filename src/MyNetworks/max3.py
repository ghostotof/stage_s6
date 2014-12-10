#!/usr/bin/python2
# coding:utf-8
from brian import *
from time import time

######
# DATA
######

a = int(rand() * 100)
b = int(rand() * 100)
c = int(rand() * 100)
# a = 92
# b = 69
# c = 14
# a = 61
# b = 74
# c = 60
# a = 2
# b = 0
# c = 0
# a = 28
# b = 0
# c = 0
# a = 45
# b = 35
# c = 44

spiketimes = []

for i in linspace(0, 10, a):
    spiketimes.append((0, i * ms))

for i in linspace(0, 10, b):
    spiketimes.append((1, i * ms))

for i in linspace(0, 10, c):
    spiketimes.append((2, i * ms))

############
# PARAMETERS
############

tau = 10 * ms
Vt  = 10 * mV
Vr  =  0 * mV
El  = Vr

we  =  1.1 * Vt
wi  = -we

eqs = Equations("""
dV/dt = -(V-El)/tau : volt
""")

###############
# NEURON GROUPS
###############

input = SpikeGeneratorGroup(3, spiketimes)

G1 = NeuronGroup(N = 6, model = eqs, threshold = Vt, reset = Vr)

G2 = NeuronGroup(N = 3, model = eqs, threshold = 2*Vt, reset = Vr)

##########
# SYNAPSES
##########

C1 = Connection(input, G1, 'V')
C1[0,0] = we
C1[0,1] = we
C1[0,2] = wi
C1[0,4] = wi
C1[1,2] = we
C1[1,3] = we
C1[1,0] = wi
C1[1,5] = wi
C1[2,4] = we
C1[2,5] = we
C1[2,1] = wi
C1[2,3] = wi

C2 = Connection(G1, G2, 'V')
C2[0,0] = we
C2[0,1] = wi
C2[1,0] = we
C2[1,2] = wi
C2[2,0] = wi
C2[2,1] = we
C2[3,1] = we
C2[3,2] = wi
C2[4,0] = wi
C2[4,2] = we
C2[5,1] = wi
C2[5,2] = we

C2[0,2] = wi/2
C2[1,1] = wi/2
C2[2,2] = wi/2
C2[3,0] = wi/2
C2[4,1] = wi/2
C2[5,0] = wi/2

# C3 = Connection(G2, G2, 'V')
# C3[0,1] = wi
# C3[0,2] = wi
# C3[1,0] = wi
# C3[1,2] = wi
# C3[2,0] = wi
# C3[2,1] = wi

############
# MONITORING
############

cptI = SpikeCounter(input)
cpt1 = SpikeCounter(G1)
cpt2 = SpikeCounter(G2)

M2 = StateMonitor(G2, 'V', record = True)

#########
# RUNNING
#########

run(2 * ms)

##########
# PRINTING
##########
print "a =", a
print "b =", b
print "c =", c
print ""
print "# spikes from input 0 :", cptI[0]
print "# spikes from input 1 :", cptI[1]
print "# spikes from input 2 :", cptI[2]
print ""
print "# spikes from G1 0 :", cpt1[0]
print "# spikes from G1 1 :", cpt1[1]
print "# spikes from G1 2 :", cpt1[2]
print "# spikes from G1 3 :", cpt1[3]
print "# spikes from G1 4 :", cpt1[4]
print "# spikes from G1 5 :", cpt1[5]
print ""
print "# spikes from G2 0 :", cpt2[0]
print "# spikes from G2 1 :", cpt2[1]
print "# spikes from G2 2 :", cpt2[2]

# plot(M2.times, M2[0],'r')
# plot(M2.times, M2[1],'g')
# plot(M2.times, M2[2],'b')
# legend(('a','b','c'), 'upper right')
# show()
