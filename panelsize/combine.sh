#!/bin/bash

echo "Run,P,R,time(s),RAM(MB)"
for csv in $@
do
    run=$(basename $csv .res)
    time=$(dirname $csv)/$(basename $csv .res).time
    P=$(tail -1 $csv | cut -f 4)
    R=$(tail -1 $csv | cut -f 5)
    t=$(grep wall $time | cut -d' ' -f8 | awk -F: '{ if (NF == 1) {print $NF} else if (NF == 2) {print $1 * 60 + $2} else if (NF==3) {print $1 * 3600 + $2 * 60 + $3} }')
    ram=$(grep Maximum $time | cut -d' ' -f6)
    echo $run,$P,$R,$t,$((ram/1024))
done
