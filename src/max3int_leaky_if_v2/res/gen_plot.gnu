set title "Pourcentage de reconnaissance"
set xlabel "Nombre de cas d'apprentissage de chaque maximum"
set ylabel "Pourcentage de réussite"
plot [0:1700] [0:100] "res_struct.dat" using 1:2 title "Trié" with linespoints, \
"res_struct.dat" using 1:3 title "Aléatoire" with linespoints, \
"res_struct.dat" using 1:4 title "Opti" with linespoints, \
"res_struct.dat" using 1:5 title "abc" with linespoints
pause -1
quit