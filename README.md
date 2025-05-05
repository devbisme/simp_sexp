# simp_sexp

A simple S-expression parser for Python.

## Installation

```bash
pip install simp_sexp
```

## Usage

```python
from simp_sexp import parse_string, to_string

# Parse a string into an S-expression
expr = parse_string("(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))")
print(expr)
# Output: ['define', ['factorial', 'n'], ['if', ['=', 'n', 0], 1, ['*', 'n', ['factorial', ['-', 'n', 1]]]]]

# Convert an S-expression back to a string
s_expr = to_string(expr)
print(s_expr)
# Output: (define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))
```

## Features

- Simple and lightweight S-expression parser
- Converts between string representations and Python data structures
- Handles nested expressions
- Automatically converts numbers

## License

MIT