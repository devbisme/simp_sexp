import pytest
from simp_sexp import sexp_to_nested_list, nested_list_to_sexp, prettify_sexp


def test_sexp_to_nested_list_basic():
    assert sexp_to_nested_list("(+ 1 2)") == ["+", 1, 2]
    assert sexp_to_nested_list("(define (square x) (* x x))") == ["define", ["square", "x"], ["*", "x", "x"]]


def test_sexp_to_nested_list_quotes():
    assert sexp_to_nested_list('(display "Hello world")') == ["display", "Hello world"]
    assert sexp_to_nested_list("(print 'Hello world')") == ["print", "Hello world"]


def test_nested_list_to_sexp():
    assert nested_list_to_sexp(["+", 1, 2]) == '(+ "1" "2")'
    assert nested_list_to_sexp(["define", ["square", "x"], ["*", "x", "x"]], inline=True) == '(define (square "x") (* "x" "x"))'


def test_nested_expressions():
    expr = sexp_to_nested_list("(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))")
    assert expr == ["define", ["factorial", "n"], ["if", ["=", "n", 0], 1, ["*", "n", ["factorial", ["-", "n", 1]]]]]
    sexp = nested_list_to_sexp(expr)
    # Convert back to make sure the result is equivalent
    assert sexp_to_nested_list(sexp) == expr


def test_number_conversion():
    assert sexp_to_nested_list("(+ 1 2.5)") == ["+", 1, 2.5]
    assert sexp_to_nested_list("(* -3 4)") == ["*", -3, 4]


def test_escaped_quotes():
    assert sexp_to_nested_list(r'(print "Hello \"world\"")') == ["print", 'Hello "world"']
    assert sexp_to_nested_list(r"(print 'Hello \'world\'')") == ["print", "Hello 'world'"]


def test_unclosed_quotes_error():
    with pytest.raises(ValueError):
        sexp_to_nested_list('(print "Hello world)')
    
    with pytest.raises(ValueError):
        sexp_to_nested_list("(print 'Hello world)")


def test_prettify_sexp():
    ugly_sexp = '(define (square x) (* x x))'
    pretty = prettify_sexp(ugly_sexp)
    assert '(' in pretty
    assert ')' in pretty
    assert 'define' in pretty
    assert 'square' in pretty
    
    # Test with custom indentation
    pretty_custom = prettify_sexp(ugly_sexp, spaces_per_level=4)
    assert pretty_custom.count(' ') > pretty.count(' ')


def test_roundtrip_conversion():
    original = "(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))"
    nested = sexp_to_nested_list(original)
    sexp = nested_list_to_sexp(nested)
    # Verify the round trip preserves the structure
    assert sexp_to_nested_list(sexp) == nested