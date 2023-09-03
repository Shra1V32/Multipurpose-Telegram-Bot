#!/bin/bash
k=$(file $1)

if [[ $k == *'PDF document'* ]]; then
    file_prefix="$(echo $1 | cut -f2 -d/ | cut -f1-2 -d.)"
    pdftoppm -png "$1" $file_prefix
    printf "$(ls $file_prefix*)"
else
    printf "False"
fi
