#!/usr/bin/python2
# coding:utf-8

###############
# DESCRIPTION #
###############
#
# Author: Christophe Piton
#
# Write 2 files:
#  1st : learning file with 100 happy faces then 100 not happy faces
#  2nd : testing file with 10 happy faces then 10 not happy faces
#
# Table content: (a,b)
#  - a : neuron's address
#  - b : image num
#
###############

##########
# IMPORT #
##########
import os
import brian
import pickle
import numpy
from skimage import io

############
# FUNCTION #
############
def path2tab(path, nbI, threshold):
    tab = []
    # Ouverture dossier
    dirs = os.listdir(path)
    # Pour chaque fichier
    for file in dirs:
        # Si le fichier est une image .png
        if file[-4:] == '.jpg':
            # Chargement image sous-forme tableau
            image = io.imread(path + file, as_grey=True)
            address = 0
            # Pour chaque ligne de l'image
            for ligne in image:
                # Pour chaque pixel de la ligne
                for pix in ligne:
                    # Si il est inférieur au seuil fixé (0=noir / 255=blanc)
                    if pix < threshold:
                        # Ajout du pixel au tableau pour déclencher un influx
                        # Par le neurone correspondant
                        tab.append((address, nbI))
                    # Incrémentation adresse
                    address += 1
            # Incrémentation nombre d'images traitées
            nbI += 1
    return tab, nbI

###############
# PARAM / VAR #
###############
# pathLearnHappy = '/home/totof/fac/S6/Stage/images/tests/happyL/'
# pathLearnUnhappy = '/home/totof/fac/S6/Stage/images/tests/unhappyL/'
# pathTestHappy = '/home/totof/fac/S6/Stage/images/tests/happyT/'
# pathTestUnhappy = '/home/totof/fac/S6/Stage/images/tests/unhappyT/'
pathLearnHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyMouthL/'
pathLearnUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/neutralL/'
pathTestHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyMouthT/'
pathTestUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/neutralT/'


threshold = 125

nbI = 0

########
# MAIN #
########
# Génération fichier d'apprentissage
tab1, nbI = path2tab(pathLearnHappy, nbI, threshold)

tab2, nbI = path2tab(pathLearnUnhappy, nbI, threshold)

spikesTimes = tab1 + tab2

with open('spikesTimesL.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)

# Génération fichier de test
nbI = 0
tab1, nbI = path2tab(pathTestHappy, nbI, threshold)
tab2, nbI = path2tab(pathTestUnhappy, nbI, threshold)
spikesTimes = tab1 + tab2

with open('spikesTimesT.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)
