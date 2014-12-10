#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle
import os
from skimage import io

#############
# FUNCTIONS #
#############

# Param   : Valeur entre 0 et 255
# Renvoie : Valeur entre 2 et 50
def lvl2freq(lvl):
    return (lvl/255.)*48+2

##############
# PARAMETERS #
##############

path = '/home/totof/fac/S6/Stage/images/tests/post/'

nbImages = 0
nbPixels = 0

spikeFreq = []

t_actu  =   0 * ms
t_pres  = 500 * ms
t_pause =   1 * second

dirs = os.listdir(path)

# Pour chaque fichier
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        temp = []
        image = io.imread(path + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                temp.append(freq * Hz)

        spikeFreq.append(temp)

#################
# NEURON GROUPS #
#################

# min_period = 1 * msecond
# basePeriod = 5 * min_period
min_period = 20 * msecond
basePeriod = 5 * min_period

min_weight = -10.0 * volt
max_weight = 1.0 * volt * 10.0
inc_weight = max_weight * 0.2
dec_weight = max_weight * 0.1
init_weight = ( max_weight - min_weight ) / 2.0
std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
inhib_weight = 1.0 * volt * 50.0

Vt = 15 * volt
Vr = 0.0 * volt
tau = basePeriod * (2.0/3.0)
refractory = 0.5 * basePeriod
inhibit_refractory = 1.05 * basePeriod

neuron_eqs = Equations ("""
    dv/dt = ( - v - inh ) / tau : volt
    dinh/dt = - inh / inhibit_refractory : volt
""")

###

input = PoissonGroup(400, rates = spikeFreq[0])

couche1 = NeuronGroup(N = 30,
                      model = neuron_eqs,
                      # threshold = Vt,
                      threshold = 200 * volt,
                      reset = Vr,
                      refractory = refractory)

couche2 = NeuronGroup(N = 15,
                      model = neuron_eqs,
                      # threshold = Vt,
                      threshold = 250 * volt,
                      reset = Vr,
                      refractory = refractory)

couche3 = NeuronGroup(N = 2,
                      model = neuron_eqs,
                      # threshold = Vt,
                      threshold = 100 * volt,
                      reset = Vr,
                      refractory = refractory)

############
# SYNAPSES #
############

i_c1 = Synapses(input, couche1, model = 'w:1', pre = 'v+=w')
i_c1.load_connectivity('./saveConnec_c1')

wn = []
with open('myWeights_c1', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(i_c1)):
    i_c1.w[i] = wn[i]

###

c1_c2 = Synapses(couche1, couche2, model = 'w:1', pre = 'v+=w')
c1_c2.load_connectivity('./saveConnec_c2')

wn = []
with open('myWeights_c2', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(c1_c2)):
    c1_c2.w[i] = wn[i]

###

c2_c3 = Synapses(couche2, couche3, model = 'w:1', pre = 'v+=w')
c2_c3.load_connectivity('./saveConnec_c3')

wn = []
with open('myWeights_c3', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(c2_c3)):
    print "poids de la synapse i (",i,") = ", wn[i]
    c2_c3.w[i] = wn[i]

##############
# INHIBITION #
##############

# inhib_couche1 = Connection(couche1, couche1, state = 'inh', weight = inhib_weight)
# inhib_couche2 = Connection(couche2, couche2, state = 'inh', weight = inhib_weight)
# inhib_couche3 = Connection(couche3, couche3, state = 'inh', weight = inhib_weight)

inhib_couche1 = Connection(couche1, couche1, state = 'v', weight = 0 * volt)
for i in xrange(2, len(couche1)-2):
    inhib_couche1[i, i+2] = - inhib_weight
    inhib_couche1[i, i-2] = - inhib_weight

inhib_couche2 = Connection(couche2, couche2, state = 'v', weight = - inhib_weight)
inhib_couche3 = Connection(couche3, couche3, state = 'v', weight = - inhib_weight)

# inhib_loop_1 = Connection(couche2, couche1, state = 'inh', weight = inhib_weight)
# inhib_loop_2 = Connection(couche3, couche2, state = 'inh', weight = inhib_weight)

############
# MONITORS #
############

m = SpikeCounter(couche3)
mv = StateMonitor(couche3, 'v', record = True)

##############
# SIMULATION #
##############

run(500 * ms, report = 'text')

print "Nb spikes from couche1 :"
for i in xrange(0, 30):
    print "Neurone (",i,") : ", mc1[i]
print ""
print "Nb spikes from couche2 :"
for i in xrange(0, 15):
    print "Neurone (",i,") : ", mc2[i]
print ""
for i in xrange(0, 2):
    print "Neurone (",i,") : ", mc3[i]

figure()
plot(mv.times, mv[0], 'b')
plot(mv.times, mv[1], 'r')

show()
