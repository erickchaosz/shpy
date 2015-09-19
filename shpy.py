#!/usr/bin/python -u 

import sys
import re
import glob
import collections

def tokenize(characters, tokenExprs):
    'Matches regex to characters and returns a collection of tokens'
    pos = 0         #position of the regex match
    tokens = []     #result of the tokenizing
    while (pos < len(characters)):
        for (pattern, tag) in tokenExprs:
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                token = (text, tag)
                tokens.append(token)
                pos = match.end() 
                break
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
    'ARG'     : 'sys',
    'OPT'     : 'options'}
    for text,tag in tokens:
        importItem = tagToImports.get(tag)
        if importItem:
            if importItem == 'options':
                if re.match('\s+-([b-g]|k|p|r|s|u|w|x|L|S|ot|nt)\s+', text):
                    imports.add('os')
                if re.match('\s+-(b|c|p|S)\s+', text):
                    imports.add('stat')
            else:
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

def findWhiteSpace(tokens, pos):
    while pos < len(tokens):
        (word, tag) = tokens[pos]
        if tag == 'WHITESPACE' or tag == 'NEWLINE':
            break
        pos += 1
    return pos

def echo(pyExprs, tokens, pos):
    pyExprs += 'print '
    pos = findWhiteSpace(tokens,pos) + 1     #skip whitespace
    while pos < len(tokens):         #get tokens until newline character
        (word, tag) = tokens[pos]
        if tag == 'NEWLINE':
            break
        elif tag == 'WHITESPACE':
            pyExprs += ', '
        elif tag == 'BACK_QUOTE':
            #BUG HERE!!
            (words, pos) = parse(tokens, pos)
            pyExprs += words
        else:
            if tag == 'IFSTATEMENT' or tag == 'FI' or tag == 'FORSTATEMENT' or tag == 'DONE':
                tokens[pos] = (word, 'WORD')
            (words, _) = parse([tokens[pos]])
            pyExprs += words
        pos += 1
    return (pyExprs + '\n', pos)

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
    pos = findWhiteSpace(tokens, pos)    
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
    pos = findWhiteSpace(tokens, pos) + 1
    (directory, _) = tokens[pos]
    pyExprs = pyExprs + 'os.chdir(\'' + directory + '\')'
    return (pyExprs, pos)

def exitFunc(pyExprs, tokens, pos):
    pos = findWhiteSpace(tokens, pos) + 1
    (retValue, _) = tokens[pos]
    pyExprs = pyExprs + 'sys.exit(' + retValue + ')'
    return (pyExprs, pos)

def read(pyExprs, tokens, pos):
    pos = findWhiteSpace(tokens, pos) + 1
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

def fileOPT(pyCall, pyExprs, tokens, pos, callParam = '', extraOps = ''):
    pos += 1
    (fileName, _) = parse([tokens[pos]])
    pyExprs = pyCall + '(' + fileName + callParam + ')' + extraOps
    return (pyExprs, pos)

def bOPT(pyExprs, tokens, pos):
    return fileOPT('stat.S_ISBLK(os.stat', pyExprs, tokens, pos, ').st_mode')

def cOPT(pyExprs, tokens, pos):
    return fileOPT('stat.S_ISCHR(os.stat', pyExprs, tokens, pos, ').st_mode')

def dOPT(pyExprs, tokens, pos):
    return fileOPT('os.path.isdir', pyExprs, tokens, pos)

def eOPT(pyExprs, tokens, pos):
    return fileOPT('os.path.exists', pyExprs, tokens, pos)

def fOPT(pyExprs, tokens, pos):
    return fileOPT('os.path.isfile', pyExprs, tokens, pos)

def gOPT(pyExprs):
    return fileOPT('os.stat', pyExprs, tokens, pos, '', '.st_mode & stat.S_ISGID')

def kOPT(pyExprs, tokens, pos):
    return fileOPT('os.stat', pyExprs, tokens, pos, '', '.st_mode & 01000 == 01000')
    
def pOPT(pyExprs, tokens, pos):
    return fileOPT('stat.S_ISFIFO(os.stat', pyExprs, tokens, pos, ').st_mode')

def rOPT(pyExprs, tokens, pos):
    return fileOPT('os.access', pyExprs, tokens, pos, ', os.R_OK')
  
def sOPT(pyExprs, tokens, pos):
    return fileOPT('os.path.getsize', pyExprs, tokens, pos, '' , ' > 0')

def uOPT(pyExprs):
    return fileOPT('os.stat', pyExprs, tokens, pos, '', '.st_mode & stat.S_ISUID')

def wOPT(pyExprs, tokens, pos):
    return fileOPT('os.access', pyExprs, tokens, pos, ', os.W_OK')

def xOPT(pyExprs, tokens, pos):
    return fileOPT('os.access', pyExprs, tokens, pos, ', os.X_OK')

def stringOPT(pyExprs, tokens, pos, check):
    pos += 1
    (word, _) = parse([tokens[pos]])
    pyExprs = pyExprs + 'len(' + word + ')' + check
    return (pyExprs, pos)

def zOPT(pyExprs, tokens, pos):
    return stringOPT(pyExprs, tokens, pos, ' == 0 ')

def nOPT(pyExprs, tokens, pos):
    return stringOPT(pyExprs, tokens, pos, ' > 0 ')

def LOPT(pyExprs, tokens, pos):
    return fileOPT('os.islink', pyExprs, tokens, pos)

def SOPT(pyExprs, tokens, pos):
    return fileOPT('stat.S_ISSOCK(os.stat', pyExprs, tokens, pos, ').st_mode')

def getFileCreated(fileName):
    return 'os.path.getctime(' + fileName + ')'

def filesOPT(pyExprs, tokens, pos, operator):
    (lastExpr, pyExprs) = removeLastExprs(pyExprs, tokens, pos)
    pos += 1
    (fileName, _) = parse([tokens[pos]])
    pyExprs = pyExprs + getFileCreated(lastExpr) + operator + getFileCreated(fileName)
    return (pyExprs, pos)

def ntOPT(pyExprs, tokens, pos):
    return filesOPT(pyExprs, tokens, pos, ' > ')

def otOPT(pyExprs, tokens, pos):
    return filesOPT(pyExprs, tokens, pos, ' < ')

def removeLastExprs(pyExprs, tokens, pos):
    'Return (last expr, pyExprs without last expr)'
    lastExpr = pyExprs.rsplit(None, 1)[-1]
    pyExprs =  ' '.join(pyExprs.split(' ')[:-1])
    return (lastExpr, pyExprs)

def toInt(expr):
    return 'int(' + expr + ')'

def arithOpt(pyExprs, tokens, pos, operator):
    (lastExpr, pyExprs) = removeLastExprs(pyExprs, tokens, pos)
    pos += 1
    (word, _) = parse([tokens[pos]])
    pyExprs = pyExprs + toInt(lastExpr) + operator + toInt(word)
    return (pyExprs, pos)

def eqOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' == ')

def neOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' != ')

def gtOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' > ')

def geOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' >= ')

def ltOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' < ')

def leOPT(pyExprs, tokens, pos):
    return arithOpt(pyExprs, tokens, pos, ' <= ')

def aOPT(pyExprs, tokens, pos):
    return (pyExprs + ' and ' , pos)

def oOPT(pyExprs, tokens, pos):
    return (pyExprs + ' or ', pos)

def exOPT(pyExprs, tokens, pos):
    return (pyExprs + ' not ', pos)

def test(pyExprs, tokens, pos):
    predOptions = {
        '-b' :  bOPT,
        '-c' :  cOPT,
        '-d' :  dOPT,
        '-e' :  eOPT,
        '-f' :  fOPT,
        '-g' :  gOPT,
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
    pos += 1
    optHandler = None
    while pos < len(tokens):
        (word, tag) = tokens[pos]
        if tag == 'OPT':
            opt = re.match('\s+(-[\w]+)\s+', word)
            opt = opt.group(1)
            optHandler = predOptions[opt]
            (pyExprs, pos) = optHandler(pyExprs, tokens, pos)
        else:
            (words, _) = parse([tokens[pos]])
            pyExprs += words
        pos += 1
    return (pyExprs, pos)

def ifStatement(pyExprs, tokens, pos):
    numIfs = 1 #Keeps track of how many nested ifs there are
    ifBody = []
    while True:
        (word, tag) = tokens[pos]
        if re.match('if|elif', word):
            pyExprs += word
            pos = findWhiteSpace(tokens, pos) + 1
            (word, tag) = tokens[pos]
            ifPred = [] #contains the predicate of the if statements
            while True:
                (word, tag) = tokens[pos]
                if word == 'then' and tag == 'IFSTATEMENT':
                    pos += 1
                    break
                ifPred.append(tokens[pos])
                pos += 1
            (pred, _) = parse(ifPred)   
            pyExprs = pyExprs + ' ' + pred.rstrip() + ':\n'
        elif re.match('else', word):
             pyExprs = pyExprs + word + ':\n'
        elif tag == 'FI':
            break

        numIfs = 1
        pos += 1
        ifBody = [] 
        while True:
            (word, tag) = tokens[pos]
            if word == 'if' and tag == 'IFSTATEMENT':
                numIfs += 1
            elif numIfs == 1 and (word == 'elif' or word == 'else' or tag == 'FI'):    
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
    pos = findWhiteSpace(tokens,pos) + 1     #skip whitespace
    while pos < len(tokens):         #get tokens until newline character
        (word, tag) = tokens[pos]
        if tag == 'NEWLINE':
            break
        else:
            (words, _) = parse([tokens[pos]])
            if tag != 'OPERATOR' and tag != 'WHITESPACE':
                pyExprs = pyExprs + toInt(words)
            else:
                pyExprs += words
        pos += 1
    return (pyExprs, pos - 1)

def opt(pyExprs, tokens, pos):
    (word, _) = tokens[pos]
    return (pyExprs + '\'' + word + '\'', pos)

def backQuote(pyExprs, tokens, pos):
    pos += 1 #go to first expr
    pyExprs += 'subprocess.check_output(['
    while pos < len(tokens):
        (word, tag) = tokens[pos]
        if tag == 'BACK_QUOTE':
            pos += 1
            break
        elif tag == 'WHITESPACE':
            pyExprs += ', '
        else:
            pyExprs = pyExprs + '\'' + word + '\''
        pos += 1
    pyExprs += '])\n'
    return (pyExprs , pos)

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
                'TEST'  : test,
                'BACK_QUOTE'  : backQuote}
    while (pos < len(tokens)):
        (words, tag) = tokens[pos]
        handleToken = tagFuncs[tag]
        (pyExprs, pos) = handleToken(pyExprs, tokens, pos)
        pyExprs = pyExprs.rstrip(' \t')
        pos += 1
    return (pyExprs,pos)

        
inputStr = sys.stdin.read()

tokenExprs = [
(r'#![^\n]*\n', 'SHEBANG'),
(r'for\s', 'FORSTATEMENT'),
(r'\sin\s', 'FORSTATEMENT'),
(r'do\s', 'FORSTATEMENT'),
(r'done', 'DONE'),
(r'if', 'IFSTATEMENT'),
(r'test', 'TEST'),
(r'then', 'IFSTATEMENT'),
(r'elif', 'IFSTATEMENT'),
(r'else', 'IFSTATEMENT'),
(r'fi\s', 'FI'),
(r'expr', 'EXPR'),
(r'\s+-([a-z]|O|L|G|S|nt|ot|eq|ne|gt|ge|lt|le)\s+', 'OPT'),
(r'\$[0-9]+', 'ARG'),
(r'\s+\'*(=|>|>=|<|<=|!=|\+|-|\*|\/|%)\'*\s+', 'OPERATOR'),
(r'cd', 'CD'),
(r'read', 'READ'),
(r'exit', 'EXIT'),
(r'\'[^\']*\'', 'SINGLE_QUOTE'),
(r'\"[^\"]*\"', 'DOUBLE_QUOTES'),
(r'`', 'BACK_QUOTE'),
(r'echo', 'ECHO'),
(r'ls', 'SUBPROC'),
(r'pwd', 'SUBPROC'),
(r'id', 'SUBPROC'),
(r'date', 'SUBPROC'),
(r'#[^\n]*\n', 'COMMENT'),
(r';', 'NEWLINE'),
(r'\n', 'NEWLINE'),
(r'\s+', 'WHITESPACE'),
(r'[^= \s]+=', 'VARASSIGNMENT'),
(r'\$\w+', 'VARIABLE'),
(r'(\w|\/)*\*(\w|\.)*', 'GLOB'),
(r'(\w|\/)*\?(\w|\.)*', 'GLOB'),
(r'(\w|\/)*\[(\w|\.|-)*\](\w|\.)*', 'GLOB'),
(r'[A-Za-z0-9,.\-/]+', 'WORD'),
(r'.*', 'NOTFOUND')
]

tokens = tokenize(inputStr, tokenExprs)

for token in tokens:
    print token
print

(pyExprs, _) = parse(tokens)

pyExprs = addImports(pyExprs, tokens)

print pyExprs

