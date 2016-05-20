#include "gnugo/engine/board.h"
#include "gnugo/utils/random.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "montecarlo.h"
#include "patterns.h"

int black_available[BOARDSIZE*2];
int black_available_count = 0;
int white_available[BOARDSIZE*2];
int white_available_count = 0;

int capture_goal = -1;

#define MAX_MONTE_CARLO_STACK MAXSTACK - 3

void init_available()
{
  int i, j, pos;
  black_available_count = white_available_count = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      if (BOARD(i, j) == EMPTY) {
        pos = POS(i, j);
        black_available[black_available_count++] = pos;
        white_available[white_available_count++] = pos;
      }
    }
  }
}

int play_fully_random_move(int color)
{
  int ind, pos;
  int *available_count;
  int *available;
  if(color==BLACK) {
    available = black_available;
    available_count = &black_available_count;
  } else {
    available = white_available;
    available_count = &white_available_count;
  }
  while(*available_count) {
    ind = gg_rand() % (*available_count + 1);
    if(ind==*available_count) {
      return PASS_MOVE;
      break;
    }
    pos = available[ind];
    available[ind] = available[*available_count - 1];
    (*available_count)--;

    Intersection former_values[4];
    int k;
    for (k = 0; k < 4; k++) {
      int neighbor = pos + delta[k];
      former_values[k] = board[neighbor];
    }
    if(trymove(pos, color, NULL, NO_MOVE)) {
      for (k = 0; k < 4; k++) {
        int neighbor = pos + delta[k];
        if(former_values[k] != board[neighbor]) {
          // probably slow on big board (on 9x9 board its 1.4x slower)
          init_available();
          break;
        }
      }
      // simple_showboard(stdout);printf("\n\n");
      return pos;
    }
  }
  return PASS_MOVE;
}

int play_brown_random_move(int color)
{
  /* play brown random move:
     don't play into single space eyes unless atari */
  int i, j;
  int ind, pos;
  int k;
  int ok, has_color, has_other_color;
  int other_color = OTHER_COLOR(color);
  int available_count;
  int available[board_size*board_size];
  available_count = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      if (BOARD(i, j) == EMPTY) {
        pos = POS(i, j);
        available[available_count++] = -pos;
      }
    }
  }
  
  int rejection_count = 0;
  while(available_count && rejection_count < 100) {
    ind = gg_rand() % available_count;
    pos = available[ind];
    if(pos < 0) {
      pos = -pos;
      ok = FALSE;
      has_color = has_other_color = FALSE;
      for (k = 0; k < 4; k++) {
        int neighbor_pos = pos + delta[k];
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
      if(!ok) {
        available[ind] = available[available_count - 1];
        available_count--;
        continue;
      }
      available[ind] = pos;
    }
    //printf("ok: %f %f\n", drand, score);
    available[ind] = available[available_count - 1];
    available_count--;

    if(trymove(pos, color, NULL, NO_MOVE)) {
      //simple_showboard(stdout);printf("\n\n");
      return pos;
    }
  }
  return PASS_MOVE;
}

float shape_score(stone_count, liberties_count)
{
  return stone_count * liberties_count / (stone_count*2+2.0);
}

float liberty_score_move(int move, int color)
{
  int i, k;
  int pos, stone;
  float old_score = 0.0;
  float new_score = 0.0;
  int lib_count = -1, old_liberty_count;
  int save_count = 0;
  int stone_count = 1, old_stone_count;
  int captured_stones_count = 0;
  int blocks_seen[4];
  int origin;
  for(k = 0; k < 4; k++) {
    blocks_seen[k] = -1;
  }
  
  for(i = 0; i < 4; i++) {
    pos = move + delta[i];
    stone = board[pos];
    if(stone==GRAY) {
      continue;
    }
    if(stone==EMPTY) {
      lib_count++;
      continue;
    }
    origin = find_origin(pos);
    // origin seen?
    for(k = 0; k < 4; k++) {
      if(blocks_seen[k]==origin) {
        break;
      }
    }
    if(k < 4) {
      continue;
    }
    old_stone_count = countstones(pos);
    old_liberty_count = countlib(pos);
    if(stone==color) {
      stone_count += old_stone_count;
      if(old_liberty_count==1) {
        save_count += old_stone_count;
      }
      lib_count += old_liberty_count;
      old_score = old_score + shape_score(old_stone_count, old_liberty_count);
    } else { // opposite color
      switch(old_liberty_count) {
      case 1:
        captured_stones_count += old_stone_count;
        break;
      case 2:
        new_score += 0.3;
        break;
      case 3:
        new_score += 0.2;
        break;
      case 4:
        new_score += 0.1;
      }
      old_score = old_score - shape_score(old_stone_count, old_liberty_count);
      new_score = new_score - shape_score(old_stone_count, old_liberty_count-1);
    }
  }
  lib_count += captured_stones_count;
  new_score += shape_score(stone_count, lib_count);
  new_score += save_count;
  new_score += captured_stones_count;
  if(save_count) {
    new_score += 1.5;
  }
  if(is_self_atari(move, color)) {
    new_score -= stone_count;
  }
  return new_score - old_score;
}

float score2probability(float score)
{
  /*
     > 0 -> 0.5..1.0
     ==0 -> 0.5
     < 0 -> 0..0.5
   */
  if(score==0.0) {
    return 0.5;
  }
  if(score > 0.0) {
    return score / (score + 0.5) / 2.0 + 0.5;
  }
  // score < 0.0
  score = -score;
  return 0.5 - score / (score + 0.5) / 2.0;
}

int play_liberty_shape_random_move(int color)
{
  /* play random move according to liberty shape score (like weakbot50k)
   */
  int i, j;
  int ind, pos;
  int k;
  int ok, has_color, has_other_color;
  int other_color = OTHER_COLOR(color);
  int available_count;
  int available[board_size*board_size];
  double available_score[board_size*board_size];
  double score;
#define RETURN_BEST FALSE
#if RETURN_BEST
  simple_showboard(stdout);printf("\n\n");
  double best_score = WORST_SCORE;
  int best_move = PASS_MOVE;
#endif
  available_count = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      if (BOARD(i, j) == EMPTY) {
        pos = POS(i, j);
        available[available_count] = -pos;
        available_score[available_count++] = -1;
#if RETURN_BEST
        score = liberty_score_move(pos, color) + gg_drand()/1000.0;
        mprintf("%m: %f", i, j, score);
        if(score > best_score) {
          if(is_legal(pos, color)) {
            printf(" new best");
            best_score = score;
            best_move = pos;
          }
        }
        printf("\n");
#endif
      }
    }
  }
#if RETURN_BEST
  if(best_move!=PASS_MOVE) {
    mprintf("selected move: %m: %f\n", I(best_move), J(best_move), best_score);
    trymove(best_move, color, NULL, NO_MOVE);
    return best_move;
  }
  return PASS_MOVE;
#endif
  
  int rejection_count = 0;
  while(available_count && rejection_count < 100) {
    double drand = gg_drand();
    if(drand < 0.1 / available_count) { // give pass a chance, for example seki needs this
      return PASS_MOVE;
    }
    ind = gg_rand() % available_count;
    pos = available[ind];
    if(pos < 0) {
      pos = -pos;
      ok = FALSE;
      has_color = has_other_color = FALSE;
      for (k = 0; k < 4; k++) {
        int neighbor_pos = pos + delta[k];
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
      if(!ok) {
        available[ind] = available[available_count - 1];
        available_score[ind] = available_score[available_count - 1];
        available_count--;
        continue;
      }
      available[ind] = pos;
    }
    score = available_score[ind];
    if(score < 0) {
      score = liberty_score_move(pos, color);
      score = score2probability(score);
      available_score[ind] = score;
    }
    drand = gg_drand();
    if(drand > score) {
      rejection_count++;
      //printf("rejected: %f %f\n", drand, score);
      continue;
    }
    //printf("ok: %f %f\n", drand, score);
    available[ind] = available[available_count - 1];
    available_score[ind] = available_score[available_count - 1];
    available_count--;

    if(trymove(pos, color, NULL, NO_MOVE)) {
      //simple_showboard(stdout);printf("\n\n");
      return pos;
    }
  }
  return PASS_MOVE;
}

int play_best_liberty_shape_random_move(int color)
{
  /* play random move according to liberty shape score (like weakbot50k)
   */
  int i, j;
  int ind, pos;
  int k;
  int ok, has_color, has_other_color;
  int other_color = OTHER_COLOR(color);
  int available_count;
  int available[board_size*board_size];
  double available_score[board_size*board_size];
  double score;
  //simple_showboard(stdout);printf("\n\n");
  double best_score = WORST_SCORE;
  int best_move = PASS_MOVE;
  available_count = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      if (BOARD(i, j) == EMPTY) {
        pos = POS(i, j);
        ok = FALSE;
        has_color = has_other_color = FALSE;
        for (k = 0; k < 4; k++) {
          int neighbor_pos = pos + delta[k];
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
          available[available_count] = pos;
          score = liberty_score_move(pos, color) + gg_drand()/1000.0;
          score = score2probability(score);
          available_score[available_count++] = score;
          //mprintf("%m: %f", i, j, score);
          if(score > best_score) {
            if(is_legal(pos, color)) {
              //printf(" new best");
              best_score = score;
              best_move = pos;
            }
          }
          //printf("\n");
        }
      }
    }
  }
  if(best_move!=PASS_MOVE) {
    //mprintf("selected move: %m: %f\n", I(best_move), J(best_move), best_score);
    if(gg_drand() < best_score) {
      trymove(best_move, color, NULL, NO_MOVE);
      return best_move;
    }
  }
  //mprintf("did not select move: %m: %f\n", I(best_move), J(best_move), best_score);
  
  int rejection_count = 0;
  while(available_count && rejection_count < 100) {
    ind = gg_rand() % available_count;
    pos = available[ind];
    score = available_score[ind];
    double drand = gg_drand();
    if(drand > score) {
      rejection_count++;
      //printf("rejected: %f %f\n", drand, score);
      continue;
    }
    //printf("ok: %f %f\n", drand, score);
    available[ind] = available[available_count - 1];
    available_score[ind] = available_score[available_count - 1];
    available_count--;

    if(trymove(pos, color, NULL, NO_MOVE)) {
      //simple_showboard(stdout);printf("\n\n");
      return pos;
    }
  }
  return PASS_MOVE;
}


#define FUDGE 10.0
int play_pattern_random_move(int color)
{
  /* play random move according to win frequences:
     if win frequences are 0.8 0.5 0.2
     
   */
  int i, j;
  int ind, pos;
  int k;
  int ok, has_color, has_other_color;
  int other_color = OTHER_COLOR(color);
  int available_count;
  int available[board_size*board_size];
  double available_score[board_size*board_size];
  double score;
  available_count = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      if (BOARD(i, j) == EMPTY) {
        pos = POS(i, j);
        available[available_count] = -pos;
        available_score[available_count++] = -1;
      }
    }
  }
  
  int rejection_count = 0;
  while(available_count && rejection_count < 100) {
    ind = gg_rand() % available_count;
    pos = available[ind];
    if(pos < 0) {
      pos = -pos;
      ok = FALSE;
      has_color = has_other_color = FALSE;
      for (k = 0; k < 4; k++) {
        int neighbor_pos = pos + delta[k];
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
      if(!ok) {
        available[ind] = available[available_count - 1];
        available_score[ind] = available_score[available_count - 1];
        available_count--;
        continue;
      }
      available[ind] = pos;
    }
    score = available_score[ind];
    if(score < 0) {
      PatternResult *node = get_pattern_result_table(pos, color);
      if(node) {
        score = (node->win_count_move + FUDGE) / (node->win_count_move + node->lost_count_move + FUDGE);
      } else {
        score = 0.5;
      }
      available_score[ind] = score;
    }
    double drand = gg_drand();
    if(drand > score) {
      rejection_count++;
      //printf("rejected: %f %f\n", drand, score);
      continue;
    }
    //printf("ok: %f %f\n", drand, score);
    available[ind] = available[available_count - 1];
    available_score[ind] = available_score[available_count - 1];
    available_count--;

    if(trymove(pos, color, NULL, NO_MOVE)) {
      //simple_showboard(stdout);printf("\n\n");
      return pos;
    }
  }
  return PASS_MOVE;
}

#if COMPLETELY_RANDOM
#define play_random_move play_fully_random_move

#elif BROWN_RANDOM
#define play_random_move play_brown_random_move

#elif LIBERTY_SHAPE_RANDOM
#define play_random_move play_liberty_shape_random_move

#elif BEST_LIBERTY_SHAPE_RANDOM
#define play_random_move play_best_liberty_shape_random_move

#else // PATTERN_RANDOM
#define play_random_move play_pattern_random_move

#endif


int play_random_game(int color)
{
  int count = 0;
  int move, previous_move;
  int tmp_color;
#define DUMP_SGF FALSE
#if DUMP_SGF
  SGFTree gtp_sgftree;
  sgffile_begindump(&gtp_sgftree);
#endif

  move = -1;
  init_available();
  previous_move = -1;
  move = -2;
  //check for preceeding double passes
  if(stackp >= 1) {
    get_move_from_stack(stackp - 1, &move, &tmp_color);
  }
  if(stackp >= 2) {
    get_move_from_stack(stackp - 2, &previous_move, &tmp_color);
  }
  while(stackp < MAX_MONTE_CARLO_STACK && move!=previous_move) {
    previous_move = move;
    if(capture_goal>=0) {
      if(board[capture_goal]==EMPTY) {
        break;
      }
      if(countlib(capture_goal)==1 && board[capture_goal]==OTHER_COLOR(color)) {
        int libs[1];
        findlib(capture_goal, 1, libs);
        if(trymove(libs[0], color, NULL, NO_MOVE)) {
          count++;
          break;
        }
      }
    }
#if 1
    move =  play_random_move(color);
#else // test random players against each other
    if(color==WHITE) {
      move = play_best_liberty_shape_random_move(color);
    } else {
      move = play_brown_random_move(color);
    }
#endif
    if(move!=PASS_MOVE) {
      count++;
    } //else {
    //  if(move==previous_move) {
    //    break;
    //  }
    //}
    color = OTHER_COLOR(color);
  }
#if DUMP_SGF
  printf("saving to out.sgf\n");
  sgffile_enddump("out.sgf");
#endif
  return count;
}

void undo_game(int moves)
{
  while(moves) {
    popgo();
    moves--;
  }
}

void undo_learn_game(int moves, int start_color, int win_count, int lost_count)
{
  int color, move;
  //printf("start undo\n");
  //dump_stack();
  while(moves) {
    get_move_from_stack(stackp-1, &move, &color);
    popgo();
#if LEARN_PATTERNS
/* if won and other random move also wins: 1, 1
         if lost and other random move also loses: 0, 0
         if won, but other random move loses: 1, 0
         if lost, but other random move wins: 0, 1
     */
    //printf("%i\n", stackp);
    int random_length = play_random_game(color);
    double random_score = score_board();
    if(color!=BLACK) {
      random_score = -random_score;
    }
    undo_game(random_length);
    int win2;
    int win, lost;
    if(random_score > 0) {
      win2 = 1;
    } else {
      win2 = 0;
    }
    if(win_count) { //win_count==1, lost_count==0
      if(win2) { //win, win
        win = lost = 1;
      } else { //win, lost
        win = 1;
        lost = 0;
      }
    } else { //win_count==0, lost_count==1
      if(!win2) { // lost, lost
        win = lost = 0;
      } else { // lost, win
        win = 0;
        lost = 1;
      }
    }
    if(color==start_color) {
      add_pattern_result_table(move, color, win, lost);
    } else {
      add_pattern_result_table(move, color, lost, win);
    }
#endif
    moves--;
  }
  //printf("end undo\n");
}

#if 0 // simple score board
#define USE_LIB1_DEAD_SCORING FALSE
double score_board()
{
  int i, j, k, score = 0;
  double return_score;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      int pos = POS(i, j);
      if(board[pos]==BLACK) {
        if(!USE_LIB1_DEAD_SCORING || countlib(pos)>1) {
          score++;
          //mprintf("+:%m\n", i, j);
        } else {
          score--;
          //mprintf("-:%m\n", i, j);
        }
      } else if(board[pos]==WHITE) {
        if(!USE_LIB1_DEAD_SCORING || countlib(pos)>1) {
          score--;
          //mprintf("-:%m\n", i, j);
        } else {
          score++;
          //mprintf("+:%m\n", i, j);
        }
      } else {
        int all_white = TRUE;
        int all_black = TRUE;
        for (k = 0; k < 4; k++) {
          int neighbor_pos = pos + delta[k];
          int neighbor = board[neighbor_pos];
          if(neighbor==GRAY) {
            // do nothing
          } else if(neighbor==EMPTY) {
            all_white = all_black = FALSE;
          } else if(neighbor==WHITE || (USE_LIB1_DEAD_SCORING && countlib(neighbor_pos)==1)) {
            all_black = FALSE;
          } else if(neighbor==BLACK || (USE_LIB1_DEAD_SCORING && countlib(neighbor_pos)==1)) {
            all_white = FALSE;
          }
        }
        if(all_black) {
          score++;
          //mprintf("+:%m\n", i, j);
        } else if(all_white) {
          score--;
          //mprintf("-:%m\n", i, j);
        }
      }
    }
  }
  /* if komi 7.5:
     score: 7 -> 0 -> -1
     score: 8 -> 1 -> 1

     if komi -7.5:
     score: -7 -> 0 -> 1
     score: -8 -> -1 -> -1
  */
  return_score = score - komi;
#if 0
  score-= (int)komi;
  if(score==0) {
    if(komi > ((int)komi)) {
      score--;
    } else if(komi < ((int)komi)) {
      score++;
    }
  }
#endif
  return return_score;
}

#else // Tromp-Taylor scoring

double score_board()
{
  int i, j, k, score = 0;
  double return_score;
  int mark_count = 1;
  int empty_color[BOARDSIZE];
  memset(empty_color, 0, sizeof(empty_color));
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      int pos = POS(i, j);
      if(board[pos]==BLACK) {
        score++;
      } else if(board[pos]==WHITE) {
        score--;
      }
    }
  }
  while(mark_count) {
    mark_count = 0;
    for (i = 0; i < board_size; i++) {
      for (j = 0; j < board_size; j++) {
        int pos = POS(i, j);
        if(board[pos]==EMPTY) {
          int old_mark = empty_color[pos];
          int new_mark = 0;
          for (k = 0; k < 4; k++) {
            int neighbor_pos = pos + delta[k];
            int neighbor = board[neighbor_pos];
            if(neighbor==GRAY) {
              // do nothing
            } else if(neighbor==EMPTY) {
              new_mark |= empty_color[neighbor_pos];
            } else if(neighbor==WHITE) {
              new_mark |= WHITE;
            } else if(neighbor==BLACK) {
              new_mark |= BLACK;
            }
          }
          if(new_mark!=old_mark) {
            empty_color[pos] = new_mark;
            mark_count++;
          }
        }
      }
    }
  }
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      int pos = POS(i, j);
      if(board[pos]==EMPTY) {
        if(empty_color[pos]==BLACK) {
          score++;
        } else if(empty_color[pos]==WHITE) {
          score--;
        }
      }
    }
  }
  return_score = score - komi;
  return return_score;
}

#endif // Tromp-Taylor scoring

double score_board_color(int color)
{
  double score = score_board();
  if(color!=BLACK) {
    score = -score;
  }
  return score;
}

int score_block_capture(int pos, int color, int side_to_move)
{
  int score;
  if(board[pos]==color) {
    score = 1;
  } else {
    score = -1;
  }
  if(color!=side_to_move) {
    score = -score;
  }
  return score;
}

double uct_score(int pos, int color, int side_to_move)
{
  if(capture_goal>=0) {
    return score_block_capture(pos, color, side_to_move);
  } else {
    return score_board_color(side_to_move);
  }
}

int play_random_capture_game(int pos, int color)
{
  int count = 0;
  int live = TRUE;
  int initial_pos_value = board[pos];
  int move, previous_move;
  move = -1;
  init_available();
  while(stackp < MAXSTACK-2) {
    previous_move = move;
    move =  play_random_move(color);
    if(move!=PASS_MOVE) {
      count++;
      if(board[pos] != initial_pos_value) {
        live = FALSE;
        break;
      }
    } else {
      if(move==previous_move) {
        break;
      }
    }
    color = OTHER_COLOR(color);
  }
  undo_game(count);
  return live;
}


ResultTable result_table;
static Hash_data color_hash[BLACK + 1];
#define MAX_PASS_HASH_COUNT 2
static Hash_data pass_count_hash[MAX_PASS_HASH_COUNT + 1];

void init_result_table()
{
  int num_entries = RESULT_ENTRIES;
  hash_init();
  INIT_ZOBRIST_ARRAY(color_hash);
  INIT_ZOBRIST_ARRAY(pass_count_hash);
  result_table.num_entries = num_entries;
  result_table.entries = malloc(num_entries * sizeof(result_table.entries[0]));
  if(result_table.entries == NULL) {
    perror("Couldn't allocate memory for transposition table. \n");
    exit(1);
  }
  clear_result_table();
}

void clear_result_table()
{
  memset(result_table.entries, 0, result_table.num_entries * sizeof(result_table.entries[0]));
}

void get_result_board_hash(Hash_data *hashval, int color)
{
  *hashval = board_hash;
  int pass_count = 0, move, tmp_color;
  hashdata_xor(*hashval, color_hash[color]);
  if(stackp >= 1) {
    get_move_from_stack(stackp - 1, &move, &tmp_color);
    if(move==PASS_MOVE) {
      pass_count++;
      if(stackp >= 2) {
        get_move_from_stack(stackp - 2, &move, &tmp_color);
        if(move==PASS_MOVE) {
          pass_count++;
        }
      }
    }
  }
  hashdata_xor(*hashval, pass_count_hash[pass_count]);
}

ResultNode *get_result_table(double *win_count, double *lost_count, int color)
{
  Hash_data hashval;
  ResultEntries *entry;
  ResultNode *node;
  int i;
  get_result_board_hash(&hashval, color);
  entry = &result_table.entries[hashdata_remainder(hashval, result_table.num_entries)];
  //printf("get hashval: %li\n", hashval.hashval[0]);
  for(i = 0; i < HASH_LIST_SIZE; i++) {
    if(hashdata_is_equal(hashval, entry->node_lst[i].key)) {
      //printf("get: %i\n", i);
      node = &(entry->node_lst[i]);
      *win_count = node->win_count;
      *lost_count = node->lost_count;
      return node;
    }
  }
  *win_count = 0.0;
  *lost_count = 0.0;
  return NULL;
}

void update_result_table(double win_count, double lost_count, int color)
{
  Hash_data hashval;
  ResultEntries *entry;
  ResultNode *node = NULL;
  int count, best_count = 2000000000;
  int i;
  get_result_board_hash(&hashval, color);
  entry = &result_table.entries[hashdata_remainder(hashval, result_table.num_entries)];
  //printf("update hashval: %li, %li\n", hashval.hashval[0], hashdata_remainder(hashval, result_table.num_entries));
  for(i = 0; i < HASH_LIST_SIZE; i++) {
    // if found previous one, use that
    if(hashdata_is_equal(hashval, entry->node_lst[i].key)) {
      //printf("update: found: %i\n", i);
      node = &(entry->node_lst[i]);
      break;
    } else {
      // replace least used one
      count = entry->node_lst[i].win_count + entry->node_lst[i].lost_count;
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
  node->key = hashval;
  node->win_count = win_count;
  node->lost_count = lost_count;
}

int list_board_and_pass(int *move_list) 
{
  int move_list_max = 0;
  int i, j;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      move_list[move_list_max++] = POS(i, j);
    }
  }
  move_list[move_list_max++] = PASS_MOVE;
  return move_list_max;
}

int uct_top_win_ratio_move(int color, int *best_move, double *result_win_count, double *result_lost_count)
{
  float score;
  float best_score = -1.0;
  double win_count, lost_count;
  int i;
  ResultNode *node;
  int other_color = OTHER_COLOR(color);
  int move_list[board_size*board_size + 1];
  int move_list_max;
  int move;
  int total_count, last_total_count = 0;
  move_list_max = list_board_and_pass(move_list);
  for(i = 0; i < move_list_max; i++) {
    move = move_list[i];
    if(trymove(move, color, NULL, NO_MOVE)) {
      node = get_result_table(&lost_count, &win_count, other_color);
      if(node) {
        total_count = win_count + lost_count;
        score = (float)win_count / (float)total_count;
        if(score >= best_score) {
          if(score > best_score || total_count > last_total_count) {
            best_score = score;
            *best_move = move;
            *result_win_count = win_count;
            *result_lost_count = lost_count;
            last_total_count = total_count;
          }
        }
      }
      popgo();
    }
  }
  return best_score >= 0.0;
}

double area_score_as_lost(double score)
{
  if(score < 0) {
    score = -score;
  }
  score = sqrt(score);
  score = 1.0 + board_size - score;
  if(score < 0) {
    return 0.0;
  }
  return score * AREA_SCORE_FACTOR;
}

double area_and_length_score_as_lost(double score, int white_length, int black_length, int color)
{
  double area_score = area_score_as_lost(score);
  double length_score;
  if(color==BLACK) {
    length_score = sqrt(black_length);
  } else {
    length_score = sqrt(white_length);
  }
  length_score *= GAME_LENGTH_SCORE_FACTOR;
  return area_score + length_score;
  //return area_score;
}

double area_score_as_won(double score)
{
  if(score < 0) {
    score = -score;
  }
  score = sqrt(score);
  return score * AREA_SCORE_FACTOR;
}

double area_and_length_score_as_won(double score, int white_length, int black_length, int color)
{
  double area_score = area_score_as_won(score);
  double length_score;
  if(color==BLACK) {
    length_score = sqrt(black_length);
  } else {
    length_score = sqrt(white_length);
  }
  length_score = board_size - length_score;
  if(length_score < 0) {
    length_score = 0.0;
  }
  length_score *= GAME_LENGTH_SCORE_FACTOR;
  //return area_score + length_score;
  return area_score;
}

void get_game_length(int count, int *white_length, int *black_length)
{
  int i, color, move;
  *white_length = *black_length = 0;
  for(i = 0; i < count; i++) {
    get_move_from_stack(stackp - 1 -i, &move, &color);
    if(move!=PASS_MOVE) {
      if(color==BLACK) {
        (*black_length)++;
      } else {
        (*white_length)++;
      }
    }
  }
}

void show_n_last_moves(int count)
{
  int i, color, move;
  int mi, mj;
  for(i = count; i > 0; i--) {
    get_move_from_stack(stackp - i, &move, &color);
    mi = I(move);
    mj = J(move);
    mprintf("%o%C:%m ", color, mi, mj);
  }
  printf("\n");
}

void uct_game(int block_pos, int color0)
{
  int i;
  int uct_flag = TRUE;
  int count = 0;
  double win_count, lost_count;
  // SGFTree gtp_sgftree;
  // sgffile_begindump(&gtp_sgftree);
  int block_color = GRAY;
  int color = color0;
  ResultNode *node;
  double score = 0.0;
  double random_score = 0.0;
  int white_length = 0, black_length = 0;
  int move_list[board_size*board_size + 1];
  int move_list_max;
  int print_flag = FALSE;
  int print_flag2 = FALSE;
  move_list_max = list_board_and_pass(move_list);
  capture_goal = block_pos;
  if(capture_goal>=0) {
    block_color = board[block_pos];
    ASSERT1(IS_STONE(block_color), block_pos);
  }

  //printf("UCT: start\n");
  //dump_stack();
  while(uct_flag && stackp < MAX_MONTE_CARLO_STACK) {
    int other_color;
    double move_win_count, move_lost_count;
    int move, best_move = NO_MOVE;
    ResultNode *node, *move_node;
    double best_score = WORST_SCORE;
    double v, t, n;
    node = get_result_table(&win_count, &lost_count, color);
    t = win_count + lost_count;
    if(node) {
      if(capture_goal>=0 && board[capture_goal]==EMPTY) {
        //print_flag = TRUE;
        //printf("Capture made\n");
        //simple_showboard(stdout);printf("\n\n");
        random_score = uct_score(block_pos, block_color, color);
        get_game_length(count, &white_length, &black_length);
        if(random_score > 0) {
          node->win_count++;
        } else {
          node->lost_count++;
        }
        break;
      }
      //simple_showboard(stdout);printf("\n\n");
      //printf("%i: node found %f\n", count, t);
      other_color = OTHER_COLOR(color);
      for(i = 0; i < move_list_max; i++) {
        move = move_list[i];
        if(trymove(move, color, NULL, NO_MOVE)) {
          move_node = get_result_table(&move_lost_count, &move_win_count, other_color);
          if(move_node) {
            n = move_win_count + move_lost_count;
            v = move_win_count / n;
            score =   v + sqrt((2*log(t))/(10*n));
            //printf("%i: move found: (%i, %i), (%i+%i) %f %f %f\n", count, i, j,
            //       move_win_count, move_lost_count, n, v, score);
          } else {
            score = 100.0;
          }
          //printf("score: %f ", score);
          score += gg_rand() * 1E-13;
          //printf(" -> %f\n", score);
          popgo();
          if(score > best_score) {
            best_score = score;
            best_move = move;
          }
        }
      }
      if(best_score > WORST_SCORE) {
        int passed_2 = FALSE;
        if(stackp>=1) {
          int last_color, last_move;
          get_move_from_stack(stackp-1, &last_move, &last_color);
          if(last_move==PASS_MOVE && best_move==PASS_MOVE) {
            passed_2 = TRUE;
            //printf("passed_2\n");
          }
        }
        count++;
        trymove(best_move, color, NULL, NO_MOVE);
        if(count==1 && (best_move==0 || best_move==104)) {
          //print_flag2 = TRUE;
        }
        //i = I(best_move); j = J(best_move); mprintf("best move selected: %m %f\n", i, j, best_score);
        color = other_color;
        if(passed_2) {
          random_score = uct_score(block_pos, block_color, color);
          get_game_length(count, &white_length, &black_length);
          if(print_flag2) {
            simple_showboard(stdout);printf("\n\n");
            show_n_last_moves(count);
            printf("%i: %f\n", count, random_score);
          }
          get_result_table(&move_win_count, &move_lost_count, color);
          if(random_score > 0) {
            update_result_table(move_win_count + 1, move_lost_count + area_and_length_score_as_lost(random_score, white_length, black_length, color), color);
            //update_result_table(move_win_count + 1.0 + area_and_length_score_as_won(random_score, white_length, black_length, color), move_lost_count, color);
          } else {
            update_result_table(move_win_count + area_and_length_score_as_lost(random_score, white_length, black_length, color), move_lost_count + 1 , color);
            //update_result_table(move_win_count, move_lost_count + 1.0 + area_and_length_score_as_won(random_score, white_length, black_length, color), color);
          }
          uct_flag = FALSE;
        }
      } else { //pass move is always allowed, so should never go here ...
        ASSERT1(0, NO_MOVE);
      }
    } else {
      //simple_showboard(stdout);printf("\n\n");
      int random_length = play_random_game(color);
      random_score = uct_score(block_pos, block_color, color);
      get_game_length(count + random_length, &white_length, &black_length);
      if(print_flag2) {
        simple_showboard(stdout);printf("\n\n");
        show_n_last_moves(count + random_length);
        printf("%i: random: %i, %f\n", count, random_length, random_score);
      }
      if(random_score > 0) {
        undo_learn_game(random_length, color, 1, 0);
        update_result_table(1, area_and_length_score_as_lost(random_score, white_length, black_length, color), color);
        //update_result_table(1.0 + area_and_length_score_as_won(random_score, white_length, black_length, color), 0.0, color);
      } else {
        undo_learn_game(random_length, color, 0, 1);
        update_result_table(area_and_length_score_as_lost(random_score, white_length, black_length, color), 1 , color);
        //update_result_table(0.0, 1.0 + area_and_length_score_as_won(random_score, white_length, black_length, color), color);
      }
      uct_flag = FALSE;
    }
  }
  // undo game and update counts
  while(count) {
    int move, stack_color;
    get_move_from_stack(stackp-1, &move, &stack_color);
    popgo();
    color = OTHER_COLOR(color);
    ASSERT1(color==stack_color, move);
    count--;
    if(print_flag) {
      simple_showboard(stdout);printf("\n\n");
    }
    random_score = -random_score;

#if USE_PATTERNS
    if(random_score > 0) {
      add_pattern_result_table(move, color, 1, 0);
    } else {
      add_pattern_result_table(move, color, 0, 1);
    }
#endif
    node = get_result_table(&win_count, &lost_count, color);
    if(print_flag) {
      printf("undo: %i, %f", count, random_score);
    }
    if(node) {
      //printf(" found");
      double win0 = node->win_count, lost0 = node->lost_count;
      int i, j;
      if(count==0 && print_flag2) {i = I(move); j = J(move); mprintf("%o?%m", i, j); printf(": %i: %f %f\n", move, node->win_count, node->lost_count);}
      if(random_score > 0) {
        node->win_count += 1.0; // + area_and_length_score_as_won(random_score, white_length, black_length, color);
        node->lost_count += area_and_length_score_as_lost(random_score, white_length, black_length, color);
      } else {
        node->lost_count += 1.0; // + area_and_length_score_as_won(random_score, white_length, black_length, color);
        node->win_count += area_and_length_score_as_lost(random_score, white_length, black_length, color);
      }
      if(count==0 && print_flag2) {i = I(move); j = J(move); mprintf("%o!%m", i, j); printf(": %f %f %f %f\n\n", node->win_count, node->lost_count, node->win_count - win0, node->lost_count - lost0);}
    }
    //printf("\n");
  }
  // sgffile_enddump("out.sgf");
  //printf("UCT: end\n");
  //dump_stack();
}
