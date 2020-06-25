#!/bin/bash

FILES=$1

echo "k,c,q,mult,TP,FP,FN,P,R,secs,ram"
for f in $@
do
    timefn=${f/results.csv/time}
    k=$(echo $f | cut -d'.' -f2 | cut -c2-)
    c=$(echo $f | cut -d'.' -f3,4 | cut -c2-)
    q=$(echo $f | cut -d'.' -f5 | cut -c2-)
    s=$(echo $f | cut -d'.' -f6)
    t=$(grep wall $timefn | cut -d' ' -f8 | awk -F: '{ if (NF == 1) {print $NF} else if (NF == 2) {print $1 * 60 + $2} else if (NF==3) {print $1 * 3600 + $2 * 60 + $3} }')
    ram=$(grep Maximum $timefn | cut -d' ' -f6)
    echo $k,$c,$q,$s,$(tail -1 ${f} | sed 's/\t/,/g'),$t,$((ram/1024/1024))
done
