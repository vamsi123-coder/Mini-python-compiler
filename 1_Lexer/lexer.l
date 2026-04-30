/* ── LEXER (Flex) ── Phase 1: Tokenizer ──────────────────────── */
/* Turns raw Python source text → stream of tokens               */

%{
#include "y.tab.h"   /* token names from parser */
%}

%%

/* Keywords */
if          { return IF;    }
else        { return ELSE;  }
while       { return WHILE; }
for         { return FOR;   }
in          { return IN;    }
range       { return RANGE; }
print       { return PRINT; }
True        { return T;     }
False       { return F;     }

/* Operators */
"+"   { return PLUS;   }
"-"   { return MINUS;  }
"*"   { return MUL;    }
"/"   { return DIVIDE; }
"="   { return EQUAL;  }
">="  { return GREATERTHANEQUAL; }
"<="  { return LESSTHANEQUAL;    }
">"   { return GREATERTHAN;      }
"<"   { return LESSTHAN;         }
"=="  { return DOUBLEEQUAL;      }

/* Literals & Identifiers */
[0-9]+(\.[0-9]+)?       { yylval = strdup(yytext); return NUM; }
[a-zA-Z_][a-zA-Z0-9_]* { yylval = strdup(yytext); return ID;  }
\".*\"                  { yylval = strdup(yytext); return STRING; }

/* Structure */
"\n"  { return NL;     }
"\t"  { return INDENT; }
"("   { return SPECIAL_START; }
")"   { return SPECIAL_END;   }
":"   { return COLON;  }
","   { return COMMA;  }

%%
int yywrap() { return 1; }
