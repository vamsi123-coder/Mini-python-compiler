# Phase 4 – Optimised Intermediate Code Generation

## What it does
Takes the raw TAC from Phase 3 and applies **two optimisations** to make
the code faster and smaller before generating machine code.

## Optimisation 1 — Constant Propagation
If a variable always holds a known constant, replace it with that value.

| Before              | After               |
|---------------------|---------------------|
| `a = 10`            | `a = 10`            |
| `t0 = a + b`        | `t0 = 10 + 9`  ✅   |
| `t1 = t0 + 100`     | `t1 = 19 + 100` ✅  |
| `c = t1`            | `c = 119`  ✅ (folded) |

**Saving:** Fewer arithmetic instructions at runtime.

## Optimisation 2 — Packing Temporaries (Dead Temp Elimination)
If a temporary is assigned and immediately used, merge the two steps.
Results stored as **Quadruples**: `(op, arg1, arg2, result)`.

| Before           | After (quadruple) |
|------------------|-------------------|
| `t2 = e * f`     | `* e f d` (direct) |
| `d = t2`         | *(t2 gone)*        |

## Quadruples table
```
op      arg1   arg2   result
=       10            a
=       9             b
+       a      b      t0
+       t0     100    t1
=       t1            c
*       e      f      t2
=       t2            d
>=      a      b      t3
goto                  l1
=       t0            a
*       t2     100    t5
=       t5            g
=       10            u
=       99            j
```

## Key idea
- Constant propagation: look up variable value in symbol table → substitute
- Quadruples: 4-field records, easy to translate to registers in Phase 5
