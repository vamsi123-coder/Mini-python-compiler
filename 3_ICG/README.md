# Phase 3 – Intermediate Code Generation (ICG)

## What it does
Walks the AST and produces **Three-Address Code (TAC)** — a simple,
machine-independent instruction format.  Each instruction has at most
**3 operands**: `result = arg1 op arg2`

## Why TAC?
- Easy to optimize (Phase 4)
- Easy to translate to assembly (Phase 5)
- Independent of target CPU

## TAC Rules
| Source code       | TAC produced              |
|-------------------|--------------------------|
| `c = a + b + 100` | `t0 = a + b` <br> `t1 = t0 + 100` <br> `c = t1` |
| `if(a >= b):`     | `t3 = a >= b` <br> `if not t3 goto l1` |
| end of if body    | `l1:` (label)             |

## Full output for inp.py
```
a = 10
b = 9
t0 = a + b
t1 = t0 + 100
c  = t1
e  = 10
f  = 8
t2 = e * f
d  = t2
l0: t3 = a >= b
    if not t3 goto l1
    t4 = a + b
    a  = t4
    t5 = e * f
    t6 = t5 * 100
    g  = t6
l1: u = 10
    j = 99
```

## Key idea
- Every arithmetic expression creates a **new temporary** (t0, t1 …)
- `if` statements use **labels** (l0, l1 …) and `goto`
- Temporaries are tracked in the symbol table just like variables

## How to run
Same build as Phase 2 — the grammar actions now also emit ICG strings.
```bash
./compiler < inp.py     # prints tokens + symbol table + ICG
```
