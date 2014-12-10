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

let "nbCasBase = 100"

for i in $(seq 1 20);
do
    let "nbCasTests = $nbCasBase * $i"
    let "nbCasOK = 0"
    let "nbCasKO = 0"

    for j in $(seq 0 99);
    do
	./max3int.py -r -n $nbCasTests -s $mode
	
	./max3int.py -m test

	if [ $? -eq 50 ]
	then
	    nbCasKO=$(expr $nbCasKO + 1)
	else
	    nbCasOK=$(expr $nbCasOK + 1)
	fi

    done

    echo ""
    echo "Pour $nbCasTests :"
    echo "Nombre de cas OK : $nbCasOK"
    echo "Nombre de cas KO : $nbCasKO"
    echo ""
done
