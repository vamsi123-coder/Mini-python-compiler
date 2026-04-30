```markdown
# 🐍 Mini Python Compiler — 5 Phase Implementation

## 👥 Team

| Name | Roll Number |
|------|-------------|
| M. Sai Sushanth | 160123733194 |
| S. Abdullah | 160123733201 |
| V. Saikumar | 160123733205 |
| V. J. Vamsi Krishna | 160123733206 |
| K. Amulya | 160123733320 |

> **Guide:** Dr. G. Vanitha
> **College:** Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad
> **Year:** 2025–2026

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
[ Phase 1 ] LEXER (Flex)
  │
  ▼
[ Phase 2 ] PARSER / AST (Bison)
  │
  ▼
[ Phase 3 ] ICG (Three Address Code)
  │
  ▼
[ Phase 4 ] OPTIMISED ICG
  │
  ▼
[ Phase 5 ] TARGET CODE (Assembly-like)
```

---

## ⚙️ Phases Overview

### Phase 1 — Lexical Analysis
- Converts input source code into tokens
- Builds the Symbol Table
```
Example: a = 10  →  ID EQUAL INT
```

### Phase 2 — Syntax Analysis
- Checks grammar rules using Bison
- Builds the Abstract Syntax Tree (AST)
```
Example: (= a (+ a b))
```

### Phase 3 — Intermediate Code Generation
- Generates Three-Address Code (TAC)
```
t0 = a + b
t1 = t0 + 100
if not t2 goto L1
```

### Phase 4 — Optimised ICG
- Applies Constant Folding & Propagation
```
t0 = 10 + 9
c  = 119
```

### Phase 5 — Target Code Generation
- Converts TAC to assembly-like code
- Uses FIFO register allocation
```
MOV R0, #10
ADD R2, R0, R1
```

---

## 📁 Folder Structure

```
mini-python-compiler/
├── inp.py
├── 1_Lexer/
│   └── lexer.l
├── 2_AST/
│   └── parser.y
├── 3_ICG/
│   └── icg.c
├── 4_Optimized_ICG/
│   └── optimised_icg.c
└── 5_Target_Code/
    └── target_code.py
```

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| **Flex** | Lexer generator |
| **Bison** | Parser generator |
| **GCC** | Compile C source files |
| **Python** | Target code generation (Phase 5) |

---

## 🚀 How to Run

### ▶️ Phases 1–4

```bash
cd 1_Lexer/
bison -d proj1.y
flex proj.l
gcc lex.yy.c proj1.tab.c -o compiler -lm
./compiler < ../inp.py
```

### ▶️ Phase 5

```bash
cd 5_Target_Code/
# Copy the ICG output into IntermediateCode.txt first
python3 target_code.py
```

---

## 🎯 Objective

Build a complete mini compiler to understand every stage of the compiler pipeline:
- **Lexical Analysis** — Tokenise source code
- **Syntax Analysis** — Validate grammar and build AST
- **Intermediate Code Generation** — Produce Three-Address Code
- **Optimisation** — Apply constant folding and propagation
- **Target Code Generation** — Emit register-based assembly-like instructions
```