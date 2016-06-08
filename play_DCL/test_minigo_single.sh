#!/bin/bash
#PATH=usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/local/cuda-7.0:/usr/local/cuda-7.0/bin:/usr/lib/jvm/java-7-oracle/bin:/usr/lib/jvm/java-7-oracle/db/bin
#THEANO_FLAGS='device=gpu0'
#KERAS_BACKEND=theano 
CUDA_LAUNCH_BLOCKING=1 THEANO_FLAGS='device=gpu0' python /home/sclab/dclee/minigo/play_gtp.py
