/* ── Phase 4: Optimised ICG ──────────────────────────────────── */
/* Two optimisation passes on the TAC produced in Phase 3         */

/* ── OPTIMISATION 1: Constant Propagation ───────────────────── */
/*
   If a variable is assigned a known constant, substitute it
   everywhere that variable is used.

   Before:
       a = 10
       b = 9
       t0 = a + b      ← a and b are known constants

   After:
       a  = 10
       b  = 9
       t0 = 10 + 9     ← substituted
       t1 = 19 + 100   ← t0=19 also substituted
       c  = 119        ← fully folded
*/

void constant_propagation(SymbolTable *st, TAC *code) {
    for each instruction in code:
        if arg1 is a variable with known constant value:
            replace arg1 with that constant
        if arg2 is a variable with known constant value:
            replace arg2 with that constant
        // evaluate if both args are now constants (constant folding)
        if both args are constants:
            compute result and store in symbol table
}

/* ── OPTIMISATION 2: Packing Temporaries (Dead Code Elim.) ───── */
/*
   Remove temporaries that are used only once immediately after
   being defined — merge the two instructions into one.

   Before:
       t2 = e * f
       d  = t2        ← t2 used only here, can eliminate

   After (quadruple table just stores op/arg1/arg2/result directly):
       *  e  f  d     ← no t2 needed
*/

/* ── QUADRUPLES ────────────────────────────────────────────────── */
/*
   Final representation: table of (op, arg1, arg2, result)

   op      arg1   arg2   result
   =       10            a
   =       9             b
   +       a      b      t0
   +       t0     100    t1
   =       t1            c
   *       e      f      t2
   =       t2            d
   Label               l0
   >=      a      b      t3
   goto                l1
   =       t0            a       ← uses already-computed t0
   *       t2     100    t5
   =       t5            g
   Label               l1
   =       10            u
   =       99            j
*/

/* ── OPTIMISED ICG OUTPUT ──────────────────────────────────────── */
/*
   a  = 10
   b  = 9
   t0 = 10 + 9         ← constant propagation
   t1 = 19 + 100       ← constant propagation
   c  = 119            ← fully folded
   e  = 10
   f  = 8
   t2 = 10 * 8         ← constant propagation
   d  = 80             ← folded
l0:
   t3 = 10 >= 9        ← propagated
   t4 = not 1
   if 0 goto l1        ← branch known at compile time (dead branch!)
   a  = 19
   t5 = 80 * 100
   g  = 8000
l1:
   u = 10
   j = 99
*/
