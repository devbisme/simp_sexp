# History

## 0.3.2
- `to_str()` now formats the complete S-expression once instead of reformatting every nested level, making it about five times faster.
- Fixed stray spaces in `to_str()` output when `break_inc` is 2 or more. Output with the default settings is unchanged.

## 0.3.1
- Quotes within a quoted string are now escaped.

## 0.3.0
- Added Sexp method value for extracting the value from an S-expression with a single item of form (key, value). 

## 0.2.2
- Updated compatible Python versions to include 3.6.

## 0.2.1
- Updated compatible Python versions to include 3.7.

## 0.2.0
- Added Sexp method rmv_quotes for removing quotes from elements within S-expressions

## 0.1.0 (Initial Release)
- Initial release of simp_sexp
- Simple and lightweight S-expression parser
- Parse and manipulate S-expressions with an intuitive object-oriented interface
- Convert between string representations and Python data structures
- Nested expressions are handled automatically
- Pretty-printing support for readable output
- Advanced search capabilities for finding elements within complex S-expressions
- Support for quoted strings with proper escape handling
- Automatic type conversion for numbers
- Support for Python 3.8+