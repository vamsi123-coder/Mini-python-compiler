# Phase 1 – Lexer & Symbol Table

## What it does
Reads Python source code character by character and groups them into **tokens**.
Also builds a **Symbol Table** tracking every variable.

## Input  (`inp.py`)
```python
a = 10
b = 9
c = a + b + 100
if(a >= b):
    a = a + b
```

## Output (tokens printed)
```
ID equal int
ID equal int
ID equal ID plus ID plus int
if special_start ID greaterthanequal ID special_end colon
indent ID equal ID plus ID
```

## Symbol Table produced
| LABEL | TYPE       | VALUE | SCOPE  |
|-------|------------|-------|--------|
| a     | IDENTIFIER | 19    | local  |
| b     | IDENTIFIER | 9     | global |
| c     | IDENTIFIER | 119   | global |

## How to run
```bash
flex lexer.l          # generates lex.yy.c
bison -d parser.y     # generates y.tab.c + y.tab.h
gcc lex.yy.c y.tab.c -o compiler
./compiler < inp.py
```

## Key idea
- **Flex** uses regex rules → each match returns a token number
- `yylval` carries the token's value (e.g. variable name "a")
- Symbol table stores variables with value, scope, line number
