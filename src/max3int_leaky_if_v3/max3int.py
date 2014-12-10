#!/usr/bin/python2
# coding:utf-8


# max3int_leaky_if_v3
#
# pres_time = 50 ms
# Potentiel des neurones : -74 -> -54 mV
# Modèle : leaky_IF(tau = 2/3 * 5 ms, El = -74 mV)
# Modèle STDP : w:1
#               dApre/dt=-Apre/taupre : 1
#               dApost/dt=-Apost/taupost : 1
# Comportement STDP : pre = vm+=w
#                           Apre+=dApre
#                           w=clip(w+Apost,gmin,gmax)
#                     post = Apost+=dApost
#                            w=clip(w+Apre,gmin,gmax)
# Sans inhibition latérale


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
parser.add_option("-n", "--number", help="Specify number of each case (integer and 200 as default)", default=200)
parser.add_option("-s", "--sort", help="Specify sorting cases management: sorted | mixed (default) | opti | ABC", default="mixed")
parser.add_option("-S", "--supervision", help="Specify supervision type: exci (default) | inhi", default="exci")
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
if (options.mode == "supervised") and (options.supervision != "exci") and (options.supervision != "inhi"):
    parser.print_help()
    exit(13)

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

if (options.sort != "mixed") and (options.sort != "sorted") and (options.sort != "opti") and (options.sort != "ABC") :
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

from genSpikesTimes import *

###############
#  VARIABLES  #
###############
pres_time = 50 * ms

min_period = 1 * ms
base_period = 5 * min_period

gmin = -15 * mV
gmax = 15 * mV

# inhib_weight = -25 * mV
# inhib_weight = -50 * mV
# inhib_weight = -75 * mV
inhib_weight = -100 * mV
learn_weight = 25 * mV
teach_time_diff = 1 * ms

number_neurons_couche = 3

Vt = -54 * mV
Vr = -60 * mV
El = -74 * mV
tau = base_period * (2.0/3.0)
refractory = 0.9 * pres_time
inhibit_refractory = 1.05 * base_period

neuron_eqs = leaky_IF(tau = tau, El = El)

taupre = 500 * ms
taupost = 500 * ms
dApre = 0.01
dApost = -dApre * taupre / taupost * 1.05
dApost *= gmax
dApre *= gmax

stdp_model = '''
w:1
dApre/dt=-Apre/taupre : 1
dApost/dt=-Apost/taupost : 1
'''

pre='''
vm+=w
Apre+=dApre
w=clip(w+Apost,gmin,gmax)
'''

post='''
Apost+=dApost
w=clip(w+Apre,gmin,gmax)
'''

###

# Génération des temps de déclenchement des influx nerveux
if options.sort == "sorted":
    temp = genSpikesTimesSorted(options.number, pres_time)
elif options.sort == "opti":
    temp = genSpikesTimesOpti(options.number, pres_time)
elif options.sort == "ABC":
    temp = genSpikesTimesABC(options.number, pres_time)
else:
    temp = genSpikesTimesMixed(options.number, pres_time)

t_spikes = []
for l in temp:
    maxi, adr, tim = l
    t_spikes.append((adr, tim))

if options.mode == "supervised":
    if options.supervision == "inhi":
        t_teach  = genTeachTimesInhib(temp, teach_time_diff)
    else:
        t_teach  = genTeachTimesExci(temp, teach_time_diff)

#########################
#  GROUPES DE NEURONES  #
#########################
input = SpikeGeneratorGroup(6, t_spikes)

couche = NeuronGroup(N = number_neurons_couche,
                           model = neuron_eqs,
                           threshold = Vt,
                           reset = Vr,
                           refractory = refractory)

##############
#  SYNAPSES  #
##############

# Si apprentissage
if options.mode != "test":
    c_c1 = Synapses(input, couche, stdp_model,
                    pre=pre,
                    post=post)

    c_c1[:,:] = True
    if options.randWeights:
        if options.verbose:
            print "Poids aléatoires positifs ou nuls"
        c_c1.w = '(rand() * 15) * mV'
    else:
        if options.verbose:
            print "Poids non aléatoires"
        c_c1.w = '0 * mV'
    
    # Inhibition latérale
    inhib_couche = Connection(couche, couche, state = 'vm', weight = 0 * volt)

    inhib_couche[0,1] = inhib_weight
    inhib_couche[0,2] = inhib_weight
    inhib_couche[1,0] = inhib_weight
    inhib_couche[1,2] = inhib_weight
    inhib_couche[2,0] = inhib_weight
    inhib_couche[2,1] = inhib_weight

    if options.mode == "supervised":
        # Teacher    
        teacher = SpikeGeneratorGroup(3, t_teach)

        teach_c1 = Connection(teacher, couche, state = 'vm')
        if options.supervision == "inhi":
            learn_weight = -learn_weight
        
        teach_c1[0,0] = learn_weight
        teach_c1[1,1] = learn_weight
        teach_c1[2,2] = learn_weight
    
# Sinon test de classification
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

# cptInh = SpikeCounter(teacher)

################
#  SIMULATION  #
################

# Si apprentissage
if options.mode != "test":    
    for i in xrange(0, (3 * options.number) + 1):
        if options.verbose:
            print "Case {}:".format(i)
            run(pres_time, report='text')
        else:
            run(pres_time)
        # Si on veut sauvegarder les poids synaptiques intermédiaires
        if options.saveWeights != None:
            nameTemp = folderPath + "/file" + ("%04d"%(i,)) + ".spw"
            wi = []
            for wn in c_c1.w:
                wi.append(wn)
            with open(nameTemp, 'wb') as fichier:
                mon_pick = pickle.Pickler(fichier)
                mon_pick.dump(wi)

    # Sauvegarde apprentissage final
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

# Si classification
else:
    nbCas = 0
    nbCasOK = 0
    nbCasKO = 0

    nbCasOKa = 0
    nbCasOKb = 0
    nbCasOKc = 0
    nbCasKOa = 0
    nbCasKOb = 0
    nbCasKOc = 0
    
    run(pres_time)
    for i in xrange(0, 3 * options.number):
        nbCas += 1
        old_cpt0 = cpt[0]
        old_cpt1 = cpt[1]
        old_cpt2 = cpt[2]

        if options.verbose:
            print "Case {}:".format(nbCas)
            run(pres_time)
        else:
            run(pres_time)
        
        cptA = cpt[0] - old_cpt0
        cptB = cpt[1] - old_cpt1
        cptC = cpt[2] - old_cpt2

        maxi, adr, tim = temp[i*3]

        # Si le bon maximum est identifié
        if (((maxi == 'a') and (cptA == 1) and (cptB == 0) and (cptC == 0)) or ((maxi == 'b') and (cptA == 0) and (cptB == 1) and (cptC == 0)) or ((maxi == 'c') and (cptA == 0) and (cptB == 0) and (cptC == 1))) :
            nbCasOK += 1
            if maxi == 'a':
                nbCasOKa += 1
            elif maxi == 'b':
                nbCasOKb += 1
            else:
                nbCasOKc += 1
        # Sinon mauvaise réponse
        else:
            nbCasKO += 1
            if maxi == 'a':
                nbCasKOa += 1
            elif maxi == 'b':
                nbCasKOb += 1
            else:
                nbCasKOc += 1
            if options.verbose:
                print ""
                print "Maximum attendu : {}".format(maxi)
                print "Résultat obtenu:"
                print "\tNeurone 'a': {}".format(cptA)
                print "\tNeurone 'b': {}".format(cptB)
                print "\tNeurone 'c': {}".format(cptC)
                print "Tensions:"
                print "\tNeurone 'a': {}".format(couche[0].vm)
                print "\tNeurone 'b': {}".format(couche[1].vm)
                print "\tNeurone 'c': {}".format(couche[2].vm)

    if options.verbose:
        print "\nNombre de cas total : {}\nNombre de cas OK : {}\nNombre de cas KO : {}".format(nbCas, nbCasOK, nbCasKO)
        print "\nDétails:\nCas OK:\n\ta = {}\n\tb = {}\n\tc = {}\nCas KO:\n\ta = {}\n\tb = {}\n\tc = {}".format(nbCasOKa, nbCasOKb, nbCasOKc, nbCasKOa, nbCasKOb, nbCasKOc)
        

#####################
#  AFFICHAGE GRAPH  #
#####################
if options.graph:
    thres = []
    for x in range(len(moni.times)):
        thres.append(Vt)
    figure()
    subplot(311)
    plot(moni.times, moni[0],'b')
    plot(moni.times,thres, 'r')
    subplot(312)
    plot(moni.times, moni[1],'r')
    plot(moni.times,thres, 'b')
    subplot(313)
    plot(moni.times, moni[2],'g')
    plot(moni.times,thres, 'r')
    
    show()

if (options.mode == "test"):
    res = (nbCasOK * 100) / nbCas
    exit(res)
