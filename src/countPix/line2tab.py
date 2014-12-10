#!/usr/bin/python2
# coding:utf-8

import brian
from random import randint
from random import shuffle

def lines2tab(nb,lineSize):
    res = []
    for i in xrange(0,nb):
        n = randint(0,lineSize)
        line = []
        for j in xrange(0,n):
            line.append(50*brian.Hz)
        for j in xrange(n,lineSize):
            line.append(2*brian.Hz)
        shuffle(line)
        res.append((n,line))
    return res

###########
#  TESTS  #
###########
if __name__ == "__main__":
    n = 3
    data = lines2tab(n,5)
    print data

