#!/bin/bash
#submit the input
#take burst mode off the commandline

EMAIL=di.franco@gmail.com

for n in {input,output}
do
    jstart -m ae -N "cocytus-$n" -mem 2g -e /data/project/cocytus/logs -o /data/project/cocytus/logs -continuous /data/project/cocytus/c-env/bin/python /data/project/cocytus/workspace/cocytus-$n.py 
done
#launch somes workers on changes
for worker in {changes,failed}
do
    for i in {1..4}
    do
	jstart -m ae -N "$worker$i" -mem 2g -e /data/project/cocytus/logs -o /data/project/cocytus/logs /data/project/cocytus/c-env/bin/rqworker -H tools-redis $worker
    done
done

#-cwd /data/project/cocytus/workspace
