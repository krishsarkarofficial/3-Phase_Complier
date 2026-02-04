class SemanticError(Exception):
    """Custom exception for semantic errors."""
    def __init__(self, message, line):
        super().__init__(f"Semantic Error on line {line}: {message}")
        self.line = line

class SymbolTable:
    """A simple symbol table with basic scope management."""
    def __init__(self):
        # A stack of dictionaries, where each dict is a scope
        self.scopes = [{}] 

    def enter_scope(self):
        """Enter a new, nested scope."""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            print("Warning: Cannot exit global scope.")

    def declare(self, name, type, line):
        """Declare a variable in the current scope."""
        scope = self.scopes[-1]
        if name in scope:
            raise SemanticError(f"Variable '{name}' already declared in this scope.", line)
        scope[name] = type

    def lookup(self, name, line):
        """Look up a variable's type, searching from inner to outer scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variable '{name}' not declared.", line)

class SemanticAnalyzer:
    """
    Walks the class-based AST to perform semantic checks, such as
    type checking and variable declaration.
    """
    def __init__(self):
        self.sym_table = SymbolTable()
        self.errors = []

    def analyze(self, node, errors):
        """Public method to start analysis."""
        self.errors = errors # Use the error list from the parser
        try:
            self.visit(node)
        except SemanticError as e:
            self.errors.append(str(e))
        
        # We return the data type of the "main" program, which is 'void'
        return 'void'

    def visit(self, node):
        """Main dispatch method, matches the new IRGenerator."""
        if node is None:
            return None
            
        class_name = node.__class__.__name__
        
        if class_name == 'Program':
            return self.visit_Program(node)
        elif class_name == 'VarDecl':
            return self.visit_VarDecl(node)
        elif class_name == 'Assign':
            return self.visit_Assign(node)
        elif class_name == 'If':
            return self.visit_If(node)
        elif class_name == 'Block':
            return self.visit_Block(node)
        elif class_name == 'BinOp':
            return self.visit_BinOp(node)
        elif class_name == 'RelOp':
            return self.visit_RelOp(node)
        elif class_name == 'Number':
            return self.visit_Number(node)
        elif class_name == 'Id':
            return self.visit_Id(node)
        else:
            raise TypeError(f"Unknown node type: {class_name}")

    def visit_Program(self, node):
        for statement in node.children:
            self.visit(statement)
        return 'void'

    def visit_Block(self, node):
        self.sym_table.enter_scope()
        for statement in node.children:
            self.visit(statement)
        self.sym_table.exit_scope()
        return 'void'

    def visit_VarDecl(self, node):
        var_name = node.var_name.value
        var_type = node.var_type.value
        line = node.var_name.line

        self.sym_table.declare(var_name, var_type, line)

        if node.value is not None:
            # Declaration with assignment (e.g., int a = 10;)
            value_type = self.visit(node.value)
            if var_type != value_type:
                raise SemanticError(f"Cannot assign type '{value_type}' to variable '{var_name}' of type '{var_type}'.", line)
        return 'void'

    def visit_Assign(self, node):
        var_name = node.var_name.value
        line = node.var_name.line
        
        # Check if declared
        var_type = self.sym_table.lookup(var_name, line)
        
        # Check type of value
        value_type = self.visit(node.value)
        
        if var_type != value_type:
            raise SemanticError(f"Cannot assign type '{value_type}' to variable '{var_name}' of type '{var_type}'.", line)
        return 'void'

    def visit_If(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            # Note: Our RelOp returns 'bool', but a plain 'int' is not a bool
            raise SemanticError(f"If condition must be a boolean expression (e.g., a > b), but got '{condition_type}'.", node.condition.op.line)
        
        self.visit(node.if_block)
        if node.else_block:
            self.visit(node.else_block)
        return 'void'

    def visit_BinOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        line = node.op.line

        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            raise SemanticError(f"Arithmetic operation '{node.op.value}' can only be used on numbers, not '{left_type}' and '{right_type}'.", line)
        
        # Type promotion: int + float = float
        if 'float' in (left_type, right_type):
            return 'float'
        return 'int'

    def visit_RelOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        line = node.op.line

        if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
            raise SemanticError(f"Relational operation '{node.op.value}' can only be used on numbers, not '{left_type}' and '{right_type}'.", line)
        
        # Relational operations always return a boolean
        return 'bool'

    def visit_Number(self, node):
        if '.' in node.value:
            return 'float'
        return 'int'

    def visit_Id(self, node):
        # Return the type of the variable from the symbol table
        return self.sym_table.lookup(node.value, node.line)

