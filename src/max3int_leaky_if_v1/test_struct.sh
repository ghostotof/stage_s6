#!/bin/bash

mode=$1

if [ -z $mode ]
then
    echo "Choisir un mode pour l'apprentissage parmis mixed | sorted | opti | ABC"
    exit 1
fi

if [ $mode != "mixed" ] && [ $mode != "opti" ] && [ $mode != "sorted" ] && [ $mode != "ABC" ]
then
    echo "Mode $mode incorrect"
    exit 1
fi

let "nbCasBase = 10"

for i in $(seq 1 20);
do
    let "nbCasTests = $nbCasBase * $i"
    let "moy = 0"

    for j in $(seq 0 99);
    do
	./max3int.py -r -n $nbCasTests -s $mode
	
	./max3int.py -m test

	moy=$(expr $moy + $?)

    done
    
    moy=$(expr $moy / 100)

    echo "nbCas $nbCasTests"
    echo "pourcentage $moy"
    echo ""
done

let "nbCasBase = 100"

for i in $(seq 3 20);
do
    let "nbCasTests = $nbCasBase * $i"
    let "moy = 0"

    for j in $(seq 0 99);
    do
	./max3int.py -r -n $nbCasTests -s $mode
	
	./max3int.py -m test

	moy=$(expr $moy + $?)

    done
    
    moy=$(expr $moy / 100)

    echo "nbCas $nbCasTests"
    echo "pourcentage $moy"
    echo ""
done
