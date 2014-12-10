#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle

##############
# PARAMETERS #
##############

min_period = %MIN_PER * msecond
base_period = %BAS_PER * min_period

t_pres = %T_PRES * base_period
t_pres_tot = %T_TOT * t_pres

inhib_weight = %INH_W * volt

###

tab = []
with open('spikesTimesT.spt','rb') as file:
    depick = pickle.Unpickler(file)
    tab = depick.load()

spikesTimes = []
tabHN = []
nIm = -1
oldI = -1
nbImagesH = 0
nbImagesN = 0
nbCol = 40
t_col  = t_pres / nbCol

# Pour chaque ligne du tableau
for id,fn,h,i,a,c in tab:
    # Si nouvelle image
    if oldI != i:
        oldI = i
        nIm += 1
        tabHN.append((h, fn))
        # Si c'est un visage souriant
        if h:
            nbImagesH += 1
        # Sinon ce n'est pas un visage souriant
        else:
            nbImagesN += 1
    spikesTimes.append((a, nIm * t_pres_tot + c * t_col))

nbImages = nbImagesH + nbImagesN

###

nbN_I = %NBN_I

nbN_1 = %NBN_1
Vt_1 = %VT_1 * volt
Vr_1 = %VR_1 * volt
tau_1 = %TAU_1 * base_period
refractory_1 = %CREF_1 * %RREF_1
inhibit_refractory_1 = %INH_REF_1 * base_period

neuron_eqs_1 = Equations ("""
    dv/dt = ( - v - inh ) / tau_1 : volt
    dinh/dt = - inh / inhibit_refractory_1 : volt
""")

nbN_2 = %NBN_2
Vt_2 = %VT_2 * volt
Vr_2 = %VR_2 * volt
tau_2 =%TAU_2 * base_period
refractory_2 = %CREF_2 * %RREF_2
inhibit_refractory_2 = %INH_REF_2 * base_period

neuron_eqs_2 = Equations ("""
    dv/dt = ( - v - inh ) / tau_2 : volt
    dinh/dt = - inh / inhibit_refractory_2 : volt
""")

nbN_3 = %NBN_3
Vt_3 = %VT_3 * volt
Vr_3 = %VR_3 * volt
tau_3 = %TAU_3 * base_period
refractory_3 = %CREF_3 * %RREF_3
inhibit_refractory_3 = %INH_REF_3 * base_period

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

c1_c2 = Synapses(couche1, couche2, model = 'w:1', pre = 'v+=w')
c1_c2.load_connectivity('./%CO_1_2')
wn = []
with open('%PDS_1_2', 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()
for i in xrange(0, len(c1_c2)):
    c1_c2.w[i] = wn[i]

c2_c3 = Synapses(couche2, couche3, model = 'w:1', pre = 'v+=w')
c2_c3.load_connectivity('./%CO_2_3')
wn = []
with open('%PDS_2_3', 'rb') as fichier:
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

##############
# SIMULATION #
##############

print "Init:"
print "Nb visages souriants :", nbImagesH
print "Nb visages non souriants :", nbImagesN

for n in xrange(0, nbImages):
    h, fn = tabHN[n]

    old_cptN0 = mc3[0]
    old_cptN1 = mc3[1]

    run(t_pres_tot)

    print ""

    if h:
        print "Image", n, "(happy):", fn
    else:
        print "Image", n, "(neutral):", fn
        
    print "Neurone 0:", mc3[0] - old_cptN0
    print "Neurone 1:", mc3[1] - old_cptN1

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

# figure('Potentiels')
# for i in xrange(0, len(couche3)):
#     plot(mv3.times, mv3[i])
# savefig("testST_" + str(int(time())) + "_V.png")
