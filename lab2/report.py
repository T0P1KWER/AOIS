from logic import build_sdnf, build_sknf, format_karnaugh_header, join_with_separator
from minimization import format_implicant_bits


def build_report(expression_text, parsed_expression, rows, forms, polynomial_data, post_data, dummy_variables, derivatives, minimization_data, karnaugh_data):
    lines = []
    lines.append("Выражение: " + expression_text)
    add_blank_line(lines)

    add_truth_table(lines, rows, parsed_expression["variables"])
    add_blank_line(lines)

    lines.append("СКНФ: " + forms["sknf"]["expression"])
    lines.append("СДНФ: " + forms["sdnf"]["expression"])
    add_blank_line(lines)

    lines.append("СКНФ (числовая форма): " + build_square_list(forms["sknf"]["numbers"]))
    lines.append("СДНФ (числовая форма): " + build_square_list(forms["sdnf"]["numbers"]))
    lines.append("Индексная форма функции: " + str(forms["index"]["index"]))
    lines.append("Формула Жегалкина: " + format_polynomial(polynomial_data["expression"]))
    add_blank_line(lines)

    lines.append("Свойства функции:")
    lines.append("T0: " + str(post_data["T0"]))
    lines.append("T1: " + str(post_data["T1"]))
    lines.append("S: " + str(post_data["S"]))
    lines.append("M: " + str(post_data["M"]))
    lines.append("L: " + str(post_data["L"]))
    add_blank_line(lines)

    if dummy_variables:
        lines.append("Фиктивные переменные: " + join_with_separator(dummy_variables, ", "))
    else:
        lines.append("Фиктивные переменные: отсутствуют")
    add_blank_line(lines)

    lines.append("Канонические формы булевых производных:")
    add_blank_line(lines)
    add_derivatives(lines, derivatives)

    add_minimization_block(lines, minimization_data["cnf"], "SKNF")
    add_blank_line(lines)
    add_minimization_block(lines, minimization_data["dnf"], "SDNF")
    add_blank_line(lines)

    lines.append("Минимизированная СКНФ (расчетный метод): " + minimization_data["cnf"]["expression"])
    lines.append("Минимизированная СДНФ (расчетный метод): " + minimization_data["dnf"]["expression"])
    add_blank_line(lines)

    add_coverage_table(lines, minimization_data["cnf"], "SKNF")
    add_blank_line(lines)
    add_coverage_table(lines, minimization_data["dnf"], "SDNF")
    add_blank_line(lines)

    lines.append("Минимизированная СКНФ (расчетно-табличный метод): " + minimization_data["cnf"]["expression"])
    lines.append("Минимизированная СДНФ (расчетно-табличный метод): " + minimization_data["dnf"]["expression"])
    add_blank_line(lines)

    add_karnaugh(lines, karnaugh_data, minimization_data)
    return "\n".join(lines)


def add_blank_line(lines):
    lines.append("")


def add_truth_table(lines, rows, variables):
    header = join_with_separator(variables, "  ") + " | f"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        values = []
        for variable_name in variables:
            values.append(str(row["assignment"][variable_name]))
        lines.append(join_with_separator(values, "  ") + " | " + str(row["result"]))


def build_square_list(numbers):
    texts = []
    for number in numbers:
        texts.append(str(number))
    return "[" + join_with_separator(texts, ", ") + "]"


def format_polynomial(polynomial_text):
    text = polynomial_text.replace(" ⊕ ", " + ")
    text = text.replace("*", "")
    return text


def add_derivatives(lines, derivatives):
    for derivative in derivatives:
        variable_group = join_with_separator(list(derivative["variables"]), "")
        lines.append("Производная dF/d" + variable_group + ":")
        if derivative["free_variables"]:
            derivative_sdnf = build_sdnf(derivative["rows"], derivative["free_variables"])
            derivative_sknf = build_sknf(derivative["rows"], derivative["free_variables"])
            lines.append("СДНФ(dF/d" + variable_group + ") = " + normalize_expression_text(derivative_sdnf["expression"]))
            lines.append("СКНФ(dF/d" + variable_group + ") = " + normalize_expression_text(derivative_sknf["expression"]))
        else:
            value_text = str(derivative["rows"][0]["result"])
            lines.append("СДНФ(dF/d" + variable_group + ") = " + value_text)
            lines.append("СКНФ(dF/d" + variable_group + ") = " + value_text)
        add_blank_line(lines)


def add_minimization_block(lines, minimization_result, label):
    lines.append("Минимизация расчетным методом (" + label + "):")
    add_blank_line(lines)

    lines.append("Этап 1 (" + label + "): Исходные термы")
    add_implicant_bits_only(lines, minimization_result["initial_implicants"])
    add_blank_line(lines)

    stage_number = 2
    for stage in minimization_result["stages"]:
        lines.append("Этап " + str(stage_number) + " (" + label + "): Склеивание")
        if stage["pairs"]:
            add_implicant_bits_only(lines, stage["result_implicants"])
        else:
            lines.append("Склеивание завершено, новых термов нет.")
            add_blank_line(lines)
            add_implicant_bits_only(lines, minimization_result["prime_implicants"])
        add_blank_line(lines)
        stage_number += 1

    final_expression = minimization_result["expression"]
    if label == "SDNF":
        final_expression = wrap_single_terms(final_expression)
    lines.append("Финальный результат (" + label + "): " + final_expression)


def add_implicant_bits_only(lines, implicants):
    if not implicants:
        lines.append("-")
        return
    for implicant in implicants:
        lines.append(format_implicant_bits(implicant["bits"]).replace("X", "-"))


def add_coverage_table(lines, minimization_result, label):
    lines.append("Минимизация расчетно-табличным методом (" + label + "):")
    lines.append("Этап 1 (" + label + "): Исходные термы")
    add_implicant_bits_only(lines, minimization_result["initial_implicants"])
    add_blank_line(lines)

    stage_number = 2
    for stage in minimization_result["stages"]:
        lines.append("Этап " + str(stage_number) + " (" + label + "): Склеивание")
        if stage["pairs"]:
            add_implicant_bits_only(lines, stage["result_implicants"])
        else:
            lines.append("Склеивание завершено, новых термов нет.")
        add_blank_line(lines)
        stage_number += 1

    lines.append("Этап " + str(stage_number) + " (" + label + "): Удаление избыточных импликант")
    add_implicant_bits_only(lines, minimization_result["selected_implicants"])
    add_blank_line(lines)

    lines.append("Таблица покрытия:")
    header_parts = []
    for number in minimization_result["row_numbers"]:
        header_parts.append(format_number_bits(number, minimization_result))
    header = "    | " + join_with_separator(header_parts, " | ")
    lines.append(header)
    lines.append("-" * len(header))

    for row in minimization_result["coverage_table"]:
        marks = []
        for mark in row["marks"]:
            if mark:
                marks.append("X  ")
            else:
                marks.append("   ")
        line = format_implicant_bits(row["implicant"]["bits"]).replace("X", "-")
        line += " | " + join_with_separator(marks, "| ")
        lines.append(line)


def add_karnaugh(lines, karnaugh_data, minimization_data):
    lines.append("Карта Карно:")
    if not karnaugh_data["available"]:
        lines.append(karnaugh_data["message"])
        return

    map_data = karnaugh_data["dnf"]
    layer_index = 0
    while layer_index < len(map_data["layers"]):
        current_layer = map_data["layers"][layer_index]
        if map_data["layer_variables"] and current_layer["layer_values"]:
            lines.append(current_layer["layer_values"] + ":")
        header = format_karnaugh_header(map_data) + " | " + join_with_separator(map_data["column_codes"], " | ")
        lines.append(header)
        lines.append("-" * len(header))

        row_index = 0
        while row_index < len(map_data["row_codes"]):
            row_name = map_data["row_codes"][row_index]
            if row_name == "":
                row_name = "-"
            values = []
            for value in current_layer["cells"][row_index]:
                values.append(str(value))
            lines.append(pad_left(row_name, 3) + " | " + join_with_separator(values, " | "))
            row_index += 1
        add_blank_line(lines)
        layer_index += 1

    lines.append("Минимизированная СКНФ (карта Карно): " + minimization_data["cnf"]["expression"])
    lines.append("Минимизированная СДНФ (карта Карно): " + wrap_single_terms(minimization_data["dnf"]["expression"]))


def normalize_expression_text(expression_text):
    return expression_text


def wrap_single_terms(expression_text):
    parts = expression_text.split(" | ")
    normalized_parts = []
    for part in parts:
        if " & " in part:
            normalized_parts.append(part)
        elif part in ("0", "1"):
            normalized_parts.append(part)
        elif part.startswith("(") and part.endswith(")"):
            normalized_parts.append(part)
        else:
            normalized_parts.append("(" + part + ")")
    return join_with_separator(normalized_parts, " | ")


def format_number_bits(number, minimization_result):
    if not minimization_result["initial_implicants"]:
        return str(number)
    width = len(minimization_result["initial_implicants"][0]["bits"])
    return format(number, "0" + str(width) + "b")


def pad_left(text, width):
    """Добавляет пробелы слева для более ровного вывода."""
    result = str(text)
    while len(result) < width:
        result = " " + result
    return result
