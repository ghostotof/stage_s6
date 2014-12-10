#!/bin/bash

####################################
#                                  #
# Dossier de l'applicatif à tester #
#                                  #
####################################
path="/home/cpiton/src/MyNetworks/balayageEdges/"

#####################
#                   #
# Paramètres de sed #
#                   #
#####################
sed_param_learn=""
sed_param_test=""

##########################
#                        #
# Variables du programme #
#                        #
##########################

# Temps

min_period="1.0"                       # msecond
sed_param_learn="s|%MIN_PER|$min_period|"
sed_param_test="s|%MIN_PER|$min_period|"

base_period="125"                      # coef min_period
sed_param_learn="$sed_param_learn;s|%BAS_PER|$base_period|"
sed_param_test="$sed_param_test;s|%BAS_PER|$base_period|"

t_pres="4"                             # coef base_period
sed_param_learn="$sed_param_learn;s|%T_PRES|$t_pres|"
sed_param_test="$sed_param_test;s|%T_PRES|$t_pres|"

t_pres_tot="2"                         # coef t_pres
sed_param_learn="$sed_param_learn;s|%T_TOT|$t_pres_tot|"
sed_param_test="$sed_param_test;s|%T_TOT|$t_pres_tot|"

# Poids

min_weight="-10.0"                     # volt
sed_param_learn="$sed_param_learn;s|%MIN_W|$min_weight|"

max_weight="10.0"                      # volt
sed_param_learn="$sed_param_learn;s|%MAX_W|$max_weight|"

inc_weight="0.1"                       # coef max_weight
sed_param_learn="$sed_param_learn;s|%INC_W|$inc_weight|"

dec_weight="0.05"                      # coef max_weight
sed_param_learn="$sed_param_learn;s|%DEC_W|$dec_weight|"

init_weight="0"                        # volt
sed_param_learn="$sed_param_learn;s|%INI_W|$init_weight|"

std_init_weight="10.0"                 # volt
sed_param_learn="$sed_param_learn;s|%STD_INI_W|$std_init_weight|"

inh_weight="50.0"                      # volt
sed_param_learn="$sed_param_learn;s|%INH_W|$inh_weight|"
sed_param_test="$sed_param_test;s|%INH_W|$inh_weight|"

# Couches de neurones

nbN_I="40"                             # nombre de neurones de la couche input
sed_param_learn="$sed_param_learn;s|%NBN_I|$nbN_I|"
sed_param_test="$sed_param_test;s|%NBN_I|$nbN_I|"

# Couche 1

nbN_1="40"                             # nombre de neurones
sed_param_learn="$sed_param_learn;s|%NBN_1|$nbN_1|"
sed_param_test="$sed_param_test;s|%NBN_1|$nbN_1|"

Vt_1="15.0"                            # volt
sed_param_learn="$sed_param_learn;s|%VT_1|$Vt_1|"
sed_param_test="$sed_param_test;s|%VT_1|$Vt_1|"

Vr_1="0.0"                             # volt
sed_param_learn="$sed_param_learn;s|%VR_1|$Vr_1|"
sed_param_test="$sed_param_test;s|%VR_1|$Vr_1|"

tau_1="(2.0/3.0)"                      # coef base_period
sed_param_learn="$sed_param_learn;s|%TAU_1|$tau_1|"
sed_param_test="$sed_param_test;s|%TAU_1|$tau_1|"

coef_ref_1="0.5"                       # coef temps refractaire
sed_param_learn="$sed_param_learn;s|%CREF_1|$coef_ref_1|"
sed_param_test="$sed_param_test;s|%CREF_1|$coef_ref_1|"

ref_ref_1="t_col"                      # base sur laquelle est appliquée le coef
sed_param_learn="$sed_param_learn;s|%RREF_1|$ref_ref_1|"
sed_param_test="$sed_param_test;s|%RREF_1|$ref_ref_1|"

inh_ref_1="1.05"                       # coef base_period
sed_param_learn="$sed_param_learn;s|%INH_REF_1|$inh_ref_1|"
sed_param_test="$sed_param_test;s|%INH_REF_1|$inh_ref_1|"

# Couche 2

nbN_2="20"                             # nombre de neurones
sed_param_learn="$sed_param_learn;s|%NBN_2|$nbN_2|"
sed_param_test="$sed_param_test;s|%NBN_2|$nbN_2|"

Vt_2="15.0"                            # volt
sed_param_learn="$sed_param_learn;s|%VT_2|$Vt_2|"
sed_param_test="$sed_param_test;s|%VT_2|$Vt_2|"

Vr_2="0.0"                             # volt
sed_param_learn="$sed_param_learn;s|%VR_2|$Vr_2|"
sed_param_test="$sed_param_test;s|%VR_2|$Vr_2|"

tau_2="(2.0/3.0)"                      # coef t_pres
sed_param_learn="$sed_param_learn;s|%TAU_2|$tau_2|"
sed_param_test="$sed_param_test;s|%TAU_2|$tau_2|"

coef_ref_2="0.5"                       # coef temps refractaire
sed_param_learn="$sed_param_learn;s|%CREF_2|$coef_ref_2|"
sed_param_test="$sed_param_test;s|%CREF_2|$coef_ref_2|"

ref_ref_2="t_col"                      # base sur laquelle est appliquée le coef
sed_param_learn="$sed_param_learn;s|%RREF_2|$ref_ref_2|"
sed_param_test="$sed_param_test;s|%RREF_2|$ref_ref_2|"

inh_ref_2="1.05"                       # coef base_period
sed_param_learn="$sed_param_learn;s|%INH_REF_2|$inh_ref_2|"
sed_param_test="$sed_param_test;s|%INH_REF_2|$inh_ref_2|"

# Couche 3

nbN_3="2"                              # nombre de neurones
sed_param_learn="$sed_param_learn;s|%NBN_3|$nbN_3|"
sed_param_test="$sed_param_test;s|%NBN_3|$nbN_3|"

Vt_3="15.0"                            # volt
sed_param_learn="$sed_param_learn;s|%VT_3|$Vt_3|"
sed_param_test="$sed_param_test;s|%VT_3|$Vt_3|"

Vr_3="0.0"                             # volt
sed_param_learn="$sed_param_learn;s|%VR_3|$Vr_3|"
sed_param_test="$sed_param_test;s|%VR_3|$Vr_3|"

# tau_3="(2.0/3.0)"                      # coef t_pres
# sed_param_learn="$sed_param_learn;s|%TAU_3|$tau_3|"
# sed_param_test="$sed_param_test;s|%TAU_3|$tau_3|"

coef_ref_3="0.5"                       # coef temps refractaire
sed_param_learn="$sed_param_learn;s|%CREF_3|$coef_ref_3|"
sed_param_test="$sed_param_test;s|%CREF_3|$coef_ref_3|"

ref_ref_3="t_pres"                     # base sur laquelle est appliquée le coef
sed_param_learn="$sed_param_learn;s|%RREF_3|$ref_ref_3|"
sed_param_test="$sed_param_test;s|%RREF_3|$ref_ref_3|"

inh_ref_3="1.05"                       # coef base_period
sed_param_learn="$sed_param_learn;s|%INH_REF_3|$inh_ref_3|"
sed_param_test="$sed_param_test;s|%INH_REF_3|$inh_ref_3|"

# STDP

ltp="2.0"                              # coef base_period
sed_param_learn="$sed_param_learn;s|%LTP|$ltp|"

#############
#           #
# Lancement #
#           #
#############
cd $path

for i in `seq 2 2`;
do
    # Fichiers entre apprentissage et test
    
    co_1_2="saveConnec_1_2_Tau3_$i.spc"
    sed_param_learn="$sed_param_learn;s|%CO_1_2|$co_1_2|"
    sed_param_test="$sed_param_test;s|%CO_1_2|$co_1_2|"
    
    co_2_3="saveConnec_2_3_Tau3_$i.spc"
    sed_param_learn="$sed_param_learn;s|%CO_2_3|$co_2_3|"
    sed_param_test="$sed_param_test;s|%CO_2_3|$co_2_3|"

    poids_1_2="weights_1_2_Tau3_$i.spw"
    sed_param_learn="$sed_param_learn;s|%PDS_1_2|$poids_1_2|"
    sed_param_test="$sed_param_test;s|%PDS_1_2|$poids_1_2|"

    poids_2_3="weights_2_3_Tau3_$i.spw"
    sed_param_learn="$sed_param_learn;s|%PDS_2_3|$poids_2_3|"
    sed_param_test="$sed_param_test;s|%PDS_2_3|$poids_2_3|"

    # Paramètres à tester

    tau_3="$i*(1.0/3.0)"                      # coef t_pres
    sed_param_learn="$sed_param_learn;s|%TAU_3|$tau_3|"
    sed_param_test="$sed_param_test;s|%TAU_3|$tau_3|"

    # Génération des sources

    sed -e $sed_param_learn learnST_US_gen.py >> learnST_US_Tau3_$i.py
    sed -e $sed_param_test testST_US_gen.py >> testST_US_Tau3_$i.py
    
    chmod +x learnST_US_Tau3_$i.py
    chmod +x testST_US_Tau3_$i.py

    # Exécution

    echo "Exécution learnST_US_Tau3_$i.py : "`date`

    message=`./learnST_US_Tau3_$i.py`
    
    echo -e "Résultats après apprentissage\nlearnST_US_Tau3_$i\n\n$message" >> resTestTau3_$i.txt

    echo -e "\n\n#######################################################\n\n" >> resTestTau3_$i.txt
    
    echo "Exécution testST_US_Tau3_$i.py : "`date`

    message=`./testST_US_Tau3_$i.py`

    echo -e "Résultats après tests\ntestST_US_Tau3_$i.py\n\n$message" >> resTestTau3_$i.txt

    # Nettoyage

    rm learnST_US_Tau3_$i.py testST_US_Tau3_$i.py 
    rm saveConnec_1_2_Tau3_$i.spc saveConnec_2_3_Tau3_$i.spc 
    rm weights_1_2_Tau3_$i.spw weights_2_3_Tau3_$i.spw

    dayDir=`date +%Y%m%d`
    
    if [ ! -d "resTests" ]
    then
	mkdir "resTests"
    fi
    
    if [ ! -d "resTests/$dayDir" ]
    then
	mkdir "resTests/$dayDir"
    fi

    mv resTestTau3_* "resTests/$dayDir/"

done
