#!/usr/bin/python2
# coding:utf-8

################
#  PARAMETRES  #
################
from optparse import OptionParser
import os
import sys

parser = OptionParser()

parser.add_option("-v", "--verbose", action="store_true",
                  help="Write output informations (not only errors).",
                  default=False)

parser.add_option("-g", "--graph", action="store_true",
                  help="Print graph", 
                  default=False)

parser.add_option("-n", "--number", 
                  help="Specify number of each case (integer, def=100)", 
                  default=100)

parser.add_option("-m", "--mode", 
                  help="Specify mode: learning (def) | testing", 
                  default="learning")

(options, args) = parser.parse_args()

try:
    options.number = int(options.number)
except :
    parser.print_help()
    exit(101)

if (options.mode != "learning") and (options.mode != "testing"):
    parser.print_help()
    exit(102)

#############
#  IMPORTS  #
#############
from brian import *
from brian.library.IF import *
from time import time

import pickle

from line2tab import *

###############
#  VARIABLES  #
###############
pres_time = 500 * ms
repos_time = 2 * pres_time
# repos_time = 0*ms

nb_classes = 6

N_input = 5
N_hl_sg = 6
N_hl = nb_classes * N_hl_sg
N_output = nb_classes

# Neurones
taum = 10 * ms
vt = -54 * mV
vr = -60 * mV
El = -74 * mV

neuron_eqs = leaky_IF(tau = taum, El = El)

# STDP
taupre = 20 * ms
taupost = taupre
gmax = 15 * mV
gmin = -gmax
dApre = .01
dApost = -dApre * taupre / taupost * 1.05
dApost *= gmax
dApre *= gmax

inhib_weight = -60 * mV
learn_weight =  20 * mV

# Data
freqRepos = []
for i in xrange(0,N_input):
    freqRepos.append(2*Hz)

freqReposTeach = []
for i in xrange(0,N_output):
    freqReposTeach.append(0*Hz)

data = lines2tab(options.number, N_input)

(n,rates) = data[0]

#########################
#  GROUPES DE NEURONES  #
#########################
input = PoissonGroup(N_input, rates)

hidden_layer = NeuronGroup(N = N_hl,
                           model = neuron_eqs,
                           threshold = vt,
                           reset = vr)

hl_subgr = []
for i in xrange(0,nb_classes):
    hl_subgr.append(hidden_layer.subgroup(N_hl_sg))

output = NeuronGroup(N = N_output,
                     model = neuron_eqs,
                     threshold = vt,
                     reset = vr)

if options.mode == "learning":
    ratesTeach = freqReposTeach
    ratesTeach[n] = 50*Hz
    teacher = PoissonGroup(N_output,ratesTeach)

##############
#  SYNAPSES  #
##############
if options.mode == "learning":
    # Synapses entre les deux premières couches
    in_hl = Synapses(input, hidden_layer,
                     model='''w:1
                     dApre/dt=-Apre/taupre : 1 (event-driven)
                     dApost/dt=-Apost/taupost : 1 (event-driven)''',
                     pre='''vm+=w
                     Apre+=dApre
                     w=clip(w+Apost,gmin,gmax)''',
                     post='''
                     Apost+=dApost
                     w=clip(w+Apre,gmin,gmax)''')
    in_hl[:,:] = True
    in_hl.w = 'rand()*gmax'

    # Synapses entre les deux dernières couches
    hl_out = Synapses(hidden_layer, output,
                     model='''w:1
                     dApre/dt=-Apre/taupre : 1 (event-driven)
                     dApost/dt=-Apost/taupost : 1 (event-driven)''',
                     pre='''vm+=w
                     Apre+=dApre
                     w=clip(w+Apost,gmin,gmax)''',
                     post='''
                     Apost+=dApost
                     w=clip(w+Apre,gmin,gmax)''')
    hl_out[:,:] = True
    hl_out.w = 'rand()*gmax'

    # Synapses de supervision
    t_out = Connection(teacher, output, state = 'vm')
    t_out.connect_one_to_one(teacher, output, weight = learn_weight)
    
    # Inhibition latérale
    hl_inh = Connection(hidden_layer, hidden_layer, state = 'vm')
    for i in range(N_hl):
        for j in range(N_hl):
            if i == j:
                hl_inh[i,j] = 0
            else:
                hl_inh[i,j] = inhib_weight

    out_inh = Connection(output, output, state = 'vm')
    for i in range(N_output):
        for j in range(N_output):
            if i == j:
                out_inh[i,j] = 0
            else:
                out_inh[i,j] = inhib_weight

# options.mode == "testing"
else:
    # Synapses entre les deux premières couches
    in_hl = Synapses(input, hidden_layer, model='w:1', pre='vm+=w')
    in_hl.load_connectivity('in_hl.spc')
    with open('in_hl.spw', 'rb') as fichier:
        depick = pickle.Unpickler(fichier)
        wn = depick.load()
    for i in xrange(0, len(in_hl)):
        in_hl.w[i] = wn[i]

    # Synapses entre les deux dernières couches
    hl_out = Synapses(hidden_layer, output, model='w:1', pre='vm+=w')
    hl_out.load_connectivity('hl_out.spc')
    with open('hl_out.spw', 'rb') as fichier:
        depick = pickle.Unpickler(fichier)
        wn = depick.load()
    for i in xrange(0, len(hl_out)):
        hl_out.w[i] = wn[i]
    
###############
#  MONITEURS  #
###############
if options.graph:
    hl_vm = StateMonitor(hidden_layer, 'vm', record = True)
    in_hl_w  = StateMonitor(in_hl, 'w', record = True)
    out_vm = StateMonitor(output, 'vm', record = True)
    hl_out_w  = StateMonitor(hl_out, 'w', record = True)

cpt = SpikeCounter(output)

################
#  SIMULATION  #
################
if options.mode == "learning":
    for i in xrange(0,options.number):
        (n,rates) = data[i]
        ratesTeach = []
        for j in xrange(0, N_output):
            if j == n:
                ratesTeach.append(50*Hz)
            else:
                ratesTeach.append(2*Hz)
        
        input.rate = rates
        teacher.rate = ratesTeach

        if options.verbose:
            print "Cas :", i
            print "n =", n
            print "rates =", rates
            print "teach =", ratesTeach
            print ""

        run(pres_time)

        # Temps de pause entre deux présentations
        input.rate = freqRepos
        teacher.rate = freqReposTeach

        run(repos_time)

    # Sauvegarde apprentissage
    in_hl.save_connectivity('./in_hl.spc')
    wn = []
    for wi in in_hl.w:
        wn.append(wi)
    with open('in_hl.spw', 'wb') as fichier:
        pick = pickle.Pickler(fichier)
        pick.dump(wn)
        
    hl_out.save_connectivity('./hl_out.spc')
    wn = []
    for wi in hl_out.w:
        wn.append(wi)
    with open('hl_out.spw', 'wb') as fichier:
        pick = pickle.Pickler(fichier)
        pick.dump(wn)

# options.mode == "testing"
else:
    nbCas = 0
    nbCasOK = 0
    nbCasKO = 0
    for i in xrange(0, options.number):
        nbCas += 1
        old_cpt = []
        for j in xrange(0, N_output):
            old_cpt.append(cpt[j])
        
        (n,rates) = data[i]

        input.rate = rates

        if options.verbose:
            print "Cas :", i
            print "n =", n
            print "rates =", rates
            print ""

        run(pres_time)

        cpt_f = []
        for j in xrange(0, N_output):
            cpt_f.append(cpt[j] - old_cpt[j])
        
        maxi = -1
        i_maxi = -1
        for j in xrange(0, N_output):
            if cpt_f[j] > maxi:
                maxi = cpt_f[j]
                i_maxi = j
        
        if options.verbose:
            for j in xrange(0, N_output):
                print "cpt_f[{}] = {}".format(j, cpt_f[j])
            print "ind max =", i_maxi
            print ""

        if i_maxi == n:
            nbCasOK += 1
        else:
            nbCasKO += 1

        # Temps de pause entre deux présentations
        input.rate = freqRepos
        run(repos_time)
    
    print "Nombre de cas =", nbCas
    print "OK =", nbCasOK
    print "KO =", nbCasKO
