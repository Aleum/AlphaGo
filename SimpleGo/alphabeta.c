#include "gnugo/engine/board.h"
#include "gnugo/utils/random.h"
#include "alphabeta.h"

#define WORST_SCORE -1000000000

int alpha_beta_search(int pos, int color, int depth, int alpha, int beta)
{
  int best_score, best_move, score;
  int i, j, move, other_color;
  //int move_list[depth];
  if(board[pos]==EMPTY) {
    return -1;
  }
  if(depth==0) {
    return 0;
  }
  best_score = WORST_SCORE;
  best_move = PASS_MOVE;
  other_color = OTHER_COLOR(color);
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      move = POS(i, j);
      if(trymove(move, color, NULL, NO_MOVE)) {
        score = alpha_beta_search(pos, other_color, depth-1, -beta, -alpha);
        popgo();
        score = -score;
        if(score > best_score) {
          best_score = score;
          if(score >= alpha) {
            alpha = score;
            if(score >= beta) {
              i = j = board_size; // jump out all loops
              break;
            }
          }
        }
      }
    }
  }
  if(best_score==WORST_SCORE) {
    best_score = 0;
  }
  return best_score;
}


int alpha_beta_search_random(int pos, int color, int depth, int alpha, int beta, int limit)
{
  int best_score, best_move, score;
  int i, j, move, other_color;
  int move_list[board_size*board_size];
  int move_list_index = 0;
  int current_limit = limit;
  //int move_list[depth];
  if(board[pos]==EMPTY) {
    return -1;
  }
#if 0
  if(depth==0) {
    return 0;
  }
#endif
  if(depth<=0) {
    if(-depth > 2* board_size * board_size) {
      return 0;
    }
    current_limit = limit = RAND_FACTOR;
  }
  best_score = WORST_SCORE;
  best_move = PASS_MOVE;
  other_color = OTHER_COLOR(color);
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      move = POS(i, j);
      if(is_legal(move, color)) {
        int ok, has_color, has_other_color, k;
        ok = FALSE;
        has_color = has_other_color = FALSE;
        for (k = 0; k < 4; k++) {
          int neighbor_pos = move + delta[k];
          int neighbor = board[neighbor_pos];
          if(neighbor==EMPTY) {
            ok = TRUE;
            break;
          } else if(neighbor==color) {
            if(has_other_color || countlib(neighbor_pos)==1) {
              ok = TRUE;
              break;
            }
            has_color = TRUE;
          } else if(neighbor==other_color) {
            if(has_color || countlib(neighbor_pos)==1) {
              ok = TRUE;
              break;
            }
            has_other_color = TRUE;
          }
        }
        if(ok) {
          move_list[move_list_index++] = move;
        }
      }
    }
  }
  while(move_list_index) {
    if(current_limit>=RAND_FACTOR || current_limit > gg_rand()%RAND_FACTOR) {
      int no = gg_rand() % move_list_index;
      move = move_list[no];
      move_list[no] = move_list[--move_list_index];
      current_limit -= RAND_FACTOR;
    } else {
      break;
    }
    if(trymove(move, color, NULL, NO_MOVE)) {
      score = alpha_beta_search_random(pos, other_color, depth-1, -beta, -alpha, limit);
      popgo();
      score = -score;
      if(score > best_score) {
        best_score = score;
        if(score >= alpha) {
          alpha = score;
          if(score >= beta) {
            break;
          }
        }
      }
    }
  }
  if(best_score==WORST_SCORE) {
    best_score = 0;
  }
  return best_score;
}
