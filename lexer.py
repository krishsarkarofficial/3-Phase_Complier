import re

# Token specs
# NOTE: Order matters. Multi-char ops must come BEFORE single-char ops.
TOKEN_SPECIFICATION = [
    ("NUMBER",   r'\d+(\.\d+)?'),       # int or float
    ("ID",       r'[A-Za-z_]\w*'),     # identifiers
    ("OP_REL",   r'==|!=|<=|>=|<|>'),  # Relational ops
    ("OP_ASSIGN",r'='),                # Assignment op
    ("OP_ARITH", r'[\+\-\*/]'),        # Arithmetic ops
    ("DELIM",    r'[(){};,]'),         # Delimiters
    ("NEWLINE",  r'\n'),               # Line breaks
    ("SKIP",     r'[ \t]+|//.*'),      # Spaces, tabs, and comments
    ("MISMATCH", r'.'),                # Anything else (error)
]

KEYWORDS = {"if", "else", "int", "float"}

# Build the master regex
token_regex_str = "|".join(
    f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION
)
token_regex = re.compile(token_regex_str)

class Token:
    """A simple class to hold token information."""
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', L{self.line})"

def tokenize(code):
    """
    Analyzes the source code and returns a list of Tokens and a list of Errors.
    """
    tokens = []
    errors = []
    line_num = 1

    for mo in token_regex.finditer(code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == "NUMBER":
            tokens.append(Token(kind, value, line_num))
        elif kind == "ID":
            if value in KEYWORDS:
                tokens.append(Token("KEYWORD", value, line_num))
            else:
                tokens.append(Token(kind, value, line_num))
        elif kind == "OP_REL":
            tokens.append(Token(kind, value, line_num))
        elif kind == "OP_ASSIGN":
            tokens.append(Token(kind, value, line_num))
        elif kind == "OP_ARITH":
            tokens.append(Token(kind, value, line_num))
        elif kind == "DELIM":
            tokens.append(Token(kind, value, line_num))
        elif kind == "NEWLINE":
            line_num += 1
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            errors.append(f"Lexical Error: Unexpected character '{value}' at line {line_num}")
    
    # Add an End-of-File token
    tokens.append(Token("EOF", "EOF", line_num))
    return tokens, errors

