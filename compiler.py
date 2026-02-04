import sys
import json

# Import all compiler stages
from lexer import tokenize
from parser import Parser, ParseError, pretty_print_ast
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from code_generator import CodeGenerator

def format_list_output(items, title):
    """Helper function to format list outputs for the results file."""
    if not items:
        return f"{title}:\n  (No output for this stage)"
    
    header = f"{title}:\n" + "-" * (len(title) + 1) + "\n"
    formatted_items = "\n".join(f"  {item}" for item in items)
    return header + formatted_items + "\n\n"

def format_errors(errors, title):
    """Helper function to format error lists."""
    if not errors:
        return ""  # No errors
    
    header = f"!!! {title} !!!\n" + "=" * (len(title) + 4) + "\n"
    formatted_errors = "\n".join(f"  - {e}" for e in errors)
    return header + formatted_errors + "\n\n"

def run_pipeline(source_code):
    """
    Runs the full compiler pipeline on the given source code.
    Returns a dictionary of results and a boolean success status.
    """
    results = {
        "tokens": "",
        "ast": "",
        "semantic_errors": "",
        "ir": "",
        "optimized_ir": "",
        "final_code": "",
        "errors": ""
    }
    
    all_errors = []

    # 1. Lexical Analysis
    try:
        tokens, lexer_errors = tokenize(source_code)
        results["tokens"] = "\n".join(map(str, tokens))
        if lexer_errors:
            all_errors.extend(lexer_errors)
            results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
            return results, False
    except Exception as e:
        all_errors.append(f"Lexer failed: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # 2. Syntax Analysis (Parsing)
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        results["ast"] = pretty_print_ast(ast)
        
        # Handle recoverable syntax errors
        if parser.errors:
            syntax_errors = [str(e) for e in parser.errors]
            all_errors.extend(syntax_errors)
            # We add to results but don't stop, to show recoverable errors
            results["errors"] = format_errors(all_errors, "COMPILATION CONTINUING WITH RECOVERED ERRORS")

    except ParseError as e:
        all_errors.append(f"Syntax Error: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False
    except Exception as e:
        all_errors.append(f"Parser failed: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # 3. Semantic Analysis
    try:
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        if semantic_analyzer.errors:
            all_errors.extend(str(e) for e in semantic_analyzer.errors)
            results["semantic_errors"] = format_errors(
                [str(e) for e in semantic_analyzer.errors], 
                "Semantic Errors"
            )
    except Exception as e:
        all_errors.append(f"Semantic Analyzer failed: {e}")
        # Continue to show previous errors if this stage fails
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # If there are any errors from any stage so far, stop.
    if all_errors:
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # 4. Intermediate Code Generation
    try:
        ir_gen = IRGenerator()
        ir_code = ir_gen.generate(ast)
        results["ir"] = "\n".join(ir_code)
    except Exception as e:
        all_errors.append(f"IR Generator failed: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # 5. Optimization
    try:
        optimizer = Optimizer()
        optimized_ir = optimizer.optimize(ir_code)
        results["optimized_ir"] = "\n".join(optimized_ir)
    except Exception as e:
        all_errors.append(f"Optimizer failed: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # 6. Final Code Generation
    try:
        code_gen = CodeGenerator()
        final_code = code_gen.generate(optimized_ir)
        results["final_code"] = "\n".join(final_code)
    except Exception as e:
        all_errors.append(f"Code Generator failed: {e}")
        results["errors"] = format_errors(all_errors, "COMPILATION FAILED")
        return results, False

    # If we got here, it's a success
    return results, True

def main():
    """
    Main function to run the compiler from the command line.
    """
    if len(sys.argv) != 3:
        print("Usage: python compiler.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    results, success = run_pipeline(source_code)

    # Write all results to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if not success:
                f.write(results["errors"])
                print(f"!!! COMPILATION FAILED !!!\nSee '{output_file}' for errors.")
            else:
                f.write("********** COMPILATION SUCCESSFUL **********\n\n")
                print(f"Compilation successful! See '{output_file}' for details.")

            f.write(format_list_output(results["tokens"].splitlines(), "1. Tokens"))
            f.write(format_list_output(results["ast"].splitlines(), "2. Abstract Syntax Tree (AST)"))
            
            if results["semantic_errors"]:
                f.write(results["semantic_errors"] + "\n")

            f.write(format_list_output(results["ir"].splitlines(), "3. Intermediate Representation (IR)"))
            f.write(format_list_output(results["optimized_ir"].splitlines(), "4. Optimized IR"))
            f.write(format_list_output(results["final_code"].splitlines(), "5. Final Code"))

    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

