from logic import join_with_separator

DON_T_CARE_SIGN = "X"


def minimize_function(rows, variables):
    ones = collect_row_numbers(rows, 1)
    zeros = collect_row_numbers(rows, 0)
    return {
        "dnf": minimize_by_numbers(ones, variables, "dnf"),
        "cnf": minimize_by_numbers(zeros, variables, "cnf"),
    }


def collect_row_numbers(rows, expected_value):
    numbers = []
    for row_index, row in enumerate(rows):
        if row["result"] == expected_value:
            numbers.append(row_index)
    return numbers


def minimize_by_numbers(row_numbers, variables, mode):
    if not row_numbers:
        return build_empty_minimization_result(mode, row_numbers)
    initial_implicants = create_initial_implicants(row_numbers, len(variables))
    stages, prime_implicants = build_gluing_stages(initial_implicants)
    coverage_table = build_coverage_table(prime_implicants, row_numbers)
    selected_implicants = select_cover(prime_implicants, row_numbers)
    expression_text = build_expression(selected_implicants, variables, mode)
    return {
        "mode": mode,
        "row_numbers": row_numbers,
        "initial_implicants": initial_implicants,
        "stages": stages,
        "prime_implicants": prime_implicants,
        "coverage_table": coverage_table,
        "selected_implicants": selected_implicants,
        "expression": expression_text,
    }


def build_empty_minimization_result(mode, row_numbers):
    if mode == "dnf":
        expression_text = "0"
    else:
        expression_text = "1"
    return {
        "mode": mode,
        "row_numbers": row_numbers,
        "initial_implicants": [],
        "stages": [],
        "prime_implicants": [],
        "coverage_table": [],
        "selected_implicants": [],
        "expression": expression_text,
    }


def create_initial_implicants(row_numbers, variable_count):
    implicants = []
    for row_number in row_numbers:
        bits = build_bits_by_number(row_number, variable_count)
        implicants.append({"bits": bits, "numbers": [row_number]})
    return implicants


def build_bits_by_number(row_number, variable_count):
    bits = []
    shift = variable_count - 1
    while shift >= 0:
        bits.append((row_number >> shift) & 1)
        shift -= 1
    return bits


def build_gluing_stages(initial_implicants):
    stages = []
    current_implicants = clone_implicants(initial_implicants)
    while True:
        stage = build_single_stage(current_implicants)
        stages.append(stage)
        if not stage["pairs"]:
            break
        current_implicants = stage["result_implicants"]
    return stages, collect_prime_implicants(stages)


def clone_implicants(implicants):
    result = []
    for implicant in implicants:
        result.append({
            "bits": implicant["bits"][:],
            "numbers": implicant["numbers"][:],
        })
    return result


def build_single_stage(implicants):
    pairs = []
    combined_flags = []
    index = 0
    while index < len(implicants):
        combined_flags.append(False)
        index += 1
    result_implicants = []
    left_index = 0
    while left_index < len(implicants):
        right_index = left_index + 1
        while right_index < len(implicants):
            combined = combine_two_implicants(implicants[left_index], implicants[right_index])
            if combined is not None:
                combined_flags[left_index] = True
                combined_flags[right_index] = True
                pairs.append({
                    "left": implicants[left_index],
                    "right": implicants[right_index],
                    "result": combined,
                })
                add_unique_implicant(result_implicants, combined)
            right_index += 1
        left_index += 1
    uncombined_implicants = []
    index = 0
    while index < len(implicants):
        if not combined_flags[index]:
            uncombined_implicants.append(implicants[index])
        index += 1
    return {
        "pairs": pairs,
        "result_implicants": result_implicants,
        "uncombined_implicants": uncombined_implicants,
    }


def combine_two_implicants(left_implicant, right_implicant):
    difference_count = 0
    result_bits = []
    index = 0
    while index < len(left_implicant["bits"]):
        left_bit = left_implicant["bits"][index]
        right_bit = right_implicant["bits"][index]
        if left_bit == right_bit:
            result_bits.append(left_bit)
        else:
            if left_bit is None or right_bit is None:
                return None
            difference_count += 1
            result_bits.append(None)
        index += 1
    if difference_count != 1:
        return None
    return {
        "bits": result_bits,
        "numbers": sorted(left_implicant["numbers"] + right_implicant["numbers"]),
    }


def add_unique_implicant(result_implicants, new_implicant):
    for implicant in result_implicants:
        if implicant["bits"] == new_implicant["bits"] and implicant["numbers"] == new_implicant["numbers"]:
            return
    result_implicants.append(new_implicant)


def collect_prime_implicants(stages):
    prime_implicants = []
    for stage in stages:
        for implicant in stage["uncombined_implicants"]:
            add_unique_prime_implicant(prime_implicants, implicant)
    return prime_implicants


def add_unique_prime_implicant(prime_implicants, new_implicant):
    for implicant in prime_implicants:
        if implicant["bits"] == new_implicant["bits"]:
            return
    prime_implicants.append(new_implicant)


def build_coverage_table(prime_implicants, row_numbers):
    table = []
    for implicant in prime_implicants:
        marks = []
        for row_number in row_numbers:
            marks.append(implicant_covers_number(implicant, row_number))
        table.append({"implicant": implicant, "marks": marks})
    return table


def implicant_covers_number(implicant, row_number):
    bits = build_bits_by_number(row_number, len(implicant["bits"]))
    index = 0
    while index < len(bits):
        implicant_bit = implicant["bits"][index]
        if implicant_bit is not None and implicant_bit != bits[index]:
            return False
        index += 1
    return True


def select_cover(prime_implicants, row_numbers):
    best_cover = []
    best_key = None
    total_masks = 2 ** len(prime_implicants)
    current_mask = 1
    while current_mask < total_masks:
        current_cover = build_cover_by_mask(prime_implicants, current_mask)
        if cover_all_numbers(current_cover, row_numbers):
            current_key = build_cover_quality_key(current_cover)
            if best_key is None or current_key < best_key:
                best_key = current_key
                best_cover = current_cover
        current_mask += 1
    return best_cover


def build_cover_by_mask(prime_implicants, current_mask):
    cover = []
    index = 0
    while index < len(prime_implicants):
        if (current_mask >> index) & 1:
            cover.append(prime_implicants[index])
        index += 1
    return cover


def cover_all_numbers(cover, row_numbers):
    for row_number in row_numbers:
        if not is_covered_by_any(cover, row_number):
            return False
    return True


def is_covered_by_any(cover, row_number):
    for implicant in cover:
        if implicant_covers_number(implicant, row_number):
            return True
    return False


def build_cover_quality_key(cover):
    implicant_count = len(cover)
    literal_count = 0
    for implicant in cover:
        literal_count += count_literals(implicant["bits"])
    return implicant_count, literal_count


def count_literals(bits):
    count = 0
    for bit in bits:
        if bit is not None:
            count += 1
    return count


def build_expression(implicants, variables, mode):
    if not implicants:
        if mode == "dnf":
            return "0"
        return "1"
    parts = []
    for implicant in implicants:
        parts.append(build_text_by_implicant(implicant, variables, mode))
    if mode == "dnf":
        return join_with_separator(parts, " | ")
    return join_with_separator(parts, " & ")


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


def format_implicant_bits(bits):
    symbols = []
    for bit in bits:
        if bit is None:
            symbols.append(DON_T_CARE_SIGN)
        else:
            symbols.append(str(bit))
    return "".join(symbols)
