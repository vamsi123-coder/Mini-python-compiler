#!/usr/bin/env python3
"""
Complete Mini Python Compiler — 5 Phases
Lexer → AST → ICG → Optimized ICG → Target Code
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Union

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — LEXER & SYMBOL TABLE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Token:
    type: str
    value: str
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class SymbolTable:
    def __init__(self):
        self.symbols = {}
    
    def add(self, name, value=None, scope='global'):
        self.symbols[name] = {'value': value, 'scope': scope}
    
    def get(self, name):
        return self.symbols.get(name)
    
    def update(self, name, value):
        if name in self.symbols:
            self.symbols[name]['value'] = value
    
    def display(self):
        print("\n┌─ SYMBOL TABLE ─────────────────────┐")
        print("│ LABEL     │ TYPE       │ VALUE     │")
        print("├───────────┼────────────┼───────────┤")
        for label, info in self.symbols.items():
            print(f"│ {label:<9} │ IDENTIFIER │ {str(info['value']):<9} │")
        print("└────────────────────────────────────┘")

class Lexer:
    KEYWORDS = {'if', 'else', 'while', 'print', 'True', 'False', 'for', 'in', 'range'}
    OPERATORS = {'+', '-', '*', '/', '=', '>=', '<=', '>', '<', '=='}
    
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []
        self.symbol_table = SymbolTable()
    
    def tokenize(self):
        """Convert source code into tokens"""
        self.code = re.sub(r'#.*$', '', self.code, flags=re.MULTILINE)  # Remove comments
        
        for line_no, line in enumerate(self.code.split('\n'), 1):
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            # Basic indentation detection
            indent_spaces = len(line) - len(line.lstrip())
            if indent_spaces > 0:
                self.tokens.append(Token('INDENT', 'INDENT'))
                
            i = indent_spaces
            while i < len(line):
                # Skip whitespace
                if line[i].isspace():
                    i += 1
                    continue
                
                # Multi-char operators first (>=, <=, ==)
                if i + 1 < len(line) and line[i:i+2] in ['>=', '<=', '==']:
                    self.tokens.append(Token(line[i:i+2], line[i:i+2]))
                    i += 2
                    continue
                
                # Single-char operators
                if line[i] in '+-*/=><':
                    self.tokens.append(Token(line[i], line[i]))
                    i += 1
                    continue
                
                # Single-char delimiters
                if line[i] in '(),:':
                    self.tokens.append(Token(line[i], line[i]))
                    i += 1
                    continue
                
                # Numbers
                if line[i].isdigit():
                    num = ''
                    while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                        num += line[i]
                        i += 1
                    self.tokens.append(Token('NUM', num))
                    continue
                
                # Identifiers & Keywords
                if line[i].isalpha() or line[i] == '_':
                    word = ''
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        word += line[i]
                        i += 1
                    
                    if word in self.KEYWORDS:
                        self.tokens.append(Token(word.upper(), word))
                    else:
                        self.tokens.append(Token('ID', word))
                        self.symbol_table.add(word)
                    continue
                
                i += 1
            
            # Add newline token
            if line.strip():
                self.tokens.append(Token('NL', '\\n'))
        
        return self.tokens

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — AST (Abstract Syntax Tree)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ASTNode:
    type: str
    children: List['ASTNode']
    value: Optional[str] = None
    
    def __repr__(self, indent=0):
        prefix = "  " * indent
        if self.value:
            return f"{prefix}({self.type} {self.value})"
        elif not self.children:
            return f"{prefix}({self.type})"
        else:
            result = f"{prefix}({self.type}\n"
            for child in self.children:
                result += child.__repr__(indent + 1) + "\n"
            result += f"{prefix})"
            return result

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != 'NL']  # Remove newlines
        self.pos = 0
        self.current = self.tokens[0] if tokens else None
    
    def peek(self):
        return self.current
    
    def consume(self, expected=None):
        token = self.current
        if expected and token.type != expected:
            raise SyntaxError(f"Expected {expected}, got {token.type}")
        self.pos += 1
        self.current = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return token
    
    def parse(self):
        return self.parse_program()
    
    def parse_program(self):
        stmts = []
        while self.current:
            stmts.append(self.parse_statement())
        return ASTNode('PROGRAM', stmts)
    
    def parse_statement(self):
        if self.current.type == 'IF':
            return self.parse_if()
        elif self.current.type == 'WHILE':
            return self.parse_while()
        elif self.current.type == 'FOR':
            return self.parse_for()
        elif self.current.type == 'PRINT':
            return self.parse_print()
        else:
            return self.parse_assignment()
    
    def parse_assignment(self):
        id_token = self.consume('ID')
        self.consume('=')
        expr = self.parse_expression()
        return ASTNode('=', [expr], id_token.value)
    
    def parse_block(self):
        body = []
        while self.current and self.current.type == 'INDENT':
            self.consume('INDENT')
            body.append(self.parse_statement())
        if not body and self.current:
            body.append(self.parse_statement())
        return ASTNode('BODY', body)
        
    def parse_print(self):
        self.consume('PRINT')
        has_paren = False
        if self.current and self.current.type == '(':
            self.consume('(')
            has_paren = True
        elif self.current and self.current.type == '=':
            # Handle assignment to print (e.g. print = 1)
            self.consume('=')
            expr = self.parse_expression()
            return ASTNode('=', [expr], 'print')
        
        expr = self.parse_expression()
        if has_paren:
            self.consume(')')
        return ASTNode('PRINT', [expr])

    def parse_if(self):
        self.consume('IF')
        has_paren = False
        if self.current and self.current.type == '(':
            self.consume('(')
            has_paren = True
        cond = self.parse_expression()
        if has_paren:
            self.consume(')')
        self.consume(':')
        body = self.parse_block()
        return ASTNode('IF', [cond, body])
        
    def parse_while(self):
        self.consume('WHILE')
        has_paren = False
        if self.current and self.current.type == '(':
            self.consume('(')
            has_paren = True
        cond = self.parse_expression()
        if has_paren:
            self.consume(')')
        self.consume(':')
        body = self.parse_block()
        return ASTNode('WHILE', [cond, body])
        
    def parse_for(self):
        self.consume('FOR')
        id_token = self.consume('ID')
        self.consume('IN')
        self.consume('RANGE')
        self.consume('(')
        limit = self.parse_expression()
        self.consume(')')
        self.consume(':')
        body = self.parse_block()
        return ASTNode('FOR', [ASTNode('ID', [], id_token.value), limit, body])
    
    def parse_expression(self):
        return self.parse_comparison()
    
    def parse_comparison(self):
        left = self.parse_additive()
        
        while self.current and self.current.type in ['>=', '<=', '>', '<', '==']:
            op = self.consume().value
            right = self.parse_additive()
            left = ASTNode(op, [left, right])
        
        return left
    
    def parse_additive(self):
        left = self.parse_multiplicative()
        
        while self.current and self.current.type in ['+', '-']:
            op = self.consume().value
            right = self.parse_multiplicative()
            left = ASTNode(op, [left, right])
        
        return left
    
    def parse_multiplicative(self):
        left = self.parse_primary()
        
        while self.current and self.current.type in ['*', '/']:
            op = self.consume().value
            right = self.parse_primary()
            left = ASTNode(op, [left, right])
        
        return left
    
    def parse_primary(self):
        if self.current.type == 'NUM':
            token = self.consume()
            return ASTNode('NUM', [], token.value)
        elif self.current.type == 'ID':
            token = self.consume()
            return ASTNode('ID', [], token.value)
        elif self.current.type == '(':
            self.consume('(')
            expr = self.parse_expression()
            self.consume(')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {self.current}")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — ICG (Intermediate Code Generation)
# ═══════════════════════════════════════════════════════════════════════════════

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
    
    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self):
        label = f"l{self.label_count}"
        self.label_count += 1
        return label
    
    def emit(self, op, arg1='', arg2='', result=''):
        self.code.append((op, arg1, arg2, result))
    
    def generate(self, ast):
        self.gen_node(ast)
        return self.code
    
    def gen_node(self, node):
        if node.type == 'PROGRAM':
            for child in node.children:
                self.gen_node(child)
        
        elif node.type == '=':
            # Assignment: var = expr
            var_name = node.value
            if len(node.children) > 0:
                result = self.gen_node(node.children[0])
                self.emit('=', result, '', var_name)
            else:
                # Direct constant assignment
                self.emit('=', node.value, '', var_name)
        
        elif node.type in ['+', '-', '*', '/']:
            arg1 = self.gen_node(node.children[0]) if len(node.children) > 0 else ''
            arg2 = self.gen_node(node.children[1]) if len(node.children) > 1 else ''
            result = self.new_temp()
            self.emit(node.type, arg1, arg2, result)
            return result
        
        elif node.type in ['>=', '<=', '>', '<', '==']:
            arg1 = self.gen_node(node.children[0]) if len(node.children) > 0 else ''
            arg2 = self.gen_node(node.children[1]) if len(node.children) > 1 else ''
            result = self.new_temp()
            self.emit(node.type, arg1, arg2, result)
            return result
        
        elif node.type == 'IF':
            cond = self.gen_node(node.children[0])
            label_false = self.new_label()
            self.emit('if_not', cond, '', label_false)
            self.gen_node(node.children[1])
            self.emit('label', label_false)
            
        elif node.type == 'WHILE':
            label_start = self.new_label()
            label_end = self.new_label()
            self.emit('label', label_start)
            cond = self.gen_node(node.children[0])
            self.emit('if_not', cond, '', label_end)
            self.gen_node(node.children[1])
            self.emit('goto', '', '', label_start)
            self.emit('label', label_end)
            
        elif node.type == 'FOR':
            var_name = node.children[0].value
            self.emit('=', '0', '', var_name)
            label_start = self.new_label()
            label_end = self.new_label()
            self.emit('label', label_start)
            limit = self.gen_node(node.children[1])
            cond_res = self.new_temp()
            self.emit('<', var_name, limit, cond_res)
            self.emit('if_not', cond_res, '', label_end)
            self.gen_node(node.children[2])
            temp_inc = self.new_temp()
            self.emit('+', var_name, '1', temp_inc)
            self.emit('=', temp_inc, '', var_name)
            self.emit('goto', '', '', label_start)
            self.emit('label', label_end)
            
        elif node.type == 'PRINT':
            res = self.gen_node(node.children[0])
            self.emit('print', res, '', '')
        
        elif node.type == 'BODY':
            for child in node.children:
                self.gen_node(child)
        
        elif node.type == 'NUM':
            return node.value
        
        elif node.type == 'ID':
            return node.value
        
        return ''
    
    def get_quadruples(self):
        """Return ICG as quadruples: (op, arg1, arg2, result)"""
        return self.code
    
    def get_triples(self):
        """Convert ICG to triples: (op, arg1, arg2) - no explicit result"""
        triples = []
        for i, (op, arg1, arg2, result) in enumerate(self.code):
            # Result position is implicit (index in array)
            triples.append((op, arg1, arg2, i))
        return triples
    
    def get_indirect_triples(self):
        """Indirect triples with separate index pointer table"""
        triples_list = []
        index_table = []
        
        for i, (op, arg1, arg2, result) in enumerate(self.code):
            triples_list.append((op, arg1, arg2))
            index_table.append(i)
        
        return triples_list, index_table

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — OPTIMIZED ICG (Constant Propagation + Dead Code Elimination)
# ═══════════════════════════════════════════════════════════════════════════════
class Optimizer:
    def __init__(self, symbol_table: dict):
        self.symbol_table = symbol_table
 
        # Bookkeeping reset at the start of each optimize() call
        self.constants: dict[str, int]   = {}   # var -> known constant value
        self.copies:    dict[str, str]   = {}   # var -> canonical source
        self.avail:     dict[tuple, str] = {}   # (op,a,b) -> tmp holding result
        self.log:       list[str]        = []   # human-readable pass notes
 
    # -----------------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------------
 
    def optimize(self, code: list[Instr]) -> list[Instr]:
        """
        Apply all optimisation passes and return the improved instruction list.
        Call self.log after this to see what each pass did.
        """
        self.constants = {}
        self.copies    = {}
        self.avail     = {}
        self.log       = []
 
        code = self._constant_propagation(code)
        code = self._copy_propagation(code)
        code = self._constant_folding(code)
        code = self._common_subexpression_elimination(code)
        code = self._strength_reduction(code)
        code = self._loop_invariant_code_motion(code)
        code = self._dead_code_elimination(code)
        code = self._peephole_optimization(code)
 
        return code
 
    # -----------------------------------------------------------------------
    # Pass 1 — Constant propagation
    # Replace every use of a variable known to hold a constant with that value.
    # -----------------------------------------------------------------------
 
    def _constant_propagation(self, code: list[Instr]) -> list[Instr]:
        constants: dict[str, str] = {}   # var -> literal string of its value
        result = []
 
        for op, a1, a2, res in code:
            # Track simple assignments of a literal
            if op == '=' and a1 is not None and self._is_literal(a1):
                constants[res] = a1
 
            # Substitute known constants into operands
            new_a1 = constants.get(a1, a1) if a1 is not None else a1
            new_a2 = constants.get(a2, a2) if a2 is not None else a2
 
            if new_a1 != a1 or new_a2 != a2:
                self.log.append(
                    f"[ConstProp] {op} {a1},{a2}->{res}  =>  {op} {new_a1},{new_a2}->{res}"
                )
 
            result.append((op, new_a1, new_a2, res))
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 2 — Copy propagation
    # When x = y, replace later uses of x with y (the original source).
    # -----------------------------------------------------------------------
 
    def _copy_propagation(self, code: list[Instr]) -> list[Instr]:
        copies: dict[str, str] = {}
        result = []
 
        for op, a1, a2, res in code:
            # Look up the canonical source for each operand
            new_a1 = self._resolve_copy(a1, copies)
            new_a2 = self._resolve_copy(a2, copies)
 
            if op == '=' and new_a1 is not None and not self._is_literal(new_a1):
                copies[res] = new_a1   # record the copy
 
            # If res is reassigned, the old copy is no longer valid
            if res is not None:
                copies.pop(res, None)
 
            if new_a1 != a1 or new_a2 != a2:
                self.log.append(
                    f"[CopyProp] {op} {a1},{a2}->{res}  =>  {op} {new_a1},{new_a2}->{res}"
                )
 
            result.append((op, new_a1, new_a2, res))
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 3 — Constant folding
    # Evaluate binary/unary expressions whose operands are both constants.
    # -----------------------------------------------------------------------
 
    def _constant_folding(self, code: list[Instr]) -> list[Instr]:
        self.constants = {}   # var -> int (used by later passes too)
        result = []
 
        for op, a1, a2, res in code:
            if op == '=' and a1 is not None and self._is_literal(a1):
                self.constants[res] = int(a1)
                result.append((op, a1, a2, res))
                continue
 
            if op in ('+', '-', '*', '/', '%', '**'):
                v1 = self._as_int(a1)
                v2 = self._as_int(a2)
                if v1 is not None and v2 is not None and not (op in ('/', '%') and v2 == 0):
                    folded = self._eval(op, v1, v2)
                    if folded is not None:
                        self.log.append(
                            f"[ConstFold] {a1} {op} {a2} = {folded}  ->  {res}"
                        )
                        self.constants[res] = folded
                        result.append(('=', str(folded), None, res))
                        continue
 
            # Track unmodified result constants
            if op == '=' and a1 is not None and self._is_literal(a1):
                self.constants[res] = int(a1)
 
            result.append((op, a1, a2, res))
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 4 — Common subexpression elimination (CSE)
    # If (op a1 a2) was already computed into tmp_x, reuse tmp_x.
    # -----------------------------------------------------------------------
 
    def _common_subexpression_elimination(self, code: list[Instr]) -> list[Instr]:
        available: dict[tuple, str] = {}   # (op, a1, a2) -> result var
        result = []
 
        for op, a1, a2, res in code:
            if op in ('+', '-', '*', '/', '%', '**'):
                key = (op, a1, a2)
                comm_key = (op, a2, a1) if op in ('+', '*') else None
 
                existing = available.get(key) or (comm_key and available.get(comm_key))
                if existing and existing != res:
                    self.log.append(
                        f"[CSE] {a1} {op} {a2} already in {existing}; reusing for {res}"
                    )
                    result.append(('=', existing, None, res))
                    # Mark res as an alias
                    available[(op, a1, a2)] = existing
                    continue
 
                available[key] = res
 
            # Any assignment to res invalidates cached exprs that used res
            if res is not None:
                available = {k: v for k, v in available.items()
                             if v != res and k[1] != res and k[2] != res}
 
            result.append((op, a1, a2, res))
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 5 — Strength reduction
    # Replace costly operations with cheaper equivalents.
    #   x * 2   ->  x + x
    #   x * 1   ->  x  (via assignment)
    #   x * 0   ->  0
    #   x ** 2  ->  x * x
    #   x / 1   ->  x
    # -----------------------------------------------------------------------
 
    def _strength_reduction(self, code: list[Instr]) -> list[Instr]:
        result = []
 
        for op, a1, a2, res in code:
            reduced = None
 
            if op == '*':
                v1, v2 = self._as_int(a1), self._as_int(a2)
                if v2 == 0 or v1 == 0:
                    reduced = ('=', '0', None, res)
                elif v2 == 1:
                    reduced = ('=', a1, None, res)
                elif v1 == 1:
                    reduced = ('=', a2, None, res)
                elif v2 == 2:
                    reduced = ('+', a1, a1, res)
                elif v1 == 2:
                    reduced = ('+', a2, a2, res)
 
            elif op == '/' and self._as_int(a2) == 1:
                reduced = ('=', a1, None, res)
 
            elif op == '**' and self._as_int(a2) == 2:
                reduced = ('*', a1, a1, res)
 
            elif op == '+':
                v1, v2 = self._as_int(a1), self._as_int(a2)
                if v1 == 0:
                    reduced = ('=', a2, None, res)
                elif v2 == 0:
                    reduced = ('=', a1, None, res)
 
            elif op == '-' and self._as_int(a2) == 0:
                reduced = ('=', a1, None, res)
 
            if reduced:
                self.log.append(
                    f"[StrReduce] {a1} {op} {a2} -> {res}  =>  {reduced}"
                )
                result.append(reduced)
            else:
                result.append((op, a1, a2, res))
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 6 — Loop invariant code motion (LICM)
    # Detect LOOP_BEGIN / LOOP_END markers and hoist invariant computations.
    #
    # Expected instruction forms:
    #   ('LOOP_BEGIN', None, None, None)
    #   ('LOOP_END',   None, None, None)
    # Everything between them is treated as a single loop body.
    # -----------------------------------------------------------------------
 
    def _loop_invariant_code_motion(self, code: list[Instr]) -> list[Instr]:
        result:  list[Instr] = []
        i = 0
 
        while i < len(code):
            op, a1, a2, res = code[i]
 
            if op != 'LOOP_BEGIN':
                result.append(code[i])
                i += 1
                continue
 
            # Collect the loop body
            j = i + 1
            loop_body: list[Instr] = []
            while j < len(code) and code[j][0] != 'LOOP_END':
                loop_body.append(code[j])
                j += 1
 
            # Variables defined inside the loop (may change each iteration)
            defined_in_loop: set[str] = {instr[3] for instr in loop_body if instr[3]}
 
            invariant:     list[Instr] = []
            new_loop_body: list[Instr] = []
 
            for instr in loop_body:
                iop, ia1, ia2, ires = instr
                deps = {x for x in (ia1, ia2) if x is not None and not self._is_literal(x)}
 
                # Invariant if: is a binary/unary op whose dependencies are all
                # either literals or variables defined OUTSIDE the loop
                if iop in ('+', '-', '*', '/', '%', '**', '=') and \
                   not (deps & defined_in_loop):
                    self.log.append(f"[LICM] hoisting: {iop} {ia1},{ia2}->{ires}")
                    invariant.append(instr)
                    defined_in_loop.discard(ires)   # no longer varies in loop
                else:
                    new_loop_body.append(instr)
 
            # Emit: hoisted code, then the slimmer loop
            result.extend(invariant)
            result.append(('LOOP_BEGIN', None, None, None))
            result.extend(new_loop_body)
            result.append(('LOOP_END', None, None, None))
 
            i = j + 1   # skip past LOOP_END
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 7 — Dead code elimination (DCE)
    # Remove instructions whose result is never subsequently used.
    # -----------------------------------------------------------------------
 
    def _dead_code_elimination(self, code: list[Instr]) -> list[Instr]:
        # Collect all used variables (= any arg that is not a literal)
        used: set[str] = set()
        for op, a1, a2, res in code:
            for arg in (a1, a2):
                if arg is not None and not self._is_literal(arg):
                    used.add(arg)
 
        result = []
        for instr in code:
            op, a1, a2, res = instr
            # Keep if: no result, result is used, it's a control-flow op, or
            # it could have side-effects (CALL, PRINT, etc.)
            if res is None or res in used or op in ('LOOP_BEGIN', 'LOOP_END',
                                                     'CALL', 'PRINT', 'RETURN'):
                result.append(instr)
            else:
                self.log.append(f"[DCE] removed dead: {op} {a1},{a2}->{res}")
 
        return result
 
    # -----------------------------------------------------------------------
    # Pass 8 — Peephole optimisation
    # Inspect a small sliding window and replace inefficient patterns:
    #   x = y followed immediately by y = x  ->  drop the second
    #   x = x                                ->  drop (self-assignment)
    #   x = 0; y = x + 0                    ->  handled by const propagation,
    #                                            but catch any stragglers here
    # -----------------------------------------------------------------------
 
    def _peephole_optimization(self, code: list[Instr]) -> list[Instr]:
        changed = True
        while changed:
            changed = False
            result: list[Instr] = []
            skip: set[int] = set()
 
            for i, instr in enumerate(code):
                if i in skip:
                    continue
 
                op, a1, a2, res = instr
 
                # Pattern: x = x  (self-assignment)
                if op == '=' and a1 == res and a2 is None:
                    self.log.append(f"[Peephole] dropped self-assignment: {res} = {a1}")
                    changed = True
                    continue
 
                # Pattern: t1 = t2 ; t2 = t1  (swap — drop the reverse copy)
                if i + 1 < len(code):
                    nop, na1, na2, nres = code[i + 1]
                    if op == '=' and nop == '=' and a2 is None and na2 is None:
                        if a1 == nres and na1 == res:
                            self.log.append(
                                f"[Peephole] dropped redundant swap: {nop} {na1}->{nres}"
                            )
                            result.append(instr)
                            skip.add(i + 1)
                            changed = True
                            continue
 
                # Pattern: add / sub 0 survivors
                if op in ('+', '-') and a2 is not None and self._as_int(a2) == 0:
                    self.log.append(f"[Peephole] {op} 0 is a no-op; replaced with copy")
                    result.append(('=', a1, None, res))
                    changed = True
                    continue
                if op == '+' and a1 is not None and self._as_int(a1) == 0:
                    self.log.append(f"[Peephole] 0 + x is a no-op; replaced with copy")
                    result.append(('=', a2, None, res))
                    changed = True
                    continue
 
                result.append(instr)
 
            code = result
 
        return code
 
    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
 
    @staticmethod
    def _is_literal(value: Optional[str]) -> bool:
        if value is None:
            return False
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
 
    def _as_int(self, value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        if self._is_literal(value):
            return int(value)
        return self.constants.get(value)
 
    @staticmethod
    def _eval(op: str, v1: int, v2: int) -> Optional[int]:
        try:
            if op == '+':  return v1 + v2
            if op == '-':  return v1 - v2
            if op == '*':  return v1 * v2
            if op == '/':  return v1 // v2
            if op == '%':  return v1 % v2
            if op == '**': return v1 ** v2
        except (ZeroDivisionError, OverflowError):
            pass
        return None
 
    @staticmethod
    def _resolve_copy(var: Optional[str], copies: dict[str, str]) -> Optional[str]:
        if var is None:
            return None
        # Follow the chain to the ultimate source
        seen = set()
        while var in copies and var not in seen:
            seen.add(var)
            var = copies[var]
        return var

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — TARGET CODE GENERATION (Assembly-like)
# ═══════════════════════════════════════════════════════════════════════════════

class TargetCodeGenerator:
    def __init__(self):
        self.num_regs = 13
        self.reg_used = [False] * self.num_regs
        self.var_reg = {}
        self.spill_order = []
        self.asm = []
    
    def alloc_reg(self):
        """Allocate a free register or spill"""
        for i in range(self.num_regs):
            if not self.reg_used[i]:
                self.reg_used[i] = True
                return f'R{i}'
        
        # Spill oldest register
        evict_var = self.spill_order.pop(0)
        evict_reg = self.var_reg.pop(evict_var)
        self.asm.append(f'ST {evict_var}, {evict_reg}')
        return evict_reg
    
    def get_reg(self, var):
        """Get register for variable"""
        if var in self.var_reg:
            return self.var_reg[var]
        r = self.alloc_reg()
        self.var_reg[var] = r
        self.spill_order.append(var)
        return r
    
    def generate(self, code):
        """Generate target code from optimized ICG"""
        for op, arg1, arg2, result in code:
            if op == '=':
                # mov instruction
                r = self.get_reg(result)
                self.asm.append(f'MOV {r}, #{arg1}')
            
            elif op == 'label':
                self.asm.append(f'{arg1}:')
            
            elif op == 'if_not':
                r = self.get_reg(arg1)
                self.asm.append(f'BNEQZ {r}, {arg2}')
            
            elif op in ['+', '-', '*', '/']:
                ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
                r1 = self.get_reg(arg1)
                r2 = self.get_reg(arg2)
                rd = self.get_reg(result)
                self.asm.append(f'{ops[op]} {rd}, {r1}, {r2}')
        
        # Flush remaining variables
        for var, reg in self.var_reg.items():
            if var[0] != 't':
                self.asm.append(f'ST {var}, {reg}')
        
        return self.asm

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN COMPILER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def get_token_category(token):
    """Categorize a token"""
    if token.type in ['IF', 'ELSE', 'WHILE', 'PRINT', 'TRUE', 'FALSE']:
        return 'KEYWORD'
    elif token.type == 'NUM':
        return 'NUMBER'
    elif token.type == 'ID':
        return 'IDENTIFIER'
    elif token.type in ['+', '-', '*', '/', '=', '>=', '<=', '>', '<', '==']:
        return 'OPERATOR'
    elif token.type in ['(', ')', ':', ',']:
        return 'DELIMITER'
    else:
        return 'OTHER'

def compile_program(source_code):
    print("\n" + "="*70)
    print(" MINI PYTHON COMPILER — 5 PHASES")
    print("="*70)
    
    # PHASE 1: LEXER
    print("\n┌─ PHASE 1: LEXER ────────────────────────────────────────────────┐")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    # Display tokens in tabular format
    print("│ Token Table (Lexical Analysis):                                │")
    print("├──────┬─────────────┬──────────────┬──────────────┤")
    print("│ No.  │ Token Type  │ Token Value  │ Category     │")
    print("├──────┼─────────────┼──────────────┼──────────────┤")
    
    for i, token in enumerate(tokens):
        if token.type == 'NL':
            continue  # Skip newlines for display
        category = get_token_category(token)
        value_display = token.value if len(str(token.value)) <= 12 else str(token.value)[:9] + "..."
        print(f"│ {i:<4} │ {token.type:<11} │ {value_display:<12} │ {category:<12} │")
    
    print("└──────┴─────────────┴──────────────┴──────────────┘")
    lexer.symbol_table.display()
    
    # PHASE 2: PARSER / AST
    print("\n┌─ PHASE 2: PARSER / AST ────────────────────────────────────────┐")
    parser = Parser(tokens)
    ast = parser.parse()
    print("│ Abstract Syntax Tree:                                          │")
    ast_str = str(ast).split('\n')
    for line in ast_str:
        print(f"│ {line:<65} │")
    print("└────────────────────────────────────────────────────────────────┘")
    
    # PHASE 3: ICG
    print("\n┌─ PHASE 3: ICG (Intermediate Code Generation) ──────────────────┐")
    codegen = CodeGenerator()
    icg = codegen.generate(ast)
    
    # Get different representations
    quadruples = codegen.get_quadruples()
    triples = codegen.get_triples()
    indirect_triples, index_table = codegen.get_indirect_triples()
    
    # Display QUADRUPLES
    print("│                                                                  │")
    print("│ 1. QUADRUPLES (op, arg1, arg2, result):                         │")
    print("├──────┬─────────┬──────────┬──────────┬──────────┤")
    print("│ Idx  │ Operator│ Arg1     │ Arg2     │ Result   │")
    print("├──────┼─────────┼──────────┼──────────┼──────────┤")
    for i, (op, arg1, arg2, result) in enumerate(quadruples):
        op_disp = op[:7] if len(op) <= 7 else op[:4]+"."
        arg1_d = str(arg1)[:8] if arg1 else "-"
        arg2_d = str(arg2)[:8] if arg2 else "-"
        res_d = str(result)[:8] if result else "-"
        print(f"│ {i:<4} │ {op_disp:<7} │ {arg1_d:<8} │ {arg2_d:<8} │ {res_d:<8} │")
    print("└──────┴─────────┴──────────┴──────────┴──────────┘")
    
    # Display TRIPLES
    print("│                                                                  │")
    print("│ 2. TRIPLES (op, arg1, arg2) - Result is index in array:         │")
    print("├──────┬─────────┬──────────┬──────────┐")
    print("│ Idx  │ Operator│ Arg1     │ Arg2     │")
    print("├──────┼─────────┼──────────┼──────────┤")
    for i, (op, arg1, arg2, idx) in enumerate(triples):
        op_disp = op[:7] if len(op) <= 7 else op[:4]+"."
        arg1_d = str(arg1)[:8] if arg1 else "-"
        arg2_d = str(arg2)[:8] if arg2 else "-"
        print(f"│ {i:<4} │ {op_disp:<7} │ {arg1_d:<8} │ {arg2_d:<8} │")
    print("└──────┴─────────┴──────────┴──────────┘")
    
    # Display INDIRECT TRIPLES
    print("│                                                                  │")
    print("│ 3. INDIRECT TRIPLES - Triples with Index Pointer Table:         │")
    print("│                                                                  │")
    print("│ Index Table:        Triples Table:                              │")
    print("├──────┬──────────┬──────┬─────────┬──────────┬──────────┐")
    print("│ Ptr  │ Instr#   │ Idx  │ Op      │ Arg1     │ Arg2     │")
    print("├──────┼──────────┼──────┼─────────┼──────────┼──────────┤")
    for i, (op, arg1, arg2) in enumerate(indirect_triples):
        ptr = index_table[i] if i < len(index_table) else i
        op_disp = op[:7] if len(op) <= 7 else op[:4]+"."
        arg1_d = str(arg1)[:8] if arg1 else "-"
        arg2_d = str(arg2)[:8] if arg2 else "-"
        print(f"│ {i:<4} │ {ptr:<8} │ {i:<4} │ {op_disp:<7} │ {arg1_d:<8} │ {arg2_d:<8} │")
    print("└──────┴──────────┴──────┴─────────┴──────────┴──────────┘")
    print("└────────────────────────────────────────────────────────────────┘")
    
    # PHASE 4: OPTIMIZED ICG
    print("\n┌─ PHASE 4: OPTIMIZED ICG (Quadruples Format) ───────────────────┐")
    optimizer = Optimizer(lexer.symbol_table)
    optimized_icg = optimizer.optimize(icg)
    
    # Get representations for optimized code
    opt_quadruples = optimized_icg
    opt_triples = [(op, arg1, arg2, i) for i, (op, arg1, arg2, result) in enumerate(optimized_icg)]
    
    print("│ Optimizations Applied: Constant Propagation + Constant Folding │")
    print("│                                                                  │")
    print("├──────┬─────────┬──────────┬──────────┬──────────┤")
    print("│ Idx  │ Operator│ Arg1     │ Arg2     │ Result   │")
    print("├──────┼─────────┼──────────┼──────────┼──────────┤")
    for i, (op, arg1, arg2, result) in enumerate(opt_quadruples):
        op_disp = op[:7] if len(op) <= 7 else op[:4]+"."
        arg1_d = str(arg1)[:8] if arg1 else "-"
        arg2_d = str(arg2)[:8] if arg2 else "-"
        res_d = str(result)[:8] if result else "-"
        print(f"│ {i:<4} │ {op_disp:<7} │ {arg1_d:<8} │ {arg2_d:<8} │ {res_d:<8} │")
    print("└──────┴─────────┴──────────┴──────────┴──────────┘")
    print("└────────────────────────────────────────────────────────────────┘")
    
    # PHASE 5: TARGET CODE
    print("\n┌─ PHASE 5: TARGET CODE GENERATION ──────────────────────────────┐")
    target_gen = TargetCodeGenerator()
    target_code = target_gen.generate(optimized_icg)
    print("│ Assembly-like Target Code:                                     │")
    for i, instr in enumerate(target_code):
        print(f"│  {i:2d}. {instr:<62} │")
    print("└────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "="*70)
    print(" COMPILATION COMPLETE")
    print("="*70 + "\n")
    
    return {
        'tokens': tokens,
        'ast': ast,
        'icg': icg,
        'triples': triples,
        'indirect_triples': indirect_triples,
        'index_table': index_table,
        'optimized_icg': optimized_icg,
        'target_code': target_code
    }

import webbrowser
import os

def generate_html_report(result):
    tokens_html = ""
    for i, token in enumerate(result['tokens']):
        if token.type != 'NL':
            category = get_token_category(token)
            tokens_html += f"<tr><td>{i}</td><td>{token.type}</td><td>{str(token.value)}</td><td>{category}</td></tr>"
            
    ast_html = "<pre>" + str(result['ast']).replace('<', '&lt;').replace('>', '&gt;') + "</pre>"
    
    icg_html = ""
    for i, (op, arg1, arg2, res) in enumerate(result['icg']):
        icg_html += f"<tr><td>{i}</td><td>{op}</td><td>{arg1}</td><td>{arg2}</td><td>{res}</td></tr>"
        
    triples_html = ""
    for i, (op, arg1, arg2, idx) in enumerate(result['triples']):
        triples_html += f"<tr><td>{i}</td><td>{op}</td><td>{arg1}</td><td>{arg2}</td></tr>"
        
    indirect_triples_html = ""
    index_table = result['index_table']
    for i, (op, arg1, arg2) in enumerate(result['indirect_triples']):
        ptr = index_table[i] if i < len(index_table) else i
        indirect_triples_html += f"<tr><td>{i}</td><td>{ptr}</td><td>{i}</td><td>{op}</td><td>{arg1}</td><td>{arg2}</td></tr>"
        
    opt_icg_html = ""
    for i, (op, arg1, arg2, res) in enumerate(result['optimized_icg']):
        opt_icg_html += f"<tr><td>{i}</td><td>{op}</td><td>{arg1}</td><td>{arg2}</td><td>{res}</td></tr>"
        
    target_html = ""
    for i, instr in enumerate(result['target_code']):
        target_html += f"<div>{i:2d}. {instr}</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini Python Compiler Report</title>
        <style>
            :root {{
                --bg: #0f172a;
                --surface: rgba(30, 41, 59, 0.7);
                --text: #f8fafc;
                --accent: #38bdf8;
                --border: rgba(255, 255, 255, 0.1);
            }}
            body {{
                font-family: 'Inter', system-ui, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 2rem;
                background-image: radial-gradient(circle at 50% 0%, #1e293b, #0f172a);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                text-align: center;
                background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                margin-bottom: 2rem;
            }}
            .tabs {{
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
                justify-content: center;
            }}
            .tab-btn {{
                background: var(--surface);
                border: 1px solid var(--border);
                color: var(--text);
                padding: 1rem 2rem;
                border-radius: 12px;
                cursor: pointer;
                font-size: 1.1rem;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }}
            .tab-btn.active, .tab-btn:hover {{
                background: rgba(56, 189, 248, 0.2);
                border-color: var(--accent);
                box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
                transform: translateY(-2px);
            }}
            .tab-content {{
                display: none;
                background: var(--surface);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 2rem;
                animation: fadeIn 0.4s ease-out;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            .tab-content.active {{
                display: block;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 1rem;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }}
            th {{
                color: var(--accent);
                font-weight: 600;
            }}
            tr:hover {{
                background: rgba(255,255,255,0.05);
            }}
            pre, .code-block {{
                font-family: 'Fira Code', monospace;
                background: rgba(0,0,0,0.3);
                padding: 1.5rem;
                border-radius: 8px;
                overflow-x: auto;
                line-height: 1.6;
            }}
            hr {{
                border: 0;
                border-top: 1px solid var(--border);
                margin: 3rem 0;
            }}
            .section-title {{
                color: var(--accent);
                font-size: 1.5rem;
                margin-top: 2rem;
                margin-bottom: 1rem;
                border-left: 4px solid var(--accent);
                padding-left: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mini Python Compiler Output</h1>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="showTab('lexer')">1. Lexer</button>
                <button class="tab-btn" onclick="showTab('ast')">2. AST Parser</button>
                <button class="tab-btn" onclick="showTab('icg')">3. ICG</button>
                <button class="tab-btn" onclick="showTab('opt')">4. Optimized ICG</button>
                <button class="tab-btn" onclick="showTab('target')">5. Target Code</button>
            </div>

            <div id="lexer" class="tab-content active">
                <h2>Lexical Analysis (Tokens)</h2>
                <table>
                    <tr><th>Index</th><th>Token Type</th><th>Value</th><th>Category</th></tr>
                    {tokens_html}
                </table>
            </div>

            <div id="ast" class="tab-content">
                <h2>Abstract Syntax Tree</h2>
                {ast_html}
            </div>

            <div id="icg" class="tab-content">
                <h2>Intermediate Code Generation</h2>
                
                <h3 class="section-title">1. Quadruples (op, arg1, arg2, result)</h3>
                <table>
                    <tr><th>Idx</th><th>Operator</th><th>Arg1</th><th>Arg2</th><th>Result</th></tr>
                    {icg_html}
                </table>
                
                <hr>
                
                <h3 class="section-title">2. Triples (op, arg1, arg2)</h3>
                <p style="opacity: 0.8; margin-bottom: 1rem;">Result is implicitly the index in the array.</p>
                <table>
                    <tr><th>Idx</th><th>Operator</th><th>Arg1</th><th>Arg2</th></tr>
                    {triples_html}
                </table>
                
                <hr>
                
                <h3 class="section-title">3. Indirect Triples</h3>
                <p style="opacity: 0.8; margin-bottom: 1rem;">Triples accessed via an Index Pointer Table.</p>
                <table>
                    <tr><th>Ptr</th><th>Instr#</th><th>Idx</th><th>Operator</th><th>Arg1</th><th>Arg2</th></tr>
                    {indirect_triples_html}
                </table>
            </div>

            <div id="opt" class="tab-content">
                <h2>Optimized ICG (Constant Folding & Propagation)</h2>
                <table>
                    <tr><th>Idx</th><th>Operator</th><th>Arg1</th><th>Arg2</th><th>Result</th></tr>
                    {opt_icg_html}
                </table>
            </div>

            <div id="target" class="tab-content">
                <h2>Assembly Target Code</h2>
                <div class="code-block">
                    {target_html}
                </div>
            </div>
        </div>

        <script>
            function showTab(tabId) {{
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                event.target.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
    
    with open('compiler_output.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("\\n\\n[+] Generated beautiful HTML report at 'compiler_output.html'")
    
    try:
        webbrowser.open('file://' + os.path.realpath('compiler_output.html'))
    except:
        pass

import sys

if __name__ == '__main__':
    # Get input file from command line, default to inp.py
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'inp.py'
    
    # Read input program
    with open(input_file, 'r') as f:
        source = f.read()
    
    # Run compiler
    result = compile_program(source)
    
    # Generate visual HTML report
    generate_html_report(result)
