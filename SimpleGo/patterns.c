#include "gnugo/engine/board.h"
#include <stdlib.h>
#include <string.h>
#include "patterns.h"

PatternResultTable pattern_result_table;

static Hash_data pattern_hash[PATTERN_SIZE * 4 * 4 * 2]; // PATTERN_SIZE * pieces * liberties * colors

void init_pattern_result_table()
{
  int num_entries = PATTERN_RESULT_ENTRIES;
  hash_init();
  pattern_result_table.num_entries = num_entries;
  pattern_result_table.entries = malloc(num_entries * sizeof(pattern_result_table.entries[0]));
  if(pattern_result_table.entries == NULL) {
    perror("Couldn't allocate memory for transposition table. \n");
    exit(1);
  }
  INIT_ZOBRIST_ARRAY(pattern_hash);
  clear_pattern_result_table(CLEAR_TYPE_ALL);
}

void clear_pattern_result_table(int type)
{
  int i, j;
  switch(type) {
  case CLEAR_TYPE_ALL:
    memset(pattern_result_table.entries, 0, pattern_result_table.num_entries * sizeof(pattern_result_table.entries[0]));
    break;
  case CLEAR_TYPE_GAME: //clears move too
    for(i=0; i < pattern_result_table.num_entries; i++) {
      for(j=0; j < PATTERN_HASH_LIST_SIZE; j++) {
        pattern_result_table.entries[i].node_lst[j].win_count_game = 0;
        pattern_result_table.entries[i].node_lst[j].lost_count_game = 0;
      }
    }
  case CLEAR_TYPE_MOVE:
    for(i=0; i < pattern_result_table.num_entries; i++) {
      for(j=0; j < PATTERN_HASH_LIST_SIZE; j++) {
        pattern_result_table.entries[i].node_lst[j].win_count_move = 0;
        pattern_result_table.entries[i].node_lst[j].lost_count_move = 0;
      }
    }
  }
}

/*
  8
 407
91!3B
 526
  A
*/
int pattern_delta[PATTERN_SIZE] = {NS, -1, -NS, 1,
                                   NS-1, -NS-1, -NS+1, NS+1,
                                   2*NS, -2, -2*NS, 2};
int pattern_edge_check[PATTERN_SIZE] = {NS, -1, -NS, 1,
                                        NS-1, -NS-1, -NS+1, NS+1,
                                        NS, -1, -NS, 1}; // others same as delta, except last 4

void pattern_calc_hash(PatternResult *pattern, int pos, int color)
{
  int i, pos2, pos3;
  int piece, liberties;
  int key;
  hashdata_clear(&(pattern->key));
  color -= WHITE;
  for(i = 0; i < PATTERN_SIZE; i++) {
    pos2 = pos + pattern_delta[i];
    pos3 = pos + pattern_edge_check[i];
    liberties = 1;
    if(board[pos3]==GRAY) {
      piece = GRAY;
    } else {
      piece = board[pos2];
      if(IS_STONE(piece)) {
        liberties = countlib(pos2);
        if(liberties > 4) {
          liberties = 4;
        }
      }
    }
    liberties--;
    key = color + (piece<<1) + (liberties<<3);
    pattern->pattern[i] = key;
    key += (i<<5);
    hashdata_xor(pattern->key, pattern_hash[key]);
  }
}

PatternResult *get_pattern_result_table(int pos, int color)
{
  PatternResult pattern;
  PatternResultEntries *entry;
  PatternResult *node;
  pattern_calc_hash(&pattern, pos, color);
  int i;
  entry = &pattern_result_table.entries[hashdata_remainder(pattern.key, pattern_result_table.num_entries)];
  //printf("get hashval: %li\n", pattern.key.hashval[0]);
  for(i = 0; i < PATTERN_HASH_LIST_SIZE; i++) {
    if(hashdata_is_equal(pattern.key, entry->node_lst[i].key)) {
      //printf("get: %i\n", i);
      node = &(entry->node_lst[i]);
      return node;
    }
  }
  return NULL;
}

void add_pattern_result_table(int pos, int color, int win_count, int lost_count)
{
  PatternResult pattern;
  PatternResultEntries *entry;
  PatternResult *node = NULL;
  int count, best_count = 2000000000;
  int i;
  pattern_calc_hash(&pattern, pos, color);
  entry = &pattern_result_table.entries[hashdata_remainder(pattern.key, pattern_result_table.num_entries)];
  //printf("update hashval: %li, %li\n", pattern.key.hashval[0], hashdata_remainder(pattern.key, pattern_result_table.num_entries));
  for(i = 0; i < PATTERN_HASH_LIST_SIZE; i++) {
    // if found previous one, use that
    if(hashdata_is_equal(pattern.key, entry->node_lst[i].key)) {
      //printf("update: found: %i\n", i);
      node = &(entry->node_lst[i]);
      break;
    } else {
      // replace least used one
      count = entry->node_lst[i].win_count_move + entry->node_lst[i].lost_count_move;
      if(count < best_count) {
        //printf("update: new best: %i, %i, %i\n", i, count, best_count);
        best_count = count;
        node = &(entry->node_lst[i]);
      } else {
        //printf("update: worse: %i, %i, %i", i, count, best_count);
      }
      //printf(" %li\n", entry->node_lst[i].key.hashval[0]);
    }
  }
  node->key = pattern.key;
  memcpy(node->pattern, pattern.pattern, sizeof(pattern.pattern));
  node->win_count_move += win_count;
  node->lost_count_move += lost_count;
}

int dump_pattern_result_table(char *filename)
{
  int i, j, k;
  FILE *fp;
  fp = fopen(filename, "w");
  if(!fp) {
    return FALSE;
  }
  for(i=0; i < pattern_result_table.num_entries; i++) {
    for(j=0; j < PATTERN_HASH_LIST_SIZE; j++) {
      PatternResult *node = &(pattern_result_table.entries[i].node_lst[j]);
      if(node->key.hashval[0]==0) {
        continue;
      }
      for(k=0; k < PATTERN_SIZE; k++) {
        if(!fprintf(fp, "%i ", (int)node->pattern[k])) {
          fclose(fp);
          return FALSE;
        }
      }
      if(!fprintf(fp, "%i %i %i %i %i %i\n",
                  node->win_count_total, node->lost_count_total,
                  node->win_count_game, node->lost_count_game,
                  node->win_count_move, node->lost_count_move)) {
        fclose(fp);
        return FALSE;
      }
    }
  }
  fclose(fp);
  return TRUE;
}

void add_loaded_pattern_result_table(PatternResult *pattern)
{
  int i;
  int key;
  PatternResultEntries *entry;
  PatternResult *node = NULL;
  int count, best_count = 2000000000;
  hashdata_clear(&(pattern->key));
  /* calc hash from already compressed pattern */
  for(i = 0; i < PATTERN_SIZE; i++) {
    key = pattern->pattern[i];
    key += (i<<5);
    hashdata_xor(pattern->key, pattern_hash[key]);
  }
  /* actually add */
  entry = &pattern_result_table.entries[hashdata_remainder(pattern->key, pattern_result_table.num_entries)];
  for(i = 0; i < PATTERN_HASH_LIST_SIZE; i++) {
    if(hashdata_is_equal(pattern->key, entry->node_lst[i].key)) {
      node = &(entry->node_lst[i]);
      break;
    } else {
      // replace least used one
      count = entry->node_lst[i].win_count_move + entry->node_lst[i].lost_count_move;
      if(count < best_count) {
        best_count = count;
        node = &(entry->node_lst[i]);
      }
    }
  }
  node->key = pattern->key;
  memcpy(node->pattern, pattern->pattern, sizeof(pattern->pattern));
  node->win_count_move = pattern->win_count_move;
  node->lost_count_move = pattern->lost_count_move;
}

int load_pattern_result_table(char *filename)
{
  PatternResult node;
  int i;
  FILE *fp;
  fp = fopen(filename, "r");
  if(!fp) {
    return FALSE;
  }
  while(TRUE) {
    for(i = 0; i < PATTERN_SIZE; i++) {
      int tmp;
      if(fscanf(fp, "%i", &tmp)!=1) {
        fclose(fp);
        return i==0;
      }
      node.pattern[i] = tmp;
    }
    if(fscanf(fp, "%i %i %i %i %i %i\n",
              &node.win_count_total, &node.lost_count_total,
              &node.win_count_game, &node.lost_count_game,
              &node.win_count_move, &node.lost_count_move)!=6) {
      fclose(fp);
      return FALSE;
    }
    add_loaded_pattern_result_table(&node);
  }
}
