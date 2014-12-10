#!/usr/bin/python2
# coding:utf-8

from brian import *

def comp_temp(v1, v2):
    ident1, max1 = v1
    ident2, max2 = v2
    if ident1 < ident2:
        return -1
    elif ident1 > ident2:
        return 1
    else:
        return 0

def add_motif(tab, maxi, t):
    if maxi == 'a':
        tab.append((maxi, 0, t))
        tab.append((maxi, 1, t))
        if rand() < 0.5:
            tab.append((maxi, 3, t))
        else:
            tab.append((maxi, 5, t))
    elif maxi == 'b':
        tab.append((maxi, 2, t))
        tab.append((maxi, 3, t))
        if rand() < 0.5:
            tab.append((maxi, 1, t))
        else:
            tab.append((maxi, 4, t))
    else:
        tab.append((maxi, 4, t))
        tab.append((maxi, 5, t))
        if rand() < 0.5:
            tab.append((maxi, 0, t))
        else:
            tab.append((maxi, 2, t))

def genSpikesTimesMixed(nb, pres_time):
    """
    Génère et renvoie un tableau d'influx avec nb cas où a est le max,
    nb cas où b est le max et nb cas où c est le max,
    Les cas ne sont pas triés et le tableau est de la forme:
    - le max (a, b ou c)
    - l'adresse du neurone qui doit déclencher l'influx
    - le moment où ce neurone doit déclencher l'influx
    """
    temp = []
    res = []
    for i in xrange(0, 3 * nb):
        ident = rand()
        if (i < nb):
            temp.append((ident, 'a'))
        elif (i < 2 * nb):
            temp.append((ident, 'b'))
        else:
            temp.append((ident, 'c'))
    temp = sorted(temp, comp_temp)
    i = 0
    for ident, maxi in temp:
        i += 1

        add_motif(res, maxi, i * pres_time)

    return res

def genSpikesTimesSorted(nb, pres_time):
    """
    Génère et renvoie un tableau d'influx avec nb cas où a est le max,
    nb cas où b est le max et nb cas où c est le max,
    Les cas sont triés (a est max, puis b puis c) et le tableau est de la forme:
    - le max (a, b ou c)
    - l'adresse du neurone qui doit déclencher l'influx
    - le moment où ce neurone doit déclencher l'influx
    """
    res = []
    for i in xrange(1, 3 * nb + 1):
        # a est max
        if i <= nb:

            add_motif(res, 'a', i * pres_time)

        # b est max
        elif i <= (2 * nb):
            
            add_motif(res, 'b', i * pres_time)

        # c est max
        else:

            add_motif(res, 'c', i * pres_time)

    return res

def genSpikesTimesOpti(nb, pres_time):
    """
    Génère et renvoie un tableau d'influx avec nb cas où a est le max,
    nb cas où b est le max et nb cas où c est le max,
    Les cas sont triés par triplets mais les triplets eux mêmes ne sont pas triés.
    Le tableau est de la forme:
    - le max (a, b ou c)
    - l'adresse du neurone qui doit déclencher l'influx
    - le moment où ce neurone doit déclencher l'influx
    """
    res = []
    for i in xrange(0, nb):
        a = rand()
        b = rand()
        c = rand()
        if max(a,b,c) == a:

            add_motif(res, 'a', (i * 3 + 1) * pres_time)
            
            if max(b,c) == b:

                add_motif(res, 'b', (i * 3 + 2) * pres_time)
                add_motif(res, 'c', (i * 3 + 3) * pres_time)

            else:

                add_motif(res, 'c', (i * 3 + 2) * pres_time)
                add_motif(res, 'b', (i * 3 + 3) * pres_time)

        elif max(a,b,c) == b:

            add_motif(res, 'b', (i * 3 + 1) * pres_time)

            if max(a,c) == a:

                add_motif(res, 'a', (i * 3 + 2) * pres_time)
                add_motif(res, 'c', (i * 3 + 3) * pres_time)

            else:

                add_motif(res, 'c', (i * 3 + 2) * pres_time)
                add_motif(res, 'a', (i * 3 + 3) * pres_time)

        else:

            add_motif(res, 'c', (i * 3 + 1) * pres_time)

            if max(a,b) == a:

                add_motif(res, 'a', (i * 3 + 2) * pres_time)
                add_motif(res, 'b', (i * 3 + 3) * pres_time)

            else:

                add_motif(res, 'b', (i * 3 + 2) * pres_time)
                add_motif(res, 'a', (i * 3 + 3) * pres_time)

    return res

def genSpikesTimesABC(nb, pres_time):
    """
    Génère et renvoie un tableau d'influx avec nb cas où a est le max,
    nb cas où b est le max et nb cas où c est le max,
    Les cas sont triés pour faire des triplets abc abc abc... et le tableau est de la forme:
    - le max (a, b ou c)
    - l'adresse du neurone qui doit déclencher l'influx
    - le moment où ce neurone doit déclencher l'influx
    """
    temp = []
    res = []
    for i in xrange(1, 3 * nb + 1):
        j = i % 3
        if (j == 1):
            add_motif(res, 'a', i * pres_time)
        elif (j == 2):
            add_motif(res, 'b', i * pres_time)
        else:
            add_motif(res, 'c', i * pres_time)

    return res
    
def genTeachTimesInhib(spikesTimes):
    n = len(spikesTimes)
    i = 0
    res = []
    while i < n:
        maxi, adr, tim = spikesTimes[i]
        if maxi == 'a':
            res.append((1, tim - 1 * ms))
            res.append((2, tim - 1 * ms))
        elif maxi == 'b':
            res.append((0, tim - 1 * ms))
            res.append((2, tim - 1 * ms))
        else:
            res.append((0, tim - 1 * ms))
            res.append((1, tim - 1 * ms))
        i += 3
    return res

def genTeachTimesExci(spikesTimes):
    n = len(spikesTimes)
    i = 0
    res = []
    while i < n:
        maxi, adr, tim = spikesTimes[i]
        if maxi == 'a':
            res.append((0, tim + 1 * ms))
        elif maxi == 'b':
            res.append((1, tim + 1 * ms))
        else:
            res.append((2, tim + 1 * ms))
        i += 3
    return res

###########
#  TESTS  #
###########
if __name__ == "__main__":

    tab = genSpikesTimesMixed(3, 20*ms)
    # tab = genSpikesTimesSorted(3, 20*ms)
    # tab = genSpikesTimesOpti(3, 20*ms)
    # tea = genTeachTimesInhib(tab)
    tea = genTeachTimesExci(tab)
    
    i = 0
    for l in tab:
        if (i % 3) == 0:
            print ""
        i += 1
        print l
    print ""
    
    for l in tea:
        print l
    
    print len(tab)
    print len(tea)
