#!/usr/bin/python2
# coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys

try:
    fileIn = sys.argv[1]
    fileOut = sys.argv[2]
except Exception, e:
    print "Erreur paramètres : {}".format(e)
    sys.exit(-1)

fig = plt.figure()
ax = fig.add_subplot(111)

wn = []
with open(fileIn, 'rb') as fichier:
    mon_depick = pickle.Unpickler(fichier)
    wn = mon_depick.load()

N = len(wn)

width = 1

ind = np.arange(N)

rects = ax.bar(ind, wn, width, color='black')

ax.set_xlim(-width, len(ind)+width)
ax.set_ylim(min(wn)-1, max(wn)+1)
ax.set_ylabel('Poids')

# plt.show()

fig.savefig(fileOut)
