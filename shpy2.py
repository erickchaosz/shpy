#!/usr/bin/python -u 

import sys
import re
import glob
import collections

def tokenize(characters, tokenExprs):
    'Matches regex to characters and returns a collection of tokens'
    pos = 0         #position of the regex match
    tokens = []     #result of the tokenizing
    while pos < len(characters):
        match = None
        for (pattern, tag) in tokenExprs:
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            sys.stderr.write('Illegal character: ' + characters[pos] + '\n')
            sys.exit(1)
        else:
            pos = match.end()  
    return tokens

def findImports(tokens):
    'Find which imports are needed from the tokens and return a set of import items'
    imports = set()
    tagToImports = {
    'SUBPROC' : 'subprocess',
    'CD'      : 'os',
    'SYS'     : 'sys',
    'GLOB'    : 'glob',
    'READ'    : 'sys',
    'ARG'     : 'sys'}
    for text,tag in tokens:
        importItem = tagToImports.get(tag)
        if importItem:
            imports.add(importItem)
    return imports

def findNewLine(text):
    'Return the position of the first new line char'
    match = re.match(r'[^\n]*\n',text)
    pos = 0
    if match:
        pos = match.end() 
    return pos

def addImports(pyExprs, tokens):
    'Add the imports to pyExprs'
    pos = findNewLine(pyExprs)
    importStatements = ''
    imports = findImports(tokens)
    for item in imports:
        importStatements = importStatements + 'import ' + item + '\n'
    pyExprs = pyExprs[:pos] + importStatements + pyExprs[pos:] #add the imports after shebang
    return pyExprs

def shebang(pyExprs, tokens, pos):
    return (pyExprs + '#!/usr/bin/python2.7 -u\n', pos)

def newline(pyExprs, tokens, pos):
    return (pyExprs + '\n', pos)

def echo(pyExprs, tokens, pos):
    pyExprs += 'print '
    pos += 1
    while pos < len(tokens):         #get tokens until newline character
        (word, tag) = tokens[pos]
        if tag == 'NEWLINE':
            break
        else:
            if tag == 'IFSTATEMENT' or tag == 'FI' or tag == 'FORSTATEMENT' or tag == 'DONE':
                tokens[pos] = (word, 'WORD')
            (words, _) = parse([tokens[pos]])
            pyExprs += words
            pyExprs += ', '
            if word[-1] == '\n':
                break
        pos += 1
    return (pyExprs.rstrip(', ') + '\n', pos)

def whitespace(pyExprs, tokens, pos):
    return (pyExprs + ' ', pos)

def word(pyExprs, tokens, pos):
    (words, tag) = tokens[pos]
    return (pyExprs + '\''+ words + '\'', pos)

def quotes(pyExprs, tokens, pos):
    (words, tag) = tokens[pos]
    return (pyExprs + words, pos)    

def subproc(pyExprs, tokens, pos):
    pyExprs += 'subprocess.call([' 
    (subprocess, _) = tokens[pos]
    pyExprs = pyExprs + '\'' + subprocess + '\''
    pos += 1
    while pos < len(tokens):         #get tokens until newline character
        (word, tag) = tokens[pos]
        if tag == 'NEWLINE':
            break
        elif tag == 'WHITESPACE':
            pyExprs += ', '
        else:
            (words, _) = parse([tokens[pos]])
            pyExprs += words
        pos += 1
    pyExprs += '])'
    return (pyExprs, pos-1)

def number(pyExprs, tokens, pos):
    (num, _) = tokens[pos]
    return (pyExprs + num, pos)

def variable(pyExprs, tokens, pos):
    (var, _) = tokens[pos]
    m = re.match(r'\$(\w+)', var)
    var = m.group(1)
    return (pyExprs + var, pos)

def varassignment(pyExprs, tokens, pos):
    (var, _) = tokens[pos]
    m = re.match(r'([^=]+)=', var)
    var = m.group(1)
    pyExprs = pyExprs + var + ' = ' 
    return (pyExprs, pos)

def cd(pyExprs, tokens, pos):
    pos += 1
    (directory, _) = tokens[pos]
    pyExprs = pyExprs + 'os.chdir(\'' + directory + '\')'
    return (pyExprs, pos)

def exitFunc(pyExprs, tokens, pos):
    pos += 1
    (retValue, _) = tokens[pos]
    pyExprs = pyExprs + 'sys.exit(' + retValue + ')'
    return (pyExprs, pos)

def read(pyExprs, tokens, pos):
    pos += 1
    (word, tag) = tokens[pos]
    pyExprs = pyExprs + word + ' = ' + 'sys.stdin.readline().rstrip()'
    return (pyExprs, pos)


def forStatement(pyExprs, tokens, pos):
    numLoop = 0 #Keeps track of how many nested loops there are
    pyExprs += 'for ' 
    pos += 1
    (var, tag) = tokens[pos]
    pyExprs = pyExprs + var + ' in '
    pos += 2
    while pos < len(tokens): #loop until the do statement
        (word, tag) = tokens[pos]
        if tag == 'FORSTATEMENT' and re.match(r'do\s+',word):
            pyExprs = pyExprs.rstrip(', \n')
            pyExprs += ':\n'
            pos += 1
            break
        elif tag == 'WHITESPACE':
            pyExprs += ', '
        else:
            (word, _) = parse([tokens[pos]])
            pyExprs += word
        pos += 1
    numLoop += 1
    forBodyTokens = []
    while numLoop > 0: #adds the body of the loop tokens into the forBodyTokens
        (word, tag) = tokens[pos]
        if re.match(r'for\s+', word):
            numLoop += 1
        elif tag == 'DONE':
            numLoop -= 1
        if numLoop > 0:
            forBodyTokens.append(tokens[pos])
        pos += 1
    (words, _) = parse(forBodyTokens)
    forBodyList = words.split('\n') 
    forBody = ''
    for line in forBodyList: #adds tabs to the body of the loop
        if line:
            forBody = forBody + '\t' + line.lstrip(' ') + '\n'
    return (pyExprs + forBody, pos-1)

def bOPT(pyExprs):
    pass

def cOPT(pyExprs):
    pass

def dOPT(pyExprs):
    #import os.path
    pyExprs = 'os.path.isdir(' + pyExprs.rstrip() + ')'
    return pyExprs

def eOPT(pyExprs):
    pass

def fOPT(pyExprs):
    pass

def gOPT(pyExprs):
    pass

def hOPT(pyExprs):
    pass

def kOPT(pyExprs):
    pass

def nOPT(pyExprs):
    pass

def pOPT(pyExprs):
    pass

def rOPT(pyExprs):
    #import os
    pyExprs = 'os.access(' + pyExprs.rstrip() + ', os.R_OK)'
    return pyExprs

def sOPT(pyExprs):
    pass

def uOPT(pyExprs):
    pass

def wOPT(pyExprs):
    pass

def xOPT(pyExprs):
    pass

def zOPT(pyExprs):
    pass

def LOPT(pyExprs):
    pass

def OOPT(pyExprs):
    pass

def GOPT(pyExprs):
    pass

def SOPT(pyExprs):
    pass

def ntOPT(pyExprs):
    pass

def otOPT(pyExprs):
    pass

def eqOPT(pyExprs):
    pass

def neOPT(pyExprs):
    pass

def gtOPT(pyExprs):
    pass

def geOPT(pyExprs):
    pass

def ltOPT(pyExprs):
    pass

def leOPT(pyExprs):
    pass

def aOPT(pyExprs):
    pass

def oOPT(pyExprs):
    pass

def exOPT(pyExprs):
    pass

def predParse(tokens):
    predOptions = {
        '-b' :  bOPT,
        '-c' :  cOPT,
        '-d' :  dOPT,
        '-e' :  eOPT,
        '-f' :  fOPT,
        '-g' :  gOPT,
        '-h' :  hOPT,
        '-k' :  kOPT,
        '-n' :  nOPT,
        '-p' :  pOPT,
        '-r' :  rOPT,
        '-s' :  sOPT,
        '-u' :  uOPT,
        '-w' :  wOPT,
        '-x' :  xOPT,
        '-z' :  zOPT,
        '-L' :  LOPT,
        '-O' :  OOPT,
        '-G' :  GOPT,
        '-S' :  SOPT,
        '-nt' :  ntOPT,
        '-ot' :  otOPT,
        '-eq' :  eqOPT,
        '-ne' :  neOPT,
        '-gt' :  gtOPT,
        '-ge' :  geOPT,
        '-lt' :  ltOPT,
        '-le' :  leOPT,
        '-a' : aOPT,
        '-o' : oOPT,
        '!'  : exOPT
    }
    pyExprs = ''
    optHandler = None
    pos = 0
    while pos < len(tokens):
        (word, tag) = tokens[pos]
        if tag == 'OPT':
            opt = re.match('\s+(-[\w]+)\s+', word)
            opt = opt.match(1)
            optHandler = predOptions[opt]
        else:
            (words, _) = parse([(word, tag)])
            pyExprs += words
        pos += 1
    if optHandler:
        pass
    return (pyExprs, None)


def test(pyExprs, tokens, pos):
    predOptions = {
        '-b' :  bOPT,
        '-c' :  cOPT,
        '-d' :  dOPT,
        '-e' :  eOPT,
        '-f' :  fOPT,
        '-g' :  gOPT,
        '-h' :  hOPT,
        '-k' :  kOPT,
        '-n' :  nOPT,
        '-p' :  pOPT,
        '-r' :  rOPT,
        '-s' :  sOPT,
        '-u' :  uOPT,
        '-w' :  wOPT,
        '-x' :  xOPT,
        '-z' :  zOPT,
        '-L' :  LOPT,
        '-O' :  OOPT,
        '-G' :  GOPT,
        '-S' :  SOPT,
        '-nt' :  ntOPT,
        '-ot' :  otOPT,
        '-eq' :  eqOPT,
        '-ne' :  neOPT,
        '-gt' :  gtOPT,
        '-ge' :  geOPT,
        '-lt' :  ltOPT,
        '-le' :  leOPT,
        '-a' : aOPT,
        '-o' : oOPT,
        '!'  : exOPT
    }
    #FIX THIS!!
    pos += 1
    predExprs = ''
    optHandler = None
    while pos < len(tokens):
        (word, tag) = tokens[pos]
        if tag == 'OPT':
            opt = re.match('\s+(-[\w]+)\s+', word)
            opt = opt.match(1)
            optHandler = predOptions[opt]
        else:
            (words, _) = parse([tokens[pos]])
            predExprs += words
        pos += 1
    if optHandler:
        predExprs = optHandler(predExprs)
    return (pyExprs + predExprs, pos)

def ifStatement(pyExprs, tokens, pos):
    numIfs = 1 #Keeps track of how many nested ifs there are
    ifBody = []
    while True:
        (word, tag) = tokens[pos]
        if re.match(r'(if|elif)\s+', word):
            pyExprs += word
            pos += 1
            (word, tag) = tokens[pos]
            ifPred = [] #contains the predicate of the if statements
            while True:
                (word, tag) = tokens[pos]
                if re.match(r'then\s+', word) and tag == 'IFSTATEMENT':
                    break
                ifPred.append(tokens[pos])
                pos += 1
            (pred, _) = parse(ifPred)
            pyExprs = pyExprs.rstrip() + ' ' + pred.rstrip() + ':\n'
        elif re.match(r'else\s+', word):
             pyExprs = pyExprs + word.rstrip() + ':\n'
        elif tag == 'FI':
            break

        numIfs = 1
        pos += 1
        ifBody = [] 
        while True:
            (word, tag) = tokens[pos]
            if re.match(r'if\s+',word) and tag == 'IFSTATEMENT':
                numIfs += 1
            elif numIfs == 1 and re.match(r'(elif|else|fi)\s+', word):
                break
            elif numIfs > 1 and tag == 'FI':
                numIfs -= 1
            ifBody.append(tokens[pos])
            pos += 1
        (body, _) = parse(ifBody)            
        ifBodyList = body.split('\n')
        ifBody = ''
        for line in ifBodyList:
            if line:
                ifBody = ifBody + '\t' + line.lstrip(' ') + '\n'
        pyExprs += ifBody
    return (pyExprs, pos)

def done(pyExprs, tokens, pos):
    return (pyExprs, pos)

def glob(pyExprs, tokens, pos):
    (word, _) = tokens[pos]
    globCall = 'sorted(glob.glob(\"' + word + '\"))' 
    return (pyExprs + globCall, pos)

def arg(pyExprs, tokens, pos):
    (word, _) = tokens[pos]
    argIndex = word[1:]
    getArg = 'sys.argv[' + argIndex + ']'
    return (pyExprs + getArg, pos)

def operator(pyExprs, tokens, pos):
    (currOperator, _) = tokens[pos]
    match = re.search(r'(=|>|>=|<|<=|!=|\+|-|\*|\/|%)',currOperator) #remove quotes
    currOperator = match.group(1)
    pyOperator = ''
    if currOperator == '=':
        pyOperator = '=='
    else:
        pyOperator = currOperator
    return (pyExprs + ' ' + pyOperator + ' ', pos)

def comment(pyExprs, tokens, pos):
    (word, _) = tokens[pos]
    return (pyExprs + word, pos)

def expr(pyExprs, tokens, pos):
    pos += 1
    while pos < len(tokens):         #get tokens until newline character
        (word, tag) = tokens[pos]
        if tag == 'NEWLINE':
            break
        else:
            (words, _) = parse([tokens[pos]])
            if tag != 'OPERATOR' and tag != 'WHITESPACE':
                pyExprs = pyExprs + 'int(' + words + ')'
            else:
                pyExprs += words
        pos += 1
    return (pyExprs, pos - 1)

def opt(pyExprs, tokens, pos):
    (word, _) = tokens[pos]
    return (pyExprs + '\'' + word + '\'', pos)

def parse(tokens, pos=0):
    pyExprs = ""
    tagFuncs = {'SHEBANG' : shebang,
                'ECHO'    : echo,
                'NEWLINE' : newline,
                'WHITESPACE' : whitespace,
                'WORD' : word,
                'NUMBER' : number,
                'SINGLE_QUOTE' : quotes,
                'DOUBLE_QUOTES' : quotes,
                'SUBPROC'  : subproc,
                'VARASSIGNMENT'   : varassignment,
                'VARIABLE'   : variable,
                'EXIT'   : exitFunc,
                'READ'  : read,
                'CD'  : cd,
                'FORSTATEMENT' : forStatement,
                'DONE' : done,
                'GLOB' : glob,
                'ARG'  : arg,
                'OPERATOR' : operator,
                'IFSTATEMENT' : ifStatement,
                'COMMENT' : comment,
                'EXPR'   : expr,
                'OPT'   : opt,
                'TEST'  : test}
    while (pos < len(tokens)):
        (words, tag) = tokens[pos]
        handleToken = tagFuncs[tag]
        (pyExprs, pos) = handleToken(pyExprs, tokens, pos)
        pos += 1
    return (pyExprs,pos)

        
inputStr = sys.stdin.read()

tokenExprs = [
(r'\n|;', 'NEWLINE'),
(r'\s+', None),
(r'#![^\n]*\n', 'SHEBANG'),
(r'for\s+', 'FORSTATEMENT'),
(r'in\s+', 'FORSTATEMENT'),
(r'done\s+', 'DONE'),
(r'do\s+', 'FORSTATEMENT'),
(r'if\s+', 'IFSTATEMENT'),
(r'test\s+', 'TEST'),
(r'then\s+', 'IFSTATEMENT'),
(r'elif\s+', 'IFSTATEMENT'),
(r'else\s+', 'IFSTATEMENT'),
(r'fi\s+', 'FI'),
(r'\'[^\']*\'', 'SINGLE_QUOTE'),
(r'\"[^\"]*\"', 'DOUBLE_QUOTES'),
(r'expr', 'EXPR'),
(r'(\w|\/)*\*(\w|\.)*', 'GLOB'),
(r'(\w|\/)*\?(\w|\.)*', 'GLOB'),
(r'(\w|\/)*\[(\w|\.|-)*\](\w|\.)*', 'GLOB'),
(r'-([a-z]|O|L|G|S|nt|ot|eq|ne|gt|ge|lt|le)', 'OPT'),
(r'\$[0-9]+', 'ARG'),
(r'\'*(=|>|>=|<|<=|!=|\+|-|\*|\/|%)\'*\s+', 'OPERATOR'),
(r'cd', 'CD'),
(r'read', 'READ'),
(r'exit', 'EXIT'),
(r'echo', 'ECHO'),
(r'ls', 'SUBPROC'),
(r'pwd', 'SUBPROC'),
(r'id', 'SUBPROC'),
(r'date', 'SUBPROC'),
(r'#[^\n]*\n', 'COMMENT'),
(r'[^= \s]+=', 'VARASSIGNMENT'),
(r'\$\w+', 'VARIABLE'),
(r'[A-Za-z0-9,.\-/_]+', 'WORD')
]

tokens = tokenize(inputStr, tokenExprs)

for token in tokens:
    print token
print

(pyExprs, _) = parse(tokens)

pyExprs = addImports(pyExprs, tokens)

print pyExprs

