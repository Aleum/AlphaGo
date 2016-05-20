#ifndef MONTECARLO_H
#define MONTECARLO_H

#include "c_board.h"

#define COMPLETELY_RANDOM FALSE
#define BROWN_RANDOM FALSE
#define LIBERTY_SHAPE_RANDOM TRUE
#define BEST_LIBERTY_SHAPE_RANDOM FALSE

int play_random_move(int color);
int play_random_game();
void undo_game(int moves);
double score_board();
int play_random_capture_game(int pos, int color);
void uct_game(int pos, int color);

typedef struct {
  Hash_data key;
  double win_count, lost_count;
} ResultNode;

#define HASH_LIST_SIZE 4

typedef struct {
  ResultNode node_lst[HASH_LIST_SIZE];
} ResultEntries;

typedef struct {
  unsigned int num_entries;
  ResultEntries *entries;
} ResultTable;

extern ResultTable result_table;

#define RESULT_ENTRIES 1048576
void init_result_table();
void clear_result_table();
ResultNode *get_result_table(double *win_count, double *lost_count, int color);
void update_result_table(double win_count, double lost_count, int color);
int uct_top_win_ratio_move(int color, int *best_move, double *result_win_count, double *result_lost_count);

#define AREA_SCORE_FACTOR 0.001
#define GAME_LENGTH_SCORE_FACTOR 0.0 //(AREA_SCORE_FACTOR * 0.01)

#define WORST_SCORE -1000000000

#endif // MONTECARLO_H
