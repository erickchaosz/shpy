#!/bin/bash

#echo for in do if else elif fi done

if 
test 1 = 3
then
  echo aa
fi
 
for file in 1 2 3
do 
for num in 3 2 1
do 
if test $num = 3 
then
echo $num
else
echo $file 
fi 
done
done

echo hello world

a=erick
echo my name is $a
pwd
for file in *
do
echo $file
done
echo 'hello' aa
      echo aa
      ls -l '/dev/null'
      echo aa         bb
cd /tmp
expr 1 '*' 1 % 4
echo
echo             "aa"

start=$1
finish=$2

number=$start
while test $number -le $finish
do
    echo $number
    number=`expr $number + 1`  # increment number
done
