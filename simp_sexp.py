"""
Simple S-expression parser and formatter for Python.

This module provides utilities for converting between S-expressions (as used in Lisp,
KiCad, and other formats) and Python data structures. It includes functions for:
- Converting S-expression strings to nested Python lists
- Converting nested Python lists back to S-expression strings
- Pretty-formatting S-expression strings with proper indentation

These utilities are useful when working with CAD file formats, configuration files,
or any other data format that uses S-expressions.
"""

__all__ = ["sexp_to_nested_list", "nested_list_to_sexp", "prettify_sexp"]


def parse_value(input_str):
    """
    Parse a string into an int, float, or string based on its content.
    
    This function attempts to convert a string to the most appropriate data type.
    It tries first as an integer, then as a floating-point number, and finally
    returns the original string if neither conversion works.
    
    Args:
        input_str (str): The input string to parse.
        
    Returns:
        int, float, or str: The parsed value in the most appropriate type.
        
    Examples:
        >>> parse_value("42")
        42
        >>> parse_value("3.14")
        3.14
        >>> parse_value("hello")
        'hello'
        >>> parse_value("42.0")
        42.0
        >>> parse_value("")
        ''
    """
    # Handle empty strings
    if not input_str:
        return input_str
        
    try:
        # Try to parse as int
        return int(input_str)
    except ValueError:
        try:
            # Try to parse as float
            return float(input_str)
        except ValueError:
            # If it can't be parsed as int or float, return as string
            return input_str

def sexp_to_nested_list(s_expr):
    """
    Parse an S-expression string into nested Python lists.
    
    This function converts a string containing an S-expression (a format commonly used in Lisp, 
    KiCad, and other systems) into a nested Python list structure. It handles:
    - Quoted strings (both single and double quotes)
    - Nested parenthetical expressions
    - Automatic type conversion (strings, integers, floats)
    - Escaped characters in strings
    
    Args:
        s_expr (str): The S-expression string to parse.
    
    Returns:
        list: A nested list representation of the S-expression with:
            - Quote marks removed from strings
            - Numbers converted to appropriate numeric types
            - Nested expressions as sublists
    
    Examples:
        >>> sexp_to_nested_list('(define (square x) (* x x))')
        ['define', ['square', 'x'], ['*', 'x', 'x']]
        >>> sexp_to_nested_list('(display "Hello world")')
        ['display', 'Hello world']
        >>> sexp_to_nested_list('(values 1 2.5 "text" \'quoted\')')
        ['values', 1, 2.5, 'text', 'quoted']
        >>> sexp_to_nested_list('(list (nested "data") 123)')
        ['list', ['nested', 'data'], 123]
        
    Raises:
        ValueError: If there are syntax errors like unclosed quotes or parentheses in the S-expression.
    """
    result = []  # The outermost list that will be returned
    stack = [result]  # Stack of active lists, starting with the result list
    current_token = ""  # Current token being built
    in_single_quote = False
    in_double_quote = False
    quote_content = ""  # Store content inside quote marks
    i = 0
    
    while i < len(s_expr):
        char = s_expr[i]
        
        # Handle escaped characters
        if char == '\\' and i + 1 < len(s_expr):
            next_char = s_expr[i + 1]
            if in_single_quote or in_double_quote:
                if next_char in ["'", '"', '\\']: 
                    quote_content += next_char  # Add the escaped character directly
                else:
                    quote_content += char + next_char  # Keep the backslash for other escapes
            else:
                current_token += char + next_char
            i += 2
            continue
            
        # Handle opening quotes
        if char == "'" and not in_double_quote and not in_single_quote:
            # Process any token before the quote
            if current_token.strip():
                stack[-1].append(parse_value(current_token.strip()))
                current_token = ""
            in_single_quote = True
            quote_content = ""  # Reset quote content
            
        elif char == '"' and not in_single_quote and not in_double_quote:
            # Process any token before the quote
            if current_token.strip():
                stack[-1].append(parse_value(current_token.strip()))
                current_token = ""
            in_double_quote = True
            quote_content = ""  # Reset quote content
            
        # Handle closing quotes
        elif char == "'" and in_single_quote:
            in_single_quote = False
            stack[-1].append(quote_content)  # Add quote content without the quotes
            
        elif char == '"' and in_double_quote:
            in_double_quote = False
            stack[-1].append(quote_content)  # Add quote content without the quotes
            
        # Handle characters inside quotes
        elif in_single_quote or in_double_quote:
            quote_content += char
            
        # Handle opening parenthesis outside of quotes
        elif char == '(' and not in_single_quote and not in_double_quote:
            # If there's a current token, add it to the active list
            if current_token.strip():
                stack[-1].append(parse_value(current_token.strip()))
                current_token = ""
            
            # Create a new list and make it the active list
            new_list = []
            stack[-1].append(new_list)
            stack.append(new_list)
            
        # Handle closing parenthesis outside of quotes
        elif char == ')' and not in_single_quote and not in_double_quote:
            # If there's a current token, add it to the active list
            if current_token.strip():
                stack[-1].append(parse_value(current_token.strip()))
                current_token = ""
            
            # Change the active list to the parent list
            if len(stack) > 1:  # Make sure we don't pop the outermost list
                stack.pop()
                
        # Handle whitespace outside of quotes
        elif char.isspace() and not in_single_quote and not in_double_quote:
            # If there's a current token, add it to the active list
            if current_token.strip():
                stack[-1].append(parse_value(current_token.strip()))
                current_token = ""
                
        # Handle all other characters outside of quotes
        else:
            if not (in_single_quote or in_double_quote):
                current_token += char
            
        i += 1
    
    # Handle any remaining token
    if current_token.strip():
        stack[-1].append(parse_value(current_token.strip()))
    
    # Check if we ended with unclosed quotes
    if in_single_quote or in_double_quote:
        raise ValueError("Unclosed quote in S-expression")
    
    # Return the first element of the result list to remove the extra level of nesting
    return result[0] if len(result) == 1 else result

def nested_list_to_sexp(nested_list, quote_nums=False, quote_strs=False, **prettify_kwargs):
    """
    Convert nested Python lists to an S-expression string.
    
    This function transforms a nested list structure into a properly formatted S-expression string.
    It handles quoting of elements according to S-expression conventions and can apply
    pretty-formatting to the output.
    
    Args:
        nested_list (list): A nested list structure representing an S-expression.
        quote_nums (bool): If True, wrap numeric values (int/float) in double-quotes.
                           If False, print numbers without quotes. Default is True.
        quote_strs (bool): If True, wrap string values in double-quotes if they don't
                           already have quotes. If False, print strings without additional
                           quotes. Default is True.
        **prettify_kwargs: Keyword arguments passed to the prettify_sexp function:
            - break_inc (int): Controls when linebreaks are inserted based on nesting level. 
              Default is 1 (break at every level). Set to 0 or negative for no linebreaks.
            - spaces_per_level (int): Number of spaces per indentation level. Default is 2.
    
    Returns:
        str: The corresponding S-expression string with proper formatting.
    
    Examples:
        >>> nested_list_to_sexp(['define', ['square', 'x'], ['*', 'x', 'x']])
        '(define (square "x") (* "x" "x"))'
        >>> nested_list_to_sexp([1, 2, 3], quote_nums=False)
        '(1 2 3)'
        >>> nested_list_to_sexp(['list', 'a', 'b'], quote_strs=False)
        '(list a b)'
        >>> nested_list_to_sexp(['cmd', 42, 'text'], quote_nums=False, quote_strs=True)
        '(cmd 42 "text")'
    """
    if not isinstance(nested_list, list):
        # If it's not a list, return it as a string
        return str(nested_list)

    if not nested_list:
        # Return empty parentheses for an empty list
        return "()"

    # Convert each element to an S-expression
    elements = []
    for i, item in enumerate(nested_list):
        if isinstance(item, list):
            # Recursively convert nested lists
            elements.append(nested_list_to_sexp(item, quote_nums, quote_strs))
        else:
            # For non-list items
            item_str = str(item)
            
            # First element is never quoted
            if i == 0:
                elements.append(item_str)
                continue
            
            # Check if item is already quoted
            already_quoted = (item_str.startswith('"') and item_str.endswith('"')) or \
                             (item_str.startswith("'") and item_str.endswith("'"))
            
            # Apply quoting rules based on type and parameters
            if isinstance(item, (int, float)):
                if quote_nums and not already_quoted:
                    elements.append(f'"{item_str}"')
                else:
                    elements.append(item_str)
            else:  # String or other type
                if quote_strs and not already_quoted:
                    elements.append(f'"{item_str}"')
                else:
                    elements.append(item_str)

    # Join all elements with spaces, wrap with parentheses, and make it pretty.
    return prettify_sexp("(" + " ".join(elements) + ")", **prettify_kwargs)

def prettify_sexp(sexp, **prettify_kwargs):
    """
    Format an S-expression string with proper indentation for readability.
    
    This function takes an S-expression string and beautifies it with consistent 
    indentation and line breaks to improve human readability. It respects string
    literals (both single and double-quoted) and handles escaped characters properly.
    
    Args:
        sexp (str): The S-expression string to format.
        **prettify_kwargs: Keyword arguments to control formatting behavior:
            - break_inc (int): Controls when linebreaks are inserted. When positive,
              a linebreak is added before any opening parenthesis that increases
              the nesting level to a multiple of this value. When 0 or negative,
              no linebreaks are added but single spaces are inserted before opening
              and after closing parentheses. Default is 1 (break at every level).
            - spaces_per_level (int): Number of spaces per indentation level. Default is 2.
              Only applied when break_inc > 0.
        
    Returns:
        str: The formatted S-expression string with proper indentation and structure.
        
    Examples:
        >>> prettify_sexp("(foo (bar baz) qux)")
        '(foo\\n  (bar baz)\\n  qux)'
        >>> prettify_sexp("(foo (bar baz) qux)", break_inc=0)
        '(foo (bar baz) qux)'
        >>> prettify_sexp("(a (b (c (d))))", break_inc=2)
        '(a (b\\n    (c (d))))'
        >>> prettify_sexp("(deeply (nested (expression)))", spaces_per_level=4)
        '(deeply\\n    (nested\\n        (expression)))'
        >>> prettify_sexp('(with "quoted \\"strings\\"" (intact))')
        '(with\\n  "quoted \\"strings\\""\\n  (intact))'
    """
    break_inc = prettify_kwargs.get('break_inc', 1)
    spaces_per_level = prettify_kwargs.get('spaces_per_level', 2)

    # Remove all newlines from the input
    sexp = sexp.replace('\n', '')

    result = []

    level = 0  # Nesting level of parentheses.
    in_string = None  # None, "'", or '"'.
    escaped = False  # True if the last character was a backslash.
    i = 0
    last_char = None  # Keep track of the last character added to the result
    
    while i < len(sexp):
        char = sexp[i]

        # Handle string literals within the S expression.
        if in_string:
            if escaped:
                # This is an escaped character, add it and continue.
                result.append(char)
                escaped = False
            elif char == '\\':
                # Next character will be escaped.
                result.append(char)
                escaped = True
            elif char == in_string:
                # End of string literal.
                result.append(char)
                in_string = None
            else:
                # Regular character within a string.
                result.append(char)
            i += 1
            continue

        # Handle parentheses and normal characters.
        if char == '(':
            # For break_inc <= 0, add one space before opening parenthesis if not at start
            # and last character is not whitespace or opening parenthesis
            if break_inc <= 0 and result and last_char != ' ' and last_char != '(':
                result.append(' ')
            
            # Add newline and indentation before opening parenthesis if needed
            if break_inc > 0 and level > 0 and (level % break_inc) == 0:
                result.append('\n')
                result.append(' ' * (level * spaces_per_level))
            
            result.append(char)
            last_char = char
            level += 1

            # Skip any whitespace after opening parenthesis.
            i += 1
            while i < len(sexp) and sexp[i].isspace():
                i += 1
            continue

        elif char == ')':
            level -= 1
            result.append(char)
            last_char = char
            
            # For break_inc <= 0, add one space after closing parenthesis
            # if not at end and next character is not a closing parenthesis or whitespace
            if break_inc <= 0 and i + 1 < len(sexp) and sexp[i + 1] not in [')', ' ', '\t', '\n']:
                result.append(' ')
                last_char = ' '

        elif char in ["'", '"']:
            in_string = char
            result.append(char)
            last_char = char

        elif char.isspace():
            # Look for whitespace after current character
            j = i + 1
            while j < len(sexp) and sexp[j].isspace():
                j += 1

            # When break_inc <= 0, only add one space between tokens
            if break_inc <= 0:
                if j < len(sexp) and sexp[j] != ')' and last_char != ' ' and last_char != '(':
                    result.append(' ')
                    last_char = ' '
            else:
                # Regular handling for break_inc > 0
                if j < len(sexp) and sexp[j] == ')':
                    i = j - 1
                else:
                    result.append(char)
                    last_char = char

        else:
            # Nothing special about this character, so just add it to the result.
            result.append(char)
            last_char = char

        i += 1

    return ''.join(result)
