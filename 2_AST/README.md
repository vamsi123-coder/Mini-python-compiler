# Phase 2 – Abstract Syntax Tree (AST)

## What it does
Parses the token stream using grammar rules and builds a **tree** that
represents the structure of the program — no raw text, just relationships.

## Input  (token stream from Phase 1)
```
ID equal ID plus ID plus int
```

## Output  (AST printed as nested list)
```
( SEQ
  ( = a 10 )
  ( SEQ
    ( = c ( + ( + a b ) 100 ) )
    ( SEQ
      ( IF ( >= a b )
        ( SEQ ( = a ( + a b ) ) NULL )
      )
    NULL )
  )
)
```

## Grammar rules (simplified)
```
program   → stmt_list
stmt_list → stmt stmt_list  |  ε
stmt      → ID = expr NL
          | IF (expr) : body
expr      → expr + term  |  term
term      → term * factor |  factor
factor    → NUM | ID | (expr)
```

## Key idea
- Grammar is **recursive** — expressions nest inside expressions
- Each grammar rule creates a **tree node** with left/right children
- `buildTree("op", left, right)` → makes one node
- `printTree(root)` → walks tree recursively and prints it

## How to run
```bash
# Same build as Phase 1 — the .y file now includes AST node functions
bison -d parser.y
flex lexer.l
gcc lex.yy.c parser.tab.c -o ast
./ast < inp.py
```
