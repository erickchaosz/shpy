#!/usr/bin/python2.7 -u
import os
import stat
import subprocess
import re

def loop(pyExprs, tokens, pos):
    numLoop = 0 #Keeps track of how many nested loops there are
    (loopKeyword, _) = tokens[pos]
    pyExprs = pyExprs + loopKeyword + ' '
    pos = nextPos(pos)
    (var, tag) = tokens[pos]
    (isIn, _) = tokens[nextPos(pos)]
    isSubProc = False
    if isIn != 'in':
        loopPred = []

        while True:
            (word, tag) = tokens[pos]
            if tag == 'SUBPROC':
                isSubProc = True
            if word == 'do':
                pos = nextPos(pos)
                break
            loopPred.append(tokens[pos])
            pos = nextPos(pos)
        (pred, _) = parse(loopPred)
        if isSubProc:
            pyExprs += 'not '
        pyExprs += pred.rstrip()

    else:
        pyExprs += var
        pos = nextPos(pos)
        (pyExprs, pos) = inStatement(pyExprs, tokens, pos)
    pyExprs += ':\n'

    numLoop += 1
    loopBodyTokens = []
    while numLoop > 0: #adds the body of the loop tokens into the forBodyTokens
        (word, tag) = tokens[pos]
        if re.match(r'(for|while)', word):
            numLoop += 1
        elif tag == 'DONE':
            numLoop -= 1
        if numLoop > 0:
            loopBodyTokens.append(tokens[pos])
        pos = nextPos(pos)

    (words, _) = parse(loopBodyTokens)
    loopBodyList = words.split('\n') 
    loopBody = ''
    for line in loopBodyList: #adds tabs to the body of the loop
        if line:
            loopBody = loopBody + '\t' + line.lstrip(' ') + '\n'
    return (pyExprs + loopBody, pos-1)


def ifStatement(pyExprs, tokens, pos):
    numIfs = 1 #Keeps track of how many nested ifs there are
    ifBody = []
    while True:
        (word, tag) = tokens[pos]
        if re.match(r'(if|elif)', word):
            pyExprs += word
            pos = nextPos(pos)
            ifPred = [] #contains the predicate of the if statements
            isSubProc = False

            while True:
                (word, tag) = tokens[pos]
                if tag == 'SUBPROC':
                    isSubProc = True
                if tag == 'NEWLINE':
                    pos = nextPos(pos)
                    continue
                if word == 'then':
                    break
                ifPred.append(tokens[pos])
                pos = nextPos(pos)
            (pred, _) = parse(ifPred)
            if isSubProc:
                pyExprs += ' not'
            pyExprs = pyExprs + ' ' + pred + ':\n'
        elif re.match('else', word):
             pyExprs = pyExprs + word + ':\n'
        elif tag == 'FI':
            break

        numIfs = 1
        pos = nextPos(pos)
        ifBody = [] 
        while True:
            (word, tag) = tokens[pos]
            if re.match(r'if', word) and tag == 'IFSTATEMENT':
                numIfs += 1
            elif numIfs == 1 and re.match(r'(elif|else|fi)', word):
                break
            elif numIfs > 1 and tag == 'FI':
                numIfs -= 1
            ifBody.append(tokens[pos])
            pos = nextPos(pos)
        (body, _) = parse(ifBody)            
        ifBodyList = body.split('\n')
        ifBody = ''
        for line in ifBodyList:
            if line:
                ifBody = ifBody + '\t' + line.lstrip(' ') + '\n'
        pyExprs += ifBody
    return (pyExprs, pos)
