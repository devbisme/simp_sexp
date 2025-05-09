"""
Simple S-expression parser and formatter for Python.

This module provides utilities for working with S-expressions (as used in Lisp,
KiCad, and other formats) through an object-oriented interface. It includes:
- The Sexp class for S-expression parsing, formatting and manipulation
- Pretty-formatting S-expression strings

These utilities are useful when working with CAD file formats, configuration files,
or any other data format that uses S-expressions.
"""

__all__ = ["Sexp", "prettify_sexp"]


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
        # Try to parse as int with base 0 (auto-detects base)
        return int(input_str, base=0)
    except ValueError:
        try:
            # Try to parse as float
            return float(input_str)
        except ValueError:
            # If it can't be parsed as int or float, return as string
            return input_str

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

class Sexp(list):
    """
    A class representing an S-expression as a nested list structure.
    
    This class extends Python's built-in list with methods for parsing,
    formatting, and searching S-expressions. It provides a convenient
    object-oriented interface for working with S-expression data.
    
    Examples:
        >>> expr = Sexp('(define (square x) (* x x))')
        >>> expr
        ['define', ['square', 'x'], ['*', 'x', 'x']]
        >>> print(expr.to_str())
        (define (square "x") (* "x" "x"))
        >>> subexpr = expr.search('square')
        >>> subexpr
        [([], ['square', 'x'])]
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize an Sexp object.
        
        If the first argument is a string, it's parsed as an S-expression.
        Otherwise, behaves like the list constructor, but ensures that
        any nested lists are also Sexp objects.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # If first argument is a string, parse it as an S-expression
        if args and isinstance(args[0], str):
            s_expr = args[0]
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
                    
                    # Create a new Sexp and make it the active list
                    new_list = Sexp()
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
            
            # Initialize with the parsed result
            parsed = result[0] if len(result) == 1 else result
            super().__init__(parsed)
            
        else:
            # Initialize like a normal list first
            super().__init__(*args, **kwargs)
            
            # Convert any nested lists to Sexp objects
            for i in range(len(self)):
                if isinstance(self[i], list) and not isinstance(self[i], Sexp):
                    self[i] = Sexp(self[i])
    
    def to_str(self, quote_nums=True, quote_strs=True, **prettify_kwargs):
        """
        Convert the Sexp object to an S-expression string.
        
        Args:
            quote_nums (bool): If True, wrap numeric values in double-quotes. Default is True.
            quote_strs (bool): If True, wrap string values in double-quotes. Default is True.
            **prettify_kwargs: Keyword arguments for formatting:
                - break_inc (int): Controls when linebreaks are inserted based on nesting level.
                  Default is 1 (break at every level). Set to 0 or negative for no linebreaks.
                - spaces_per_level (int): Number of spaces per indentation level. Default is 2.
        
        Returns:
            str: The formatted S-expression string.
        """
        if not isinstance(self, list):
            # If it's not a list, return it as a string
            return str(self)

        if not self:
            # Return empty parentheses for an empty list
            return "()"

        # Convert each element to an S-expression
        elements = []
        for i, item in enumerate(self):
            if isinstance(item, list):
                # Recursively convert nested lists using their to_str method if available
                if hasattr(item, 'to_str'):
                    elements.append(item.to_str(quote_nums, quote_strs, **prettify_kwargs))
                else:
                    # Fallback for regular lists
                    elements.append(Sexp(item).to_str(quote_nums, quote_strs, **prettify_kwargs))
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
    
    def search(self, pattern, search_type='key_path', max_depth=None):
        """
        Search for elements within the Sexp that match the given pattern.
        
        Args:
            pattern: The pattern to search for. Can be a value, function, regular expression,
                    or a path string depending on the search_type.
            search_type (str): The type of search to perform. Options:
                - 'key_path': (Default) Match a slash-delimited path string, with two formats:
                    * "key1/key2/key3": Relative search - finds sublists whose path ends with these keys
                    * "/key1/key2/key3": Absolute search - finds sublists with exact matching path
                - 'value': Direct equality comparison with the first element of each sublist
                - 'first_value': Same as 'value' but for case-insensitive string comparison
                - 'contains': Check if the pattern is present anywhere in the sublist
                - 'function': Use a custom function that takes a sublist and returns True/False
                - 'regex': Use a regular expression to match against the first element
                - 'path': Match the exact path in the nested structure
            max_depth (int, optional): Maximum depth to search. If None, search all levels.
        
        Returns:
            list: A list of tuples (path, sublist) for all matches found. The path is a list
                 of indices to reach the sublist from the root.
        """
        import re

        results = []
        current_path = []
        current_keypath = []
        
        def _search_recursive(nested_list, pattern, search_type, max_depth, current_path, current_keypath):
            # Check if max_depth is reached
            if max_depth is not None and len(current_path) >= max_depth:
                return
            
            # Only process lists
            if not isinstance(nested_list, list) or not nested_list:
                return
            
            # Get the key (first element) of the current list if available
            current_key = str(nested_list[0]) if nested_list else None
            
            # Update the current keypath if we have a key
            if current_key is not None:
                current_keypath = current_keypath + [current_key]
            
            # Special handling for key_path search type
            if search_type == 'key_path' and isinstance(pattern, str):
                # Determine if this is an absolute or relative path search
                is_absolute = pattern.startswith('/')
                
                # Split the path string into individual keys
                search_keys = pattern.strip('/').split('/')
                if not search_keys:
                    return
                
                if is_absolute:
                    # Absolute path search
                    if len(search_keys) == len(current_keypath):
                        # Check if the entire keypath matches
                        if all(sk == ck for sk, ck in zip(search_keys, current_keypath)):
                            results.append((current_path.copy(), nested_list))
                    
                    # Continue searching if the current keypath is a prefix of the search path
                    should_continue_search = (len(current_keypath) < len(search_keys) and 
                                            all(sk == ck for sk, ck in zip(search_keys, current_keypath)))
                else:
                    # Relative path search
                    # Check if the end of the current keypath matches the search keys
                    if len(current_keypath) >= len(search_keys):
                        suffix = current_keypath[-len(search_keys):]
                        if all(sk == ck for sk, ck in zip(search_keys, suffix)):
                            results.append((current_path.copy(), nested_list))
                    
                    # Always continue searching for relative paths
                    should_continue_search = True
                
                # Recursively search through nested sublists if appropriate
                if should_continue_search or not is_absolute:
                    for i, item in enumerate(nested_list):
                        if isinstance(item, list):
                            new_path = current_path + [i]
                            _search_recursive(item, pattern, search_type, max_depth, 
                                             new_path, current_keypath)
                
                return
            
            # Check if the current list matches the pattern (for other search types)
            if nested_list:  # Ensure the list is not empty before checking
                match = False
                
                if search_type == 'value' and len(nested_list) > 0:
                    # Check if first element equals pattern
                    match = nested_list[0] == pattern
                    
                elif search_type == 'first_value' and len(nested_list) > 0:
                    # Case-insensitive string comparison of first element
                    if isinstance(nested_list[0], str) and isinstance(pattern, str):
                        match = nested_list[0].lower() == pattern.lower()
                    
                elif search_type == 'contains':
                    # Check if pattern exists anywhere in the list
                    match = pattern in nested_list
                    
                elif search_type == 'function':
                    # Use a custom function to determine match
                    match = pattern(nested_list)
                    
                elif search_type == 'regex' and len(nested_list) > 0:
                    # Match regex against the string representation of first element
                    if isinstance(nested_list[0], str):
                        if isinstance(pattern, str):
                            pattern = re.compile(pattern)
                        match = bool(pattern.search(str(nested_list[0])))
                    
                elif search_type == 'path':
                    # Check if the current path matches the pattern
                    match = current_path == pattern
                
                if match:
                    results.append((current_path.copy(), nested_list))
            
            # Recursively search through nested sublists
            for i, item in enumerate(nested_list):
                if isinstance(item, list):
                    new_path = current_path + [i]
                    _search_recursive(item, pattern, search_type, max_depth, 
                                    new_path, current_keypath)
        
        # Start the recursive search
        _search_recursive(self, pattern, search_type, max_depth, current_path, current_keypath)
        
        return results
    
    def __str__(self):
        """
        Return the string representation of the Sexp object as an S-expression.
        
        Returns:
            str: The S-expression string.
        """
        return self.to_str()
    
    def __repr__(self):
        """
        Return the Python representation of the Sexp object as a list.
        
        Returns:
            str: The list representation.
        """
        return super().__repr__()
    
    def append(self, item):
        """
        Append an item to the Sexp, converting lists to Sexp objects.
        
        Args:
            item: The item to append
        """
        if isinstance(item, list) and not isinstance(item, Sexp):
            super().append(Sexp(item))
        else:
            super().append(item)
    
    def extend(self, iterable):
        """
        Extend the Sexp with an iterable, converting lists to Sexp objects.
        
        Args:
            iterable: The iterable to extend with
        """
        for item in iterable:
            self.append(item)
    
    def __setitem__(self, key, value):
        """
        Set an item in the Sexp, converting lists to Sexp objects.
        
        Args:
            key: The index or slice
            value: The value to set
        """
        if isinstance(value, list) and not isinstance(value, Sexp):
            super().__setitem__(key, Sexp(value))
        else:
            super().__setitem__(key, value)
