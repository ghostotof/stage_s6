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

# let "nbCasBase = 10"

# for i in $(seq 2 2 10);
# do
#     let "nbCasTests = $nbCasBase * $i"
#     let "moy = 0"

#     for j in $(seq 0 49);
#     do
# 	./max3int.py -n $nbCasTests -s $mode
	
# 	./max3int.py -m test

# 	moy=$(expr $moy + $?)

#     done
    
#     moy=$(expr $moy / 50)

#     echo "nbCas $nbCasTests"
#     echo "pourcentage $moy"
#     echo ""
# done

let "nbCasBase = 100"

for i in $(seq 2 2);
do
    let "nbCasTests = $nbCasBase * $i"
    let "moy = 0"

    for j in $(seq 0 49);
    do
	./max3int.py -n $nbCasTests -s $mode
	
	./max3int.py -m test

	moy=$(expr $moy + $?)

    done
    
    moy=$(expr $moy / 50)

    echo "nbCas $nbCasTests"
    echo "pourcentage $moy"
    echo ""
done
