#!/usr/bin/python2
# coding:utf-8

import random
import brian

def genMaxSorted(nb):
    res = []
    for i in xrange(0,nb):
        res.append(('a'))
    for i in xrange(0,nb):
        res.append(('b'))
    for i in xrange(0,nb):
        res.append(('c'))
    return res
    
def genMaxMixed(nb):
    res = genMaxSorted(nb)
    random.shuffle(res)
    return res

def genMaxOpti(nb):
    res = []
    for i in xrange(0, nb):
        a = brian.rand()
        b = brian.rand()
        c = brian.rand()
        if max(a,b,c) == a:
            res.append('a')
            if max(b,c) == b:
                res.append('b')
                res.append('c')
            else:
                res.append('c')
                res.append('b')
        elif max(a,b,c) == b:
            res.append('b')
            if max(a,c) == a:
                res.append('a')
                res.append('c')
            else:
                res.append('c')
                res.append('a')
        else:
            res.append('c')
            if max(a,b) == a:
                res.append('a')
                res.append('b')
            else:
                res.append('b')
                res.append('a')
    return res

def genMaxABC(nb):
    res = []
    for i in xrange(0,nb):
        res.append('a')
        res.append('b')
        res.append('c')
    return res

def genTabFreq(maxi):
    res = []
    if maxi == 'a':
        if brian.rand() > 0.5:
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
        else:
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
    elif maxi == 'b':
        if brian.rand() > 0.5:
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
        else:
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
    else:
        if brian.rand() > 0.5:
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
        else:
            res.append(2*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(2*brian.Hz)
            res.append(50*brian.Hz)
            res.append(50*brian.Hz)
    return res

def genTabFreqTeach(maxi):
    res = []
    if maxi == 'a':
        res.append(50*brian.Hz)
        res.append(2*brian.Hz)
        res.append(2*brian.Hz)
    elif maxi == 'b':
        res.append(2*brian.Hz)
        res.append(50*brian.Hz)
        res.append(2*brian.Hz)
    else:
        res.append(2*brian.Hz)
        res.append(2*brian.Hz)
        res.append(50*brian.Hz)
    return res        

###########
#  TESTS  #
###########
if __name__ == "__main__":
    n = 3
    tab = genMaxSorted(n)
    print tab
    tab = genMaxMixed(n)
    print tab
    tab = genMaxOpti(n)
    print tab
    tab = genMaxABC(n)
    print tab
    tab = genTabFreq('a')
    print tab
    tab = genTabFreqTeach('a')
    print tab
