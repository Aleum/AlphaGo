#!/bin/bash
#PATH=/home/sclab/anaconda2/bin:/usr/local/cuda-7.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-7-oracle/bin:/usr/lib/jvm/java-7-oracle/db/bin:/usr/lib/jvm/java-7-oracle/jre/bin
CUDA_LAUNCH_BLOCKING=1 THEANO_FLAGS='device=gpu1' KERAS_BACKEND=theano python evaluator_aleum.py 50001 &
CUDA_LAUNCH_BLOCKING=1 THEANO_FLAGS='device=gpu2' KERAS_BACKEND=theano python evaluator_aleum.py 50002 &
CUDA_LAUNCH_BLOCKING=1 THEANO_FLAGS='device=gpu3' KERAS_BACKEND=theano python evaluator_aleum.py 50003 &
CUDA_LAUNCH_BLOCKING=1 THEANO_FLAGS='device=gpu0' KERAS_BACKEND=theano python evaluator_aleum.py 50004 &

