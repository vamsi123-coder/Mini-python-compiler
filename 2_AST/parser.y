/* ── PARSER (Bison) ── Phase 2: Abstract Syntax Tree ──────────── */
/* Grammar rules that build a tree from the token stream          */

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define YYSTYPE char*

/* Tree node */
typedef struct Node {
    char *name;
    struct Node *left, *right;
} node;

node* newNode(char *n, node *l, node *r) {
    node *nd = malloc(sizeof(node));
    nd->name = strdup(n);
    nd->left = l; nd->right = r;
    return nd;
}

void printTree(node *n) {
    if (!n) return;
    printf("( %s ", n->name);
    printTree(n->left);
    printTree(n->right);
    printf(")");
}
%}

%token ID NUM STRING IF ELSE WHILE PRINT FOR IN RANGE
%token PLUS MINUS MUL DIVIDE EQUAL
%token GREATERTHANEQUAL LESSTHAN LESSTHANEQUAL GREATERTHAN DOUBLEEQUAL
%token NL INDENT COLON SPECIAL_START SPECIAL_END COMMA T F

%%

/* A program is a sequence of statements */
program : stmt_list          { printTree($1); }
        ;

stmt_list
    : stmt stmt_list         { $$ = newNode("SEQ", $1, $2); }
    |                        { $$ = newNode("NULL", NULL, NULL); }
    ;

stmt
    : ID EQUAL expr NL       { $$ = newNode("=",  newNode($1,0,0), $3); }
    | IF SPECIAL_START expr SPECIAL_END COLON NL body
                             { $$ = newNode("IF", $3, $7); }
    | WHILE SPECIAL_START expr SPECIAL_END COLON NL body
                             { $$ = newNode("WHILE", $3, $7); }
    | FOR ID IN RANGE SPECIAL_START expr SPECIAL_END COLON NL body
                             { $$ = newNode("FOR", newNode($2,0,0), $10); }
    ;

body
    : block_stmts            { $$ = $1; }
    ;

block_stmts
    : INDENT stmt block_stmts { $$ = newNode("SEQ", $2, $3); }
    | INDENT stmt             { $$ = $2; }
    ;

expr
    : expr PLUS  term        { $$ = newNode("+", $1, $3); }
    | expr MINUS term        { $$ = newNode("-", $1, $3); }
    | expr GREATERTHANEQUAL term { $$ = newNode(">=", $1, $3); }
    | expr LESSTHANEQUAL term { $$ = newNode("<=", $1, $3); }
    | expr GREATERTHAN term  { $$ = newNode(">", $1, $3); }
    | expr LESSTHAN term     { $$ = newNode("<", $1, $3); }
    | expr DOUBLEEQUAL term  { $$ = newNode("==", $1, $3); }
    | term                   { $$ = $1; }
    ;

term
    : term MUL factor        { $$ = newNode("*", $1, $3); }
    | term DIVIDE factor     { $$ = newNode("/", $1, $3); }
    | factor                 { $$ = $1; }
    ;

factor
    : NUM                    { $$ = newNode($1, NULL, NULL); }
    | ID                     { $$ = newNode($1, NULL, NULL); }
    | SPECIAL_START expr SPECIAL_END { $$ = $2; }
    ;

%%
