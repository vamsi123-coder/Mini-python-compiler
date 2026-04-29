# Mini Python Compiler — Class Presentation

## The Input Program (`inp.py`)
```python
a = 10
b = 9
c = a + b + 100
e = 10
f = 8
d = e * f
if(a >= b):
    a = a + b
    g = e * f * 100
u = 10
j = 99
```

---

## Compiler Pipeline — 5 Phases

```
inp.py
  │
  ▼
┌─────────────────────────────────┐
│  Phase 1 — LEXER  (Flex .l)    │  → Tokens + Symbol Table
│  "a=10"  →  ID EQUAL INT       │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Phase 2 — PARSER / AST        │  → Tree structure
│  (Bison .y)                    │
│  "= a (+ a b)"                 │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Phase 3 — ICG                 │  → Three-Address Code
│  t0 = a + b                    │
│  if not t3 goto l1             │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Phase 4 — OPTIMISED ICG       │  → Constant Propagation
│  t0 = 10 + 9  (substituted)   │     + Quadruples table
│  c  = 119     (folded)         │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  Phase 5 — TARGET CODE (Python)│  → Assembly + FIFO Register Alloc
│  MOV R0, #10                   │
│  ADD R2, R0, R1                │
└─────────────────────────────────┘
```

---

## 5 Folders → 5 Members

| Folder             | Topic               | Files to explain       |
|--------------------|---------------------|------------------------|
| `1_Lexer/`         | Tokens & Symbol Table | `lexer.l`, README.md |
| `2_AST/`           | Abstract Syntax Tree  | `parser.y`, README.md |
| `3_ICG/`           | Intermediate Code     | `icg.c`, README.md   |
| `4_Optimized_ICG/` | Optimisations         | `optimised_icg.c`, README.md |
| `5_Target_Code/`   | Assembly Generation   | `target_code.py`, README.md |

---

## Tools Used
| Tool  | Purpose                          |
|-------|----------------------------------|
| Flex  | Lexer generator (reads `.l`)     |
| Bison | Parser generator (reads `.y`)    |
| GCC   | Compiles generated C code        |
| Python| Target code generator (Phase 5)  |

## How to build & run (Phases 1–4)
```bash
cd 1_Lexer/         
bison -d proj1.y
flex proj.l
gcc lex.yy.c proj1.tab.c -o compiler -lm
./compiler < ../inp.py
```

## How to run Phase 5
```bash
cd 5_Target_Code/
# First copy the ICG output into IntermediateCode.txt
python3 target_code.py
```
