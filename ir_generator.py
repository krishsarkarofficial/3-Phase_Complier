class IRGenerator:
    """
    Generates a simple Three-Address Code (TAC) representation
    from the CLASS-BASED Abstract Syntax Tree (AST).
    
    This version uses a more explicit visitor pattern to match the parser.py
    AST structure and avoid bugs from generic fallbacks.
    """
    def __init__(self):
        self.ir_code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        """Public method to start the IR generation process."""
        self.ir_code = []
        self.visit(node)
        return self.ir_code

    def visit(self, node):
        """
        Main visit method that dispatches to the correct specific
        visit method based on the node's class name.
        """
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
        """
        Visits the root 'Program' node.
        node.children = [statement1, statement2, ...]
        """
        for statement in node.children:
            self.visit(statement)

    def visit_VarDecl(self, node):
        """
        Visits a variable declaration.
        node.var_type (Token)
        node.var_name (Token)
        node.value (Node or None)
        """
        var_type = node.var_type.value
        var_name = node.var_name.value
        
        self.ir_code.append(f"DECLARE {var_type} {var_name}")

        if node.value is not None:
            # This is a declaration with assignment (e.g., int a = 10;)
            src = self.visit(node.value)
            self.ir_code.append(f"{var_name} = {src}")

    def visit_Assign(self, node):
        """
        Visits an assignment statement.
        node.var_name (Token)
        node.value (Node)
        """
        var_name = node.var_name.value
        src = self.visit(node.value)
        self.ir_code.append(f"{var_name} = {src}")

    def visit_If(self, node):
        """
        Visits an if-statement (with optional else).
        node.condition (Node)
        node.if_block (Block Node)
        node.else_block (Block Node or None)
        """
        
        # 1. Evaluate the condition
        condition_var = self.visit(node.condition)
        
        # 2. Create labels
        end_label = self.new_label()
        
        if node.else_block:
            # This is an if-else statement
            else_label = self.new_label()
            
            self.ir_code.append(f"IF_FALSE {condition_var} GOTO {else_label}")
            
            # 3. 'If' block
            self.visit(node.if_block)
            self.ir_code.append(f"GOTO {end_label}") # Skip the 'else' block
            
            # 4. 'Else' block
            self.ir_code.append(f"LABEL {else_label}")
            self.visit(node.else_block)
            
        else:
            # This is a simple 'if' statement (no else)
            self.ir_code.append(f"IF_FALSE {condition_var} GOTO {end_label}")
            
            # 3. 'If' block
            self.visit(node.if_block)
        
        # 5. End label
        self.ir_code.append(f"LABEL {end_label}")

    def visit_Block(self, node):
        """
        Visits a block of statements.
        node.children = [statement1, statement2, ...]
        """
        for statement in node.children:
            self.visit(statement)

    def visit_BinOp(self, node):
        """
        Visits a binary operation.
        node.left (Node)
        node.op (Token)
        node.right (Node)
        Returns the temporary variable holding the result.
        """
        left_src = self.visit(node.left)
        right_src = self.visit(node.right)
        op = node.op.value
        
        result_temp = self.new_temp()
        self.ir_code.append(f"{result_temp} = {left_src} {op} {right_src}")
        
        return result_temp

    def visit_RelOp(self, node):
        """
        Services a relational operation (e.g., >, <, ==).
        node.left (Node)
        node.op (Token)
        node.right (Node)
        Returns the temporary variable holding the boolean result.
        """
        left_src = self.visit(node.left)
        right_src = self.visit(node.right)
        op = node.op.value
        
        result_temp = self.new_temp()
        self.ir_code.append(f"{result_temp} = {left_src} {op} {right_src}")
        
        return result_temp

    def visit_Number(self, node):
        """
        Visits a literal number.
        node.value (str)
        """
        return node.value

    def visit_Id(self, node):
        """
        Visits an identifier (variable name).
        node.value (str)
        """
        return node.value

