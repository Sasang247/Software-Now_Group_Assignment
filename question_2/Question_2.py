"""
evaluator.py

Reads mathematical expressions from a text file, parses and evaluates each
expression using recursive descent parsing, and writes the results to
'output.txt' in the same directory as the input file.

Features:
- Supports +, -, *, /
- Supports nested parentheses
- Supports unary negation
- Rejects unary plus
- Supports implicit multiplication, e.g.:
    2(3+4)
    (2)(3)
    3(-2)
    2 3   -> interpreted as 2*3 after tokenisation
- Uses plain functions only (no classes)
"""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Any



# Number formatting helpers


def format_decimal_literal(value: Decimal) -> str:
    """
    Format a numeric literal for the parse tree.

    Whole numbers are displayed without a decimal point.
    Other numbers are displayed without unnecessary trailing zeros.
    """
    normalized = value.normalize()

    if normalized == normalized.to_integral():
        return str(int(normalized))

    text = format(normalized, "f")
    text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def format_result_value(value: float) -> str:
    """
    Format the final computed result.

    - Whole numbers are displayed without decimal places.
    - Otherwise values are rounded to 4 decimal places.
    """
    if value.is_integer():
        return str(int(value))

    rounded = round(value, 4)
    if rounded.is_integer():
        return str(int(rounded))

    return f"{rounded:.4f}".rstrip("0").rstrip(".")



# Tokenisation


def is_number_start(text: str, index: int) -> bool:
    """
    Return True if a number can start at text[index].

    Supports:
    - digits: 12
    - decimals: 3.5
    - leading decimal point: .5
    """
    char = text[index]

    if char.isdigit():
        return True

    if char == ".":
        return index + 1 < len(text) and text[index + 1].isdigit()

    return False


def read_number(text: str, start: int) -> tuple[Decimal, int]:
    """
    Read a numeric literal starting at position 'start'.

    Returns:
        (Decimal value, next index)

    Raises:
        ValueError if the number format is invalid.
    """
    index = start
    dot_count = 0
    digit_count = 0

    while index < len(text) and (text[index].isdigit() or text[index] == "."):
        if text[index] == ".":
            dot_count += 1
            if dot_count > 1:
                raise ValueError("Invalid number format")
        else:
            digit_count += 1
        index += 1

    if digit_count == 0:
        raise ValueError("Invalid number format")

    number_text = text[start:index]

    try:
        value = Decimal(number_text)
    except InvalidOperation as exc:
        raise ValueError("Invalid number format") from exc

    return value, index


def needs_implicit_multiplication(previous_token: tuple[str, Any],
                                  current_token: tuple[str, Any]) -> bool:
    """
    Determine whether an implicit multiplication operator should be inserted
    between two adjacent tokens.

    Valid examples:
    - 2(3+4)
    - (2)(3)
    - 2 3
    - 3(-2)
    - (-2)4
    """
    previous_type, previous_value = previous_token
    current_type, current_value = current_token

    left_can_end_value = (
        previous_type == "NUM" or
        (previous_type == "RPAREN")
    )

    right_can_start_value = (
        current_type == "NUM" or
        current_type == "LPAREN"
    )

    return left_can_end_value and right_can_start_value


def tokenize(expression: str) -> list[tuple[str, Any]]:
    """
    Convert an input expression into tokens.

    Token types:
    - NUM
    - OP
    - LPAREN
    - RPAREN
    - END

    Implicit multiplication is inserted as OP:*.
    Unary negation is NOT folded into a number token.
    """
    raw_tokens: list[tuple[str, Any]] = []
    index = 0

    while index < len(expression):
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if is_number_start(expression, index):
            number_value, index = read_number(expression, index)
            raw_tokens.append(("NUM", number_value))
            continue

        if char in "+-*/":
            raw_tokens.append(("OP", char))
            index += 1
            continue

        if char == "(":
            raw_tokens.append(("LPAREN", "("))
            index += 1
            continue

        if char == ")":
            raw_tokens.append(("RPAREN", ")"))
            index += 1
            continue

        raise ValueError(f"Invalid character: {char}")

    tokens_with_implicit_mult: list[tuple[str, Any]] = []

    for token in raw_tokens:
        if tokens_with_implicit_mult:
            previous = tokens_with_implicit_mult[-1]
            if needs_implicit_multiplication(previous, token):
                tokens_with_implicit_mult.append(("OP", "*"))
        tokens_with_implicit_mult.append(token)

    tokens_with_implicit_mult.append(("END", None))
    return tokens_with_implicit_mult


def token_to_string(token: tuple[str, Any]) -> str:
    """
    Convert a token to the required output format.
    """
    token_type, value = token

    if token_type == "NUM":
        return f"[NUM:{format_decimal_literal(value)}]"
    if token_type == "OP":
        return f"[OP:{value}]"
    if token_type == "LPAREN":
        return "[LPAREN:(]"
    if token_type == "RPAREN":
        return "[RPAREN:)]"
    if token_type == "END":
        return "[END]"

    raise ValueError("Unknown token type")


def tokens_to_string(tokens: list[tuple[str, Any]]) -> str:
    """
    Convert a full token list into the required display format.
    """
    return " ".join(token_to_string(token) for token in tokens)



# Recursive descent parsing


def current_token(tokens: list[tuple[str, Any]], position: int) -> tuple[str, Any]:
    """
    Return the current token.
    """
    return tokens[position]


def parse_expression(tokens: list[tuple[str, Any]], position: int) -> tuple[Any, int]:
    """
    Parse the lowest-precedence level: + and -
    """
    left_node, position = parse_term(tokens, position)

    while True:
        token_type, token_value = current_token(tokens, position)

        if token_type == "OP" and token_value in ("+", "-"):
            operator = token_value
            position += 1
            right_node, position = parse_term(tokens, position)
            left_node = ("bin", operator, left_node, right_node)
        else:
            break

    return left_node, position


def parse_term(tokens: list[tuple[str, Any]], position: int) -> tuple[Any, int]:
    """
    Parse the middle-precedence level: * and /
    """
    left_node, position = parse_factor(tokens, position)

    while True:
        token_type, token_value = current_token(tokens, position)

        if token_type == "OP" and token_value in ("*", "/"):
            operator = token_value
            position += 1
            right_node, position = parse_factor(tokens, position)
            left_node = ("bin", operator, left_node, right_node)
        else:
            break

    return left_node, position


def parse_factor(tokens: list[tuple[str, Any]], position: int) -> tuple[Any, int]:
    """
    Parse unary negation and primary expressions.

    Unary plus is explicitly rejected.
    """
    token_type, token_value = current_token(tokens, position)

    if token_type == "OP" and token_value == "+":
        raise ValueError("Unary plus is not supported")

    if token_type == "OP" and token_value == "-":
        position += 1
        operand_node, position = parse_factor(tokens, position)
        return ("neg", operand_node), position

    return parse_primary(tokens, position)


def parse_primary(tokens: list[tuple[str, Any]], position: int) -> tuple[Any, int]:
    """
    Parse number literals and parenthesised expressions.
    """
    token_type, token_value = current_token(tokens, position)

    if token_type == "NUM":
        return ("num", token_value), position + 1

    if token_type == "LPAREN":
        position += 1
        node, position = parse_expression(tokens, position)

        if current_token(tokens, position)[0] != "RPAREN":
            raise ValueError("Missing closing parenthesis")

        return node, position + 1

    raise ValueError("Expected number or parenthesised expression")


def parse(tokens: list[tuple[str, Any]]) -> Any:
    """
    Parse a full expression and ensure all tokens are consumed.
    """
    node, position = parse_expression(tokens, 0)

    if current_token(tokens, position)[0] != "END":
        raise ValueError("Unexpected token after complete expression")

    return node



# Tree formatting


def tree_to_string(node: Any) -> str:
    """
    Convert a parse tree into the required prefix-style tree format.
    """
    node_type = node[0]

    if node_type == "num":
        return format_decimal_literal(node[1])

    if node_type == "neg":
        return f"(neg {tree_to_string(node[1])})"

    if node_type == "bin":
        operator, left_node, right_node = node[1], node[2], node[3]
        return f"({operator} {tree_to_string(left_node)} {tree_to_string(right_node)})"

    raise ValueError("Unknown node type")


# Evaluation


def evaluate_tree(node: Any) -> float:
    """
    Evaluate a parse tree and return the numeric result as float.
    """
    node_type = node[0]

    if node_type == "num":
        return float(node[1])

    if node_type == "neg":
        return -evaluate_tree(node[1])

    if node_type == "bin":
        operator, left_node, right_node = node[1], node[2], node[3]
        left_value = evaluate_tree(left_node)
        right_value = evaluate_tree(right_node)

        if operator == "+":
            return left_value + right_value
        if operator == "-":
            return left_value - right_value
        if operator == "*":
            return left_value * right_value
        if operator == "/":
            if right_value == 0:
                raise ValueError("Division by zero")
            return left_value / right_value

    raise ValueError("Invalid parse tree")



# Per-expression processing


def evaluate_expression(expression: str) -> dict:
    """
    Evaluate one expression and return the required dictionary structure.

    On success:
        {
            "input": original text,
            "tree": tree string,
            "tokens": token string,
            "result": float
        }

    On failure:
        {
            "input": original text,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR"
        }
    """
    try:
        tokens = tokenize(expression)
        tree = parse(tokens)
        result = evaluate_tree(tree)

        return {
            "input": expression,
            "tree": tree_to_string(tree),
            "tokens": tokens_to_string(tokens),
            "result": float(result),
        }

    except Exception:
        return {
            "input": expression,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR",
        }


# Output writing


def result_to_output_block(record: dict) -> str:
    """
    Convert a result record into the required four-line output block.
    """
    if record["result"] == "ERROR":
        result_text = "ERROR"
    else:
        result_text = format_result_value(record["result"])

    return (
        f"Input: {record['input']}\n"
        f"Tree: {record['tree']}\n"
        f"Tokens: {record['tokens']}\n"
        f"Result: {result_text}"
    )


def write_output_file(output_path: str, results: list[dict]) -> None:
    """
    Write all expression results to output.txt.
    """
    blocks = [result_to_output_block(record) for record in results]
    content = "\n\n".join(blocks)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)



# Required interface


def evaluate_file(input_path: str) -> list[dict]:
    """
    Read expressions from input_path, evaluate each line, write output.txt
    in the same directory, and return the result list.
    """
    with open(input_path, "r", encoding="utf-8") as file:
        lines = [line.rstrip("\n") for line in file]

    results = [evaluate_expression(line) for line in lines]

    output_path = os.path.join(os.path.dirname(input_path), "output.txt")
    write_output_file(output_path, results)

    return results