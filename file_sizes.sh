#!/bin/sh

small="Small files:"
medium="Medium-sized files:"
large="Large files:"

for file in `ls`
do
  if [ `wc -l < $file` -lt 10 ]
  then
    small="$small $file"
  elif [ `wc -l < $file` -lt 100 ]
  then
    medium="$medium $file"
  else
    large="$large $file"
  fi
done

echo $small
echo $medium
echo $large
