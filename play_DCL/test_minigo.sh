#!/bin/bash
mv 2016* old
mv result/* old
mv g*log old
mv mini*log old

today=`date +%Y%m%d_%H%M%S`

#rm -rf 2016*

mkdir $today

chmod 700 $today

cd $today
#PATH=/home/sclab/anaconda2/bin:/usr/local/cuda-7.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-7-oracle/bin:/usr/lib/jvm/java-7-oracle/db/bin:/usr/lib/jvm/java-7-oracle/jre/bin
#filename=$today
c=0
for ((b=0;b<1;b++))
do
for ((a=0;a<1;a++,c++))
do
	#echo -e "\t" $a
        filename=$today'_'$c
        echo -e "filename=" $filename   
        CUDA_LAUNCH_BLOCKING=1 
        THEANO_FLAGS='device=gpu0'
        KERAS_BACKEND=theano 
	gogui-twogtp -black 'python /home/sclab/dclee/simplego/play_gtp.py' -white 'python /home/sclab/dclee/minigo/play_gtp.py' -size 9 -verbose -xml -auto -sgffile ttt -force -sgffile $filename -games 10 
        #sleep 600
done
sleep 3 
done

echo -e "ended zzzzzzzzz"
