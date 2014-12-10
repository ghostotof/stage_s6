set title "Pourcentage de réussite d'apprentissage"
set xlabel "Nombre de cas d'apprentissage de chaque maximum"
set ylabel "Pourcentage de réussite"
plot [10:2000] [0:100] "res_struct.dat" title "aaa bbb ccc" with linespoints
replot "res_struct.dat" using 1:3 title "bacbbcaac" with linespoints
replot "res_struct.dat" using 1:4 title "bac abc cba" with linespoints
replot "res_struct.dat" using 1:5 title "abc abc abc" with linespoints
pause -1
quit