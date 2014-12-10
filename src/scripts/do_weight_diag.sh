#!/bin/bash

fichiers=`ls *.spw`

for fichier in $fichiers;
do    
    echo "Fichier : $fichier"
    
    sortie=${fichier/spw/png}
    
    crea_diag_poids.py $fichier $sortie
    
    echo ""
done
