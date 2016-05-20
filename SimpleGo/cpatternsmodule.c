#include "Python.h"
#include <stdio.h>

#define TRUE 1
#define FALSE 0

#define EDGE 0
#define EMPTY 1
#define WHITE 2
#define BLACK 3
#define COLOR_NUM 4

char COLOR2CHR[4] = {'-', '.', 'O', 'X'};

#define ONLY_ADJACENT TRUE

#define MAX_PATTERN_SIZE 500

typedef struct _node
{
  char valueFlag;
  char x, y;
  union 
  {
    struct _node ***next;
    long count;
  };
} TreeNode;

int size = 0;
int current_max_pattern_size = 0;

TreeNode root;

typedef struct 
{
  char x, y;
  char color;
} PatternNode;

void printPattern(PatternNode *pattern, int patternSize)
{
  int i;
  for(i = 0; i < patternSize; i++) {
    printf("((%i, %i), '%c'), ", (int)pattern[i].x, (int)pattern[i].y, COLOR2CHR[(int)pattern[i].color]);
  }
  printf("\n");
}

inline int cmpPattern(PatternNode *pattern1, PatternNode *pattern2)
{
  return memcmp(pattern1, pattern2, sizeof(PatternNode));
}

inline void swapPattern(PatternNode *pattern1, PatternNode *pattern2)
{
  PatternNode tmp = *pattern1;
  *pattern1 = *pattern2;
  *pattern2 = tmp;
}

int cmp_pattern(const void *node1, const void *node2)
{
  return cmpPattern((PatternNode*)node1, (PatternNode*)node2);
}

inline void sortPattern(PatternNode *pattern, int patternSize)
{
  switch(patternSize) {
  case 1:
    break;
  case 2:
    if(cmpPattern(pattern, pattern + 1) > 0) {
      swapPattern(pattern, pattern + 1);
    }
    break;
  case 3:
    if(cmpPattern(pattern, pattern + 1) > 0) {
      swapPattern(pattern, pattern + 1);
    }
    if(cmpPattern(pattern + 1, pattern + 2) > 0) {
      swapPattern(pattern + 1, pattern + 2);
      if(cmpPattern(pattern, pattern + 1) > 0) {
        swapPattern(pattern, pattern + 1);
      }
    }
    break;
  case 4:
    /*
      D C B A
       ?   ?
      C D A B
         ?
      C A D B
       ?   ?
      A C B D
         ?
      A B C D
     */
    if(cmpPattern(pattern, pattern + 1) > 0) {
      swapPattern(pattern, pattern + 1);
    }
    if(cmpPattern(pattern + 2, pattern + 3) > 0) {
      swapPattern(pattern + 2, pattern + 3);
    }
    if(cmpPattern(pattern + 1, pattern + 2) > 0) {
      swapPattern(pattern + 1, pattern + 2);
      int seeMiddle = FALSE;
      if(cmpPattern(pattern, pattern + 1) > 0) {
        swapPattern(pattern, pattern + 1);
        seeMiddle = TRUE;
      }
      if(cmpPattern(pattern + 2, pattern + 3) > 0) {
        swapPattern(pattern + 2, pattern + 3);
        seeMiddle = TRUE;
      }
      if(seeMiddle && cmpPattern(pattern + 1, pattern + 2) > 0) {
        swapPattern(pattern + 1, pattern + 2);
      }
    }
    break;
  default:
    qsort(pattern, patternSize, sizeof(*pattern), cmp_pattern);
  }
}

PatternNode *normalize(PatternNode *pattern, int patternSize, int size)
{
  static PatternNode bestPattern[MAX_PATTERN_SIZE];
  PatternNode currentPattern[patternSize];
  int ref, i;
  int min_x, min_y;
  bestPattern[0].x = 127;
  for(ref = 0; ref < 8; ref++) {
    min_x = size + 2;
    min_y = size + 2;
    for(i = 0; i < patternSize; i++) {
      int x, y;
      x = pattern[i].x;
      y = pattern[i].y;
#define REF(newx, newy) currentPattern[i].x = (newx);   \
  currentPattern[i].y = (newy);                     \
  currentPattern[i].color = pattern[i].color;          \
  break;

      switch(ref) {
      case 0: REF(x, y);
      case 1: REF(size+1-x, y);
      case 2: REF(x, size+1-y);
      case 3: REF(size+1-x, size+1-y);
      case 4: REF(y, x);
      case 5: REF(y, size+1-x);
      case 6: REF(size+1-y, x);
      case 7: REF(size+1-y, size+1-x);
      }
      if(currentPattern[i].x < min_x) {
        min_x = currentPattern[i].x;
      }
      if(currentPattern[i].y < min_y) {
        min_y = currentPattern[i].y;
      }
    }
    for(i = 0; i < patternSize; i++) {
      currentPattern[i].x -= min_x;
      currentPattern[i].y -= min_y;
    }
    sortPattern(currentPattern, patternSize);

    int colorSwapFlag = FALSE;
    for(i = 0; i < patternSize; i++) {
      if(!colorSwapFlag) {
        if(currentPattern[i].color==WHITE) {
          break;
        }
        if(currentPattern[i].color==BLACK) {
          colorSwapFlag = TRUE;
        }
      }
      if(colorSwapFlag) {
        switch(currentPattern[i].color) {
        case WHITE: currentPattern[i].color = BLACK; break;
        case BLACK: currentPattern[i].color = WHITE; break;
        }
      }
    }
    
#if 0
    printf("ref:%i\n", ref);
    printPattern(currentPattern, patternSize);
    printPattern(bestPattern, patternSize);
#endif
    if(memcmp(currentPattern, bestPattern, sizeof(currentPattern)) < 0) {
      memcpy(bestPattern, currentPattern, sizeof(currentPattern));
#if 0
      printf("new!\n");
      printPattern(bestPattern, patternSize);
#endif
    }
  }
  return bestPattern;
}

void update_pattern(PatternNode *normalizedPattern, int patternSize, int size)
{
  int childSize = sizeof(TreeNode*) * (size + 2);
  int colorSize = sizeof(TreeNode) * COLOR_NUM;
  TreeNode *node = &root;
  TreeNode **nodeList;
  int i, j;
#if 0
  printPattern(normalizedPattern, patternSize);
#endif
  for(i = 0; i < patternSize; i++) {
    int x, y, color;
    x = normalizedPattern[i].x;
    y = normalizedPattern[i].y;
    color = normalizedPattern[i].color;
    if(node->valueFlag) {
      node->valueFlag = FALSE;
      node->next = malloc(childSize);
      memset(node->next, 0, childSize);
    }
    if(!node->next[x]) {
      node->next[x] = malloc(childSize);
      memset(node->next[x], 0, childSize);
    }
    nodeList = node->next[x];
    if(!nodeList[y]) {
      nodeList[y] = malloc(colorSize);
      memset(nodeList[y], 0, colorSize);
      for(j = 0; j < COLOR_NUM; j++) {
        nodeList[y][j].valueFlag = TRUE;
      }
    }
    node = nodeList[y];
    node = node + color;
    if(node->valueFlag) {
      node->count++;
    }
  }
}

void update(char *goban, int gobanSize, int patternSize, PatternNode *pattern, int patterni)
{
  int ind;
  int x, y, i;
  char color = EMPTY;
  TreeNode *node;
  PatternNode *currentPattern = pattern + patterni;
  PatternNode *normalizedPattern;
  ind = -1;
  for(y = 0; y <= gobanSize + 1; y++) {
    currentPattern->y = y;
    for(x = 0; x <= gobanSize + 1; x++) {
      ind++;
      currentPattern->x = x;
      if(ONLY_ADJACENT && patterni) {
        for(i = 0; i < patterni; i++) {
          int dist_sum = abs(pattern[i].x - x) + abs(pattern[i].y - y);
          if(dist_sum == 1) break;
        }
        if(i == patterni) continue;
      }
      switch(goban[ind]) {
      case '.': color = EMPTY; break;
      case 'X': color = BLACK; break;
      case 'O': color = WHITE; break;
      case '-': color = EDGE; break;
      }
      currentPattern->color = color;
      if(patternSize==1) {
        normalizedPattern = normalize(pattern, patterni + 1, gobanSize);
        for(i = 0; i < patterni; i++) {
          if(cmpPattern(normalizedPattern + i, normalizedPattern + i + 1)==0) {
            break;
          }
        }
        if(i >= patterni) {
          update_pattern(normalizedPattern, patterni + 1, gobanSize);
        }
      } else {
        update(goban, gobanSize, patternSize - 1, pattern, patterni + 1);
      }
    }
  }
}

static PyObject *cpatterns_update(PyObject *self, PyObject *args)
{
  char *goban;
  int gobanStringSize;
  int gobanSize;
  int patternSize;
  PatternNode pattern[MAX_PATTERN_SIZE];
  if(!PyArg_ParseTuple(args, "s#ii", &goban, &gobanStringSize, &gobanSize, &patternSize))
    return NULL;
  if(size==0) {
    size = gobanSize;
    root.valueFlag = TRUE;
  } else if(size != gobanSize) {
    PyErr_SetString(PyExc_ValueError, "goban size doesn't match");
    return NULL;
  }
  if((gobanSize+2) * (gobanSize+2) != gobanStringSize) {
    PyErr_SetString(PyExc_ValueError, "goban string size doesn't match");
    return NULL;
  }
  if(patternSize > MAX_PATTERN_SIZE) {
    PyErr_SetString(PyExc_ValueError, "pattern size too big");
    return NULL;
  }
  if(patternSize > current_max_pattern_size) {
    current_max_pattern_size = patternSize;
  }
  update(goban, gobanSize, patternSize, pattern, 0);
  Py_INCREF(Py_None);
  return Py_None;
}

long totalCount;
long selectedCount;

void dump(PyObject *dict, TreeNode *node0, PatternNode *pattern, int patterni, int size, int countLimit)
{
  TreeNode *node;
  TreeNode **nodeList;
  int x, y, color;
  if(node0->valueFlag) {
    if(!node0->count || patterni < current_max_pattern_size) {
      return;
    }
    printPattern(pattern, patterni);
    printf("%li\n", node0->count);
    totalCount++;
    if(node0->count < countLimit) {
      return;
    }
    selectedCount++;

    PyObject *count = PyInt_FromLong(node0->count);
    PyObject *key = PyTuple_New(patterni);
    if(!count || !key) {
      return;
    }
    
    int i;
    for(i = 0; i < patterni; i++) {
      char colorStr[2];
      colorStr[0] = COLOR2CHR[(int)pattern[i].color];
      colorStr[1] = 0;
      PyObject *info = Py_BuildValue("((ii)s)", (int)pattern[i].x, (int)pattern[i].y, colorStr);;
      PyTuple_SET_ITEM(key, i, info);
    }
    if(PyDict_SetItem(dict, key, count)) return;
  } else {
    for(x = 0; x <= size + 1; x++) {
      if(node0->next[x]) {
        nodeList = node0->next[x];
        for(y = 0; y <= size + 1; y++) {
          node = nodeList[y];
          if(node) {
            for(color = 0; color < COLOR_NUM; color++, node++) {
              pattern[patterni].x = x;
              pattern[patterni].y = y;
              pattern[patterni].color = color;
              dump(dict, node, pattern, patterni + 1, size, countLimit);
            }
          }
        }
      }
    }
  }
}

static PyObject *cpatterns_dump(PyObject *self, PyObject *args)
{
  PyObject *dict;
  TreeNode *node = &root;
  PatternNode pattern[MAX_PATTERN_SIZE];
  int gobanSize;
  int countLimit;
  if(!PyArg_ParseTuple(args, "ii", &gobanSize, &countLimit))
    return NULL;
  dict = PyDict_New();
  if(!dict) {
    return NULL;
  }
  totalCount = selectedCount = 0;
  dump(dict, node, pattern, 0, gobanSize, countLimit);
  printf("all count: %li, selected count: %li\n", totalCount, selectedCount);
  return dict;
}


static PyMethodDef cPatternsMethods[] = {
  {"update",  cpatterns_update, METH_VARARGS},
  {"dump",  cpatterns_dump, METH_VARARGS},
  {NULL,      NULL}        /* Sentinel */
};


void initcpatterns()
{
  (void) Py_InitModule("cpatterns", cPatternsMethods);
}
