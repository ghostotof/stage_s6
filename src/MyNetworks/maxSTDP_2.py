#!/usr/bin/python2
# coding:utf-8
from brian import *
from time import time

############
# PARAMETERS
############

# simulation
t_sim   = 2000
t_app   = int(t_sim / 2)
t_test  = t_sim - t_app
t_uni   =   66
nb_tot  = 30
nb_app  = int(nb_tot / 2)
nb_test = nb_tot - nb_app

# input
N_in = 6
spiketimes = []

spikeTeach = []

print "t_sim   =", t_sim
print "t_uni   =", t_uni
print "nb_tot  =", nb_tot
print "nb_app  =", nb_app
print "nb_test =", nb_test

## apprentissage a plus grand
for i in xrange(0, nb_app):
    spiketimes.append((0, (i * t_uni) * ms))
    spiketimes.append((1, (i * t_uni) * ms))
    # spiketimes.append((2, i * t_uni * ms))
    if rand() < 0.5:
        spiketimes.append((3, (i * t_uni) * ms))
    else:
        spiketimes.append((5, (i * t_uni) * ms))
    # spiketimes.append((4, i * t_uni * ms))
    spikeTeach.append((0, (i * t_uni) * ms + 1 * ms))

## test nimp
for i in xrange(nb_app, nb_tot):
    if rand() < 0.5: # a n'est pas le plus grand
        if rand() < 0.5: # c est le plus grand
            spiketimes.append((0, (i * t_uni) * ms))
            spiketimes.append((4, (i * t_uni) * ms))
            spiketimes.append((5, (i * t_uni) * ms))
        else: # b est le plus grand
            spiketimes.append((1, (i * t_uni) * ms))
            spiketimes.append((2, (i * t_uni) * ms))
            spiketimes.append((3, (i * t_uni) * ms))
    else: # a est le plus grand
        spiketimes.append((0, (i * t_uni) * ms))
        spiketimes.append((1, (i * t_uni) * ms))
        if rand() < 0.5:
            spiketimes.append((3, (i * t_uni) * ms))
        else:
            spiketimes.append((5, (i * t_uni) * ms))

# first layer
N_c1 = 3

taum     =  10 * ms
taue     =   5 * ms
Ee       =   0 * mV
Vt       = -54 * mV
Vr       = -60 * mV
El       = -74 * mV

# eqs_c1 = Equations("""
# dv/dt  = (ge*(Ee-Vr)+El-v)/taum : volt
# dge/dt = -ge/taue : 1
# """)
eqs_c1 = Equations("""
dv/dt  = (ge-(v-El))/taum : volt
dge/dt = -ge/taue : volt
""")

# stdp
tau_pre  = 20 * ms
tau_post = tau_pre

gmax = 0.01
dA_pre  = 0.01
dA_post = -dA_pre * tau_pre / tau_post * 1.05
dA_post *= gmax
dA_pre  *= gmax

eqs_stdp = """
w : volt
A_pre : 1
A_post : 1
"""

op_stdp_pre = """
ge += w
A_pre  = A_pre * exp((lastupdate-t)/tau_pre) + dA_pre
A_post = A_post * exp((lastupdate-t)/tau_post)
w = clip(w + A_post, 0, gmax)
"""

op_stdp_post = """
A_pre = A_pre * exp((lastupdate-t)/tau_pre)
A_post = A_post * exp((lastupdate-t)/tau_post) + dA_post
w = clip(w + A_pre, 0, gmax)
"""

###############
# NEURON GROUPS
###############

input = SpikeGeneratorGroup(N_in, spiketimes)

c1 = NeuronGroup(N = N_c1, model = eqs_c1, threshold = Vt, reset = Vr)
c1.v = Vr

teacher = SpikeGeneratorGroup(3, spikeTeach)

##########
# SYNAPSES
##########

S = Synapses(input, c1, model = eqs_stdp, pre = op_stdp_pre, post = op_stdp_post)
S[:,:] = True
S.w = 'rand() * gmax'

T = Connection(teacher, c1, 'ge')
T[0,0] = Vt + 1 * mV

############
# MONITORING
############

rate = PopulationRateMonitor(c1)
M = StateMonitor(S, 'w', record = True)
Mv = StateMonitor(c1, 'v', record = True)
cpt_in = SpikeCounter(input)
cpt_c1 = SpikeCounter(c1)

############
# SIMULATION
############

start_time = time()
run(t_app * ms, report = 'text')
print "Learning time:", time() - start_time

print "# spikes from input 0 =", cpt_in[0]
print "# spikes from input 1 =", cpt_in[1]
print "# spikes from input 2 =", cpt_in[2]
print "# spikes from input 3 =", cpt_in[3]
print "# spikes from input 4 =", cpt_in[4]
print "# spikes from input 5 =", cpt_in[5]
print ""
print "# spikes from c1 0 =", cpt_c1[0]
print "# spikes from c1 1 =", cpt_c1[1]
print "# spikes from c1 2 =", cpt_c1[2]

S.pre = 'ge += w'

start_time = time()
run(t_test * ms, report = 'text')
print "Testing time:", time() - start_time

print "# spikes from input 0 =", cpt_in[0]
print "# spikes from input 1 =", cpt_in[1]
print "# spikes from input 2 =", cpt_in[2]
print "# spikes from input 3 =", cpt_in[3]
print "# spikes from input 4 =", cpt_in[4]
print "# spikes from input 5 =", cpt_in[5]
print ""
print "# spikes from c1 0 =", cpt_c1[0]
print "# spikes from c1 1 =", cpt_c1[1]
print "# spikes from c1 2 =", cpt_c1[2]

figure()
subplot(311)
# plot(rate.times / second, rate.smooth_rate(100 * ms))
plot(Mv.times, Mv[0])
plot(Mv.times, Mv[1])
plot(Mv.times, Mv[2])
legend(('0','1','2'), 'upper right')
subplot(312)
plot(S.w[:] / gmax, '.')
subplot(313)
hist(S.w[:] / gmax, 20)
figure()
# plot(M.times, M[0] / gmax, 'b')
# plot(M.times, M[1] / gmax, 'r')
# plot(M.times, M[2] / gmax, 'g')
# plot(M.times, M[3] / gmax, 'b')
# plot(M.times, M[4] / gmax, 'r')
# plot(M.times, M[5] / gmax, 'g')
# plot(M.times, M[6] / gmax, 'b')
# plot(M.times, M[7] / gmax, 'r')
# plot(M.times, M[8] / gmax, 'g')
# plot(M.times, M[9] / gmax, 'b')
# plot(M.times, M[10] / gmax, 'r')
# plot(M.times, M[11] / gmax, 'g')
# plot(M.times, M[12] / gmax, 'b')
# plot(M.times, M[13] / gmax, 'r')
# plot(M.times, M[14] / gmax, 'g')
# plot(M.times, M[15] / gmax, 'b')
# plot(M.times, M[16] / gmax, 'r')
# plot(M.times, M[17] / gmax, 'g')
plot(M.times, M[0] / gmax, 'b')
plot(M.times, M[1] / gmax, 'b')
plot(M.times, M[2] / gmax, 'b')
plot(M.times, M[3] / gmax, 'b')
plot(M.times, M[4] / gmax, 'b')
plot(M.times, M[5] / gmax, 'b')
plot(M.times, M[6] / gmax, 'r')
plot(M.times, M[7] / gmax, 'r')
plot(M.times, M[8] / gmax, 'r')
plot(M.times, M[9] / gmax, 'r')
plot(M.times, M[10] / gmax, 'r')
plot(M.times, M[11] / gmax, 'r')
plot(M.times, M[12] / gmax, 'g')
plot(M.times, M[13] / gmax, 'g')
plot(M.times, M[14] / gmax, 'g')
plot(M.times, M[15] / gmax, 'g')
plot(M.times, M[16] / gmax, 'g')
plot(M.times, M[17] / gmax, 'g')
show()
