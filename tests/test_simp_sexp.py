import pytest
from simp_sexp import tokenize, parse, parse_string, to_string, ParseError


def test_tokenize():
    assert tokenize("(+ 1 2)") == ["(", "+", "1", "2", ")"]
    assert tokenize("(define (square x) (* x x))") == ["(", "define", "(", "square", "x", ")", "(", "*", "x", "x", ")", ")"]


def test_parse():
    assert parse(["(", "+", "1", "2", ")"]) == ["+", 1, 2]
    assert parse(["(", "define", "(", "square", "x", ")", "(", "*", "x", "x", ")", ")"]) == ["define", ["square", "x"], ["*", "x", "x"]]


def test_parse_string():
    assert parse_string("(+ 1 2)") == ["+", 1, 2]
    assert parse_string("(define (square x) (* x x))") == ["define", ["square", "x"], ["*", "x", "x"]]


def test_to_string():
    assert to_string(["+", 1, 2]) == "(+ 1 2)"
    assert to_string(["define", ["square", "x"], ["*", "x", "x"]]) == "(define (square x) (* x x))"


def test_nested_expressions():
    expr = parse_string("(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))")
    assert expr == ["define", ["factorial", "n"], ["if", ["=", "n", 0], 1, ["*", "n", ["factorial", ["-", "n", 1]]]]]
    assert to_string(expr) == "(define (factorial n) (if (= n 0) 1 (* n (factorial (- n 1)))))"


def test_number_conversion():
    assert parse_string("(+ 1 2.5)") == ["+", 1, 2.5]
    assert parse_string("(* -3 4)") == ["*", -3, 4]


def test_parse_errors():
    with pytest.raises(ParseError):
        parse_string("(")
    
    with pytest.raises(ParseError):
        parse_string(")")
        
    with pytest.raises(ParseError):
        parse_string("(+ 1 2")