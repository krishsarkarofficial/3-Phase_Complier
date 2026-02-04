# 🧠 SimpleC: A Pedagogical Web-Based Compiler

**SimpleC** is an educational, multi-stage compiler for a small, C-like language.  
Its primary innovation is that it’s not just a command-line compiler — it’s a **full-stack web application** that visually demonstrates each stage of compilation.

---

## 🌐 Overview

SimpleC combines a **Python Flask backend** (running the compiler pipeline) with a **modern HTML/JavaScript frontend** that acts as an IDE.  

Users can write code, compile it, and instantly explore each phase of compilation through a tab-based interface — from **tokens and AST** to **final generated assembly**.

> ✨ The compiler also includes an **intelligent error-reporting engine** that gives _human-friendly suggestions_ for common syntax mistakes, instead of just stopping at the first error.

![SimpleC IDE Screenshot](screenshot.png)
*A screenshot of the SimpleC IDE frontend, showing the code editor on the left and tabbed output (Errors, AST, etc.) on the right.*

---

## ⚙️ Core Features

### 🧩 Full Compiler Pipeline

| Stage | File | Description |
|-------|------|-------------|
| **Lexer** | `lexer.py` | Scans the source code and produces tokens. |
| **Parser** | `parser.py` | Builds an Abstract Syntax Tree (AST). |
| **Semantic Analyzer** | `semantic_analyzer.py` | Checks for type errors and variable scopes. |
| **IR Generator** | `ir_generator.py` | Creates a Three-Address Code (TAC) representation. |
| **Optimizer** | `optimizer.py` | Performs basic optimizations (e.g., Constant Folding). |
| **Code Generator** | `code_generator.py` | Generates final x86-like assembly code. |

---

### 💻 Web-Based IDE (`compiler_frontend.html`)

- A sleek, modern code editor  
- Tabbed output view for **Tokens**, **AST**, **IR**, **Optimized IR**, and **Final Code**
- Real-time status updates (e.g., “✅ Compilation Successful!”)
- Intelligent error reporting with human-readable suggestions

---

### 🧠 Intelligent Error Reporting

Instead of stopping at the first syntax error, the compiler:
- Detects multiple errors in one run  
- Uses heuristics to provide **actionable suggestions**, e.g.  
  > `Did you forget a ';' after line 3?`

---

### 🖥️ Backend Server (`server.py`)

- Lightweight **Flask** server that hosts the web frontend  
- Exposes a `/compile` API endpoint to run the Python compiler pipeline on-demand  

---

## 🧮 Supported Language Features (SimpleC)

| Category | Features |
|-----------|-----------|
| **Data Types** | `int`, `float` |
| **Operators** | `+`, `-`, `*`, `/` |
| **Relational Operators** | `>`, `<`, `==`, `!=`, `>=`, `<=` |
| **Control Flow** | `if`, `else` |
| **Other** | `//` comments, variable assignments |

---

## 🚀 How to Run This Project

### 1️⃣ Install Dependencies

You’ll need **Python** and **pip** installed.  
Open your terminal in the project root and install:

```bash
pip install Flask
pip install flask-cors
