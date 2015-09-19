#!/bin/bash
Andrew=great
if test $Andrew = great
then
    #echo inside inner if
    if test Erick = great
    then
       echo correct
    elif test Erick = fantastic
    then
      echo yes
    else
      echo no
    fi
    echo going out
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
