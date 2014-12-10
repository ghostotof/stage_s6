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

min_period = %MIN_PER * msecond
base_period = %BAS_PER * min_period

t_pres = %T_PRES * base_period
t_pres_tot = %T_TOT * t_pres

min_weight = %MIN_W * volt
max_weight = %MAX_W * volt
inc_weight = %INC_W * max_weight
dec_weight = %DEC_W * max_weight
# init_weight = ( max_weight - min_weight ) / 2.0
init_weight = %INI_W * volt
# std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
std_init_weight = %STD_INI_W * volt
inhib_weight = %INH_W * volt

###

tab = []
with open('spikesTimesL.spt','rb') as file:
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
        else:
            nbImagesN += 1
    spikesTimes.append((a, nIm * t_pres_tot + c * t_col))

nbImages = nbImagesH + nbImagesN

###
# Init (HappyBrian):
# 
# Vt_1 = 
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
tau_2 = %TAU_2 * t_pres
refractory_2 = %CREF_2 * %RREF_2
inhibit_refractory_2 = %INH_REF_2 * base_period

neuron_eqs_2 = Equations ("""
    dv/dt = ( - v - inh ) / tau_2 : volt
    dinh/dt = - inh / inhibit_refractory_2 : volt
""")

nbN_3 = %NBN_3
Vt_3 = %VT_3 * volt
Vr_3 = %VR_3 * volt
tau_3 = %TAU_3 * t_pres
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

###

stdp_ltp = %LTP * base_period

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

    wi = []
    for wn in c1_c2.w:
        wi.append(wn)

    with open(nom + '_w_c1_c2_' + str('%04d' % n) + '.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)

    wi = []
    for wn in c2_c3.w:
        wi.append(wn)

    with open(nom + '_w_c2_c3_' + str('%04d' % n) + '.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)
    
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

c1_c2.save_connectivity('./%CO_1_2')
c2_c3.save_connectivity('./%CO_2_3')

wi = []
for wn in c1_c2.w:
    wi.append(wn)

with open('%PDS_1_2', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)

wi = []
for wn in c2_c3.w:
    wi.append(wn)

with open('%PDS_2_3', 'wb') as fichier:
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
