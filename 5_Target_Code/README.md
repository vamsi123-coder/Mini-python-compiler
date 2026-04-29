# Phase 5 – Target Code Generation

## What it does
Reads the optimised ICG and produces **assembly-like machine instructions**
with real registers (R0–R12) assigned to each variable.

## Register Allocator — FIFO strategy
```
reg_used = [False] * 13    # 13 registers available

def alloc_reg():
    if a free register exists → return it
    else → SPILL: evict the oldest register (FIFO),
                  emit  ST var, Rx  (store to memory),
                  reuse that register
```

## Translation rules
| ICG instruction       | Assembly output         |
|-----------------------|------------------------|
| `a = 10`              | `MOV R0, #10`          |
| `t0 = a + b`          | `ADD R2, R0, R1`       |
| `if 0 goto l1`        | `BNEQZ R5, l1`         |
| `l0:`                 | `l0:`                  |
| variable evicted      | `ST a, R0`             |

## Full output for inp.py
```asm
MOV R0, #10       ; a = 10
MOV R1, #9        ; b = 9
MOV R2, #119      ; c = 119  (constant-folded)
MOV R3, #8        ; f = 8
MOV R4, #80       ; d = 80
l0:
MOV R5, #0
BNEQZ R5, l1      ; branch never taken (optimised-out)
MOV R6, #19       ; a = 19
MOV R7, #8000     ; g = 8000
l1:
ST b, R1
ST c, R2
ST d, R4
ST a, R6
ST g, R7
ST u, R0
ST j, R8
```

## How to run
```bash
# Generate IntermediateCode.txt first (from Phase 4 output)
python3 target_code.py      # reads IntermediateCode.txt, prints assembly
```

## Key idea
- `var_reg` dict maps variable names → register names
- `spill_order` list tracks usage order for FIFO eviction
- Temporaries (t0, t1…) are NOT stored to memory — they're discarded
