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


# !!! A OPTI
def addSpikes(tab, n, freq, t_fst, t_inter):
    tab_bis = linspace(0, 1, freq)
    for t in tab_bis:
        if (t * second) < t_inter:
            tab.append((n, (t * second + t_fst)))

##############
# PARAMETERS #
##############

path = '/home/totof/fac/S6/Stage/images/tests/post/'

nbImages = 0
nbPixels = 0

spiketimes = []

t_actu  =   0 * ms
t_pres  = 500 * ms
t_pause =   1 * second

dirs = os.listdir(path)

# Pour chaque fichier
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        nbImages += 1
        nbPixels  = 0
        image = io.imread(path + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                addSpikes(spiketimes, nbPixels, freq, t_actu, t_pres)
                nbPixels += 1

        # Fin image n => pause de 1 seconde
        t_actu += t_pres
        for i in xrange(0, nbPixels):
            addSpikes(spiketimes, i, 2, t_actu, t_pause)
            
        # Fin de la pause
        t_actu += t_pause

#################
# NEURON GROUPS #
#################

min_period = 1 * msecond
basePeriod = 5 * min_period

min_weight = -10.0 * volt
max_weight = 1.0 * volt * 10.0
inc_weight = max_weight * 0.2
dec_weight = max_weight * 0.1
init_weight = ( max_weight - min_weight ) / 2.0
std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
# inhib_weight = 1.0 * volt * 50.0
inhib_weight = 1.0 * volt * 200.0

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

input = SpikeGeneratorGroup(400, spiketimes)

couche1 = NeuronGroup(N = 50,
                      model = neuron_eqs,
                      threshold = Vt,
                      reset = Vr,
                      refractory = refractory)

couche2 = NeuronGroup(N = 20,
                      model = neuron_eqs,
                      threshold = Vt,
                      reset = Vr,
                      refractory = refractory)

couche3 = NeuronGroup(N = 2,
                      model = neuron_eqs,
                      threshold = Vt,
                      reset = Vr,
                      refractory = refractory)

############
# SYNAPSES #
############

c_c1 = Synapses(input, couche1, model = 'w:1', pre = 'v+=w')
c_c1.load_connectivity('./saveConnec_c1')

wn = []
with open('myWeights_c1', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(c_c1)):
    c_c1.w[i] = wn[i]

###

c_c2 = Synapses(couche1, couche2, model = 'w:1', pre = 'v+=w')
c_c2.load_connectivity('./saveConnec_c2')

wn = []
with open('myWeights_c2', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(c_c2)):
    c_c2.w[i] = wn[i]

###

c_c3 = Synapses(couche2, couche3, model = 'w:1', pre = 'v+=w')
c_c3.load_connectivity('./saveConnec_c3')

wn = []
with open('myWeights_c3', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

for i in xrange(0, len(c_c3)):
    c_c3.w[i] = wn[i]

##############
# INHIBITION #
##############

inhib_couche1 = Connection(couche1, couche1, state = 'inh', weight = inhib_weight)
inhib_couche2 = Connection(couche2, couche2, state = 'inh', weight = inhib_weight)
inhib_couche3 = Connection(couche3, couche3, state = 'inh', weight = inhib_weight)

inhib_loop_1 = Connection(couche2, couche1, state = 'inh', weight = inhib_weight)
inhib_loop_2 = Connection(couche3, couche2, state = 'inh', weight = inhib_weight)

############
# MONITORS #
############

m = SpikeCounter(couche3)
mv = StateMonitor(couche3, 'v', record = True)

##############
# SIMULATION #
##############

run(t_actu, report = 'text')

print "Nb spikes happy = ", m[0]
print "Nb spikes unhappy = ", m[1]

figure()
plot(mv.times, mv[0], 'b')
plot(mv.times, mv[1], 'r')

show()
