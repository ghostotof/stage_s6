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
                  help="Print graph", default=False)
parser.add_option("-r", "--randWeights", action="store_true",
                  help="Init randomly synaptic weights during learning phase", default=False)
parser.add_option("-m", "--mode", help="Specify mode: supervised (default) | unsupervised | test", default="supervised")
parser.add_option("-n", "--number", help="Specify number of each case (integer and 100 as default)", default=100)
parser.add_option("-s", "--sort", help="Specify sorting cases management: sorted | mixed (default) | opti | ABC", default="mixed")
parser.add_option("-w", "--saveWeights", help="Specify folder where you want to save the weights")

(options, args) = parser.parse_args()

if (options.mode != "supervised") and (options.mode != "unsupervised") and (options.mode != "test"):
    parser.print_help()
    exit(11)
try:
    options.number = int(options.number)
except :
    parser.print_help()
    exit(12)

if (options.saveWeights != None) and (options.mode != "test"):
    try:
        folderPath = os.getcwd() + "/" + options.saveWeights
        if not os.path.exists(folderPath):
            os.mkdir(folderPath)
        assert os.path.isdir(folderPath)
    except:
        print "Erreur lors de la création du dossier de sauvegarde"
        parser.print_help()
        exit(14)

if (options.sort != "mixed") and (options.sort != "sorted") and (options.sort != "opti") and (options.sort != "ABC"):
    parser.print_help()
    exit(15)

nameProg = sys.argv[0]
if nameProg[0:2] == "./":
    nameProg = nameProg[2:]
if nameProg[-3:] == ".py":
    nameProg = nameProg[:-3]


#############
#  IMPORTS  #
#############
from brian import *
from brian.library.IF import *
from time import time

import pickle

from genMax import *

set_global_preferences(useweave_linear_diffeq = True,
                       useweave = True,
                       weavecompiler = 'gcc',
                       gcc_options = ["""-O2 -march=native -pipe -flto"""],
#                       -fmodulo-sched -fmodulo-sched-allow-regmoves
#                       -fgcse-sm -fgcse-las -fgcse-after-reload"""],
                       openmp = True,
                       usecodegen = True,
                       usecodegenweave = True,
                       usecodegenstateupdate = True,
                       usecodegenthreshold = True,
                       usecodegenreset = True,
                       usenewpropagate = True,
                       usecstdp = True)

###############
#  VARIABLES  #
###############
pres_time = 500 * ms
repo_time = 2 * pres_time
# repo_time = 0*ms

number_neurons_couche = 3

# Neurones
# taum = 3 * ms
# taum = 166 * ms
taum = 10 * ms
vt = -54 * mV
vr = -60 * mV
El = -74 * mV

neuron_eqs = leaky_IF(tau = taum, El = El)

# STDP
# taupre = 0.5 * ms
# taupre = 28 * ms
# taupre = 10 * ms
# taupre = 20 * ms
# taupost = taupre
# gmax = 15 * mV
# gmin = -gmax
# dApre = .01
# dApost = -dApre * taupre / taupost * 1.05
# dApost *= gmax
# dApre *= gmax

min_weight = -15.0 * mV
max_weight = 15 * mV
inc_weight = max_weight * 0.2
dec_weight = max_weight * 0.1
stdp_ltp = 100 * ms
eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

inhib_weight = -20 * mV
learn_weight =  20 * mV

###

if options.sort == "sorted":
    tabMax = genMaxSorted(options.number)
elif options.sort == "opti":
    tabMax = genMaxOpti(options.number)
elif options.sort == "ABC":
    tabMax = genMaxABC(options.number)
else:
    tabMax = genMaxMixed(options.number)

tabRepos = [2*Hz, 2*Hz, 2*Hz, 2*Hz, 2*Hz, 2*Hz]
tabReposTeach = [0*Hz, 0*Hz, 0*Hz]

#########################
#  GROUPES DE NEURONES  #
#########################
rates = genTabFreq(tabMax[0])

input = PoissonGroup(6, rates)

couche = NeuronGroup(N = number_neurons_couche,
                           model = neuron_eqs,
                           threshold = vt,
                           reset = vr)

##############
#  SYNAPSES  #
##############
if options.mode != "test":
    # c_c1 = Synapses(input, couche, 
    #                 model='''w:1
    #                 dApre/dt=-Apre/taupre : 1 (event-driven)
    #                 dApost/dt=-Apost/taupost : 1 (event-driven)''',
    #                 pre='''vm+=w
    #                 Apre+=dApre
    #                 w=clip(w+Apost,gmin,gmax)''',
    #                 post='''
    #                 Apost+=dApost
    #                 w=clip(w+Apre,gmin,gmax)''')
    c_c1 = Synapses(input, couche, eqs_stdp,
                    pre="""tPre=t; vm+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")

    c_c1[:,:] = True
    if options.randWeights:
        if options.verbose:
            print "Poids aléatoires positifs ou nuls"
        c_c1.w = 'rand()*max_weight'
    else:
        if options.verbose:
            print "Poids non aléatoires"
        c_c1.w = '0 * volt'
    
    # Inhibition latérale
    inhib_couche = Connection(couche, couche, state = 'vm', weight = 0*mV)

    inhib_couche[0,1] = inhib_weight
    inhib_couche[0,2] = inhib_weight
    inhib_couche[1,0] = inhib_weight
    inhib_couche[1,2] = inhib_weight
    inhib_couche[2,0] = inhib_weight
    inhib_couche[2,1] = inhib_weight

    if options.mode == "supervised":
        ratesTeach = genTabFreqTeach(tabMax[0])

        teacher = PoissonGroup(3, ratesTeach)

        teach_c1 = Connection(teacher, couche, state = 'vm')

        teach_c1[0,0] = learn_weight
        teach_c1[1,1] = learn_weight
        teach_c1[2,2] = learn_weight
    
# options.mode == "test"
else:
    c_c1 = Synapses(input, couche, model = 'w:1', pre = 'vm+=w')

    c_c1.load_connectivity('c_c1_conn.spc')
    with open('c_c1_wei.spw', 'rb') as fichier:
        mon_depick = pickle.Unpickler(fichier)
        wn = mon_depick.load()
    for i in xrange(0, len(c_c1)):
        c_c1.w[i] = wn[i]

###############
#  MONITEURS  #
###############
if options.graph:
    moni = StateMonitor(couche, 'vm', record = True)
    m2   = StateMonitor(c_c1, 'w', record = True)

cpt = SpikeCounter(couche)

################
#  SIMULATION  #
################
if options.mode != "test":
    for i in xrange(0, (3 * options.number)):
        
        input.rate = genTabFreq(tabMax[i])
        if options.mode == "supervised":
            teacher.rate = genTabFreqTeach(tabMax[i])

        if options.verbose:
            print "Case {}:".format(i)
            run(pres_time, report='text')
        else:
            run(pres_time)
            
        # Temps de pause entre deux présentations
        input.rate = tabRepos
        if options.mode == "supervised":
            teacher.rate = tabReposTeach
        run(repo_time)

        if options.saveWeights != None:
            nameTemp = folderPath + "/file" + ("%04d"%(i,)) + ".spw"
            wi = []
            for wn in c_c1.w:
                wi.append(wn)
            with open(nameTemp, 'wb') as fichier:
                mon_pick = pickle.Pickler(fichier)
                mon_pick.dump(wi)

    # Sauvegarde apprentissage
    c_c1.save_connectivity('./c_c1_conn.spc')

    wi = []
    for wn in c_c1.w:
        wi.append(wn)

    with open('c_c1_wei.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)
        
    # Affichage
    if options.verbose:
        print "nb spikes =", cpt.nspikes
        print "nb spikes 'a' =", cpt[0]
        print "nb spikes 'b' =", cpt[1]
        print "nb spikes 'c' =", cpt[2]
    
    if options.graph:
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
# options.mode == "test"
else:
    nbCas = 0
    nbCasOK = 0
    nbCasKO = 0
    run(pres_time)
    for i in xrange(0, 3 * options.number):
        nbCas += 1
        old_cpt0 = cpt[0]
        old_cpt1 = cpt[1]
        old_cpt2 = cpt[2]

        input.rate = genTabFreq(tabMax[i])

        if options.verbose:
            print "Case {}:".format(nbCas)
            run(pres_time)
        else:
            run(pres_time)
        
        cptA = cpt[0] - old_cpt0
        cptB = cpt[1] - old_cpt1
        cptC = cpt[2] - old_cpt2

        maxi = tabMax[i]

        if (((maxi == 'a') and (cptA > cptB) and (cptA > cptC)) or ((maxi == 'b') and (cptB > cptA) and (cptB > cptC)) or ((maxi == 'c') and (cptC > cptA) and (cptC > cptB))):
            nbCasOK += 1
        else:
            nbCasKO += 1
            if options.verbose:
                print ""
                print "Maximum attendu : {}".format(maxi)
                print "Résultat obtenu:"
                print "\tNeurone 'a': {}".format(cptA)
                print "\tNeurone 'b': {}".format(cptB)
                print "\tNeurone 'c': {}".format(cptC)

        # Temps de pause entre deux présentations
        input.rate = tabRepos
        run(repo_time)

    if options.verbose:
        print "\nNombre de cas total : {}\nNombre de cas OK : {}\nNombre de cas KO : {}".format(nbCas, nbCasOK, nbCasKO)

#####################
#  AFFICHAGE GRAPH  #
#####################
if options.graph:
    figure()
    subplot(311)
    plot(moni.times, moni[0],'b')
    subplot(312)
    plot(moni.times, moni[1],'r')
    subplot(313)
    plot(moni.times, moni[2],'g')
    
    show()

if (options.mode == "test"):
    res = (nbCasOK * 100) / nbCas
    exit(res)
