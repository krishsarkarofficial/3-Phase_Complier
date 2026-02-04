
------------------------------
 0. ORIGINAL SOURCE CODE
------------------------------
// This file tests the new error recovery features

int x = 10 // Missing semicolon

if (x > 5 { // Missing closing parenthesisx = 1;}

if (y > 2); { // Unexpected semicolony = 2;}

x = 5 // Missing semicolony = 10;

------------------------------
 1. LEXICAL ANALYSIS (TOKENS)
------------------------------
Token(KEYWORD, 'int', L3)
Token(ID, 'x', L3)
Token(OP, '=', L3)
Token(NUMBER, '10', L3)
Token(KEYWORD, 'if', L5)
Token(DELIM, '(', L5)
Token(ID, 'x', L5)
Token(OP, '>', L5)
Token(NUMBER, '5', L5)
Token(DELIM, '{', L5)
Token(KEYWORD, 'if', L7)
Token(DELIM, '(', L7)
Token(ID, 'y', L7)
Token(OP, '>', L7)
Token(NUMBER, '2', L7)
Token(DELIM, ')', L7)
Token(DELIM, ';', L7)
Token(DELIM, '{', L7)
Token(ID, 'x', L9)
Token(OP, '=', L9)
Token(NUMBER, '5', L9)
Token(EOF, '', L9)

------------------------------
 SYNTAX ERRORS
------------------------------
Syntax Error on line 5: Missing ';' after declaration. Encountered KEYWORD('if')
   -> Suggestion: Did you forget a ';' at the end of the declaration?
Syntax Error on line 5: Missing ')' after if-condition. Encountered '{'
   -> Suggestion: Did you forget a ')' before the '{'?
Syntax Error on line 7: Unexpected ';' after if-condition. This creates an empty 'if' statement.
   -> Suggestion: Did you mean to delete this ';'?
Syntax Error on line 9: Expected ';' after expression statement. Encountered EOF('')
Syntax Error on line 9: Missing '}' to close block. Encountered EOF('')
Syntax Error on line 9: Missing '}' to close block. Encountered EOF('')

------------------------------
 2. SYNTAX ANALYSIS (AST)
------------------------------
Program
  .children (List):
    [0]:
        VarDecl
          .type_node:
            Type [Value: int]
          .var_node:
            Variable [Value: x]
          .assign_node:
            Assign [Op: =]
              .left:
                Variable [Value: x]
              .right:
                Number [Value: 10]
    [1]:
        If
          .condition:
            BinOp [Op: >]
              .left:
                Variable [Value: x]
              .right:
                Number [Value: 5]
          .if_block:
            Block
              .statements (List):
                [0]:
                    If
                      .condition:
                        BinOp [Op: >]
                          .left:
                            Variable [Value: y]
                          .right:
                            Number [Value: 2]
                      .if_block:
                        Block
                          .statements (List):
                            [0]:
                                Assign [Op: =]
                                  .left:
                                    Variable [Value: x]
                                  .right:
                                    Number [Value: 5]


------------------------------
 SEMANTIC ERRORS
------------------------------
Semantic Error: Variable 'y' not declared on line 7
