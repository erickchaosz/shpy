#!/bin/bash

if true
then echo true
fi

echo aa || ls && echo bb || echo cc && ls
