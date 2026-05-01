
# 🐍 Mini Python Compiler — 5 Phase Implementation

---

## 👥 Team

| S.No | Name | Roll Number |
|------|------|-------------|
| 1 | M. Sai Sushanth | 160123733194 |
| 2 | S. Abdullah | 160123733201 |
| 3 | V. Saikumar | 160123733205 |
| 4 | V. J. Vamsi Krishna | 160123733206 |
| 5 | K. Amulya | 160123733320 |

| Field | Details |
|-------|---------|
| 🎓 Guide | Dr. G. Vanitha |
| 🏫 College | Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad |
| 📅 Year | 2025–2026 |
| 🔧 Language | C (Flex + Bison + GCC) + Python |

---

## 📥 Input Program (`inp.py`)

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

## 🔄 Compiler Pipeline

```
inp.py
  │
  ▼
[ Phase 1 ] ──► LEXER            (Flex)   → Tokens + Symbol Table
  │
  ▼
[ Phase 2 ] ──► PARSER / AST     (Bison)  → Abstract Syntax Tree
  │
  ▼
[ Phase 3 ] ──► ICG              (C)      → Three Address Code (TAC)
  │
  ▼
[ Phase 4 ] ──► OPTIMISED ICG    (C)      → Constant Folding & Propagation
  │
  ▼
[ Phase 5 ] ──► TARGET CODE      (Python) → Assembly-like Output
```

---

## ⚙️ Phases Overview

### 🔹 Phase 1 — Lexical Analysis
Converts raw source code into a stream of tokens and builds the Symbol Table.

| Input | Output |
|-------|--------|
| `a = 10` | `ID EQUAL INT` |
| `if(a >= b)` | `IF LPAREN ID GEQ ID RPAREN` |

---

### 🔹 Phase 2 — Syntax Analysis (AST)
Validates grammar using Bison and constructs an Abstract Syntax Tree (AST).

```
(= a (+ a b))
(if (>= a b) (= a (+ a b)))
```

---

### 🔹 Phase 3 — Intermediate Code Generation
Produces Three-Address Code (TAC) from the AST.

```
t0 = a + b
t1 = t0 + 100
c  = t1
t2 = a >= b
if not t2 goto L1
a  = a + b
L1:
```

---

### 🔹 Phase 4 — Optimised ICG
Applies **Constant Folding** and **Constant Propagation** to reduce redundant computations.

```
# Before Optimization        # After Optimization
t0 = a + b          ──►      t0 = 19
t1 = t0 + 100       ──►      c  = 119
```

---

### 🔹 Phase 5 — Target Code Generation
Converts optimised TAC to assembly-like instructions using **FIFO register allocation**.

```asm
MOV R0, #10
MOV R1, #9
ADD R2, R0, R1
MOV R3, #100
ADD R4, R2, R3
```

---

## 📁 Folder Structure

```
mini-python-compiler/
│
├── inp.py                        ← Input source program
│
├── 1_Lexer/
│   └── lexer.l                   ← Flex lexer specification
│
├── 2_AST/
│   └── parser.y                  ← Bison parser + AST builder
│
├── 3_ICG/
│   └── icg.c                     ← Intermediate Code Generator
│
├── 4_Optimized_ICG/
│   └── optimised_icg.c           ← Constant folding & propagation
│
└── 5_Target_Code/
    ├── target_code.py            ← Target code generator
    └── IntermediateCode.txt      ← ICG output (input for Phase 5)
```

---

## 🛠️ Tools & Technologies

| Tool | Version | Purpose |
|------|---------|---------|
| **Flex** | 2.6+ | Lexer / tokenizer generator |
| **Bison** | 3.x+ | Parser + AST generator |
| **GCC** | 9.x+ | Compile C phase files |
| **Python** | 3.x | Target code generation (Phase 5) |
| **Linux/WSL** | — | Recommended environment |

---

## 🚀 How to Run

### ▶️ Phases 1–4 (Lexer → Parser → ICG → Optimised ICG)

```bash
cd 1_Lexer/
bison -d proj1.y
flex proj.l
gcc lex.yy.c proj1.tab.c -o compiler -lm
./compiler < ../inp.py
```

### ▶️ Phase 5 (Target Code Generation)

```bash
cd 5_Target_Code/
# Paste the ICG output from Phase 3/4 into IntermediateCode.txt
python3 target_code.py
```

---

## 🎯 Objective

Design and implement a complete mini compiler for a subset of Python to understand each stage of the compilation process end-to-end:

| Phase | Concept Covered |
|-------|----------------|
| Phase 1 | Lexical Analysis — tokenising source code |
| Phase 2 | Syntax Analysis — grammar validation + AST construction |
| Phase 3 | Intermediate Code Generation — Three-Address Code (TAC) |
| Phase 4 | Optimisation — constant folding and propagation |
| Phase 5 | Target Code Generation — register-based assembly output |

---

## 📌 Notes

- All phases are implemented independently by individual team members.
- Phases 1–4 use **Flex + Bison + GCC** on a Linux/WSL environment.
- Phase 5 uses **Python** and reads TAC from `IntermediateCode.txt`.
- The project covers the full front-end and back-end of a compiler.
```
