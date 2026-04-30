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
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.constants = {}
    
    def optimize(self, code):
        """Apply constant propagation and folding"""
        optimized = []
        
        for op, arg1, arg2, result in code:
            # Constant propagation
            if op == '=':
                try:
                    value = int(arg1)
                    self.constants[result] = value
                    optimized.append((op, arg1, arg2, result))
                except:
                    optimized.append((op, arg1, arg2, result))
            
            # Constant folding for binary operations
            elif op in ['+', '-', '*', '/']:
                new_arg1 = str(self.constants.get(arg1, arg1))
                new_arg2 = str(self.constants.get(arg2, arg2))
                
                try:
                    val1, val2 = int(new_arg1), int(new_arg2)
                    if op == '+': folded = val1 + val2
                    elif op == '-': folded = val1 - val2
                    elif op == '*': folded = val1 * val2
                    elif op == '/': folded = val1 // val2
                    
                    self.constants[result] = folded
                    optimized.append((op, new_arg1, new_arg2, result))
                except:
                    optimized.append((op, arg1, arg2, result))
            
            else:
                optimized.append((op, arg1, arg2, result))
        
        return optimized

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
