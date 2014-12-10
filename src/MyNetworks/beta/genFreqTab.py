#!/usr/bin/python2
# coding:utf-8

###############
# DESCRIPTION #
###############
# Génère un fichier contenant un tableau de n tableaux de fréquence
# Chaque sous-tableau est un tableau de fréquence correspondant à une image
###############

##########
# IMPORT #
##########

from brian import *
import pickle
import os
from skimage import io

#############
# FUNCTIONS #
#############

def lvl2freq(lvl):
    return (lvl/255.)*48+2

###############
# PARAM / VAR #
###############

pathHappy = '/home/totof/fac/S6/Stage/images/tests/happy/'
pathUnhappy = '/home/totof/fac/S6/Stage/images/tests/unhappy/'

spikeFreq = []

########
# MAIN #
########

dirs = os.listdir(pathHappy)

# Pour chaque fichier du dossier de visages souriants
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        temp = []
        image = io.imread(pathHappy + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                temp.append(freq * Hz)

        spikeFreq.append(temp)

dirs = os.listdir(pathUnhappy)

# Pour chaque fichier
for file in dirs:
    # Si c'est une image
    if file[-4:] == '.png':
        temp = []
        image = io.imread(pathUnhappy + file)
        
        # Pour chaque ligne de chaque image
        for ligne in image:
            # Pour chaque pixel de chaque image
            for pix in ligne:
                freq = lvl2freq(pix)
                temp.append(freq * Hz)
        
        spikeFreq.append(temp)

# Écriture du fichier
with open('spikeFreq.spt', 'wb') as fichier:
    pick = pickle.Pickler(fichier)
    pick.dump(spikeFreq)
