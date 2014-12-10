#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle
import os
from skimage import io

##############
# PARAMETERS #
##############

nbImagesS = 100
nbImagesNS = 100
n = 0

pauseFreq   = []
spikeFreq   = []
teachFreqS  = [50*Hz, 2*Hz]
teachFreqNS = [2*Hz, 50*Hz]
teachFreqSi = [0*Hz,  0*Hz]

t_actu  =   0 * ms
t_pres  = 500 * ms
t_pause =   1 * second
t_elem  = t_pres + t_pause

for i in xrange(0, 400):
    pauseFreq.append(2 * Hz)

with open('spikeFreq.spt', 'rb') as fichier:
    depick = pickle.Unpickler(fichier)
    spikeFreq = depick.load()

def wTab(t):
    global n

    if t == ((n+1)*t_elem):
        n += 1

    if (t >= n * t_elem) and (t < n * t_elem + t_pres):
        return spikeFreq[n]
    else:
        return pauseFreq

def wTeach(t):
    global n

    if (t >= n * t_elem) and (t < n * t_elem + t_pres):
        if n < nbImagesS:
            return teachFreqS
        else:
            return teachFreqNS
    else:
        return teachFreqSi

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

input = PoissonGroup(400, rates = lambda t: wTab(t))

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

# stdp_ltp = basePeriod * 2
stdp_ltp = basePeriod / 2

eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

###

i_c1 = Synapses(input, couche1, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

i_c1[:,:] = True
# i_c1.w = '8 * volt'
i_c1.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'

c1_c2 = Synapses(couche1, couche2, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c1_c2[:,:] = True
# c1_c2.w = '8 * volt'
c1_c2.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'

c2_c3 = Synapses(couche2, couche3, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c2_c3[:,:] = True
# c2_c3.w = '8 * volt'
c2_c3.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'

###########
# TEACHER #
###########

teacher = PoissonGroup(2, rates = lambda t: wTeach(t))

inh_c1 = Connection(teacher, couche3, state = 'v')
inh_c1[0,0] = -15*volt
inh_c1[1,1] = -15*volt

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

mc1 = SpikeCounter(couche1)
mc2 = SpikeCounter(couche2)
mc3 = SpikeCounter(couche3)
# m1   = StateMonitor(i_c1, 'w', record = True)
# m2   = StateMonitor(c1_c2, 'w', record = True)
m3 = StateMonitor(c2_c3, 'w', record = [0,1])

##############
# SIMULATION #
##############

run(200 * t_elem, report = 'text')

########
# SAVE #
########

i_c1.save_connectivity('./saveConnec_c1')
c1_c2.save_connectivity('./saveConnec_c2')
c2_c3.save_connectivity('./saveConnec_c3')

wi = []
for wn in i_c1.w:
    wi.append(wn)

with open('myWeights_c1', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c1_c2.w:
    wi.append(wn)

with open('myWeights_c2', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c2_c3.w:
    wi.append(wn)

with open('myWeights_c3', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

print "Nb spikes from couche1 :"
for i in xrange(0, 30):
    print "Neurone (",i,") : ", mc1[i]
print ""
print "Nb spikes from couche2 :"
for i in xrange(0, 15):
    print "Neurone (",i,") : ", mc2[i]
print ""
print "Nb spikes from couche3 :"
for i in xrange(0, 2):
    print "Neurone (",i,") : ", mc3[i]

figure()
plot(m3.times, m3[0], 'b')
plot(m3.times, m3[1], 'r')

show()
