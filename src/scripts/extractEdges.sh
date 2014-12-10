#!/bin/bash

pathSrcHL="/home/christophe/Documents/Stage/images/genki4k/happyL/"
pathDstHL="/home/christophe/Images/edgesHappyL/"
pathSrcHT="/home/christophe/Documents/Stage/images/genki4k/happyT/"
pathDstHT="/home/christophe/Images/edgesHappyT/"
pathSrcNL="/home/christophe/Documents/Stage/images/genki4k/unhappyL/"
pathDstNL="/home/christophe/Images/edgesNeutralL/"
pathSrcNT="/home/christophe/Documents/Stage/images/genki4k/unhappyT/"
pathDstNT="/home/christophe/Images/edgesNeutralT/"

pathRelease="/home/christophe/Documents/Stage/src/ExtractEdges/Release/"

cd $pathSrcHL

fichiers=`ls`

cd $pathRelease

for fichier in $fichiers;
do
    ./ExtractEdges $pathSrcHL $pathDstHL $fichier 50
done

echo "Happy Edges Learning Generated"

cd $pathSrcHT

fichiers=`ls`

cd $pathRelease

for fichier in $fichiers;
do
    ./ExtractEdges $pathSrcHT $pathDstHT $fichier 50
done

echo "Happy Edges Testing Generated"

cd $pathSrcNL

fichiers=`ls`

cd $pathRelease

for fichier in $fichiers;
do
    ./ExtractEdges $pathSrcNL $pathDstNL $fichier 50
done

echo "Neutral Edges Learning Generated"

cd $pathSrcNT

fichiers=`ls`

cd $pathRelease

for fichier in $fichiers;
do
    ./ExtractEdges $pathSrcNT $pathDstNT $fichier 50
done

echo "Neutral Edges Testing Generated"
