# simp_sexp

A simple S-expression parser for Python.

## Features

- Simple and lightweight S-expression parser
- Parse and manipulate S-expressions with an intuitive object-oriented interface
- Convert between string representations and Python data structures
- Nested expressions are handled automatically
- Pretty-printing support for readable output
- Advanced search capabilities for finding elements within complex S-expressions
- Support for quoted strings with proper escape handling
- Automatic type conversion for numbers

## Installation

```bash
pip install simp_sexp
```

## Usage

### Basic Parsing and Formatting

```python
from simp_sexp import Sexp, prettify_sexp

# Parse a string into an S-expression
expr = Sexp("(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))")
print(expr)
# Output: ['define', ['factorial', 'n'], ['if', ['=', 'n', 0], 1, ['*', 'n', ['factorial', ['-', 'n', 1]]]]]

# Convert an S-expression back to a string
s_expr = expr.to_str()
print(s_expr)
# Output: (define (factorial "n") (if (= "n" 0) 1 (* "n" (factorial (- "n" 1)))))

# Format with pretty printing (default behavior)
pretty = expr.to_str(indent=4)
print(pretty)
"""
Output:
(define
    (factorial "n")
    (if
        (= "n" 0)
        1
        (* "n" (factorial (- "n" 1)))))
"""

# Format without line breaks
compact = expr.to_str(break_inc=0)
print(compact)
# Output: (define (factorial "n") (if (= "n" 0) 1 (* "n" (factorial (- "n" 1)))))
```

### Working with Simple Expressions

```python
from simp_sexp import Sexp

# Simple list
expr1 = Sexp("(a b c)")
print(expr1)  # ['a', 'b', 'c']

# Numbers are automatically converted
expr2 = Sexp("(1 2.5 -3)")
print(expr2)  # [1, 2.5, -3]

# Mixed types
expr3 = Sexp("(add 10 20)")
print(expr3)  # ['add', 10, 20]

# Create S-expressions from Python lists
list_expr = Sexp(['define', ['square', 'x'], ['*', 'x', 'x']])
print(list_expr.to_str(break_inc=0))
# Output: (define (square "x") (* "x" "x"))

# Control quoting behavior
print(list_expr.to_str(quote_strs=False, break_inc=0))
# Output: (define (square x) (* x x))
```

### Handling Nested Expressions

```python
from simp_sexp import Sexp

# Nested lists
nested = Sexp("(a (b c) (d (e f)))")
print(nested)  # ['a', ['b', 'c'], ['d', ['e', 'f']]]

# Access elements
print(nested[0])  # 'a'
print(nested[1])  # ['b', 'c']
print(nested[2][1][0])  # 'e'

# Modify elements
nested[1][1] = 'modified'
print(nested)  # ['a', ['b', 'modified'], ['d', ['e', 'f']]]

# Add elements
nested[2][1].append('g')
print(nested)  # ['a', ['b', 'modified'], ['d', ['e', 'f', 'g']]]

# Lisp-like function calls
lambda_expr = Sexp("(lambda (x) (+ x 1))")
print(lambda_expr)  # ['lambda', ['x'], ['+', 'x', 1]]
```

### Searching S-expressions

```python
from simp_sexp import Sexp
import re

# Create a complex S-expression
config = Sexp("""
(config
  (version 1.0)
  (settings
    (theme dark)
    (font "Courier New")
    (size 12))
  (keybindings
    (save "Ctrl+S")
    (open "Ctrl+O")
    (preferences
      (toggle "Ctrl+P")
      (help "F1"))))
""")

# Search by key path (relative)
font_results = config.search("font")
print(font_results[0][1])  # ['font', 'Courier New']

# Search by absolute path
version_results = config.search("/config/version")
print(version_results[0][1])  # ['version', 1.0]

# Search using a function
results = config.search(lambda x: len(x) > 2 and x[0] == 'settings')
print(results[0][1])  # ['settings', ['theme', 'dark'], ['font', 'Courier New'], ['size', 12]]

# Search using regex
ctrl_bindings = config.search(re.compile(r'^Ctrl\+'))
print([match[1] for _, match in ctrl_bindings])  # Will show all Ctrl+ keybindings

# Search with contains=True to match any element
theme_results = config.search("dark", contains=True)
print(theme_results[0][1])  # ['theme', 'dark']

# Case-insensitive search
prefs = config.search("PREFERENCES", ignore_case=True)
print(prefs[0][1])  # ['preferences', ['toggle', 'Ctrl+P'], ['help', 'F1']]
```

### Manipulating S-expressions

```python
from simp_sexp import Sexp

# Start with a simple expression
expr = Sexp("(define x 10)")

# Convert to list and modify
expr[2] = 20
print(expr.to_str())  # (define "x" 20)

# Add elements
expr.append(['comment', 'updated value'])
print(expr.to_str(break_inc=0))  # (define "x" 20 (comment "updated value"))

# Create a new expression from scratch
new_expr = Sexp()
new_expr.append('if')
new_expr.append(['>', 'x', 0])
new_expr.append('positive')
new_expr.append('negative')
print(new_expr.to_str(quote_strs=False, break_inc=0))
# Output: (if (> x 0) positive negative)

# Replace parts of an expression
def replace_value(sublist):
    if sublist and sublist[0] == 'x':
        return ['y']
    return sublist

# Find and replace operations in complex expressions
math_expr = Sexp("(+ (* x 3) (/ x 2))")
for path, match in math_expr.search('x'):
    # Create the full path to the parent element
    parent_path = path[:-1]
    index = path[-1]
    
    # Navigate to the parent element
    parent = math_expr
    for i in parent_path:
        parent = parent[i]
        
    # Replace 'x' with 'y'
    parent[index] = 'y'

print(math_expr.to_str(quote_strs=False, break_inc=0))
# Output: (+ (* y 3) (/ y 2))
```

### Working with Files

```python
from simp_sexp import Sexp

# Example of loading an S-expression from a file
def load_config(filename):
    with open(filename, 'r') as f:
        config_str = f.read()
    return Sexp(config_str)

# Example of saving an S-expression to a file
def save_config(config_sexp, filename):
    with open(filename, 'w') as f:
        f.write(config_sexp.to_str(indent=2))

# Usage example (pseudo-code)
# config = load_config("config.sexp")
# config[1][2] = "new_value"  # Modify the config
# save_config(config, "config.sexp")
```

## License

MIT