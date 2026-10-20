#!/bin/bash

rm report.csv

i=1
DATASET='Human_vital_signs_R.csv'
while [[ 1 ]]; do
    line=`sed $i'q;d' $DATASET`
    echo $line >> report.csv
    echo $line
    i=$(( i + 1 ))
    sleep 1
done

