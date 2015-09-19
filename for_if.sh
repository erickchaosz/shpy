#!/bin/bash

echo for in do if else elif fi done

if test 1 = 3
then
  echo aa
fi

if
test 2 -eq 4 
then
echo true
fi

if test /dev/null -ot aye.sh
then
echo true
fi

if test $number -gt 100000000 -o  $number -lt -100000000
    then
        echo Terminating because series has become too large
        exit 0
    fi

if test -c /dev/null
then
    echo a
fi

if test -d /dev/null
then
    echo /dev/null
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
echo             "aa"
echo '$@'
echo "$@"
echo
echo 'aa'
echo `echo 1`
number=`echo 2`
