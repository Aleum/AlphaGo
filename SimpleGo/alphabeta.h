#ifndef ALPHABETA_H
#define ALPHABETA_H

#include "c_board.h"

#define RAND_FACTOR 1000000

int alpha_beta_search(int pos, int color, int depth, int alpha, int beta);
int alpha_beta_search_random(int pos, int color, int depth, int alpha, int beta, int limit);

#endif // ALPHABETA_H
