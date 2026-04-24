from utils import print_array

BCD_2421_ENCODE = {
    0: [0, 0, 0, 0], 1: [0, 0, 0, 1], 2: [0, 0, 1, 0], 3: [0, 0, 1, 1], 4: [0, 1, 0, 0],
    5: [1, 0, 1, 1], 6: [1, 1, 0, 0], 7: [1, 1, 0, 1], 8: [1, 1, 1, 0], 9: [1, 1, 1, 1],
}
BCD_2421_DECODE = {tuple(v): k for k, v in BCD_2421_ENCODE.items()}


def decimal_digit_to_2421(d):
    if 0 <= d <= 9:
        return BCD_2421_ENCODE[d].copy()
    raise ValueError(f"Цифра должна быть 0-9, получено {d}")


def decimal_to_2421_bcd(num):
    if num == 0:
        return BCD_2421_ENCODE[0].copy()
    if num < 0:
        num = -num
    result = []
    while num > 0:
        digit = num % 10
        result = decimal_digit_to_2421(digit) + result
        num //= 10
    return result


def _pad_to_4(bits):
    bits = bits.copy()
    while len(bits) % 4 != 0:
        bits = [0] + bits
    return bits


def _2421_to_decimal(bits):
    bits = _pad_to_4(bits)
    res = 0
    for i in range(0, len(bits), 4):
        tetrad = bits[i:i + 4]
        key = tuple(tetrad)
        if key in BCD_2421_DECODE:
            res = res * 10 + BCD_2421_DECODE[key]
        else:
            # Если тетрада невалидна, пробуем интерпретировать как обычный BCD
            val = tetrad[0] * 8 + tetrad[1] * 4 + tetrad[2] * 2 + tetrad[3] * 1
            res = res * 10 + val
    return res


def add_2421_bcd(bcd1, bcd2):
    # Выравниваем длину и делаем кратной 4
    bcd1 = _pad_to_4(bcd1.copy())
    bcd2 = _pad_to_4(bcd2.copy())
    max_len = max(len(bcd1), len(bcd2))

    # Дополняем ведущими нулями
    while len(bcd1) < max_len:
        bcd1 = [0] + bcd1
    while len(bcd2) < max_len:
        bcd2 = [0] + bcd2

    # Двоичное сложение
    result = []
    carry = 0
    for i in range(max_len - 1, -1, -1):
        total = bcd1[i] + bcd2[i] + carry
        result.insert(0, total % 2)
        carry = total // 2
    if carry:
        result.insert(0, 1)

    # Дополняем до кратности 4
    result = _pad_to_4(result)

    # Коррекция для 2421 BCD (по тетрадам справа налево)
    num_tetrads = len(result) // 4
    carry_corr = 0

    for t in range(num_tetrads - 1, -1, -1):
        tetra_start = t * 4
        tetrad = result[tetra_start:tetra_start + 4]

        # Вычисляем значение тетрады
        tetrad_value = tetrad[0] * 8 + tetrad[1] * 4 + tetrad[2] * 2 + tetrad[3] * 1

        # Проверяем нужна ли коррекция
        need_correction = False

        # Если значение > 9 или тетрада не валидна для 2421
        if tetrad_value > 9:
            need_correction = True
        elif tetrad_value >= 5 and tetrad_value <= 9:
            # Для 2421: 5-9 должны начинаться с 1
            if tetrad[0] == 0:
                need_correction = True

        if need_correction:
            # Добавляем 6 (0110) к тетраде
            correction = [0, 1, 1, 0]
            carry_corr = 0
            for j in range(3, -1, -1):
                pos = tetra_start + j
                if pos >= 0:
                    total = result[pos] + correction[j] + carry_corr
                    result[pos] = total % 2
                    carry_corr = total // 2

            # Если есть перенос из коррекции, добавляем к предыдущей тетраде
            if carry_corr and tetra_start >= 4:
                for j in range(tetra_start - 1, -1, -1):
                    if result[j] == 0:
                        result[j] = 1
                        carry_corr = 0
                        break
                    else:
                        result[j] = 0

    # Снова дополняем до кратности 4
    result = _pad_to_4(result)

    # Убираем ведущие нулевые тетрады (но оставляем минимум 4 бита)
    while len(result) > 4:
        if result[:4] == [0, 0, 0, 0]:
            result = result[4:]
        else:
            break

    return result


def task_7_bcd_2421_add(num1, num2):
    print("\n--- ЗАДАНИЕ 7: 2421 BCD ---")
    if num1 < 0 or num2 < 0:
        print("  2421 BCD поддерживает только неотрицательные числа")
        num1, num2 = abs(num1), abs(num2)
    bcd1 = decimal_to_2421_bcd(num1)
    bcd2 = decimal_to_2421_bcd(num2)
    result = add_2421_bcd(bcd1, bcd2)
    print("Результат (бин): ", end="")
    print_array(result)
    print(f"(dec: {_2421_to_decimal(result)})")
    return result
