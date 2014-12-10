#!/bin/bash

sorted="res_tests_sorted.txt"
mixed="res_tests_mixed.txt"
opti="res_tests_opti.txt"
abc="res_tests_abc.txt"

out="res_struct.dat"

echo "# nombre de cas | sorted | mixed | opti | abc" > $out

linesNb=`grep nbCas < $sorted`
linesPcSorted=`grep pourcentage < $sorted`
linesPcMixed=`grep pourcentage < $mixed`
linesPcOpti=`grep pourcentage < $opti`
linesPcAbc=`grep pourcentage < $abc`

nbL=`grep -c nbCas < $sorted`

for i in $(seq 1 $nbL);
do
    nb=`echo $linesNb | cut -d' ' -f$(($i*2))`
    pcSort=`echo $linesPcSorted | cut -d' ' -f$(($i*2))`
    pcMix=`echo $linesPcMixed | cut -d' ' -f$(($i*2))`
    pcOpti=`echo $linesPcOpti | cut -d' ' -f$(($i*2))`
    pcAbc=`echo $linesPcAbc | cut -d' ' -f$(($i*2))`

    echo "$nb $pcSort $pcMix $pcOpti $pcAbc" >> $out
done
