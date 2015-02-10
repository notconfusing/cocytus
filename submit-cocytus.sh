#!/bin/bash
#submit the input
#take burst mode off the commandline
for n in {input,output}
do
    jsub -N "cocytus-$n" -mem 1g -e /data/project/cocytus/logs -o /data/project/cocytus/logs -continuous /data/project/cocytus/c-env/bin/python /data/project/cocytus/workspace/cocytus-$n.py 
done
#launch somes workerds on changes
for worker in {changes,failed}
do
    for i in {1..4}
    do
	jsub -N "$worker$i" -mem 320m -e /data/project/cocytus/logs -o /data/project/cocytus/logs -continuous /data/project/cocytus/c-env/bin/rqworker -H tools-redis $worker
    done
done

#-cwd /data/project/cocytus/workspace
