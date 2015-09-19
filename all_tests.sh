#!/bin/bash
echo hello world

ls -l /dev/null

ls /dev/null

pwd

ls
id
date

echo When old age shall this generation waste,
echo Thou shalt remain, in midst of other woe
echo Than ours, a friend to man, to whom thou sayst,
echo Beauty is truth, truth beauty, - that is all
echo Ye know on earth, and all ye need to know.

a=hello
b=world
echo $a $b

cd /tmp
pwd

for word in Houston 1202 alarm
do
    echo $word
done


for word in Houston 1202 alarm
do
    echo $word
    exit 0
done

for c_file in *.c
do
    echo gcc -c $c_file
done

for n in one two three
do
    read line
    echo Line $n $line
done

echo My first argument is $1
echo My second argument is $2
echo My third argument is $3
echo My fourth argument is $4
echo My fifth argument is $5

if test Andrew = great
then
    echo correct
elif test Andrew = fantastic
then
    echo yes
else
    echo error
fi

if test Andrew = great
then
    echo correct
else
    echo error
fi

echo 'hello world'

echo 'When old age shall this generation waste,'
echo 'Thou shalt remain, in midst of other woe'
echo 'Than ours, a friend to man, to whom thou sayst,'
echo '"Beauty is truth, truth beauty",  -  that is all'
echo 'Ye know on earth, and all ye need to know.'

echo "hello world"

if test -r /dev/null
then
    echo a
fi
if test -r nonexistantfile
then
    echo b
fi

if test -d /dev/null
then
    echo /dev/null
fi
if test -d /dev
then
    echo /dev
fi

echo 1;     echo 3;
     echo 4
for i in 1, 2, 3
do
  echo $i
done

for file in 1 2 3
do
echo $file
done

for file in digit[k-s].sh
do
  echo $file
done

for file in digit?.sh
do
  echo $file
done

a=1
c=4
b=5

echo $c,$a,$b, $c there is no spoon, $b
echo 1; echo 3;

if test Andrew = great
then
    if test I = cool
    then
       echo aye
    elif test you = here
         then
         echo yes
    fi
    echo correct
elif test Erick = great
then
  echo amazing
else
  if test you = cool
then
echo aye
fi
    echo error
fi

if test erick = rocks
   then echo cheers
fi


echo for in do if else elif fi done

if test 1 = 3
then
  echo aa
fi

if
test 2 = 4 
then
echo true
fi

if test -r /dev/null
then
    echo a
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
echo
