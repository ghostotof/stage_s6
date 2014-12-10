#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle

##############
# PARAMETERS #
##############

nb_ex = 250
nb_test = 500
nb_sui = 750
spiketimes = []
teachTimes = []

pres_time = 20 * ms

# a plus grand
for i in xrange(1, nb_ex):
    spiketimes.append((0, i * pres_time))
    spiketimes.append((1, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((3, i * pres_time))
    else:
        spiketimes.append((5, i * pres_time))
    teachTimes.append((1, i * pres_time - 1 * ms))
    teachTimes.append((2, i * pres_time - 1 * ms))

# b plus grand
for i in xrange(nb_ex, nb_test):
    spiketimes.append((2, i * pres_time))
    spiketimes.append((3, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((1, i * pres_time))
    else:
        spiketimes.append((4, i * pres_time))
    teachTimes.append((0, i * pres_time - 1 * ms))
    teachTimes.append((2, i * pres_time - 1 * ms))

# c plus grand
for i in xrange(nb_test, nb_sui):
    spiketimes.append((4, i * pres_time))
    spiketimes.append((5, i * pres_time))
    if rand() < 0.5:
        spiketimes.append((0, i * pres_time))
    else:
        spiketimes.append((2, i * pres_time))
    teachTimes.append((1, i * pres_time - 1 * ms))
    teachTimes.append((0, i * pres_time - 1 * ms))

# for i in xrange(nb_ex, nb_test):
    # if rand() < 0.5:
    #     spiketimes.append((0, i * pres_time))
    #     spiketimes.append((4, i * pres_time))
    # else:
    #     spiketimes.append((1, i * pres_time))
    #     spiketimes.append((2, i * pres_time))
    # if rand() < 0.5:
    #     spiketimes.append((3, i * pres_time))
    # else:
    #     spiketimes.append((5, i * pres_time))

min_period = 1 * msecond
#basePeriod = 255 * min_period
basePeriod = 5 * min_period

# min_weight = 0.0 * volt
min_weight = -10.0 * volt
max_weight = 1.0 * volt * 10.0
# inc_weight = max_weight * 0.1
# dec_weight = max_weight * 0.05
inc_weight = max_weight * 0.2
dec_weight = max_weight * 0.1
init_weight = ( max_weight - min_weight ) / 2.0
std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
inhib_weight = 1.0 * volt * 50.0

number_neurons_couche = 3
# Vt = 200.0 * volt
Vt = 15 * volt
Vr = 0.0 * volt
tau = basePeriod * (2.0/3.0)
refractory = 0.5 * basePeriod
inhibit_refractory = 1.05 * basePeriod

neuron_eqs = Equations ("""
    dv/dt = ( - v - inh ) / tau : volt
    dinh/dt = - inh / inhibit_refractory : volt
""")

stdp_ltp = basePeriod * 2

eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

#################
# NEURON GROUPS #
#################

input = SpikeGeneratorGroup(6, spiketimes)

couche = NeuronGroup(N = number_neurons_couche,
                           model = neuron_eqs,
                           threshold = Vt,
                           reset = Vr,
                           refractory = refractory)

############
# SYNAPSES #
############

c_c1 = Synapses(input, couche, eqs_stdp,
    pre="""tPre=t; v+=w""",
    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
            (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
c_c1[:,:] = True

# c_c1.w = 'clip(init_weight + std_init_weight*randn(), min_weight, max_weight)'
c_c1.w = '8 * volt'

###########
# TEACHER #
###########

teacher = SpikeGeneratorGroup(3, teachTimes)

inh_c1 = Connection(teacher, couche, state = 'v')
inh_c1[0,0] = -15*volt
inh_c1[1,1] = -15*volt
inh_c1[2,2] = -15*volt

# c_c1 = Connection(input, couche, 'v', weight = clip(init_weight + std_init_weight*randn(), min_weight, max_weight))

# gmax = 0.01

# eqs_stdp='''
# dA_pre/dt=-A_pre/tau_pre : 1
# dA_post/dt=-A_post/tau_post : 1
# '''

# stdp = STDP(c_c1, eqs = eqs_stdp, pre='A_pre+=dA_pre;w+=A_post',
#           post='A_post+=dA_post;w+=A_pre', wmax=gmax)

inhib_couche = Connection(couche, couche, state = 'inh', weight = 0 * volt)
# inhib_couche = Connection(couche, couche, state = 'v', weight = 0 * volt)
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

run(15000 * ms, report = 'text')
# run(400 * ms, report = 'text')

print "nb spikes =", cpt.nspikes
print "nb spikes 'a' =", cpt[0]
print "nb spikes 'b' =", cpt[1]
print "nb spikes 'c' =", cpt[2]
print ""
print "nb spikes inh =", cptInh.nspikes
print "nb spikes 'a' =", cptInh[0]
print "nb spikes 'b' =", cptInh[1]
print "nb spikes 'c' =", cptInh[2]

figure(20)
subplot(311)
plot(moni.times, moni[0],'b')
subplot(312)
plot(moni.times, moni[1],'r')
subplot(313)
plot(moni.times, moni[2],'g')
# legend(('0','1','2'), 'upper right')
#savefig("maxSTDP1_" + str(int(time())) + "_V.png")

# figure()
# subplot(311)
# plot(m2.times, m2[0])
# plot(m2.times, m2[3])
# plot(m2.times, m2[6])
# plot(m2.times, m2[9])
# plot(m2.times, m2[12])
# plot(m2.times, m2[15])
# subplot(312)
# plot(m2.times, m2[1])
# plot(m2.times, m2[4])
# plot(m2.times, m2[7])
# plot(m2.times, m2[10])
# plot(m2.times, m2[13])
# plot(m2.times, m2[16])
# subplot(313)
# plot(m2.times, m2[2])
# plot(m2.times, m2[5])
# plot(m2.times, m2[8])
# plot(m2.times, m2[11])
# plot(m2.times, m2[14])
# plot(m2.times, m2[17])
# savefig("maxSTDP1_" + str(int(time())) + "_W.png")

for i in xrange(0, 18):
    figure(i)
    plot(m2.times, m2[i])

show()

print "w 0 :", c_c1.w[0]
print "w 1 :", c_c1.w[1]
print "w 2 :", c_c1.w[2]
print "w 3 :", c_c1.w[3]
print "w 4 :", c_c1.w[4]
print "w 5 :", c_c1.w[5]
print "w 6 :", c_c1.w[6]

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
