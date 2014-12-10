#!/usr/bin/python2
# coding:utf-8

###############
# DESCRIPTION #
###############
#
# Author: Christophe Piton
#
# Write 2 files:
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
from skimage.filter import canny
from skimage.viewer import ImageViewer
############
# FUNCTION #
############
def path2tab(path, nbI, threshold):
    tab = []
    maxAddr = 0
    # Ouverture dossier
    dirs = os.listdir(path)
    # Pour chaque fichier
    for file in dirs:
        # Si le fichier est une image .jpg
        if file[-4:] == '.jpg':
            # Chargement image sous-forme tableau
            image = io.imread(path + file, as_grey=True)
            edges = canny(image)
            address = 0
            # Pour chaque ligne de l'image
            for ligne in edges:
                # Pour chaque pixel de la ligne
                for pix in ligne:
                    # Si le pixel est blanc (c'est un contour)
                    if pix == True:
                        # Ajout du pixel au tableau pour déclencher un influx
                        # Par le neurone correspondant
                        tab.append((address, nbI))
                        if address > maxAddr:
                            maxAddr = address
                    # Incrémentation adresse
                    address += 1
            # Incrémentation nombre d'images traitées
            nbI += 1
    print maxAddr
    return tab, nbI

###############
# PARAM / VAR #
###############
pathLearnHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyLG/'
pathLearnUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/unhappyLG/'
pathTestHappy = '/home/totof/fac/S6/Stage/images/genki4k/happyTG/'
pathTestUnhappy = '/home/totof/fac/S6/Stage/images/genki4k/unhappyTG/'

threshold = 50

nbI = 0

########
# MAIN #
########
# Génération fichier d'apprentissage
spikesTimes, nbI = path2tab(pathLearnHappy, nbI, threshold)
print "Nombre visages souriants (apprentissage) =", nbI
with open('spikesTimesLH.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)

nbI = 0
spikesTimes, nbI = path2tab(pathLearnUnhappy, nbI, threshold)
print "Nombre visages non souriants (apprentissage) =", nbI
with open('spikesTimesLU.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)

# Génération fichier de test
nbI = 0
spikesTimes, nbI = path2tab(pathTestHappy, nbI, threshold)
print "Nombre visages souriants (test) =", nbI
with open('spikesTimesTH.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)

nbI = 0
spikesTimes, nbI = path2tab(pathTestUnhappy, nbI, threshold)
print "Nombre visages non souriants (test) =", nbI
with open('spikesTimesTU.spt', 'wb') as file:
    pick = pickle.Pickler(file)
    pick.dump(spikesTimes)
