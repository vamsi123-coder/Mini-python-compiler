# ── Phase 5: Target Code Generation ─────────────────────────────
# Reads IntermediateCode.txt and emits ARM-style assembly.
# Uses a simple register allocator (FIFO when registers run out).

import re

# ── Register allocator ──────────────────────────────────────────
NUM_REGS = 13
reg_used = [False] * NUM_REGS   # True = register occupied
var_reg  = {}                    # var_reg['a'] = 'R2'
spill_order = []                 # FIFO order for spilling

def alloc_reg():
    """Return a free register, or spill the oldest one (FIFO)."""
    for i in range(NUM_REGS):
        if not reg_used[i]:
            reg_used[i] = True
            return f'R{i}'
    # Spill: evict the register used longest ago
    evict_var = spill_order.pop(0)
    evict_reg = var_reg.pop(evict_var)
    print(f'ST {evict_var}, {evict_reg}')   # store to memory
    return evict_reg

def get_reg(var):
    """Return the register already holding var, or allocate one."""
    if var in var_reg:
        return var_reg[var]
    r = alloc_reg()
    var_reg[var] = r
    spill_order.append(var)
    return r

# ── Code generator ───────────────────────────────────────────────
ops = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV',
       '>=':'GE', '<=':'LE', '>':'G', '<':'L', '==':'E'}

for raw in open('IntermediateCode.txt'):
    line = raw.strip().split()
    if not line:
        continue

    # Label:
    if len(line) == 1:
        print(line[0])

    # var = constant
    elif len(line) == 3 and line[1] == '=' and line[2].lstrip('-').isdigit():
        r = get_reg(line[0])
        print(f'MOV {r}, #{line[2]}')

    # result = arg1 op arg2
    elif len(line) == 5:
        r1 = get_reg(line[2])
        r2 = get_reg(line[4])
        rd = get_reg(line[0])
        instr = ops.get(line[3], line[3])
        print(f'{instr} {rd}, {r1}, {r2}')

    # if 0 goto label
    elif len(line) == 4 and line[0] == 'if':
        r = get_reg(line[1])
        print(f'BNEQZ {r}, {line[3]}')

# Flush remaining variables to memory
for var, reg in var_reg.items():
    if var[0] != 't':            # don't store temporaries
        print(f'ST {var}, {reg}')

# ── EXAMPLE OUTPUT ───────────────────────────────────────────────
# MOV R0, #10      ← a = 10
# MOV R1, #9       ← b = 9
# MOV R2, #119     ← c = 119
# MOV R3, #8       ← f = 8
# MOV R4, #80      ← d = 80
# l0:
# MOV R5, #0
# BNEQZ R5, l1    ← if 0 goto l1 (branch never taken — optimised!)
# MOV R6, #19     ← a = 19
# MOV R7, #8000   ← g = 8000
# l1:
# ST b, R1
# ST c, R2
# ST d, R4
# ST a, R6
# ST g, R7
