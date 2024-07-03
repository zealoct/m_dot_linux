#!/bin/bash

serfix="h c cpp"

if [ $# -ge 1 ]; then
    serfix=$1
    for ((i=2;i<=$@;i++)); do
        serfix=$serfix" "${$i}
    done
fi

for i in $serfix; do
    echo "Adding *.${i} ..."
    files=$(find ./ -name "*.${i}")
    for file in $files; do
        echo "    $file"
        git add $file
    done
done
