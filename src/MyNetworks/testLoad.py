#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle

nb_ex = 50
nb_test = 100
nb_sui = 150
spiketimes = []

pres_time = 20 * ms

# a plus grand
for i in xrange(0, nb_ex):
    spiketimes.append((0, i * pres_time))
    spiketimes.append((1, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((3, i * pres_time))
    else:
        spiketimes.append((5, i * pres_time))

# b plus grand
for i in xrange(nb_ex, nb_test):
    spiketimes.append((2, i * pres_time))
    spiketimes.append((3, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((1, i * pres_time))
    else:
        spiketimes.append((4, i * pres_time))

# c plus grand
for i in xrange(nb_test, nb_sui):
    spiketimes.append((4, i * pres_time))
    spiketimes.append((5, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((0, i * pres_time))
    else:
        spiketimes.append((2, i * pres_time))

min_period = 1 * msecond
basePeriod = 5 * min_period

inhib_weight = 1.0 * volt * 50.0

Vt = 10 * volt
Vr = 0.0 * volt
tau = basePeriod * (2.0/3.0)
refractory = 0.5 * basePeriod
inhibit_refractory = 1.05 * basePeriod

neuron_eqs = Equations ("""
    dv/dt = ( - v - inh ) / tau : volt
    dinh/dt = - inh / inhibit_refractory : volt
""")

number_neurons_couche = 3

input = SpikeGeneratorGroup(6, spiketimes)

couche = NeuronGroup(N = number_neurons_couche,
                           model = neuron_eqs,
                           threshold = Vt,
                           reset = Vr,
                           refractory = refractory)

c_c1 = Synapses(input, couche, model = 'w:1', pre = 'v+=w')

inhib_couche = Connection(couche, couche, state = 'inh', weight = 0 * volt)
inhib_couche[0,1] = inhib_weight
inhib_couche[0,2] = inhib_weight
inhib_couche[1,0] = inhib_weight
inhib_couche[1,2] = inhib_weight
inhib_couche[2,0] = inhib_weight
inhib_couche[2,1] = inhib_weight

c_c1.load_connectivity('./saveConnec')

# print ""
# print "Après load_connectivity:"
# print""
# print "w 0 :", c_c1.w[0]
# print "w 1 :", c_c1.w[1]
# print "w 2 :", c_c1.w[2]
# print "w 3 :", c_c1.w[3]
# print "w 4 :", c_c1.w[4]
# print "w 5 :", c_c1.w[5]
# print "w 6 :", c_c1.w[6]

with open('myWeights', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, 18):
    c_c1.w[i] = wn[i]

# print ""
# print "Après Unpickler:"
# print""
# print "w 0 :", c_c1.w[0]
# print "w 1 :", c_c1.w[1]
# print "w 2 :", c_c1.w[2]
# print "w 3 :", c_c1.w[3]
# print "w 4 :", c_c1.w[4]
# print "w 5 :", c_c1.w[5]
# print "w 6 :", c_c1.w[6]

moni = StateMonitor(couche, 'v', record = True)
m2   = StateMonitor(c_c1, 'w', record = True)
cpt = SpikeCounter(couche)

run(nb_sui * pres_time)

print ""
print "nb spikes from 0 =", cpt[0]
print "nb spikes from 1 =", cpt[1]
print "nb spikes from 2 =", cpt[2]

figure()
plot(moni.times, moni[0],'b')
plot(moni.times, moni[1],'r')
plot(moni.times, moni[2],'g')
legend(('0','1','2'), 'upper right')
savefig("testLoad_V.png")

show()
