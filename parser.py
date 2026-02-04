# Abstract Syntax Tree (AST) Node definitions
class AST: pass

# --- NEW PARSE ERROR CLASS ---
# This class will hold the error message and an optional suggestion.
class ParseError(Exception):
    def __init__(self, message, line, suggestion=None):
        self.message = message
        self.line = line
        self.suggestion = suggestion
    
    def __str__(self):
        # Format the error message with the suggestion if one exists
        if self.suggestion:
            return f"Syntax Error on line {self.line}: {self.message}\n   -> Suggestion: {self.suggestion}"
        return f"Syntax Error on line {self.line}: {self.message}"

# --- AST Node definitions (unchanged) ---
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Number(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Variable(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class VarDecl(AST):
    def __init__(self, type_node, var_node, assign_node=None):
        self.type_node = type_node
        self.var_node = var_node
        self.assign_node = assign_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class If(AST):
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

class Block(AST):
    def __init__(self):
        self.statements = []

class Program(AST):
    def __init__(self):
        self.children = []

# Parser implementation
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.errors = [] # This will now store ParseError objects

    def error(self, message, suggestion=None):
        # --- MODIFIED ERROR METHOD ---
        # This now creates a ParseError object
        err = ParseError(
            f"{message}. Encountered {self.current_token.type}('{self.current_token.value}')",
            self.current_token.line,
            suggestion
        )
        self.errors.append(err)
        
        # Simple error recovery: advance until a potential statement boundary
        # This helps prevent a cascade of errors.
        while self.current_token.type != 'EOF' and self.current_token.value not in [';', '}', ')']:
             self.advance()
        # If we're at a ';', consume it.
        if self.current_token.value == ';':
            self.advance()

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = self.tokens[-1] # Stay at EOF

    def eat(self, token_type, token_value=None):
        if self.current_token.type == token_type and \
           (token_value is None or self.current_token.value == token_value):
            self.advance()
        else:
            expected = f"'{token_value}'" if token_value else token_type
            # Create a ParseError, but don't add a suggestion by default.
            err = ParseError(
                f"Expected {expected}, but found {self.current_token.type}('{self.current_token.value}')",
                self.current_token.line
            )
            self.errors.append(err)
            # Advance to prevent infinite loops, but this is a hard error.
            if self.current_token.type != 'EOF':
                self.advance()


    def program(self):
        """program : (declaration | statement)*"""
        node = Program()
        while self.current_token.type != "EOF":
            if self.current_token.value in ['int', 'float']:
                node.children.extend(self.declaration())
            else:
                node.children.append(self.statement())
        return node

    def declaration(self):
        """declaration : type_specifier ID ('=' expression)? (',' ID ('=' expression)?)* ';'"""
        declarations = []
        type_node = self.type_specifier()
        while self.current_token.type == 'ID':
            var_node = self.variable()
            assign_node = None
            if self.current_token.value == '=':
                op = self.current_token
                self.eat('OP', '=')
                expr_node = self.expression()
                assign_node = Assign(var_node, op, expr_node)
            declarations.append(VarDecl(type_node, var_node, assign_node))
            if self.current_token.value == ',':
                 self.eat('DELIM', ',')
                 continue
            break
        
        # --- MODIFIED SEMICOLON HANDLING ---
        if self.current_token.value == ';':
            self.eat('DELIM', ';')
        else:
            # Heuristic: If the next token looks like the start of a new
            # statement, we assume a semicolon was forgotten.
            if self.current_token.type in ('KEYWORD', 'ID') or self.current_token.value in ('{', '}', 'EOF'):
                suggestion = "Did you forget a ';' at the end of the declaration?"
                err = ParseError(
                    f"Missing ';' after declaration. Encountered {self.current_token.type}('{self.current_token.value}')",
                    self.current_token.line,
                    suggestion
                )
                self.errors.append(err)
                # DO NOT ADVANCE. We "recover" by assuming the semicolon was
                # there, and let the parser continue from the current token.
            else:
                # This is a more confusing error, report it normally.
                self.error("Expected ';' after declaration")
        
        return declarations

    def type_specifier(self):
        """type_specifier : 'int' | 'float'"""
        token = self.current_token
        if token.value in ('int', 'float'):
            self.eat('KEYWORD', token.value)
            return Type(token)
        # Use simple error reporting for this one
        err = ParseError(
            f"Expected a type specifier (e.g., int, float), but found {token.type}('{token.value}')",
            token.line
        )
        self.errors.append(err)
        # Return a dummy type to prevent further crashes
        return Type(Token('KEYWORD', 'int', token.line))


    def statement(self):
        """statement : if_statement | block | expression_statement"""
        if self.current_token.value == 'if':
            return self.if_statement()
        elif self.current_token.value == '{':
            return self.block()
        else:
            # Expression statement (e.g., an assignment)
            node = self.expression()
            
            # --- MODIFIED SEMICOLON HANDLING ---
            if self.current_token.value == ';':
                self.eat('DELIM', ';')
            else:
                # Heuristic: If the next token looks like the start of a new
                # statement, we assume a semicolon was forgotten.
                if self.current_token.type in ('KEYWORD', 'ID') or self.current_token.value in ('{', '}', 'EOF'):
                    suggestion = "Did you forget a ';' at the end of the statement?"
                    err = ParseError(
                        f"Missing ';' after statement. Encountered {self.current_token.type}('{self.current_token.value}')",
                        self.current_token.line,
                        suggestion
                    )
                    self.errors.append(err)
                    # DO NOT ADVANCE. Recover by assuming the semicolon was there.
                else:
                    # This is a more confusing error, report it normally.
                    self.error("Expected ';' after expression statement")
            
            return node

    def if_statement(self):
        """if_statement : 'if' '(' expression ')' statement ('else' statement)?"""
        self.eat('KEYWORD', 'if')
        self.eat('DELIM', '(')
        condition = self.expression()
        
        # --- NEW HEURISTIC: Missing ')' ---
        if self.current_token.value == ')':
            self.eat('DELIM', ')')
        elif self.current_token.value == '{':
            # This is a common error: if (x > 1 { ...
            suggestion = "Did you forget a ')' before the '{'?"
            err = ParseError(
                f"Missing ')' after if-condition. Encountered '{self.current_token.value}'",
                self.current_token.line,
                suggestion
            )
            self.errors.append(err)
            # Recover by "virtually" inserting the ')' and continuing.
        else:
            # A different error, report it normally.
            self.error("Expected ')' after if-condition")

        # --- NEW HEURISTIC: Unexpected ';' ---
        if_block = None
        if self.current_token.value == ';':
            # This is a common error: if (x > 1); { ...
            suggestion = "Did you mean to delete this ';'?"
            err = ParseError(
                f"Unexpected ';' after if-condition. This creates an empty 'if' statement.",
                self.current_token.line,
                suggestion
            )
            self.errors.append(err)
            # Recover by "deleting" (eating) the semicolon and parsing
            # the *next* statement, which is what the user probably intended.
            self.eat('DELIM', ';')
            if_block = self.statement()
        else:
            if_block = self.statement()
        
        else_block = None
        if self.current_token.value == 'else':
            self.eat('KEYWORD', 'else')
            else_block = self.statement()
        
        return If(condition, if_block, else_block)

    def block(self):
        """block : '{' statement* '}'"""
        self.eat('DELIM', '{')
        node = Block()
        while self.current_token.value != '}' and self.current_token.type != 'EOF':
             node.statements.append(self.statement())
        if self.current_token.value == '}':
            self.eat('DELIM', '}')
        else:
            # Report a simple error, but don't add a suggestion
            # as it's hard to guess what the user meant.
            err = ParseError(
                f"Missing '}}' to close block. Encountered {self.current_token.type}('{self.current_token.value}')",
                self.current_token.line
            )
            self.errors.append(err)
        return node

    def expression(self):
        """expression : assignment"""
        # Check for assignment: ID = ...
        if self.current_token.type == 'ID' and self.tokens[self.pos + 1].value == '=':
             var_node = self.variable()
             op = self.current_token
             self.eat('OP', '=')
             expr = self.expression()
             return Assign(var_node, op, expr)
        return self.comparison()

    def comparison(self):
        """comparison : term (('>' | '<' | '==' | '!=' | '>=' | '<=') term)*"""
        node = self.term()
        while self.current_token.value in ('>', '<', '==', '!=', '>=', '<='):
            op = self.current_token
            self.eat('OP', op.value)
            node = BinOp(left=node, op=op, right=self.term())
        return node

    def term(self):
        """term : factor (('+' | '-') factor)*"""
        node = self.factor()
        while self.current_token.value in ('+', '-'):
            op = self.current_token
            self.eat('OP', op.value)
            node = BinOp(left=node, op=op, right=self.factor())
        return node

    def factor(self):
        """factor : primary (('*' | '/') primary)*"""
        node = self.primary()
        while self.current_token.value in ('*', '/'):
            op = self.current_token
            self.eat('OP', op.value)
            node = BinOp(left=node, op=op, right=self.primary())
        return node

    def primary(self):
        """primary : NUMBER | ID | '(' expression ')'"""
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(token)
        elif token.type == 'ID':
            return self.variable()
        elif token.value == '(':
            self.eat('DELIM', '(')
            node = self.expression()
            self.eat('DELIM', ')')
            return node
        else:
            # This is a hard error, can't really guess.
            err = ParseError(
                f"Invalid syntax in expression. Expected number, variable, or '('.",
                token.line
            )
            self.errors.append(err)
            # Return dummy node to prevent crashes
            return Number(Token('NUMBER', '0', token.line)) 

    def variable(self):
        """variable : ID"""
        node = Variable(self.current_token)
        self.eat('ID')
        return node

    def parse(self):
        ast = self.program()
        if self.current_token.type != 'EOF' and not self.errors:
             err = ParseError(
                "Unexpected tokens at end of file.",
                self.current_token.line
             )
             self.errors.append(err)
        return ast, self.errors

def pretty_print_ast(node, level=0):
    if not isinstance(node, AST): return ""
    
    indent = "  " * level
    result = f"{indent}{node.__class__.__name__}"

    # Add specific details for simple nodes
    if hasattr(node, 'value'):
        result += f" [Value: {node.value}]"
    if hasattr(node, 'op') and node.op is not None:
        result += f" [Op: {node.op.value}]"
    
    result += "\n"

    # Recursively print children
    for attr, value in node.__dict__.items():
        if attr in ['token', 'op', 'value']: # Skip primitive attributes
            continue
        
        if isinstance(value, AST):
            result += f"{indent}  .{attr}:\n"
            result += pretty_print_ast(value, level + 2)
        elif isinstance(value, list):
            result += f"{indent}  .{attr} (List):\n"
            for i, item in enumerate(value):
                if isinstance(item, AST):
                    result += f"{indent}    [{i}]:\n"
                    result += pretty_print_ast(item, level + 4)
    return result

