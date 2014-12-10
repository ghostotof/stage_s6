#!/usr/bin/python2
# coding:utf-8

from brian import *
from time import time

import pickle
import sys

###############
#             #
#  FONCTIONS  #
#             #
###############
def usage():
    """
    Affiche comment utiliser le programme et termine avec une erreur
    """
    print "\nUsage:"
    print "\t./recoFSimples.py [mode] [tri] [learningMode]"
    print "\t\t[mode] : learn | test"
    print "\t\t[tri] : sorted | mixed"
    print "\t\t[learningMode] : exci | inhi (seulement en cas d'apprentissage)"
    
    sys.exit(10)

def init_inh_lat(connec, size, wei):
    size_l = int(sqrt(size))
    for i in xrange(0,size_l):
        for j in xrange(0,size_l):
            ind = i * size_l + j
            v_h = (i-1) * size_l + j
            v_b = (i+1) * size_l + j
            v_d = i * size_l + j + 1
            v_g = i * size_l + j - 1
            v_hg = (i-1) * size_l + j - 1
            v_hd = (i-1) * size_l + j + 1
            v_bg = (i+1) * size_l + j - 1
            v_bd = (i+1) * size_l + j + 1
            
            # "Non bord"
            if ((i > 0) and (i < (size_l-1)) and (j > 0) and (j < (size_l-1))):
                connec[ind, v_h] = wei
                connec[ind, v_b] = wei
                connec[ind, v_d] = wei
                connec[ind, v_g] = wei
                connec[ind, v_hg] = wei
                connec[ind, v_hd] = wei
                connec[ind, v_bg] = wei
                connec[ind, v_bd] = wei
            # Première ligne
            elif i == 0:
                connec[ind, v_b] = wei
                if j != 0:
                    connec[ind, v_g] = wei
                    connec[ind, v_bg] = wei
                if j != (size_l-1):
                    connec[ind, v_d] = wei
                    connec[ind, v_bd] = wei
            # Dernière ligne
            elif i == (size_l-1):
                connec[ind, v_h] = wei
                if j != 0:
                    connec[ind, v_g] = wei
                    connec[ind, v_hg] = wei
                if j != (size_l-1):
                    connec[ind, v_d] = wei
                    connec[ind, v_hd] = wei
            else:
                connec[ind, v_h] = wei
                connec[ind, v_b] = wei
                if j != 0:
                    connec[ind, v_g] = wei
                    connec[ind, v_hg] = wei
                    connec[ind, v_bg] = wei
                if j != (size_l-1):
                    connec[ind, v_d] = wei
                    connec[ind, v_hd] = wei
                    connec[ind, v_bd] = wei

################
#              #
#  PARAMÈTRES  #
#              #
################
try:
    nom = sys.argv[0]
    mode = sys.argv[1]
    tri = sys.argv[2]
    
    assert((mode == "learn") or (mode == "test"))
    assert((tri == "sorted") or (tri == "mixed"))

    if mode = "learn":
        lmode = sys.argv[3]
        assert ((lmode == "exci") or (lmode == "inhi"))
except:
    usage()

###############
#             #
#  VARIABLES  #
#             #
###############

# Modèle

pres_time = 40 * ms

min_weight = -10.0 * volt
max_weight = 10.0 * volt
inc_weight = max_weight * 0.2
dec_weight = max_weight * 0.1
init_weight = ( max_weight - min_weight ) / 2.0
std_init_weight = min ( (max_weight - init_weight) , (init_weight - min_weight) )
inhib_weight = 50.0 * volt

# Couche d'entrée

nbN_in = 1600

# Couche 1

nbN_1 = 2100
nbN_1a = 1600 # 40*40
nbN_1b = 400  # 20*20
nbN_1c = 100  # 10*10
Vt_1 = 15.0 * volt
Vr_1 = 0.0 * volt
tau_1 = pres_time / 2.0
refractory_1 = tau_1 / 2.0
inh_refractory_1 = refractory_1 / 2.0

model_1 = Equations ("""
dv/dt   = ( - v - inh ) / tau_1 : volt
dinh/dt = - inh / inh_refractory_1 : volt
""")

# Couche 2

nbN_2 = 100 # Pour avoir le même ratio (~21) nbN_1/nbN_2 que Beyeler et al.
Vt_2 = 15.0 * volt
Vr_2 = 0.0 * volt
tau_2 = pres_time / 2.0
refractory_2 = tau_2 / 2.0
inh_refractory_2 = refractory_2 / 2.0

model_2 = Equations ("""
dv/dt   = ( - v - inh ) / tau_2 : volt
dinh/dt = - inh / inh_refractory_2 : volt
""")

# Couche 3

nbN_3 = 2
Vt_3 = 15.0 * volt
Vr_3 = 0.0 * volt
tau_3 = pres_time / 2.0
refractory_3 = tau_3 / 2.0
inh_refractory_3 = refractory_3 / 2.0

model_3 = Equations ("""
dv/dt   = ( - v - inh ) / tau_3 : volt
dinh/dt = - inh / inh_refractory_3 : volt
""")

# Synapses

stdp_ltp = ((tau_1 + tau_2 + tau_3) / 3.0) / 4.0

eqs_stdp = """
    w : volt
    tPre : second
    tPost : second
"""

###

if tri == "mixed":
    hon, t_spikes = genSpikesTimesMixed(pres_time)
else:
    hon, t_spikes = genSpikesTimesSorted(pres_time)

nbCas = len(hon)
nbCasH = 0
nbCasN = 0

for l in hon:
    if l == "happy":
        nbCasH += 1
    else:
        nbCasN += 1

if mode == "learn":
    if lmode == "exci":
        t_teach = genTeachTimesExci(hon, pres_time)
    else:
        t_teach = genTeachTimesInhi(hon, pres_time)

#########################
#                       #
#  GROUPES DE NEURONES  #
#                       #
#########################
input = SpikeGeneratorGroup(nbN_in, t_spikes)

couche1 = NeuronGroup(N = nbN_1
                      model = model_1,
                      threshold = Vt_1,
                      reset = Vr_1,
                      refractory = refractory_1)

couche1a = couche1.subgroup(nbN_1a)
couche1b = couche1.subgroup(nbN_1b)
couche1c = couche1.subgroup(nbN_1c)

couche2 = NeuronGroup(N = nbN_2,
                      model = model_2,
                      threshold = Vt_2
                      reset = Vr_2,
                      refractory = refractory_2)

couche3 = NeuronGroup(N = nbN_3,
                      model = model_3,
                      threshold = Vt_3,
                      reset = Vr_3,
                      refractory = refractory_3)

##############
#            #
#  SYNAPSES  #
#            #
##############
if mode == "learn":
    c_c1a = Synapses(input, couche1a, eqs_stdp,
                    pre="""tPre=t; v+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
    c_c1a[:;:] = 'i==j'
    c_c1a.w = 'rand()*10.0'
    
    c_c1b = Synapses(input, couche1b, eqs_stdp,
                    pre="""tPre=t; v+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
    for i in xrange(0, 20):
        for j in xrange(0, 20):
            indArr = i * 20 + j
            hg = 80 * i + 2 * j
            hd = 80 * i + 2 * j + 1
            bg = 80 * i + 2 * j + 40
            bd = 80 * i + 2 * j + 41
            c_c1b[hg;indArr] = True
            c_c1b[hd;indArr] = True
            c_c1b[bg;indArr] = True
            c_c1b[bd;indArr] = True
    c_c1b.w = 'rand()*10.0'

    c_c1c = Synapses(input, couche1c, eqs_stdp,
                    pre="""tPre=t; v+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
    for i in xrange(0,10):
        for j in xrange(0,10):
            indArr = i * 10 + j
            hhgg = 160 * i + 4 * j
            hhg  = 160 * i + 4 * j + 1
            hhd  = 160 * i + 4 * j + 2
            hhdd = 160 * i + 4 * j + 3
            hgg  = 160 * i + 4 * j + 40
            hg   = 160 * i + 4 * j + 41
            hd   = 160 * i + 4 * j + 42
            hdd  = 160 * i + 4 * j + 43
            bgg  = 160 * i + 4 * j + 80
            bg   = 160 * i + 4 * j + 81
            bd   = 160 * i + 4 * j + 82
            bdd  = 160 * i + 4 * j + 83
            bbgg = 160 * i + 4 * j + 120
            bbg  = 160 * i + 4 * j + 121
            bbd  = 160 * i + 4 * j + 122
            bbdd = 160 * i + 4 * j + 123
            c_c1c[hhgg;indArr] = True
            c_c1c[hhg;indArr] = True
            c_c1c[hhd;indArr] = True
            c_c1c[hhdd;indArr] = True
            c_c1c[hgg;indArr] = True
            c_c1c[hg;indArr] = True
            c_c1c[hd;indArr] = True
            c_c1c[hdd;indArr] = True
            c_c1c[bgg;indArr] = True
            c_c1c[bg;indArr] = True
            c_c1c[bd;indArr] = True
            c_c1c[bdd;indArr] = True
            c_c1c[bbgg;indArr] = True
            c_c1c[bbg;indArr] = True
            c_c1c[bbd;indArr] = True
            c_c1c[bbdd;indArr] = True
    c_c1c.w = 'rand()*10.0'

    c1_c2 = Synapses(couche1, couche2, eqs_stdp,
                    pre="""tPre=t; v+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
    c1_c2[:;:] = True
    c1_c2.w = 'rand()*10.0'

    c2_c3 = Synapses(couche2, couche3, eqs_stdp,
                    pre="""tPre=t; v+=w""",
                    post="""tPost=t; w=clip(w + (inc_weight + dec_weight)*(tPre <= tPost)*
                    (tPre + stdp_ltp >= tPost) - dec_weight, min_weight, max_weight)""")
    c2_c3[:;:] = True
    c2_c3.w = 'rand()*10.0'

    # Inhibition latérale
    inh_lat_c1a = Connection(couche1a, couche1a, state = 'inh', weight = 0 * volt)
    init_inh_lat(inh_lat_c1a, nbN_1a, inhib_weight)
    
    inh_lat_c1b = Connection(couche1b, couche1b, state = 'inh', weight = 0 * volt)
    init_inh_lat(inh_lat_c1b, nbN_1b, inhib_weight)
    
    inh_lat_c1c = Connection(couche1c, couche1c, state = 'inh', weight = 0 * volt)
    init_inh_lat(inh_lat_c1c, nbN_1c, inhib_weight)

    inh_lat_c2 = Connection(couche2, couche2, state = 'inh', weight = 0 * volt)
    init_inh_lat(inh_lat_c2, nbN_2, inhib_weight)

    inh_lat_c3 = Connection(couche3, couche3, state = 'inh', weight = 0 * volt)
    inh_lat_c3[0,1] = inhib_weight
    inh_lat_c3[1,0] = inhib_weight
    
    # Teacher
    coucheT = SpikeGeneratorGroup(nbN_3, t_teach)
    t_c3 = Connection(coucheT, couche3, state = 'v')
    if lmode == "exci":
        learn_weight = Vt_3 * 1.05
    else:
        learn_weight = - Vt_3 * 1.05
    t_c3[0,0] = learn_weight
    t_c3[1,1] = learn_weight
    
# mode == "test"
else:
    c_c1 = Synapses(input, couche1, model = 'w:1', pre = 'v+=w')

    c_c1.load_connectivity('c_c1_conn.spc')
    with open('c_c1_wei.spw', 'rb') as fichier:
        mon_depick = pickle.Unpickler(fichier)
        wn = mon_depick.load()
    for i in xrange(0, len(c_c1)):
        c_c1.w[i] = wn[i]

    c1_c2 = Synapses(couche1, couche2, model = 'w:1', pre = 'v+=w')
    
    c1_c2.load_connectivity('c1_c2_conn.spc')
    with open('c1_c2_wei.spw', 'rb') as fichier:
        mon_depick = pickle.Unpickler(fichier)
        wn = mon_depick.load()
    for i in xrange(0, len(c1_c2)):
        c1_c2.w[i] = wn[i]

    c2_c3 = Synapses(couche2, couche3, model = 'w:1', pre = 'v+=w')

    c2_c3.load_connectivity('c2_c3_conn.spc')
    with open('c2_c3_wei.spw', 'rb') as fichier:
        mon_depick = pickle.Unpickler(fichier)
        wn = mon_depick.load()
    for i in xrange(0, len(c2_c3)):
        c2_c3.w[i] = wn[i]

###############
#             #
#  MONITEURS  #
#             #
###############

cpt_c1a = SpikeCounter(couche1a)
cpt_c1b = SpikeCounter(couche1b)
cpt_c1c = SpikeCounter(couche1c)
cpt_c2 = SpikeCounter(couche2)
cpt_c3 = SpikeCounter(couche3)

################
#              #
#  SIMULATION  #
#              #
################
if mode == "learn":
    run((nbCas + 1) * pres_time, report='text')

    # Sauvegarde apprentissage
    c_c1.save_connectivity('./c_c1_conn.spc')
    wi = []
    for wn in c_c1.w:
        wi.append(wn)
    with open('c_c1_wei.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)
    
    c1_c2.save_connectivity('./c1_c2_conn.spc')
    wi = []
    for wn in c1_c2.w:
        wi.append(wn)
    with open('c1_c2_wei.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)

    c2_c3.save_connectivity('./c2_c3_conn.spc')
    wi = []
    for wn in c2_c3.w:
        wi.append(wn)
    with open('c2_c3_wei.spw', 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)
        
    # Affichage
    print "Nombre de cas = {}".format(nbCas)
    print "Nombre de cas 'happy' = {}".format(nbCasH)
    print "Nombre de cas 'neutral' = {}".format(nbCasN)
    print ""
    print "Nombre d'influx de la couche1a = {}".format(cpt_c1a.nspikes)
    print "Nombre d'influx de la couche1b = {}".format(cpt_c1b.nspikes)
    print "Nombre d'influx de la couche1c = {}".format(cpt_c1c.nspikes)
    print "Nombre d'influx de la couche2 = {}".format(cpt_c2.nspikes)
    print "Nombre d'influx de la couche3 (N0) = {}".format(cpt_c3[0])
    print "Nombre d'influx de la couche3 (N1) = {}".format(cpt_c3[1])
    
# mode == "test"
else:
    cptCas = 0
    nbCasOK = 0
    nbCasKO = 0
    run(pres_time)
    for i in xrange(0, nbCas):
        cptCas += 1
        old_cpt_c3_0 = cpt_c3[0]
        old_cpt_c3_1 = cpt_c3[1]

        run(pres_time)

        cpt_n0 = cpt_c3[0] - old_cpt_c3_0
        cpt_n1 = cpt_c3[1] - old_cpt_c3_1
        
        print "\nRésultat attendu : {}".format(hon[i])
        print "Nombre d'influx du neurone 0 = {}".format(cpt_n0)
        print "Nombre d'influx du neurone 1 = {}".format(cpt_n1)
