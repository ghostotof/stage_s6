#!/bin/bash

if [ $# -ne 3 ]
then
    echo -e "Problème nombre d'arguments\nUsage : Se placer dans le dossier contenant les fichiers avec les poids synaptiques intermédiaires puis :"
    # echo -e "\tweightWatch [lenC1] [lenC2] [minW] [maxW] [fileCo]"
    echo -e "\tweightWatch [lenC1] [lenC2] [fileCo]"
    echo -e "\t\t[lenC1]  : nombre de neurones de la première couche"
    echo -e "\t\t[lenC2]  : nombre de neurones de la seconde couche"
    # echo -e "\t\t[minW]   : poids synaptique minimum"
    # echo -e "\t\t[maxW]   : poids synaptique maximum"
    echo -e "\t\t[fileCo] : fichier de connectivité du réseau"
    exit 5
fi

let "lenC1 = $1"
let "lenC2 = $2"
# let "minW = $3"
# let "maxW = $4"
fileCo=$3

let "w = $lenC1 * 100"
let "h = $lenC2 * 100"

if [ ! -e $fileCo ]
then
    echo "Le fichier $fileCo n'existe pas"
    exit 10
fi

echo "Transformation poids -> images "

# printWeightImage.py $lenC1 $lenC2 $minW $maxW $fileCo
printWeightImage.py $lenC1 $lenC2 $fileCo

echo "Conversion images gif -> jpg"

fichiers=`ls *.gif`

for f in $fichiers ;
do
  if echo "$f" | grep -i "gif$" > /dev/null ;
    then
    jpg=`echo "$f" | sed 's/gif$/jpg/i'`
    echo "convert : $f -> $jpg"
    convert $f $jpg
  else
    echo "ignored : $f"
  fi
done

echo "Création vidéo"

mencoder mf://*.jpg -mf w=$w:h=$h:fps=25:type=jpg -ovc copy -oac copy -o sortie.avi

echo "Nettoyage si nécessaire"

if [ -e sortie.avi ]
then
    rm *.spw *.gif *.jpg
else
    echo "Pas de fichier vidéo en sortie"
    exit 11
fi
