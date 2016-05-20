all: cpatternsmodule.so c_boardmodule.so

cpatternsmodule.so: cpatternsmodule.o
	gcc -g -shared -o cpatternsmodule.so cpatternsmodule.o

cpatternsmodule.o: cpatternsmodule.c
	gcc -g -O2 -Wall -fPIC -I/usr/include/python2.4/ -c cpatternsmodule.c

c_boardmodule.so: c_boardmodule.o montecarlo.o alphabeta.o patterns.o
	gcc -g -shared -o c_boardmodule.so patterns.o montecarlo.o alphabeta.o c_boardmodule.o gnugo/engine/libboard.a gnugo/engine/libengine.a gnugo/sgf/libsgf.a gnugo/utils/libutils.a -lncurses -lm

montecarlo.o: montecarlo.c montecarlo.h patterns.h
	gcc -g -O2 -Wall -Ignugo -Ignugo/utils -Ignugo/engine -Ignugo/sgf -c montecarlo.c

alphabeta.o: alphabeta.c alphabeta.h
	gcc -g -O2 -Wall -Ignugo -Ignugo/utils -Ignugo/engine -Ignugo/sgf -c alphabeta.c

patterns.o: patterns.c patterns.h
	gcc -g -O2 -Wall -Ignugo -Ignugo/utils -Ignugo/engine -Ignugo/sgf -c patterns.c

c_boardmodule.o: c_boardmodule.c montecarlo.h alphabeta.h
	gcc -g -O2 -Wall -fPIC -I/usr/include/python2.4/ -Ignugo -Ignugo/utils -Ignugo/engine -Ignugo/sgf -c c_boardmodule.c
