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

pathHappy = '/home/totof/fac/S6/Stage/images/tests/happy/'
pathUnhappy = '/home/totof/fac/S6/Stage/images/tests/unhappy/'

nbImagesS = 0
nbImagesNS = 0
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

dirs = os.listdir(pathHappy)

# Pour chaque fichier
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        temp = []
        image = io.imread(pathHappy + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                temp.append(freq * Hz)

        spikeFreq.append(temp)
        nbImagesS += 1

dirs = os.listdir(pathUnhappy)

# Pour chaque fichier
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        temp = []
        image = io.imread(pathUnhappy + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                temp.append(freq * Hz)

        spikeFreq.append(temp)
        nbImagesNS += 1

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

min_period = 1 * msecond
# basePeriod = 5 * min_perio
basePeriod = 500 * ms

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
                      threshold = Vt,
                      reset = Vr,
                      refractory = refractory)

couche2 = NeuronGroup(N = 15,
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

stdp_ltp = basePeriod * 2

eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

###

c_c1 = Synapses(input, couche1, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c_c1[:,:] = True
c_c1.w = '8 * volt'

c_c2 = Synapses(couche1, couche2, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c_c2[:,:] = True
c_c2.w = '8 * volt'

c_c3 = Synapses(couche2, couche3, eqs_stdp,
                pre="""tPre=t; v+=w""",
                post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c_c3[:,:] = True
c_c3.w = '8 * volt'

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

inhib_couche1 = Connection(couche1, couche1, state = 'inh', weight = inhib_weight)
inhib_couche2 = Connection(couche2, couche2, state = 'inh', weight = inhib_weight)
inhib_couche3 = Connection(couche3, couche3, state = 'inh', weight = inhib_weight)

inhib_loop_1 = Connection(couche2, couche1, state = 'inh', weight = inhib_weight)
inhib_loop_2 = Connection(couche3, couche2, state = 'inh', weight = inhib_weight)

############
# MONITORS #
############

# mc = SpikeCounter(couche3)
# m1   = StateMonitor(c_c1, 'w', record = True)
# m2   = StateMonitor(c_c2, 'w', record = True)
m3   = StateMonitor(c_c3, 'w', record = True)

##############
# SIMULATION #
##############

run((nbImagesS + nbImagesNS) * t_elem, report = 'text')

########
# SAVE #
########

c_c1.save_connectivity('./saveConnec_c1')
c_c2.save_connectivity('./saveConnec_c2')
c_c3.save_connectivity('./saveConnec_c3')

wi = []
for wn in c_c1.w:
    wi.append(wn)

with open('myWeights_c1', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c_c2.w:
    wi.append(wn)

with open('myWeights_c2', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c_c3.w:
    wi.append(wn)

with open('myWeights_c3', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

figure()
plot(m3.times, m3[0])
plot(m3.times, m3[1])
plot(m3.times, m3[2])
plot(m3.times, m3[3])

show()
