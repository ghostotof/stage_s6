#!/usr/bin/python2
# coding:utf-8
from brian import *
from time import time
import pickle

############
# PARAMETERS
############

# simulation
t_stim = 500 * ms
t_pause = 1000 * ms
nb_stim = 20

F_ok = 50 * Hz
F_ko =  2 * Hz

# input
tab_in = []
tab_in.append(F_ok)
tab_in.append(F_ok)
tab_in.append(F_ko)
if rand() < 0.5:
    tab_in.append(F_ok)
    tab_in.append(F_ko)
    tab_in.append(F_ko)
else:
    tab_in.append(F_ko)
    tab_in.append(F_ko)
    tab_in.append(F_ok)

# c1
a = 0.02/ms
b = 0.2/ms
c = -65*mV
d = 8*mV/ms

eqs = Equations("""
dv/dt = (0.04/ms/mV)*v**2+(5/ms)*v+140*mV/ms-u+I/nF  : volt
du/dt = a*(b*v-u)                                    : volt/second
I                                                    : amp
""")
reset = """
v = c
u += d
"""
threshold = 30*mV

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
v += w
A_pre  = A_pre * exp((lastupdate-t)/tau_pre) + dA_pre
A_post = A_post * exp((lastupdate-t)/tau_post)
w = clip(w + A_post, 0, gmax)
"""

op_stdp_post = """
A_pre = A_pre * exp((lastupdate-t)/tau_pre)
A_post = A_post * exp((lastupdate-t)/tau_post) + dA_post
w = clip(w + A_pre, 0, gmax)
"""

##############
# NEURON GROUP
##############

input = PoissonGroup(6, tab_in)

c1 = NeuronGroup(N = 3, model = eqs, threshold = threshold, reset = reset)
c1.v = -80*mV
c1.u = 0

teach_c1 = PoissonGroup(3, [F_ok, F_ko, F_ko])

##########
# SYNAPSES
##########

S_i1 = Synapses(input, c1, model = eqs_stdp, pre = op_stdp_pre, post = op_stdp_post)
S_i1[:,:] = True
S_i1.w = 'rand() * gmax'

S_t1 = Synapses(teach_c1, c1, model = eqs_stdp, pre = op_stdp_pre, post = op_stdp_post)
S_t1[:,:] = 'i==j'
S_t1.w = 'rand() * gmax'

##########
# MONITORS
##########

Mv_c1 = StateMonitor(c1, 'v', record = True)
Mw_i1 = StateMonitor(S_i1, 'w', record = True)

############
# SIMULATION
############

for i in xrange(0, nb_stim):
    tab_in = []
    # a max
    tab_in.append(F_ok)
    tab_in.append(F_ok)
    tab_in.append(F_ko)
    if rand() < 0.5: # b > c
        tab_in.append(F_ok)
        tab_in.append(F_ko)
        tab_in.append(F_ko)
    else: # c > b
        tab_in.append(F_ko)
        tab_in.append(F_ko)
        tab_in.append(F_ok)
    
    input.rate = tab_in
    teach_c1.rate = [F_ok, 0 * Hz, 0 * Hz]

    start_time = time()
    run(t_stim)
    print "Learn num", i, " time :", time() - start_time

    tab_in = [F_ko, F_ko, F_ko, F_ko, F_ko, F_ko]
    
    input.rate = tab_in
    teach_c1.rate = [0 * Hz, 0 * Hz, 0 * Hz]

    start_time = time()
    run(t_pause)
    print "Pause num", i, " time :", time() - start_time

figure()
plot(Mv_c1.times, Mv_c1[0])
plot(Mv_c1.times, Mv_c1[1])
plot(Mv_c1.times, Mv_c1[2])
legend(('0', '1', '2'), 'upper right')

figure()
for i in xrange(0, 18):
    if i < 6:
        plot(Mw_i1.times, Mw_i1[i], 'b')
    elif i < 12:
        plot(Mw_i1.times, Mw_i1[i], 'r')
    else:
        plot(Mw_i1.times, Mw_i1[i], 'g')

show()
