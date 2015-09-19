#!/bin/sh

n=$1
text=$2

if [ $# -ne 2 ]
then
   echo "Usage: ./echon.sh <number of lines> <string>"
   exit 1
fi

if ! [[ $n =~ ^[0-9]+$ ]]
then
   echo "./echon.sh: argument 1 must be a non-negative integer"
   exit 1
fi

while [ $n -ne 0 ]
do
      echo $text
      n=$(( $n - 1))
done
exit 0
