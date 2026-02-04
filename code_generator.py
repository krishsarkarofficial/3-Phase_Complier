class CodeGenerator:
    """
    Generates hypothetical x86-like assembly code from the Intermediate Representation (IR).
    This version handles declarations, assignments, arithmetic, type casting,
    and conditional logic (if/else).
    This version correctly handles literals in binary operations and float jumps.
    """
    def __init__(self, ir):
        self.ir = ir
        self.assembly = []
        self.symbol_table = {}  # {name: {type: 'int'/'float', offset: -4, -8, etc.}}
        self.current_offset = 0 # Stack offset for local vars
        self.float_labels = {}  # Stores labels for float constants
        self.float_label_count = 0
        self.data_section = ["section .data"]
        self.text_section = []

    def get_var_offset(self, var_name):
        """Gets the stack offset for a variable."""
        if var_name not in self.symbol_table:
            # This should ideally not happen if semantic analysis is correct
            self.current_offset -= 4
            self.symbol_table[var_name] = {'type': 'unknown', 'offset': self.current_offset}
        return self.symbol_table[var_name]['offset']

    def get_var_type(self, var_name):
        """Gets the type of a variable."""
        if var_name in self.symbol_table:
            return self.symbol_table[var_name]['type']
        return 'unknown' # Fallback

    def get_float_label(self, float_val):
        """Gets or creates a data-section label for a float constant."""
        if float_val not in self.float_labels:
            label = f"__float_{self.float_label_count}"
            self.float_labels[float_val] = label
            self.float_label_count += 1
            # Add to data section
            self.data_section.append(f"    {label} dd {float_val}")
        return self.float_labels[float_val]

    def is_int_literal(self, val):
        return val.isdigit() or (val.startswith('-') and val[1:].isdigit())

    def is_float_literal(self, val):
        return '.' in val

    def generate(self):
        """Generates the assembly code from the IR list."""
        self.text_section = [
            "section .text",
            "global _start",
            "_start:",
            "    push ebp",
            "    mov ebp, esp",
            "    ; --- Begin user code ---"
        ]

        # Pre-scan for float literals in data section
        for line in self.ir:
            parts = line.split()
            if not parts: continue
            op = parts[0]
            if op == "ASSIGN":
                if self.is_float_literal(parts[2]):
                    self.get_float_label(parts[2]) # This pre-populates data_section
            elif op in ("ADD", "SUB", "MUL", "DIV"):
                if self.is_float_literal(parts[3]):
                    self.get_float_label(parts[3])
                if self.is_float_literal(parts[4]):
                    self.get_float_label(parts[4])

        # Main generation loop
        for i, line in enumerate(self.ir):
            parts = line.split()
            if not parts:
                continue
            
            op = parts[0]

            try:
                if op == "DECLARE":
                    var_type = parts[1]
                    var_name = parts[2]
                    self.current_offset -= 4
                    self.symbol_table[var_name] = {'type': var_type, 'offset': self.current_offset}
                    self.text_section.append(f"    sub esp, 4  ; Allocate space for {var_name} (type: {var_type}) at [ebp{self.current_offset}]")

                elif op == "ASSIGN":
                    var_name = parts[1]
                    value = parts[2]
                    var_info = self.symbol_table[var_name]
                    offset = var_info['offset']

                    if var_info['type'] == 'int':
                        if self.is_int_literal(value):
                            self.text_section.append(f"    mov dword [ebp{offset}], {value}")
                        else:
                            val_offset = self.get_var_offset(value)
                            self.text_section.append(f"    mov eax, dword [ebp{val_offset}]")
                            self.text_section.append(f"    mov dword [ebp{offset}], eax")
                    
                    elif var_info['type'] == 'float':
                        if self.is_float_literal(value):
                            label = self.get_float_label(value)
                            self.text_section.append(f"    fld dword [{label}]")
                            self.text_section.append(f"    fstp dword [ebp{offset}]")
                        else:
                            val_offset = self.get_var_offset(value)
                            self.text_section.append(f"    fld dword [ebp{val_offset}]")
                            self.text_section.append(f"    fstp dword [ebp{offset}]")

                elif op in ("ADD", "SUB", "MUL", "DIV"):
                    op_type, dest, src1, src2 = parts[1], parts[2], parts[3], parts[4]
                    dest_offset = self.get_var_offset(dest)

                    if op_type == 'int':
                        # Load src1 into eax
                        if self.is_int_literal(src1):
                            self.text_section.append(f"    mov eax, {src1}")
                        else:
                            self.text_section.append(f"    mov eax, dword [ebp{self.get_var_offset(src1)}]")
                        
                        # Load src2 into ebx
                        if self.is_int_literal(src2):
                            self.text_section.append(f"    mov ebx, {src2}")
                        else:
                            self.text_section.append(f"    mov ebx, dword [ebp{self.get_var_offset(src2)}]")

                        if op == "ADD": self.text_section.append("    add eax, ebx")
                        elif op == "SUB": self.text_section.append("    sub eax, ebx")
                        elif op == "MUL": self.text_section.append("    imul eax, ebx")
                        elif op == "DIV":
                            self.text_section.append("    cdq")
                            self.text_section.append("    idiv ebx")
                        
                        self.text_section.append(f"    mov dword [ebp{dest_offset}], eax")

                    elif op_type == 'float':
                        # Load src1 onto FPU stack
                        if self.is_float_literal(src1):
                            self.text_section.append(f"    fld dword [{self.get_float_label(src1)}]")
                        else:
                            self.text_section.append(f"    fld dword [ebp{self.get_var_offset(src1)}]")
                        
                        # Load src2 onto FPU stack
                        if self.is_float_literal(src2):
                            self.text_section.append(f"    fld dword [{self.get_float_label(src2)}]")
                        else:
                            self.text_section.append(f"    fld dword [ebp{self.get_var_offset(src2)}]")
                        
                        if op == "ADD": self.text_section.append("    faddp st(1), st(0)")
                        elif op == "SUB": self.text_section.append("    fsubp st(1), st(0)")
                        elif op == "MUL": self.text_section.append("    fmulp st(1), st(0)")
                        elif op == "DIV": self.text_section.append("    fdivp st(1), st(0)")
                        
                        self.text_section.append(f"    fstp dword [ebp{dest_offset}]")
                
                elif op == "CAST_TO_FLOAT":
                    dest, src = parts[1], parts[2]
                    self.text_section.append(f"    fild dword [ebp{self.get_var_offset(src)}]")
                    self.text_section.append(f"    fstp dword [ebp{self.get_var_offset(dest)}]")

                elif op == "COMPARE":
                    cmp_type, src1, cmp_op, src2 = parts[1], parts[2], parts[3], parts[4]
                    
                    if cmp_type == 'int':
                        self.text_section.append(f"    mov eax, dword [ebp{self.get_var_offset(src1)}]")
                        if self.is_int_literal(src2):
                            self.text_section.append(f"    mov ebx, {src2}")
                        else:
                            self.text_section.append(f"    mov ebx, dword [ebp{self.get_var_offset(src2)}]")
                        self.text_section.append("    cmp eax, ebx")
                    
                    elif cmp_type == 'float':
                        self.text_section.append(f"    fld dword [ebp{self.get_var_offset(src1)}]")
                        if self.is_float_literal(src2):
                            self.text_section.append(f"    fld dword [{self.get_float_label(src2)}]")
                        else:
                             self.text_section.append(f"    fld dword [ebp{self.get_var_offset(src2)}]")
                        self.text_section.append("    fcomip st(0), st(1)")
                        self.text_section.append("    fstp st(0)")

                elif op == "JUMP":
                    self.text_section.append(f"    jmp {parts[1]}")

                elif op == "JUMP_IF_FALSE":
                    prev_line = self.ir[i - 1]
                    prev_parts = prev_line.split()
                    cmp_type = prev_parts[1]
                    cmp_op = prev_parts[3]
                    
                    jump_op = ""
                    if cmp_type == 'int':
                        if cmp_op == "==": jump_op = "jne"
                        elif cmp_op == "!=": jump_op = "je"
                        elif cmp_op == ">":  jump_op = "jle"
                        elif cmp_op == ">=": jump_op = "jl"
                        elif cmp_op == "<":  jump_op = "jge"
                        elif cmp_op == "<=": jump_op = "jg"
                    elif cmp_type == 'float':
                        # Use unsigned jumps for float comparisons
                        if cmp_op == "==": jump_op = "jne" # Not equal
                        elif cmp_op == "!=": jump_op = "je"  # Equal
                        elif cmp_op == ">":  jump_op = "jbe" # Below or equal
                        elif cmp_op == ">=": jump_op = "jb"  # Below
                        elif cmp_op == "<":  jump_op = "jae" # Above or equal
                        elif cmp_op == "<=": jump_op = "ja"  # Above
                    
                    self.text_section.append(f"    {jump_op} {parts[1]} ; Jump if {cmp_op} was false")

                elif op == "LABEL":
                    self.text_section.append(f"{parts[1]}:")

            except Exception as e:
                self.text_section.append(f"\n    ; !!! ERROR GENERATING CODE FOR: '{line}' -> {e} !!!\n")

        self.text_section.extend([
            "    ; --- End of user code ---",
            "    mov esp, ebp",
            "    pop ebp",
            "    mov eax, 1",
            "    xor ebx, ebx",
            "    int 0x80"
        ])
        
        self.assembly = self.text_section
        if len(self.data_section) > 1:
            self.assembly.extend(self.data_section)

        return "\n".join(self.assembly)

