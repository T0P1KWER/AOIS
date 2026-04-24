from utils import ARRAY_SIZE, MAX_MAGNITUDE, FRACTION_PRECISION, print_array, create_array_from_decimal, invert_array, add_one_to_array, add_arrays, complement_to_decimal

def direct_code(number):
    return create_array_from_decimal(number)

def reverse_code(number):
    arr = create_array_from_decimal(number)
    if number < 0: arr = invert_array(arr)
    return arr

def complement_code(number):
    arr = create_array_from_decimal(number)
    if number < 0:
        arr = invert_array(arr)
        arr = add_one_to_array(arr)
    return arr

def task_1(number):
    print("\n--- ЗАДАНИЕ 1 ---")
    codes = [("Прямой код", direct_code(number)), ("Обратный код", reverse_code(number)), ("Доп. код", complement_code(number))]
    for name, arr in codes:
        print(f"{name}: ", end=""); print_array(arr)
        val = complement_to_decimal(arr) if name=="Доп. код" else sum(bit*2**(ARRAY_SIZE-1-i) for i, bit in enumerate(arr[1:],1)) * (-1 if arr[0] else 1)
        print(f"(dec: {val})")
    return complement_code(number)

def task_2_addition(num1, num2):
    print("\n--- ЗАДАНИЕ 2 ---")
    result = add_arrays(complement_code(num1), complement_code(num2))
    print("Результат (бин): ", end=""); print_array(result)
    print(f"(dec: {complement_to_decimal(result)})")
    return result

def task_3_subtraction(num1, num2):
    print("\n--- ЗАДАНИЕ 3 ---")
    result = add_arrays(complement_code(num1), complement_code(-num2))
    print("Результат (бин): ", end=""); print_array(result)
    print(f"(dec: {complement_to_decimal(result)})")
    return result

def task_4_multiplication(num1, num2):
    print("\n--- ЗАДАНИЕ 4 ---")
    if abs(num1) > MAX_MAGNITUDE or abs(num2) > MAX_MAGNITUDE: raise OverflowError("Magnitude exceeds limit")
    sign = 1 if (num1<0) ^ (num2<0) else 0
    mag1 = [int(x) for x in f"{abs(num1):031b}"]
    mag2 = [int(x) for x in f"{abs(num2):031b}"]
    product = [0]*62
    for i in range(31):
        if mag2[30-i]==1:
            for j in range(31):
                if mag1[30-j]==1: product[61-(i+j)] +=1
    carry = 0
    for i in range(61,-1,-1):
        product[i], carry = (product[i]+carry)%2, (product[i]+carry)//2
    final_arr = [0]*ARRAY_SIZE
    final_arr[0] = sign
    final_arr[1:] = product[-31:]
    print("Результат (бин): ", end=""); print_array(final_arr)
    dec_val = -int("".join(map(str,final_arr[1:])),2) if sign else int("".join(map(str,final_arr[1:])),2)
    print(f"(dec: {dec_val})")
    return final_arr

def task_5_division(num1, num2):
    print("\n--- ЗАДАНИЕ 5 ---")
    if num2==0: print("Ошибка: деление на 0"); return [0]*32
    sign = 1 if (num1<0) ^ (num2<0) else 0
    quotient = abs(num1)//abs(num2)
    remainder = abs(num1)%abs(num2)
    frac = int(remainder/abs(num2)*(2**FRACTION_PRECISION))
    total = (quotient<<FRACTION_PRECISION)|frac
    bin_arr = [int(x) for x in f"{total:037b}"]  # 32+5 бита
    bin_arr[0]=sign
    print("Результат (бин): ", end=""); print_array(bin_arr,int_bits=32,frac_bits=FRACTION_PRECISION)
    dec_val = (-1 if sign else 1)*(quotient + frac/(2**FRACTION_PRECISION))
    print(f"Результат (дек): {dec_val:.5f}")
    return bin_arr
