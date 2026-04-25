
AVAILABLE_VARIABLES = ["a", "b", "c", "d", "e"]
MAX_VARIABLE_COUNT = 5

NEGATION_SIGN = "!"
CONJUNCTION_SIGN = "&"
DISJUNCTION_SIGN = "|"
IMPLICATION_SIGN = "->"
EQUIVALENCE_SIGN = "~"

OPERATOR_PRIORITY = {
    NEGATION_SIGN: 5,
    CONJUNCTION_SIGN: 4,
    DISJUNCTION_SIGN: 3,
    IMPLICATION_SIGN: 2,
    EQUIVALENCE_SIGN: 1,
}

RIGHT_ASSOCIATIVE_OPERATORS = {
    NEGATION_SIGN,
    IMPLICATION_SIGN,
    EQUIVALENCE_SIGN,
}

UNARY_OPERATORS = {NEGATION_SIGN}


def normalize_expression(expression_text):
    normalized_text = expression_text.lower()
    normalized_text = normalized_text.replace(" ", "")
    normalized_text = normalized_text.replace("¬", NEGATION_SIGN)
    normalized_text = normalized_text.replace("!", NEGATION_SIGN)
    normalized_text = normalized_text.replace("∧", CONJUNCTION_SIGN)
    normalized_text = normalized_text.replace("*", CONJUNCTION_SIGN)
    normalized_text = normalized_text.replace("∨", DISJUNCTION_SIGN)
    normalized_text = normalized_text.replace("+", DISJUNCTION_SIGN)
    normalized_text = normalized_text.replace("→", IMPLICATION_SIGN)
    normalized_text = normalized_text.replace("=", EQUIVALENCE_SIGN)
    normalized_text = normalized_text.replace("↔", EQUIVALENCE_SIGN)
    return normalized_text


def is_variable(symbol):
    return symbol in AVAILABLE_VARIABLES


def is_operator(token):
    return token in OPERATOR_PRIORITY


def is_binary_operator(token):
    return is_operator(token) and token not in UNARY_OPERATORS


def tokenize(expression_text):
    tokens = []
    index = 0
    while index < len(expression_text):
        current_symbol = expression_text[index]
        if is_variable(current_symbol) or current_symbol in ("(", ")"):
            tokens.append(current_symbol)
            index += 1
            continue
        if expression_text[index:index + 2] == IMPLICATION_SIGN:
            tokens.append(IMPLICATION_SIGN)
            index += 2
            continue
        if current_symbol in (NEGATION_SIGN, CONJUNCTION_SIGN, DISJUNCTION_SIGN, EQUIVALENCE_SIGN):
            tokens.append(current_symbol)
            index += 1
            continue
        raise ValueError(f"Недопустимый символ: {current_symbol}")
    return tokens


def collect_variables(tokens):
    variables = []
    for token in tokens:
        if is_variable(token) and token not in variables:
            variables.append(token)
    variables.sort()
    if len(variables) > MAX_VARIABLE_COUNT:
        raise ValueError("Допускается не более 5 переменных.")
    return variables


def validate_tokens(tokens):
    if not tokens:
        raise ValueError("Пустое выражение.")
    balance = 0
    previous_token = None
    for token in tokens:
        if token == "(":
            balance += 1
        if token == ")":
            balance -= 1
        if balance < 0:
            raise ValueError("Лишняя закрывающая скобка.")
        check_neighbor_tokens(previous_token, token)
        previous_token = token
    if balance != 0:
        raise ValueError("Количество открывающих и закрывающих скобок не совпадает.")
    check_expression_ending(tokens[-1])


def check_neighbor_tokens(previous_token, current_token):
    if previous_token is None:
        check_expression_start(current_token)
        return
    if is_right_value(previous_token) and is_left_value(current_token):
        raise ValueError("Между значениями пропущена операция.")
    if previous_token == "(" and current_token == ")":
        raise ValueError("Пустые скобки недопустимы.")
    if is_binary_operator(previous_token) and is_binary_operator(current_token):
        raise ValueError("Две бинарные операции подряд недопустимы.")
    if previous_token == "(" and is_binary_operator(current_token):
        raise ValueError("После '(' не может идти бинарная операция.")
    if is_binary_operator(previous_token) and current_token == ")":
        raise ValueError("Перед ')' не может стоять бинарная операция.")


def is_left_value(token):
    return is_variable(token) or token == "(" or token == NEGATION_SIGN


def is_right_value(token):
    return is_variable(token) or token == ")"


def check_expression_start(first_token):
    if is_binary_operator(first_token) or first_token == ")":
        raise ValueError("Некорректное начало выражения.")


def check_expression_ending(last_token):
    if is_binary_operator(last_token) or last_token == "(":
        raise ValueError("Некорректный конец выражения.")


def should_pop_operator(stack_operator, current_operator):
    if stack_operator == "(":
        return False
    stack_priority = OPERATOR_PRIORITY[stack_operator]
    current_priority = OPERATOR_PRIORITY[current_operator]
    if current_operator in RIGHT_ASSOCIATIVE_OPERATORS:
        return stack_priority > current_priority
    return stack_priority >= current_priority


def to_postfix(tokens):
    output = []
    stack = []
    for token in tokens:
        if is_variable(token):
            output.append(token)
            continue
        if token == "(":
            stack.append(token)
            continue
        if token == ")":
            move_operators_until_open_bracket(output, stack)
            continue
        while stack and should_pop_operator(stack[-1], token):
            output.append(stack.pop())
        stack.append(token)
    while stack:
        output.append(stack.pop())
    return output


def move_operators_until_open_bracket(output, stack):
    while stack and stack[-1] != "(":
        output.append(stack.pop())
    if not stack:
        raise ValueError("Не найдена открывающая скобка.")
    stack.pop()


def evaluate_postfix(postfix_tokens, assignment):
    stack = []
    for token in postfix_tokens:
        if is_variable(token):
            stack.append(bool(assignment[token]))
            continue
        if token in UNARY_OPERATORS:
            operand = stack.pop()
            stack.append(not operand)
            continue
        right_operand = stack.pop()
        left_operand = stack.pop()
        stack.append(apply_binary_operator(token, left_operand, right_operand))
    return stack[0]


def apply_binary_operator(operator_token, left_operand, right_operand):
    if operator_token == CONJUNCTION_SIGN:
        return left_operand and right_operand
    if operator_token == DISJUNCTION_SIGN:
        return left_operand or right_operand
    if operator_token == IMPLICATION_SIGN:
        return (not left_operand) or right_operand
    return left_operand == right_operand


def parse_expression(expression_text):
    normalized_text = normalize_expression(expression_text)
    tokens = tokenize(normalized_text)
    validate_tokens(tokens)
    variables = collect_variables(tokens)
    postfix_tokens = to_postfix(tokens)
    return {
        "raw_text": expression_text,
        "normalized_text": normalized_text,
        "tokens": tokens,
        "variables": variables,
        "postfix_tokens": postfix_tokens,
    }
