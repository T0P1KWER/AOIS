
from itertools import combinations

from parser import evaluate_postfix

MAX_KARNAUGH_VARIABLE_COUNT = 5


def bool_to_int(value):
    if value:
        return 1
    return 0


def join_with_separator(items, separator):
    if not items:
        return ""
    result = items[0]
    for item in items[1:]:
        result += separator + item
    return result


def bits_to_number(bits):
    text = ""
    for bit in bits:
        text += str(bit)
    return int(text, 2)


def make_assignment_key(assignment, variables):
    values = []
    for variable_name in variables:
        values.append(assignment[variable_name])
    return tuple(values)


def generate_assignments(variables):
    assignments = []
    total_rows = 2 ** len(variables)
    row_number = 0
    while row_number < total_rows:
        assignment = {}
        variable_index = 0
        while variable_index < len(variables):
            shift = len(variables) - variable_index - 1
            bit_value = (row_number >> shift) & 1
            assignment[variables[variable_index]] = bit_value
            variable_index += 1
        assignments.append(assignment)
        row_number += 1
    return assignments


def build_truth_table(parsed_expression):
    rows = []
    assignments = generate_assignments(parsed_expression["variables"])
    for assignment in assignments:
        function_value = evaluate_postfix(parsed_expression["postfix_tokens"], assignment)
        rows.append({
            "assignment": assignment,
            "result": bool_to_int(function_value),
        })
    return rows


def build_sdnf(rows, variables):
    terms = []
    numbers = []
    for row_index, row in enumerate(rows):
        if row["result"] == 1:
            terms.append(build_minterm(row["assignment"], variables))
            numbers.append(row_index)
    expression = join_with_separator(terms, " | ")
    if not expression:
        expression = "0"
    return {"expression": expression, "numbers": numbers}


def build_sknf(rows, variables):
    clauses = []
    numbers = []
    for row_index, row in enumerate(rows):
        if row["result"] == 0:
            clauses.append(build_maxterm(row["assignment"], variables))
            numbers.append(row_index)
    expression = join_with_separator(clauses, " & ")
    if not expression:
        expression = "1"
    return {"expression": expression, "numbers": numbers}


def build_minterm(assignment, variables):
    literals = []
    for variable_name in variables:
        if assignment[variable_name] == 1:
            literals.append(variable_name)
        else:
            literals.append("!" + variable_name)
    return "(" + join_with_separator(literals, " & ") + ")"


def build_maxterm(assignment, variables):
    literals = []
    for variable_name in variables:
        if assignment[variable_name] == 0:
            literals.append(variable_name)
        else:
            literals.append("!" + variable_name)
    return "(" + join_with_separator(literals, " | ") + ")"


def build_index_form(rows):
    bits = []
    for row in rows:
        bits.append(row["result"])
    bit_text = ""
    for bit in bits:
        bit_text += str(bit)
    return {"bit_text": bit_text, "index": bits_to_number(bits)}


def build_zhegalkin_polynomial(rows, variables):
    values = []
    for row in rows:
        values.append(row["result"])
    triangle = build_difference_triangle(values)
    coefficients = []
    for triangle_row in triangle:
        coefficients.append(triangle_row[0])
    terms = []
    index = 0
    while index < len(coefficients):
        if coefficients[index] == 1:
            terms.append(build_polynomial_term(index, variables))
        index += 1
    expression = join_with_separator(terms, " + ")
    if not expression:
        expression = "0"
    return {
        "triangle": triangle,
        "coefficients": coefficients,
        "expression": expression,
    }


def build_difference_triangle(values):
    triangle = [values[:]]
    current_row = values[:]
    while len(current_row) > 1:
        next_row = []
        index = 0
        while index < len(current_row) - 1:
            next_row.append(current_row[index] ^ current_row[index + 1])
            index += 1
        triangle.append(next_row)
        current_row = next_row
    return triangle


def build_polynomial_term(index, variables):
    if index == 0:
        return "1"
    bits = format(index, "0" + str(len(variables)) + "b")
    parts = []
    bit_index = 0
    while bit_index < len(bits):
        if bits[bit_index] == "1":
            parts.append(variables[bit_index])
        bit_index += 1
    return join_with_separator(parts, "*")


def analyze_post_classes(rows, variables, polynomial_data):
    row_map = build_row_map(rows, variables)
    return {
        "T0": rows[0]["result"] == 0,
        "T1": rows[-1]["result"] == 1,
        "S": belongs_to_self_dual(row_map),
        "M": belongs_to_monotone(row_map),
        "L": is_linear_polynomial(polynomial_data, variables),
    }


def build_row_map(rows, variables):
    row_map = {}
    for row in rows:
        row_map[make_assignment_key(row["assignment"], variables)] = row["result"]
    return row_map


def belongs_to_self_dual(row_map):
    for key in row_map:
        opposite_key = invert_key(key)
        if row_map[key] == row_map[opposite_key]:
            return False
    return True


def invert_key(key):
    values = []
    for bit in key:
        if bit == 0:
            values.append(1)
        else:
            values.append(0)
    return tuple(values)


def belongs_to_monotone(row_map):
    keys = list(row_map.keys())
    first_index = 0
    while first_index < len(keys):
        second_index = 0
        while second_index < len(keys):
            smaller_key = keys[first_index]
            bigger_key = keys[second_index]
            if dominates(bigger_key, smaller_key):
                if row_map[smaller_key] > row_map[bigger_key]:
                    return False
            second_index += 1
        first_index += 1
    return True


def dominates(bigger_key, smaller_key):
    index = 0
    while index < len(bigger_key):
        if bigger_key[index] < smaller_key[index]:
            return False
        index += 1
    return True


def is_linear_polynomial(polynomial_data, variables):
    coefficients = polynomial_data["coefficients"]
    index = 0
    while index < len(coefficients):
        if coefficients[index] == 1 and count_degree(index, variables) > 1:
            return False
        index += 1
    return True


def count_degree(index, variables):
    if index == 0:
        return 0
    bits = format(index, "0" + str(len(variables)) + "b")
    degree = 0
    for bit in bits:
        if bit == "1":
            degree += 1
    return degree


def find_dummy_variables(rows, variables):
    row_map = build_row_map(rows, variables)
    dummy_variables = []
    for variable_name in variables:
        if is_dummy_variable(row_map, variables, variable_name):
            dummy_variables.append(variable_name)
    return dummy_variables


def is_dummy_variable(row_map, variables, variable_name):
    variable_index = variables.index(variable_name)
    for key in row_map:
        changed_key = flip_bit(key, variable_index)
        if row_map[key] != row_map[changed_key]:
            return False
    return True


def flip_bit(key, bit_index):
    values = list(key)
    if values[bit_index] == 0:
        values[bit_index] = 1
    else:
        values[bit_index] = 0
    return tuple(values)


def build_derivatives(rows, variables):
    if not variables:
        return []
    derivatives = []
    row_map = build_row_map(rows, variables)
    max_size = min(4, len(variables))
    size = 1
    while size <= max_size:
        for variable_group in combinations(variables, size):
            derivatives.append(build_single_derivative(variable_group, row_map, variables))
        size += 1
    return derivatives


def build_single_derivative(variable_group, row_map, variables):
    free_variables = []
    for variable_name in variables:
        if variable_name not in variable_group:
            free_variables.append(variable_name)
    derivative_rows = []
    total_rows = 2 ** len(free_variables)
    row_number = 0
    while row_number < total_rows:
        free_assignment = build_assignment_by_number(free_variables, row_number)
        derivative_value = calculate_derivative_value(variable_group, free_assignment, variables, row_map)
        derivative_rows.append({
            "assignment": free_assignment,
            "result": derivative_value,
        })
        row_number += 1
    return {
        "variables": variable_group,
        "free_variables": free_variables,
        "rows": derivative_rows,
    }


def build_assignment_by_number(variables, row_number):
    assignment = {}
    index = 0
    while index < len(variables):
        shift = len(variables) - index - 1
        assignment[variables[index]] = (row_number >> shift) & 1
        index += 1
    return assignment


def calculate_derivative_value(variable_group, free_assignment, variables, row_map):
    total_value = 0
    total_variants = 2 ** len(variable_group)
    variant = 0
    while variant < total_variants:
        full_assignment = fill_full_assignment(variable_group, free_assignment, variables, variant)
        key = make_assignment_key(full_assignment, variables)
        total_value ^= row_map[key]
        variant += 1
    return total_value


def fill_full_assignment(variable_group, free_assignment, variables, variant_number):
    assignment = {}
    group_values = {}
    index = 0
    while index < len(variable_group):
        shift = len(variable_group) - index - 1
        group_values[variable_group[index]] = (variant_number >> shift) & 1
        index += 1
    for variable_name in variables:
        if variable_name in group_values:
            assignment[variable_name] = group_values[variable_name]
        else:
            assignment[variable_name] = free_assignment[variable_name]
    return assignment


def build_karnaugh_maps(rows, variables, minimization_data):
    if len(variables) == 0:
        return {"available": False, "message": "Для константной функции карта Карно не требуется."}
    if len(variables) > MAX_KARNAUGH_VARIABLE_COUNT:
        return {"available": False, "message": "Карта Карно строится только для функций до 5 переменных."}
    return {
        "available": True,
        "dnf": build_single_karnaugh_map(rows, variables, minimization_data["dnf"], 1),
        "cnf": build_single_karnaugh_map(rows, variables, minimization_data["cnf"], 0),
    }


def build_single_karnaugh_map(rows, variables, minimization_result, target_value):
    row_variables, column_variables, layer_variables = split_variables(variables)
    row_codes = build_gray_codes(len(row_variables))
    column_codes = build_gray_codes(len(column_variables))
    cells = []
    for row_code in row_codes:
        cell_row = []
        for column_code in column_codes:
            full_bits = row_code + column_code
            row_number = int(full_bits, 2)
            cell_row.append(rows[row_number]["result"])
        cells.append(cell_row)
    groups = build_groups_from_implicants(minimization_result["selected_implicants"], variables, target_value)
    return {
        "row_variables": row_variables,
        "column_variables": column_variables,
        "layer_variables": layer_variables,
        "row_codes": row_codes,
        "column_codes": column_codes,
        "layers": [{"layer_code": "", "layer_values": "", "cells": cells}],
        "groups": groups,
    }


def split_variables(variables):
    if len(variables) == 1:
        return [], [variables[0]], []
    if len(variables) == 2:
        return [variables[0]], [variables[1]], []
    if len(variables) == 3:
        return [variables[0]], [variables[1], variables[2]], []
    if len(variables) == 4:
        return [variables[0], variables[1]], [variables[2], variables[3]], []
    return [variables[0], variables[1]], [variables[2], variables[3], variables[4]], []


def build_gray_codes(bit_count):
    if bit_count == 0:
        return [""]
    if bit_count == 1:
        return ["0", "1"]
    if bit_count == 3:
        return ["000", "001", "011", "010", "110", "111", "101", "100"]
    return ["00", "01", "11", "10"]


def build_groups_from_implicants(implicants, variables, target_value):
    groups = []
    group_number = 1
    for implicant in implicants:
        covered_rows = []
        row_number = 0
        while row_number < 2 ** len(variables):
            if implicant_covers_number(implicant, row_number):
                covered_rows.append(row_number)
            row_number += 1
        groups.append({
            "name": "K" + str(group_number),
            "numbers": covered_rows,
            "expression": build_text_by_implicant(implicant, variables, "dnf" if target_value == 1 else "cnf"),
        })
        group_number += 1
    return groups


def format_karnaugh_header(map_data):
    left_name = join_with_separator(map_data["row_variables"], "")
    right_name = join_with_separator(map_data["column_variables"], "")
    if not left_name:
        left_name = "-"
    if not right_name:
        right_name = "-"
    return left_name + "\\" + right_name


def implicant_covers_number(implicant, row_number):
    bits = build_bits_by_number(row_number, len(implicant["bits"]))
    index = 0
    while index < len(bits):
        implicant_bit = implicant["bits"][index]
        if implicant_bit is not None and implicant_bit != bits[index]:
            return False
        index += 1
    return True


def build_bits_by_number(row_number, variable_count):
    bits = []
    shift = variable_count - 1
    while shift >= 0:
        bits.append((row_number >> shift) & 1)
        shift -= 1
    return bits


def build_text_by_implicant(implicant, variables, mode):
    literals = []
    index = 0
    while index < len(variables):
        bit = implicant["bits"][index]
        variable_name = variables[index]
        if bit is not None:
            literals.append(build_literal_text(variable_name, bit, mode))
        index += 1
    if not literals:
        if mode == "dnf":
            return "1"
        return "0"
    if mode == "dnf":
        if len(literals) == 1:
            return literals[0]
        return "(" + join_with_separator(literals, " & ") + ")"
    if len(literals) == 1:
        return literals[0]
    return "(" + join_with_separator(literals, " | ") + ")"


def build_literal_text(variable_name, bit, mode):
    if mode == "dnf":
        if bit == 1:
            return variable_name
        return "!" + variable_name
    if bit == 0:
        return variable_name
    return "!" + variable_name
