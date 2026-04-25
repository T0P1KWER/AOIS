
from logic import (
    analyze_post_classes,
    build_derivatives,
    build_index_form,
    build_karnaugh_maps,
    build_sdnf,
    build_sknf,
    build_truth_table,
    build_zhegalkin_polynomial,
    find_dummy_variables,
)
from minimization import minimize_function
from parser import parse_expression
from report import build_report


def main():
    expression_text = input("Выражение: ").strip()

    try:
        parsed_expression = parse_expression(expression_text)
        rows = build_truth_table(parsed_expression)
    except ValueError as error:
        print()
        print("Ошибка:", error)
        return

    forms = {
        "sdnf": build_sdnf(rows, parsed_expression["variables"]),
        "sknf": build_sknf(rows, parsed_expression["variables"]),
        "index": build_index_form(rows),
    }
    polynomial_data = build_zhegalkin_polynomial(rows, parsed_expression["variables"])
    post_data = analyze_post_classes(rows, parsed_expression["variables"], polynomial_data)
    dummy_variables = find_dummy_variables(rows, parsed_expression["variables"])
    derivatives = build_derivatives(rows, parsed_expression["variables"])
    minimization_data = minimize_function(rows, parsed_expression["variables"])
    karnaugh_data = build_karnaugh_maps(rows, parsed_expression["variables"], minimization_data)

    report_text = build_report(
        expression_text,
        parsed_expression,
        rows,
        forms,
        polynomial_data,
        post_data,
        dummy_variables,
        derivatives,
        minimization_data,
        karnaugh_data,
    )
    print()
    print(report_text)


if __name__ == "__main__":
    main()
