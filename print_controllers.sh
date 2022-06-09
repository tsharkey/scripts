#/bin/bash

search_dir=$1

if [ -z "$search_dir" ]; then
    echo "Usage: $0 <search_dir>"
    exit 1
fi

for entry in "$search_dir"/*
do
  # print last part of file path and drop file extension
  echo "${entry##*/}" | sed 's/\..*//'
done


