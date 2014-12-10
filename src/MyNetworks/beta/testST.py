#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle

##############
# PARAMETERS #
##############

min_period = 1 * msecond
basePeriod = 125 * min_period

t_pres = basePeriod * 4

# min_weight = -10.0 * volt
# # min_weight = 0 * volt
# max_weight = 1.0 * volt * 10.0
# inc_weight = max_weight * 0.1
# dec_weight = max_weight * 0.05
# init_weight = ( max_weight - min_weight ) / 2.0
# std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
inhib_weight = 1.0 * volt * 50.0

nbN_I = 200

nbN_1 = 200
Vt_1 = 15 * volt
Vr_1 = 0.0 * volt
tau_1 = basePeriod * (2.0/3.0)
refractory_1 = 0.5 * basePeriod
inhibit_refractory_1 = 1.05 * basePeriod

neuron_eqs_1 = Equations ("""
    dv/dt = ( - v - inh ) / tau_1 : volt
    dinh/dt = - inh / inhibit_refractory_1 : volt
""")

nbN_2 = 100
Vt_2 = 15 * volt
Vr_2 = 0.0 * volt
tau_2 = basePeriod * (2.0/3.0)
refractory_2 = 0.5 * basePeriod
inhibit_refractory_2 = 1.05 * basePeriod

neuron_eqs_2 = Equations ("""
    dv/dt = ( - v - inh ) / tau_2 : volt
    dinh/dt = - inh / inhibit_refractory_2 : volt
""")

nbN_3 = 2
Vt_3 = 15 * volt
Vr_3 = 0.0 * volt
tau_3 = basePeriod * (2.0/3.0)
refractory_3 = 0.5 * basePeriod
inhibit_refractory_3 = 1.05 * basePeriod

neuron_eqs_3 = Equations ("""
    dv/dt = ( - v - inh ) / tau_3 : volt
    dinh/dt = - inh / inhibit_refractory_3 : volt
""")

###

spikesTimes = []
with open('spikesTimesT.spt','rb') as file:
    depick = pickle.Unpickler(file)
    spikesTimes = depick.load()

i = 0
for a,b in spikesTimes:
    spikesTimes[i] = (a, b * t_pres)
    i += 1

nbImagesH = 486
nbImagesN = 482
nbImages = nbImagesH + nbImagesN

#################
# NEURON GROUPS #
#################

input = SpikeGeneratorGroup(nbN_I, spikesTimes)

couche1 = NeuronGroup(N = nbN_1,
                      model = neuron_eqs_1,
                      threshold = Vt_1,
                      reset = Vr_1,
                      refractory = refractory_1)

couche2 = NeuronGroup(N = nbN_2,
                      model = neuron_eqs_2,
                      threshold = Vt_2,
                      reset = Vr_2,
                      refractory = refractory_2)

couche3 = NeuronGroup(N = nbN_3,
                      model = neuron_eqs_3,
                      threshold = Vt_3,
                      reset = Vr_3,
                      refractory = refractory_3)

############
# SYNAPSES #
############

connection = IdentityConnection(input, couche1, 'v', weight = Vt_1 * 1.05)

c1_c2 = Synapses(couche1, couche2, model = 'w:1', pre = 'v+=w')
c1_c2.load_connectivity('./saveConnec_c2')
wn = []
with open('myWeights_c2', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()
for i in xrange(0, len(c1_c2)):
    c1_c2.w[i] = wn[i]

c2_c3 = Synapses(couche2, couche3, model = 'w:1', pre = 'v+=w')
c2_c3.load_connectivity('./saveConnec_c3')
wn = []
with open('myWeights_c3', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()
for i in xrange(0, len(c2_c3)):
    c2_c3.w[i] = wn[i]

##############
# INHIBITION #
##############

# inhib_couche1 = Connection(couche1, couche1, state = 'inh', weight = 0 * volt)
# for i in xrange(2, len(couche1) - 2):
#     inhib_couche1[i, i+2] = inhib_weight
#     inhib_couche1[i, i-2] = inhib_weight

# inhib_couche2 = Connection(couche2, couche2, state = 'inh', weight = 0 * volt)
# for i in xrange(1, len(couche2) - 1):
#     inhib_couche2[i, i+1] = inhib_weight
#     inhib_couche2[i, i-1] = inhib_weight

# inhib_couche3 = Connection(couche3, couche3, state = 'inh', weight = 0 * volt)
# inhib_couche3[0,1] = inhib_weight
# inhib_couche3[1,0] = inhib_weight

inhib_loop_1 = Connection(couche2, couche1, state = 'inh', weight = inhib_weight)
inhib_loop_2 = Connection(couche3, couche2, state = 'inh', weight = inhib_weight)

############
# MONITORS #
############

mc1 = SpikeCounter(couche1)
mc2 = SpikeCounter(couche2)
mc3 = SpikeCounter(couche3)

# mv1 = StateMonitor(couche1, 'v', record = True)
# mv2 = StateMonitor(couche2, 'v', record = True)
# mv3 = StateMonitor(couche3, 'v', record = True)

##############
# SIMULATION #
##############

run(nbImagesH * t_pres, report = 'text')

print "Couche 1 :"
for i in xrange(0, nbN_1):
    print "Neurone (", i, ") : ", mc1[i]

print ""
print "Couche 2 :"
for i in xrange(0, nbN_2):
    print "Neurone (", i, ") : ", mc2[i]

print ""
print "Couche 3 :"
for i in xrange(0, nbN_3):
    print "Neurone (", i, ") : ", mc3[i]

###

run(nbImagesN * t_pres, report = 'text')

print ""
print "Couche 1 :"
for i in xrange(0, nbN_1):
    print "Neurone (", i, ") : ", mc1[i]

print ""
print "Couche 2 :"
for i in xrange(0, nbN_2):
    print "Neurone (", i, ") : ", mc2[i]

print ""
print "Couche 3 :"
for i in xrange(0, nbN_3):
    print "Neurone (", i, ") : ", mc3[i]

# figure('Potentiel')
# for i in xrange(0, len(couche2)):
#     plot(mv2.times, mv2[i])
# for i in xrange(0, len(couche3)):
#     plot(mv3.times, mv3[i])

# show()
