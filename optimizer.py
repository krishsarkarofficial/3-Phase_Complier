class Optimizer:
    """
    Performs simple optimizations on the Intermediate Representation.
    Currently implements Constant Folding.
    """
    def __init__(self, ir_code):
        self.ir_code = ir_code

    def optimize(self):
        # In the future, multiple optimization passes can be added here
        self.constant_folding()
        return self.ir_code

    def is_numeric(self, s):
        if s is None: return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    def constant_folding(self):
        """
        Replaces arithmetic operations on constants with their results
        at compile time.
        """
        optimized_code = []
        for op, arg1, arg2, result in self.ir_code:
            if op in ('ADD', 'SUB', 'MUL', 'DIV') and self.is_numeric(arg1) and self.is_numeric(arg2):
                val1 = float(arg1)
                val2 = float(arg2)
                
                if op == 'ADD': new_val = val1 + val2
                elif op == 'SUB': new_val = val1 - val2
                elif op == 'MUL': new_val = val1 * val2
                elif op == 'DIV': new_val = val1 / val2 if val2 != 0 else 0
                
                # Keep it as an int if possible
                new_val = int(new_val) if new_val == int(new_val) else new_val
                
                # Replace the operation with a simple assignment
                optimized_code.append(('ASSIGN', str(new_val), None, result))
            else:
                optimized_code.append((op, arg1, arg2, result))
        self.ir_code = optimized_code
