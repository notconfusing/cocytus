#!/bin/bash
#submit the input

EMAIL=di.franco@gmail.com
DIR=/data/project/cocytus
PYTHONPATH=$DIR/c-env/local/lib/python2.7/site-packages
source $DIR/c-env/bin/activate
cd $DIR/workspace

for n in {input,output}
do
    jstart -N "cocytus-$n" -mem 2g -e $DIR/logs -o $DIR/logs\
     -continuous -l release=trusty python $DIR/workspace/cocytus-$n.py
done
#launch somes workers on changes
for worker in {changes,failed}
do
    for i in {1..16}
    do
        jstart -N "$worker$i" -mem 2g -e $DIR/logs -o $DIR/logs\
         -continuous -l release=trusty \
         rqworker --path $DIR/workspace -u http://tools-redis:6379 $worker
    done
done

#-cwd /data/project/cocytus/workspace
