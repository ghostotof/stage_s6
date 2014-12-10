#!/usr/bin/python2
# coding:utf-8

#############
#  IMPORTS  #
#############
from brian import *
from time import time

import pickle
import sys

from genSpikesTimes import *

###############
#  FONCTIONS  #
###############
def usage():
    """
    Affiche comment utiliser le programme et termine avec une erreur
    """
    print "\nUsage:"
    print "\t./max3int_bio.py [graph] [mode] [tri] [nb] [learningMode]"
    print "\t\t[graph] : trace | notrace (affiche les graphiques ou non)"
    print "\t\t[mode] : s_learn | us_learn | test"
    print "\t\t[tri] : mixed | sorted"
    print "\t\t[nb] : nombre de cas où chaque entier est le maximum"
    print "\t\t[supervisedMode] : exci | inhi (seulement en cas d'apprentissage supervisé: mode=s_learn)"
    
    sys.exit(10)
        
################
#  PARAMETRES  #
################
try:
    nom = sys.argv[0]
    graph = sys.argv[1]
    mode = sys.argv[2]
    tri = sys.argv[3]
    nb = int(sys.argv[4])
    
    assert ((graph == "trace") or (graph == "notrace"))
    assert ((mode == "us_learn") or (mode == "s_learn") or (mode == "test"))
    assert ((tri == "mixed") or (tri == "sorted"))

    if mode == "s_learn":
        smode = sys.argv[5]
        assert ((smode == "exci") or (smode == "inhi"))
except:
    usage()

###############
#  VARIABLES  #
###############
pres_time = 20 * ms

min_period = 1 * ms
base_period = 5 * min_period

number_neurons_couche = 3

Vt = -54 * mV
Vr = -60 * mV
Ee =   0 * mV
El = -74 * mV
taum = 3 * ms
taue = 1.5 * ms

neuron_eqs = Equations ("""
dv/dt  = (ge*(Ee-Vr)+El-v)/taum : volt   # the synaptic current is linearized
dge/dt = -ge/taue : 1
""")

tau_pre = 6 * ms
tau_post = tau_pre
gmax = .01
dA_pre = .01
dA_post = -dA_pre * tau_pre / tau_post * 1.05
dA_post *= gmax
dA_pre *= gmax

eqs_stdp = """
w : 1
A_pre : 1
A_post : 1
"""

###

if tri == "mixed":
    temp = genSpikesTimesMixed(nb, pres_time)
else:
    temp = genSpikesTimesSorted(nb, pres_time)

t_spikes = []
for l in temp:
    maxi, adr, tim = l
    t_spikes.append((adr, tim))

if mode == "s_learn":
    if smode == "inhi":
        t_teach  = genTeachTimesInhib(temp)
    else:
        t_teach  = genTeachTimesExci(temp)

#########################
#  GROUPES DE NEURONES  #
#########################
input = SpikeGeneratorGroup(6, t_spikes)

couche = NeuronGroup(N = number_neurons_couche,
                           model = neuron_eqs,
                           threshold = Vt,
                           reset = Vr)

##############
#  SYNAPSES  #
##############
if ((mode == "s_learn") or (mode == "us_learn")):
    c_c1 = Synapses(input, couche, eqs_stdp,
                    pre="""
                    ge+=w
                    A_pre=A_pre*exp((lastupdate-t)/tau_pre)+dA_pre
                    A_post=A_post*exp((lastupdate-t)/tau_post)
                    w=clip(w+A_post,0,gmax)
                    """,
                    post="""
                    A_pre=A_pre*exp((lastupdate-t)/tau_pre)
                    A_post=A_post*exp((lastupdate-t)/tau_post)+dA_post
                    w=clip(w+A_pre,0,gmax)
                    """)
    c_c1[:,:] = True
    c_c1.w = 'rand()*gmax'
    
    # Inhibition latérale
    # inhib_couche = Connection(couche, couche, state = 'ge', weight = 0 * volt)

    # inhib_couche[0,1] = inhib_weight
    # inhib_couche[0,2] = inhib_weight
    # inhib_couche[1,0] = inhib_weight
    # inhib_couche[1,2] = inhib_weight
    # inhib_couche[2,0] = inhib_weight
    # inhib_couche[2,1] = inhib_weight

    if mode == "s_learn":
        # Teacher    
        teacher = SpikeGeneratorGroup(3, t_teach)

        teach_c1 = Connection(teacher, couche, state = 'v')
        if smode == "inhi":
            learn_weight = -15 * volt
        else:
            learn_weight = 30 * mV
        teach_c1[0,0] = learn_weight
        teach_c1[1,1] = learn_weight
        teach_c1[2,2] = learn_weight
    
# mode == "test"
else:
    c_c1 = Synapses(input, couche, model = 'w:1', pre = 'ge+=w')

    c_c1.load_connectivity('c_c1_conn.spc')
    with open('c_c1_wei.spw', 'rb') as fichier:
        mon_depick = pickle.Unpickler(fichier)
        wn = mon_depick.load()
    for i in xrange(0, len(c_c1)):
        c_c1.w[i] = wn[i]

###############
#  MONITEURS  #
###############
if graph == "trace":
    moni = StateMonitor(couche, 'v', record = True)
    m2   = StateMonitor(c_c1, 'w', record = True)

cpt = SpikeCounter(couche)

# cptInh = SpikeCounter(teacher)

################
#  SIMULATION  #
################
if ((mode == "s_learn") or (mode == "us_learn")):
    run(((3 * nb) + 1) * pres_time, report='text')
    
    # Sauvegarde apprentissage
    c_c1.save_connectivity('./c_c1_conn.spc')

    wi = []
    for wn in c_c1.w:
        wi.append(wn)

    with open('c_c1_wei.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)
        
    # Affichage 
    print "nb spikes =", cpt.nspikes
    print "nb spikes 'a' =", cpt[0]
    print "nb spikes 'b' =", cpt[1]
    print "nb spikes 'c' =", cpt[2]
    
    if graph == "trace":
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
# mode == "test"
else:
    run(pres_time)
    for i in xrange(0, 3 * nb):
        old_cpt0 = cpt[0]
        old_cpt1 = cpt[1]
        old_cpt2 = cpt[2]
        run(pres_time)
        maxi, adr, tim = temp[i*3]
        print "Maximum attendu : {}".format(maxi)
        print "Résultat obtenu:"
        print "\tNeurone 'a': {}".format(cpt[0]-old_cpt0)
        print "\tNeurone 'b': {}".format(cpt[1]-old_cpt1)
        print "\tNeurone 'c': {}".format(cpt[2]-old_cpt2)
        print ""
        
#####################
#  AFFICHAGE GRAPH  #
#####################
if graph == "trace":
    figure()
    subplot(311)
    plot(moni.times, moni[0],'b')
    subplot(312)
    plot(moni.times, moni[1],'r')
    subplot(313)
    plot(moni.times, moni[2],'g')
    
    show()
