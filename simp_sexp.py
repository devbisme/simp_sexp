"""
simp_sexp - A simple S-expression parser
"""

__version__ = "0.1.0"


class ParseError(Exception):
    """Exception raised for parsing errors in the S-expression."""
    pass


def tokenize(string):
    """Convert a string into a list of tokens."""
    return string.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(tokens):
    """Parse a list of tokens into an S-expression."""
    if not tokens:
        raise ParseError("Unexpected end of input")
    
    token = tokens.pop(0)
    
    if token == '(':
        expr = []
        while tokens and tokens[0] != ')':
            expr.append(parse(tokens))
        
        if not tokens:
            raise ParseError("Expected ')', got end of input")
        
        # Remove the closing parenthesis
        tokens.pop(0)
        return expr
    elif token == ')':
        raise ParseError("Unexpected ')'")
    else:
        # Try to convert to a number if possible
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return token


def parse_string(string):
    """Parse a string containing an S-expression."""
    return parse(tokenize(string))


def to_string(expr):
    """Convert an S-expression back to a string."""
    if isinstance(expr, list):
        return '(' + ' '.join(to_string(x) for x in expr) + ')'
    else:
        return str(expr)