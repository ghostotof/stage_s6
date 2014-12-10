#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle

##############
# PARAMETERS #
##############

nb_app = 100
nb_tot = nb_app * 3 + 1

nb_a  = nb_app * 1 + 1
nb_b  = nb_app * 2 + 1
nb_c  = nb_app * 3 + 1
spiketimes = []
teachTimes = []

pres_time = 20 * ms

# a plus grand
for i in xrange(1, nb_a):
    spiketimes.append((0, i * pres_time))
    spiketimes.append((1, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((3, i * pres_time))
    else:
        spiketimes.append((5, i * pres_time))
    teachTimes.append((1, i * pres_time - 1 * ms))
    teachTimes.append((2, i * pres_time - 1 * ms))

# b plus grand
for i in xrange(nb_a, nb_b):
    spiketimes.append((2, i * pres_time))
    spiketimes.append((3, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((1, i * pres_time))
    else:
        spiketimes.append((4, i * pres_time))
    teachTimes.append((0, i * pres_time - 1 * ms))
    teachTimes.append((2, i * pres_time - 1 * ms))

# c plus grand
for i in xrange(nb_b, nb_c):
    spiketimes.append((4, i * pres_time))
    spiketimes.append((5, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((0, i * pres_time))
    else:
        spiketimes.append((2, i * pres_time))
    teachTimes.append((1, i * pres_time - 1 * ms))
    teachTimes.append((0, i * pres_time - 1 * ms))

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
inhib_weight = 1.0 * volt * 50.0

number_neurons_couche = 3

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

input = SpikeGeneratorGroup(6, spiketimes)

couche = NeuronGroup(N = number_neurons_couche,
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

c_c1 = Synapses(input, couche, eqs_stdp,
    pre="""tPre=t; v+=w""",
    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
            (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

c_c1[:,:] = True
c_c1.w = '8 * volt'

###########
# TEACHER #
###########

teacher = SpikeGeneratorGroup(3, teachTimes)

inh_c1 = Connection(teacher, couche, state = 'v')
inh_c1[0,0] = -15*volt
inh_c1[1,1] = -15*volt
inh_c1[2,2] = -15*volt

##############
# INHIBITION #
##############

inhib_couche = Connection(couche, couche, state = 'inh', weight = 0 * volt)
inhib_couche[0,1] = inhib_weight
inhib_couche[0,2] = inhib_weight
inhib_couche[1,0] = inhib_weight
inhib_couche[1,2] = inhib_weight
inhib_couche[2,0] = inhib_weight
inhib_couche[2,1] = inhib_weight

############
# MONITORS #
############

moni = StateMonitor(couche, 'v', record = True)
m2   = StateMonitor(c_c1, 'w', record = True)

cpt = SpikeCounter(couche)

cptInh = SpikeCounter(teacher)

##############
# SIMULATION #
##############

run(nb_tot * pres_time, report = 'text')

print "nb spikes =", cpt.nspikes
print "nb spikes 'a' =", cpt[0]
print "nb spikes 'b' =", cpt[1]
print "nb spikes 'c' =", cpt[2]
print ""
print "nb spikes inh =", cptInh.nspikes
print "nb spikes 'a' =", cptInh[0]
print "nb spikes 'b' =", cptInh[1]
print "nb spikes 'c' =", cptInh[2]

figure()
subplot(311)
plot(moni.times, moni[0],'b')
subplot(312)
plot(moni.times, moni[1],'r')
subplot(313)
plot(moni.times, moni[2],'g')
# savefig("max_STDP_teacher_abc_" + str(int(time())) + "_V.png")

figure()
subplot(311)
plot(m2.times, m2[0])
plot(m2.times, m2[3])
plot(m2.times, m2[6])
plot(m2.times, m2[9])
plot(m2.times, m2[12])
plot(m2.times, m2[15])
subplot(312)
plot(m2.times, m2[1])
plot(m2.times, m2[4])
plot(m2.times, m2[7])
plot(m2.times, m2[10])
plot(m2.times, m2[13])
plot(m2.times, m2[16])
subplot(313)
plot(m2.times, m2[2])
plot(m2.times, m2[5])
plot(m2.times, m2[8])
plot(m2.times, m2[11])
plot(m2.times, m2[14])
plot(m2.times, m2[17])
# savefig("max_STDP_teacher_abc_" + str(int(time())) + "_W.png")

show()

########
# SAVE #
########

c_c1.save_connectivity('./saveConnec')

wi = []
for wn in c_c1.w:
    wi.append(wn)

with open('myWeights', 'wb') as fichier:
    mon_pick = pickle.Pickler(fichier)
    mon_pick.dump(wi)
