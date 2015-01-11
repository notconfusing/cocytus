#!/bin/bash

python cocytus-input.py &
#rqworker changes &> rq.log &
python cocytus-output.py &
#python cocytus-client.py &> client.log &
