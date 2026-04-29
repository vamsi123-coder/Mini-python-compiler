/* ── Phase 3: Intermediate Code Generation (ICG) ──────────────── */
/* Walks the AST and emits 3-address TAC (Three Address Code)     */
/* Format:  result = arg1  op  arg2                               */

/* --- Inside the Bison grammar actions --- */

/* Temp variable counter */
int t_count = 0;
int l_count = 0;   /* label counter */
char ICG[10000] = "";

/* Generate a new temp: t0, t1, t2 ... */
char* new_temp() {
    char *t = malloc(10);
    sprintf(t, "t%d", t_count++);
    return t;
}

/* Generate a new label: l0, l1 ... */
char* new_label() {
    char *l = malloc(10);
    sprintf(l, "l%d", l_count++);
    return l;
}

/*
  Grammar action for:   expr → expr + term
*/
// $$ = new_temp();
// sprintf(buf, "%s = %s + %s\n", $$, $1, $3);
// strcat(ICG, buf);

/*
  Grammar action for:   stmt → IF (cond) : body
*/
// char *label_false = new_label();
// sprintf(buf, "%s : t = %s\n", new_label(), cond);
// strcat(ICG, "if not t goto ");
// strcat(ICG, label_false); strcat(ICG, "\n");
// ... body code ...
// sprintf(buf, "%s :\n", label_false);
// strcat(ICG, buf);

/* ──────────────────────────────────────────────────────────────
   EXAMPLE  —  what gets generated for inp.py
   ────────────────────────────────────────────────────────────── */

/*
INPUT:
    a = 10
    b = 9
    c = a + b + 100
    if(a >= b):
        a = a + b
        g = e * f * 100

OUTPUT (Three-Address Code):
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
*/
