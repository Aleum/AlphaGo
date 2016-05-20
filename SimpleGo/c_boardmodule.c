#include "Python.h"
#include "gnugo/engine/board.h"
#include "gnugo/utils/gg_utils.h"
#include "gnugo/utils/random.h"
#include <stdio.h>
#include "montecarlo.h"
#include "alphabeta.h"
#include "patterns.h"

#define PYTHON_POS2C(i, j) POS(board_size - j, i-1)
#define C2_PYTHON_POS_I(pos) (J(pos) + 1)
#define C2_PYTHON_POS_J(pos) (board_size - I(pos))

void init_size(int size)
{
  board_size = size;
  clear_board();
}

static PyObject *cboard_test(PyObject *self, PyObject *args)
{
  int i, j, pos, k, count;
  if(!PyArg_ParseTuple(args, "iii", &i, &j, &count)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  /* printf("%i\n", pos); */
  for(k=0; k<count; k++) {
    if(trymove(pos, BLACK, NULL, NO_MOVE)) {
      /*simple_showboard(stdout);
        printf("\n");*/
      popgo();
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_test_game(PyObject *self, PyObject *args)
{
  int k, count, game_len, total_moves, black_wins;
  double score;
  if(!PyArg_ParseTuple(args, "i", &count)) {
    return NULL;
  }
  total_moves = 0;
  black_wins = 0;
  for(k=0; k<count; k++) {
    game_len = play_random_game(BLACK);
    score = score_board();
    if(score > 0) {
      black_wins++;
    }
    undo_game(game_len);
    total_moves += game_len;
    /* printf("%i\n", game_len); */
  }
  // return PyInt_FromLong(total_moves);
  return PyInt_FromLong(black_wins);
}

static PyObject *cboard_test_block(PyObject *self, PyObject *args)
{
  int i, j, pos, color, k, count, result, block_lives;
  if(!PyArg_ParseTuple(args, "(ii)ii", &i, &j, &color, &count)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  block_lives = 0;
  for(k=0; k<count; k++) {
    result = play_random_capture_game(pos, color);
    if(result) {
      block_lives++;
    }
  }
  return PyInt_FromLong(block_lives);
}

static PyObject *cboard_clear_board(PyObject *self, PyObject *args)
{
  int size;
  if(!PyArg_ParseTuple(args, "i", &size)) {
    return NULL;
  }
  while(stackp) {
    popgo();
  }
  init_size(size);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_make_move(PyObject *self, PyObject *args)
{
  int i, j, color, pos;
  if(!PyArg_ParseTuple(args, "(ii)i", &i, &j, &color)) {
    return NULL;
  }
  if(i==-1) {
    if(trymove(PASS_MOVE, color, NULL, NO_MOVE)) {
      return PyInt_FromLong(1);
    }
    return PyInt_FromLong(0);
  }
  pos = PYTHON_POS2C(i, j);
  if(trymove(pos, color, NULL, NO_MOVE)) {
    return PyInt_FromLong(1);
  }
  return PyInt_FromLong(0);
}

static PyObject *cboard_undo_move(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  popgo();
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_board_as_string(PyObject *self, PyObject *args)
{
  int i, j, ind;
  char board_string[board_size * board_size];
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  ind = 0;
  for (i = 0; i < board_size; i++) {
    for (j = 0; j < board_size; j++) {
      board_string[ind++] = BOARD(i, j);
    }
  }
  return PyString_FromStringAndSize(board_string, ind);
}

static PyObject *cboard_set_random_seed(PyObject *self, PyObject *args)
{
  unsigned int seed;
  if(!PyArg_ParseTuple(args, "i", &seed)) {
    return NULL;
  }
  set_random_seed(seed);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_rand(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  return PyInt_FromLong(gg_urand());
}

static PyObject *cboard_alpha_beta_search(PyObject *self, PyObject *args)
{
  int i, j, color, pos, score, depth, alpha, beta;
  if(!PyArg_ParseTuple(args, "(ii)iiii", &i, &j, &color, &depth, &alpha, &beta)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  score = alpha_beta_search(pos, color, depth, alpha, beta);
  return PyInt_FromLong(score);
}


static PyObject *cboard_alpha_beta_search_random(PyObject *self, PyObject *args)
{
  int i, j, color, pos, score, depth, alpha, beta, limit;
  if(!PyArg_ParseTuple(args, "(ii)iiiii", &i, &j, &color, &depth, &alpha, &beta, &limit)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  score = alpha_beta_search_random(pos, color, depth, alpha, beta, limit);
  return PyInt_FromLong(score);
}

static PyObject *cboard_get_trymove_counter(PyObject *self, PyObject *args)
{
  static long long total_count = 0;
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  total_count += get_trymove_counter();
  reset_trymove_counter();
  return PyLong_FromLongLong(total_count);
}

static PyObject *cboard_simple_showboard(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  simple_showboard(stdout);printf("\n\n");
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *cboard_uct_top_win_ratio_move(PyObject *self, PyObject *args)
{
  int color;
  int i, j;
  int move;
  double win_count, lost_count;
  if(!PyArg_ParseTuple(args, "i", &color)) {
    return NULL;
  }
  if(uct_top_win_ratio_move(color, &move, &win_count, &lost_count)) {
    i = C2_PYTHON_POS_I(move);
    j = C2_PYTHON_POS_J(move);
    return Py_BuildValue("((ii)dd)", i, j, win_count, lost_count);
  } else {
    Py_INCREF(Py_None);
    return Py_None;
  }
}

static PyObject *cboard_uct_game(PyObject *self, PyObject *args)
{
  int count, color, i;
  if(!PyArg_ParseTuple(args, "ii", &color, &count)) {
    return NULL;
  }
  for(i = 0; i < count; i++) {
    uct_game(-1, color);
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_uct_capture(PyObject *self, PyObject *args)
{
  int count, pos, color, i, j;
  if(!PyArg_ParseTuple(args, "(ii)ii", &i, &j, &color, &count)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  for(i = 0; i < count; i++) {
    uct_game(pos, color);
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_get_result_table(PyObject *self, PyObject *args)
{
  int color;
  ResultNode *node;
  double win_count, lost_count;
  if(!PyArg_ParseTuple(args, "i", &color)) {
    return NULL;
  }
  node = get_result_table(&win_count, &lost_count, color);
  if(node) {
    return Py_BuildValue("(dd)", win_count, lost_count);
  } else {
    Py_INCREF(Py_None);
    return Py_None;
  }
}

static PyObject *cboard_clear_result_table(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  clear_result_table();
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cboard_score_board(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  return PyFloat_FromDouble(score_board());
}


static PyObject *cboard_get_pattern_result_table(PyObject *self, PyObject *args)
{
  int i, j, color, pos;
  PatternResult *node;
  if(!PyArg_ParseTuple(args, "(ii)i", &i, &j, &color)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  node = get_pattern_result_table(pos, color);
  if(node) {
    return Py_BuildValue("(ii)", node->win_count_move, node->lost_count_move);
  } else {
    Py_INCREF(Py_None);
    return Py_None;
  }
}

static PyObject *cboard_add_pattern_result_table(PyObject *self, PyObject *args)
{
  int i, j, color, pos, win_count, lost_count;
  if(!PyArg_ParseTuple(args, "(ii)iii", &i, &j, &color, &win_count, &lost_count)) {
    return NULL;
  }
  pos = PYTHON_POS2C(i, j);
  add_pattern_result_table(pos, color, win_count, lost_count);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *cboard_dump_pattern_result_table(PyObject *self, PyObject *args)
{
  char *filename;
  if(!PyArg_ParseTuple(args, "s", &filename)) {
    return NULL;
  }
  return PyInt_FromLong(dump_pattern_result_table(filename));
}

static PyObject *cboard_load_pattern_result_table(PyObject *self, PyObject *args)
{
  char *filename;
  if(!PyArg_ParseTuple(args, "s", &filename)) {
    return NULL;
  }
  return PyInt_FromLong(load_pattern_result_table(filename));
}

static PyObject *cboard_set_komi(PyObject *self, PyObject *args)
{
  if(!PyArg_ParseTuple(args, "f", &komi)) {
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef cBoardMethods[] = {
  {"test",  cboard_test, METH_VARARGS},
  {"test_game",  cboard_test_game, METH_VARARGS},
  {"test_block",  cboard_test_block, METH_VARARGS},
  {"clear_board", cboard_clear_board, METH_VARARGS},
  {"make_move", cboard_make_move, METH_VARARGS},
  {"undo_move", cboard_undo_move, METH_VARARGS},
  {"board_as_string", cboard_board_as_string, METH_VARARGS},
  {"set_random_seed", cboard_set_random_seed, METH_VARARGS},
  {"rand", cboard_rand, METH_VARARGS},
  {"alpha_beta_search", cboard_alpha_beta_search, METH_VARARGS},
  {"alpha_beta_search_random", cboard_alpha_beta_search_random, METH_VARARGS},
  {"get_trymove_counter", cboard_get_trymove_counter, METH_VARARGS},
  {"simple_showboard", cboard_simple_showboard, METH_VARARGS},
  {"uct_game", cboard_uct_game, METH_VARARGS},
  {"uct_capture", cboard_uct_capture, METH_VARARGS},
  {"get_result_table", cboard_get_result_table, METH_VARARGS},
  {"clear_result_table", cboard_clear_result_table, METH_VARARGS},
  {"score_board", cboard_score_board, METH_VARARGS},
  {"get_pattern_result_table", cboard_get_pattern_result_table, METH_VARARGS},
  {"add_pattern_result_table", cboard_add_pattern_result_table, METH_VARARGS},
  {"dump_pattern_result_table", cboard_dump_pattern_result_table, METH_VARARGS},
  {"load_pattern_result_table", cboard_load_pattern_result_table, METH_VARARGS},
  {"set_komi", cboard_set_komi, METH_VARARGS},
  {"uct_top_win_ratio_move", cboard_uct_top_win_ratio_move, METH_VARARGS},
  {NULL,      NULL}        /* Sentinel */
};


void initc_board()
{
  (void) Py_InitModule("c_board", cBoardMethods);
  init_size(9);
  gg_srand(1);
  init_result_table();
  init_pattern_result_table();
  /* init_timers(); */
  /* gnugo_clear_board(board_size); */
}
