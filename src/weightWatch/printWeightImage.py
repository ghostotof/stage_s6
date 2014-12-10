#!/usr/bin/python2
# coding:utf-8

import pixel
import os
import sys
import pickle

from brian import *

def usage():
    print "\nUsage :"
    # print "\tprintWeightImage.py [lenC1] [lenC2] [minW] [maxW] [fichierCo]"
    print "\tprintWeightImage.py [lenC1] [lenC2] [fichierCo]"
    print "\t\t[lenC1]     : nombre de neurones de la première couche (entier)"
    print "\t\t[lenC2]     : nombre de neurones de la seconde couche (entier)"
    # print "\t\t[minW]      : poids minimum des synapses (entier)"
    # print "\t\t[maxW]      : poids maximum des synapses (entier)"
    print "\t\t[fichierCo] : fichier de connectivité des deux couches"
    sys.exit(10)

def norm(mini, maxi, x):
    ecart = maxi - mini
    return (x - mini) / float(ecart)

try:
    lenC1 = int(sys.argv[1])
    lenC2 = int(sys.argv[2])
    # minW  = int(sys.argv[3])
    # maxW  = int(sys.argv[4])
    fichierCo = sys.argv[3]
except :
    usage()

try:
    c1 = SpikeGeneratorGroup(lenC1, [])
    c2 = SpikeGeneratorGroup(lenC2, [])
    s = Synapses(c1, c2, model = 'w:1', pre = 'v+=w')
    s.load_connectivity(fichierCo)
except :
    print "Problème lors création des couches et/ou synapses"
    sys.exit(11)

minW = 100
maxW = -100

for file in os.listdir(os.getcwd()):
    if file[-4:] == ".spw":
        fileComp = os.getcwd() + "/" + file
        with open(fileComp, 'rb') as fd:
            mon_depick = pickle.Unpickler(fd)
            wn = mon_depick.load()
        s.w = wn
        for i in xrange(0, lenC1):
            for j in xrange(0, lenC2):
                if s.w[i,j] > maxW:
                    maxW = s.w[i,j]
                if s.w[i,j] < minW:
                    minW = s.w[i,j]

print "Poids minimum:", minW
print "Poids maximum:", maxW

for file in os.listdir(os.getcwd()):
    # print "Fichier :", file
    if file[-4:] == ".spw":
        fileComp = os.getcwd() + "/" + file
        with open(fileComp, 'rb') as fd:
            mon_depick = pickle.Unpickler(fd)
            wn = mon_depick.load()
        s.w = wn
        
        pixel.initialiser(lenC1, lenC2, 20)

        for i in xrange(0, lenC1):
            for j in xrange(0, lenC2):
                val = norm(minW, maxW, s.w[i,j])
                pixel.marquer(i, j, val)
                
        pixel.enregistrer(os.getcwd() + "/" + file[:-4] + ".gif")
