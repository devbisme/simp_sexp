"""
Simple S-expression parser and formatter for Python.

This module provides utilities for working with S-expressions (as used in Lisp,
KiCad, and other formats) through an object-oriented interface. It includes:
- The Sexp class for S-expression parsing, formatting and manipulation
- Pretty-formatting S-expression strings

These utilities are useful when working with CAD file formats, configuration files,
or any other data format that uses S-expressions.
"""

import re

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

def strip_chars(s, rmv_chars):
    """
    Remove entire sequences of characters from rmv_chars that precede newlines in s.
    
    Uses a regular expression to match and remove sequences of specified characters
    that appear immediately before newlines.
    
    Args:
        s (str): The input string to process
        rmv_chars (str): A string of characters to remove when they precede newlines
        
    Returns:
        str: The processed string with specified character sequences removed before newlines
        
    Examples:
        >>> strip_chars("Hello world!;,\\nNext line", ";,!")
        'Hello world\\nNext line'
        >>> strip_chars("Test line;;;\\nAnother line::::\\n", ";:")
        'Test line\\nAnother line\\n'
        >>> strip_chars("No newline here", "abc")
        'No newline here'
        >>> strip_chars("Mixed chars ab12\\nKeep all", "ab")
        'Mixed chars ab12\\nKeep all'
    """

    # Create a pattern that matches one or more characters from rmv_chars followed by a newline
    pattern = f'[{re.escape(rmv_chars)}]+(?=\n)'
    
    # Replace matched patterns with empty string
    return re.sub(pattern, '', s)

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
            - indent (int): Number of spaces per indentation level. Default is 2.
              Only applied when break_inc > 0.
        
    Returns:
        str: The formatted S-expression string with proper indentation and structure.
        
    Examples:
        >>> prettify_sexp("(foo (bar baz) qux)")
        '(foo\\n  (bar baz) qux)'
        >>> prettify_sexp("(foo (bar baz) qux)", break_inc=0)
        '(foo (bar baz) qux)'
        >>> prettify_sexp("(a (b (c (d))))", break_inc=2)
        '(a (b\\n    (c (d))))'
        >>> prettify_sexp("(deeply (nested (expression)))", indent=4)
        '(deeply\\n    (nested\\n        (expression)))'
        >>> prettify_sexp('(with "quoted \"strings\"" (intact))')
        '(with "quoted \"strings\""\\n  (intact))'
    """
    break_inc = prettify_kwargs.get('break_inc', 1)
    indent = prettify_kwargs.get('indent', 2)

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
                result.append(' ' * (level * indent))  # Using indent instead of spaces_per_level
            
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

    return strip_chars(''.join(result), " \t") # Remove trailing whitespace on each line

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
        >>> print(expr.to_str(break_inc=0))
        (define (square x) (* x x))
        >>> subexpr = expr.search('square', include_path=True)
        >>> subexpr
        [([1], ['square', 'x'])]
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

    def to_str(self, quote_nums=False, quote_strs=False, **prettify_kwargs):
        """
        Convert the Sexp object to an S-expression string.
        
        Args:
            quote_nums (bool): If True, wrap numeric values in double-quotes. Default is False.
            quote_strs (bool): If True, wrap string values in double-quotes. Default is False.
            **prettify_kwargs: Keyword arguments for formatting:
                - break_inc (int): Controls when linebreaks are inserted based on nesting level.
                  Default is 1 (break at every level). Set to 0 or negative for no linebreaks.
                - indent (int): Number of spaces per indentation level. Default is 2.
        
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
                        item_str = item_str.replace('"', '\\"')  # Escape double quotes
                        elements.append(f'"{item_str}"')
                    else:
                        elements.append(item_str)

        # Join all elements with spaces, wrap with parentheses, and make it pretty.
        return prettify_sexp("(" + " ".join(elements) + ")", **prettify_kwargs)

    def search(self, pattern, max_depth=None, contains=False, include_path=False, ignore_case=False):
        """
        Search for elements within the Sexp that match the given pattern.

        The search behavior is automatically determined by the pattern type:
        - string: Performs key_path search (either relative or absolute path)
        - function: Calls the function on each sublist to determine matches
        - re.Pattern: Matches regex pattern against the first element
        - list/tuple: Interprets as exact path indices to match

        Args:
            pattern: The pattern to search for:
                - str: A slash-delimited path (e.g., "key1/key2" or "/root/key1")
                - function: A function that takes a sublist and returns True/False
                - re.Pattern: A compiled regular expression to match against first element
                - list/tuple: A sequence of indices representing an exact path
            max_depth (int, optional): Maximum depth to search. If None, search all levels.
            contains (bool): If True, searches for pattern in the entire sublist,
                           not just the first element. Default is False.
            include_path (bool): If True, includes the path with each matching sublist as a tuple
                           in the results. Default is False.
            ignore_case (bool): If True, performs case-insensitive string comparisons.
                           Default is False.

        Returns:
            list: If include_path is False, return a list of of all matching sublists. Otherwise,
                 return a list of tuples (path, sublist) for all matching sublists. The path is a list
                 of indices to reach the sublist from the root.
        """
        import re

        results = []
        current_path = []
        current_keypath = []

        def _search_recursive(nested_list, pattern, max_depth, current_path, current_keypath):
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

            # Special handling for string pattern (key_path search)
            if isinstance(pattern, str):
                # Check if we're doing a contains search with a string pattern
                if contains:
                    # For a contains search with a string, we check if the pattern exists anywhere in the list
                    for i, item in enumerate(nested_list):
                        if isinstance(item, str):
                            if ignore_case:
                                if item.lower() == pattern.lower():
                                    if include_path:
                                        results.append((current_path.copy(), nested_list))
                                    else:
                                        results.append(nested_list)
                                    break
                            else:
                                if item == pattern:
                                    if include_path:
                                        results.append((current_path.copy(), nested_list))
                                    else:
                                        results.append(nested_list)
                                    break
                        elif isinstance(item, (int, float)) and str(item) == pattern:
                            # Also match numeric values as strings
                            if include_path:
                                results.append((current_path.copy(), nested_list))
                            else:
                                results.append(nested_list)
                            break

                    # Continue recursion regardless of match
                    for i, item in enumerate(nested_list):
                        if isinstance(item, list):
                            new_path = current_path + [i]
                            _search_recursive(item, pattern, max_depth, new_path, current_keypath)

                    return

                # If not a contains search, proceed with key_path search
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
                        if all(
                            (sk.lower() == ck.lower() if ignore_case else sk == ck)
                            for sk, ck in zip(search_keys, current_keypath)
                        ):
                            if include_path:
                                results.append((current_path.copy(), nested_list))
                            else:
                                results.append(nested_list)

                    # Continue searching if the current keypath is a prefix of the search path
                    should_continue_search = (len(current_keypath) < len(search_keys) and 
                                            all(
                                                (sk.lower() == ck.lower() if ignore_case else sk == ck)
                                                for sk, ck in zip(search_keys, current_keypath)
                                            ))
                else:
                    # Relative path search
                    # Check if the end of the current keypath matches the search keys
                    if len(current_keypath) >= len(search_keys):
                        suffix = current_keypath[-len(search_keys):]
                        if all(
                            (sk.lower() == ck.lower() if ignore_case else sk == ck)
                            for sk, ck in zip(search_keys, suffix)
                        ):
                            if include_path:
                                results.append((current_path.copy(), nested_list))
                            else:
                                results.append(nested_list)

                    # Always continue searching for relative paths
                    should_continue_search = True

                # Recursively search through nested sublists if appropriate
                if should_continue_search or not is_absolute:
                    for i, item in enumerate(nested_list):
                        if isinstance(item, list):
                            new_path = current_path + [i]
                            _search_recursive(item, pattern, max_depth, 
                                             new_path, current_keypath)

                return

            # Check if the current list matches the pattern
            if nested_list:  # Ensure the list is not empty before checking
                match = False

                # Function pattern - call the function with the sublist
                if callable(pattern):
                    match = pattern(nested_list)

                # Regular expression pattern
                elif hasattr(pattern, 'search') and hasattr(pattern, 'pattern'):  # Looks like a regex pattern
                    if len(nested_list) > 0 and isinstance(nested_list[0], str):
                        match = bool(pattern.search(str(nested_list[0])))

                # Path pattern (list or tuple of indices)
                elif isinstance(pattern, (list, tuple)):
                    match = current_path == list(pattern)

                # Contains search for non-string patterns
                elif contains:
                    if ignore_case and isinstance(pattern, str):
                        # For strings with ignore_case, we need to do case-insensitive comparison
                        match = any(
                            (isinstance(item, str) and item.lower() == pattern.lower())
                            for item in nested_list
                        )
                    else:
                        # For other types or case-sensitive comparison
                        match = pattern in nested_list

                if match:
                    if include_path:
                        results.append((current_path.copy(), nested_list))
                    else:
                        results.append(nested_list)

            # Recursively search through nested sublists
            for i, item in enumerate(nested_list):
                if isinstance(item, list):
                    new_path = current_path + [i]
                    _search_recursive(item, pattern, max_depth, 
                                    new_path, current_keypath)

        # Start the recursive search
        _search_recursive(self, pattern, max_depth, current_path, current_keypath)

        return results

    def add_quotes(self, pattern, stop_idx=None, **kwargs):
        """
        Search for elements matching the given pattern and add quotes to all elements 
        except the first one in each matching expression.
        
        This method accepts the same parameters as the search() method, except for 'include_path'.
        It modifies the elements directly in the original Sexp object.
        
        Args:
            pattern: The pattern to search for:
                - str: A slash-delimited path (e.g., "key1/key2" or "/root/key1")
                - function: A function that takes a sublist and returns True/False
                - re.Pattern: A compiled regular expression to match against first element
                - list/tuple: A sequence of indices representing an exact path
            stop_idx (int, optional): If provided, only add quotes to elements up to this index 
                                     (exclusive). If None, process all elements. Default is None.
            **kwargs: Keyword arguments to pass to the search() method,
                     excluding 'include_path' which is handled internally
        
        Returns:
            None: Modifications are applied in-place to the Sexp object
            
        Examples:
            >>> s = Sexp('((layer F.Cu) (pad 1 smd rect))')
            >>> s.add_quotes('layer')  # Add quotes to elements in layer expressions
            >>> print(s.to_str(break_inc=0))
            ((layer "F.Cu") (pad 1 smd rect))
            
            >>> s.add_quotes(lambda x: x[0] == 'pad', stop_idx=3)  # Add quotes using a function
            >>> print(s.to_str(break_inc=0))
            ((layer "F.Cu") (pad 1 "smd" rect))
        """

        kwargs.pop("include_path", None)
        for result in self.search(pattern, **kwargs):
            # Skip the first element (the match identifier) and process up to the stop index (exclusive)
            for i, elem in enumerate(result[1:stop_idx], 1):
                if isinstance(elem, str):
                    result[i] = f'"{result[i]}"'

    def rmv_quotes(self, pattern, stop_idx=None, **kwargs):
        """
        Search for elements matching the given pattern and remove quotes from all elements 
        except the first one in each matching expression.
        
        This method is the reverse of add_quotes() and accepts the same parameters as the search() method,
        except for 'include_path'. It modifies the elements directly in the original Sexp object.
        
        Args:
            pattern: The pattern to search for:
                - str: A slash-delimited path (e.g., "key1/key2" or "/root/key1")
                - function: A function that takes a sublist and returns True/False
                - re.Pattern: A compiled regular expression to match against first element
                - list/tuple: A sequence of indices representing an exact path
            stop_idx (int, optional): If provided, only remove quotes from elements up to this index 
                                     (exclusive). If None, process all elements. Default is None.
            **kwargs: Keyword arguments to pass to the search() method,
                     excluding 'include_path' which is handled internally
        
        Returns:
            None: Modifications are applied in-place to the Sexp object
            
        Examples:
            >>> s = Sexp('((layer "F.Cu") (pad 1 "smd" "rect"))')
            >>> s.add_quotes('layer')  # Add quotes to elements in layer expressions
            >>> s.add_quotes('pad')  # Add quotes to elements in pad expressions
            >>> s.rmv_quotes('layer')  # Remove quotes from elements in layer expressions
            >>> print(s.to_str(break_inc=0))
            ((layer F.Cu) (pad 1 "smd" "rect"))
            
            >>> s.rmv_quotes(lambda x: x[0] == 'pad')  # Remove quotes using a function
            >>> print(s.to_str(break_inc=0))
            ((layer F.Cu) (pad 1 smd rect))
        """
        
        kwargs.pop("include_path", None)
        for result in self.search(pattern, **kwargs):
            # Skip the first element (the match identifier) and process up to the stop index (exclusive)
            for i, elem in enumerate(result[1:stop_idx], 1):
                if isinstance(elem, str):
                    # Check if the string is wrapped in quotes
                    if (elem.startswith('"') and elem.endswith('"')) or (elem.startswith("'") and elem.endswith("'")):
                        # Remove the quotes
                        result[i] = elem[1:-1]

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
