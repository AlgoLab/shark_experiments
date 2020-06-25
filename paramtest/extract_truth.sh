#!/bin/bash

gtf=$1
bed=$2

for tidx in $(grep -P "\ttranscript\t" ${gtf} | grep -E -o "ENST[0-9]*")
do
    grep ":${tidx}:" ${bed} || true
done
