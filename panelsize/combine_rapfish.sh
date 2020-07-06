#!/bin/bash

function grep_time {
    fpath=$1
    grep wall $fpath | cut -d' ' -f8 | awk -F: '{ if (NF == 1) {print $NF} else if (NF == 2) {print $1 * 60 + $2} else if (NF==3) {print $1 * 3600 + $2 * 60 + $3} }' | cut -f 1 -d'.'
}

function grep_RAM {
    fpath=$1
    grep Maximum $fpath | cut -d' ' -f6
}

echo "Tool,Run,P,R,time(s),RAM(MB)"
for csv in $@
do
    tool=$(basename $(dirname $csv))
    run=$(basename $csv .res)
    P=$(tail -1 $csv | cut -f 4)
    R=$(tail -1 $csv | cut -f 5)

    itime=$(dirname $csv)/$(basename $csv .res)_index.time
    it=$(grep_time $itime)
    iram=$(grep_RAM $itime)

    mtime=$(dirname $csv)/$(basename $csv .res)_map.time
    mt=$(grep_time $mtime)
    mram=$(grep_RAM $mtime)

    t=$((it+mt))
    ram=$(( iram > mram ? iram : mram ))

    echo $tool,$run,$P,$R,$t,$((ram/1024))
done
