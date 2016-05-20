#ifndef PATTERNS_H
#define PATTERNS_H

#include "c_board.h"

/*
Diamond aka manhattan distance pattern:

  O
 OXO
OX!XO
 OXO
  O

move is at middle '!'
Other points: empty, white, black or edge
If stone, then how many liberties?: 1, 2, 3, 4>=
4**12 * 4 = 67108864 different patterns
win_count_total, lost_count_total, win_count_game, lost_count_game, win_count_move, lost_count_move: 4*6*67108864  -> 1536MiB
If there is a danger of count getting too big, divide both counts by 2



*/

#define USE_PATTERNS FALSE
#define LEARN_PATTERNS FALSE

#define PATTERN_SIZE 12

typedef struct 
{
  Hash_data key;
  unsigned char pattern[PATTERN_SIZE];
  unsigned int win_count_total, lost_count_total;
  unsigned int win_count_game, lost_count_game;
  unsigned int win_count_move, lost_count_move;
} PatternResult;


#define PATTERN_HASH_LIST_SIZE 4

typedef struct {
  PatternResult node_lst[PATTERN_HASH_LIST_SIZE];
} PatternResultEntries;

typedef struct {
  unsigned int num_entries;
  PatternResultEntries *entries;
} PatternResultTable;

extern PatternResultTable pattern_result_table;

#if USE_PATTERNS
#define PATTERN_RESULT_ENTRIES 1048576
#else
#define PATTERN_RESULT_ENTRIES 1024
#endif

#define CLEAR_TYPE_ALL 0
#define CLEAR_TYPE_GAME 1
#define CLEAR_TYPE_MOVE 2

void init_pattern_result_table();
void clear_pattern_result_table(int type);
void pattern_calc_hash(PatternResult *pattern, int pos, int color);
PatternResult *get_pattern_result_table(int pos, int color);
void add_pattern_result_table(int pos, int color, int win_count, int lost_count);
int dump_pattern_result_table(char *filename);
int load_pattern_result_table(char *filename);

#endif // PATTERNS_H
