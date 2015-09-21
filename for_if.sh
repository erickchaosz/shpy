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
$((1 '*' 1 % 4))
echo
echo             "aa"


start=$1
finish=$2
a=empty
rm -f $a
echo `echo a`
number=$start
while [[ $number -le $finish ]]
do
    echo $number
    number=`expr $number + 1`  # increment number
    for i in a b c
    do
      if test $i -gt $start 
       then  echo $i
       fi
    done
done
$#
$@
$*
start=13
if test $# -gt 0
then
    start=$1
fi


start=13
if test $# -gt 0
then
    start=$1
fi
i=0
number=$start
file=./tmp.numbers
rm -f $file
while true
do
    if test -r $file
    then
        if fgrep -x -q $number $file
        then
            echo Terminating because series is repeating
            exit 0
        fi
    fi
    #echo $number >>$file
    echo $i $number
    k=`expr $number % 2`
    if test $k -eq 1
    then
        number=`expr 7 '*' $number + 3`
    else
        number=`expr $number / 2`
    fi
     i=`expr $i + 1`
    if test $number -gt 100000000 -o  $number -lt -100000000
    then
        echo Terminating because series has become too large
        exit 0
    fi
done
rm -f $file
pwd

echo -n aaa bb
echo aa bb
