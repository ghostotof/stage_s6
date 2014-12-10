#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle
import sys

##############
# PARAMETERS #
##############

nom = sys.argv[0]
if (nom[0:2] == "./"):
    nom = nom[2:]
if (nom[-3:] == ".py"):
    nom = nom[:-3]

print nom

min_period = 1 * msecond
base_period = 125 * min_period

t_pres = base_period * 4
t_pres_tot = t_pres * 2

min_weight = -10.0 * volt
max_weight = 1.0 * volt * 10.0
inc_weight = max_weight * 0.1
dec_weight = max_weight * 0.05
# init_weight = ( max_weight - min_weight ) / 2.0
init_weight = 0 * volt
# std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
std_init_weight = 10.0 * volt
inhib_weight = %INH_W

###

tab = []
with open('spikesTimesL.spt','rb') as file:
    depick = pickle.Unpickler(file)
    tab = depick.load()

spikesTimes = []
nIm = -1
oldI = -1
nbImagesH = 0
nbImagesN = 0
nbCol = 40
t_col  = t_pres / nbCol

# Pour chaque ligne du tableau
for id,h,i,a,c in tab:
    # Si nouvelle image
    if oldI != i:
        oldI = i
        nIm += 1
        # Si c'est un visage souriant
        if h:
            nbImagesH += 1
        else:
            nbImagesN += 1
    spikesTimes.append((a, nIm * t_pres_tot + c * t_col))

nbImages = nbImagesH + nbImagesN

###
# Init (HappyBrian):
# 
# Vt_1 = 
###

nbN_I = 40

nbN_1 = 40
Vt_1 = 15 * volt
Vr_1 = 0.0 * volt
tau_1 = base_period * (2.0/3.0)
# refractory_1 = 0.5 * base_period
refractory_1 = 0.5 * t_col
inhibit_refractory_1 = 1.05 * base_period

neuron_eqs_1 = Equations ("""
    dv/dt = ( - v - inh ) / tau_1 : volt
    dinh/dt = - inh / inhibit_refractory_1 : volt
""")

nbN_2 = 20
Vt_2 = 15 * volt
Vr_2 = 0.0 * volt
tau_2 = base_period * (2.0/3.0)
refractory_2 = 0.5 * t_col
inhibit_refractory_2 = 1.05 * base_period

neuron_eqs_2 = Equations ("""
    dv/dt = ( - v - inh ) / tau_2 : volt
    dinh/dt = - inh / inhibit_refractory_2 : volt
""")

nbN_3 = 2
Vt_3 = 15 * volt
Vr_3 = 0.0 * volt
# tau_3 = base_period * (2.0/3.0)
tau_3 = base_period * (1.0/3.0)
refractory_3 = %COEF_REF3 * t_pres
inhibit_refractory_3 = 1.05 * base_period

neuron_eqs_3 = Equations ("""
    dv/dt = ( - v - inh ) / tau_3 : volt
    dinh/dt = - inh / inhibit_refractory_3 : volt
""")

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

###

stdp_ltp = base_period * 2

eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

###

c1_c2 = Synapses(couche1, couche2, eqs_stdp,
                 pre="""tPre=t; v+=w""",
                 post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                 (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c1_c2[:,:] = True
c1_c2.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'

c2_c3 = Synapses(couche2, couche3, eqs_stdp,
                 pre="""tPre=t; v+=w""",
                 post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                 (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c2_c3[:,:] = True
c2_c3.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'

##############
# INHIBITION #
##############

inhib_couche1 = Connection(couche1, couche1, state = 'inh', weight = 0 * volt)
for i in xrange(2, len(couche1) - 2):
    inhib_couche1[i, i+2] = inhib_weight
    inhib_couche1[i, i-2] = inhib_weight        
inhib_couche1[0, 2] = inhib_weight
inhib_couche1[1, 3] = inhib_weight
inhib_couche1[len(couche1)-1, len(couche1)-1 - 2] = inhib_weight
inhib_couche1[len(couche1)-2, len(couche1)-2 - 2] = inhib_weight


inhib_couche2 = Connection(couche2, couche2, state = 'inh', weight = 0 * volt)
for i in xrange(1, len(couche2) - 1):
    inhib_couche2[i, i+1] = inhib_weight
    inhib_couche2[i, i-1] = inhib_weight
inhib_couche2[0, 1] = inhib_weight
inhib_couche2[len(couche2)-1, len(couche2)-2] = inhib_weight

inhib_couche3 = Connection(couche3, couche3, state = 'inh', weight = 0 * volt)
inhib_couche3[0,1] = inhib_weight
inhib_couche3[1,0] = inhib_weight

# inhib_loop_1 = Connection(couche2, couche1, state = 'inh', weight = inhib_weight)
# inhib_loop_2 = Connection(couche3, couche2, state = 'inh', weight = inhib_weight)

############
# MONITORS #
############

mc1 = SpikeCounter(couche1)
mc2 = SpikeCounter(couche2)
mc3 = SpikeCounter(couche3)

# mv1 = StateMonitor(couche1, 'v', record = True)
# mv2 = StateMonitor(couche2, 'v', record = True)
# mv3 = StateMonitor(couche3, 'v', record = True)

# mw1_2 = StateMonitor(c1_c2, 'w', record = True)
# mw2_3 = StateMonitor(c2_c3, 'w', record = True)

##############
# SIMULATION #
##############

print "Nb images souriantes :", nbImagesH
print "Nb images non souriantes :", nbImagesN

###

for n in xrange(0, nbImages):
    id,h,i,a,c = tab[n]
    
    old_cptN0 = mc3[0]
    old_cptN1 = mc3[1]

    run(t_pres_tot)

    print ""

    if h:
        print "Image", n, "(happy):"
    else:
        print "Image", n, "(neutral):"

    print "Neurone 0:", mc3[0] - old_cptN0
    print "Neurone 1:", mc3[1] - old_cptN1
    
###
print ""
print "Total:"
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

########
# SAVE #
########

c1_c2.save_connectivity('./saveConnec_c2.spc')
c2_c3.save_connectivity('./saveConnec_c3.spc')

wi = []
for wn in c1_c2.w:
    wi.append(wn)

with open('myWeights_c2.spw', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c2_c3.w:
    wi.append(wn)

with open('myWeights_c3.spw', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

# figure('Poids')
# subplot(211)
# for i in xrange(0, len(c1_c2)):
#     plot(mw1_2.times, mw1_2[i])
# subplot(212)
# for i in xrange(0, len(c2_c3)):
#     plot(mw2_3.times, mw2_3[i])

# savefig(nom + "_" + str(int(time())) + "_W.png")

# figure('Potentiels')
# subplot(311)
# for i in xrange(0, len(couche1)):
#     plot(mv1.times, mv1[i])
# subplot(312)
# for i in xrange(0, len(couche2)):
#     plot(mv2.times, mv2[i])
# subplot(313)
# plot(mv3.times, mv3[0], 'b')
# plot(mv3.times, mv3[1], 'r')
# legend(('0','1'), 'upper right')

# savefig(nom + "_" + str(int(time())) + "_V.png")

# show()
