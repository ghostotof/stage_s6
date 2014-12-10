#!/usr/bin/python2
# coding:utf-8

###############
# DESCRIPTION #
###############
#
# Author: Christophe Piton
#
# Write 2 files:
#  1st : learning file
#  2nd : testing file
#
# Table content: (h,i,a,t)
#  - id : random id for an image
#  - h  : happy (True) or not (False)
#  - i  : image num
#  - a  : neuron's address
#  - n  : col num
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
def path2tab(path, nbI, threshold, hon):
    tab = []
    # Ouverture dossier
    dirs = os.listdir(path)
    # Pour chaque fichier
    for file in dirs:
        # Si le fichier est une image .jpg
        if file[-4:] == '.jpg':
            # Chargement image sous-forme tableau
            image = io.imread(path + file, as_grey=True)
            id = brian.randn()
            address = 0
            # Pour chaque ligne de l'image
            for ligne in image:
                col = 0
                # Pour chaque pixel de la ligne
                for pix in ligne:
                    # Si il est inférieur au seuil fixé (0=noir / 255=blanc)
                    if pix < threshold:
                        # Ajout du pixel au tableau pour déclencher un influx
                        # Par le neurone correspondant
                        tab.append((id, hon, nbI, address, col))
                    # Incrémentation numero colonne
                    col += 1
                # Incrémentation adresse
                address += 1
            # Incrémentation nombre d'images traitées
            nbI += 1
    return tab, nbI

# Tri selon d'abord l'identifiant de l'image puis le numéro de l'image puis selon le numéro de colonne
def comp(v1, v2):
    id1, h1, i1, a1, c1 = v1
    id2, h2, i2, a2, c2 = v2
    # if id1 < id2:
    #     return -1
    # elif id1 > id2:
    #     return 1
    # else:
    if i1 < i2:
        return -1
    elif i1 > i2:
        return 1
    else:
        if c1 < c2:
            return -1
        elif c1 > c2:
            return 1
        else:
            return 0

###############
# PARAM / VAR #
###############
pathLearnHappy = '/home/christophe/Documents/Stage/images/genki4k/happyMouthL/'
pathLearnUnhappy = '/home/christophe/Documents/Stage/images/genki4k/neutralL/'
pathTestHappy = '/home/christophe/Documents/Stage/images/genki4k/happyMouthT/'
pathTestUnhappy = '/home/christophe/Documents/Stage/images/genki4k/neutralT/'

# pathLearnHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyMouthL/'
# pathLearnUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/neutralL/'
# pathTestHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyMouthT/'
# pathTestUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/neutralT/'

threshold = 75

nbI = 0

########
# MAIN #
########
# Génération fichier d'apprentissage
tab1, nbI = path2tab(pathLearnHappy, nbI, threshold, True)

tab2, nbI = path2tab(pathLearnUnhappy, nbI, threshold, False)

spikesTimes = tab1 + tab2

with open('spikesTimesL.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(sorted(spikesTimes, comp))

# Génération fichier de test
nbI = 0
tab1, nbI = path2tab(pathTestHappy, nbI, threshold, True)
tab2, nbI = path2tab(pathTestUnhappy, nbI, threshold, False)
spikesTimes = tab1 + tab2

with open('spikesTimesT.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(sorted(spikesTimes, comp))
