ARRAY_SIZE = 32
EXP_BITS = 8
MANTISSA_BITS = 23
EXP_BIAS = 127
FRACTION_PRECISION = 5
MAX_MAGNITUDE = (1 << 31) - 1

def print_array(arr, int_bits=None, frac_bits=None):
    """Вывод бинарного массива с ведущими нулями и запятой для дробной части"""
    int_bits = int_bits or len(arr)
    frac_bits = frac_bits or 0
    int_part = arr[:int_bits]
    frac_part = arr[int_bits:int_bits+frac_bits] if frac_bits > 0 else []
    print("".join(map(str,int_part)), end="")
    if frac_part:
        print(",", end="")
        print("".join(map(str,frac_part)), end="")
    print()

def create_array_from_decimal(number):
    arr = [0]*ARRAY_SIZE
    if number < 0:
        arr[0] = 1
        number = -number
    index = ARRAY_SIZE-1
    while number > 0 and index > 0:
        arr[index] = number % 2
        number //= 2
        index -= 1
    return arr

def invert_array(arr):
    new_arr = arr.copy()
    for i in range(1, ARRAY_SIZE):
        new_arr[i] = 1 - new_arr[i]
    return new_arr

def add_one_to_array(arr):
    result = arr.copy()
    carry = 1
    for i in range(ARRAY_SIZE-1,0,-1):
        total = result[i] + carry
        result[i] = total % 2
        carry = total // 2
        if carry == 0: break
    return result

def add_arrays(arr1, arr2):
    result = [0]*ARRAY_SIZE
    carry = 0
    for i in range(ARRAY_SIZE-1,-1,-1):
        total = arr1[i]+arr2[i]+carry
        result[i] = total%2
        carry = total//2
    return result

def complement_to_decimal(arr):
    arr_temp = arr.copy()
    sign = arr_temp[0]
    if sign == 1:
        for i in range(1, ARRAY_SIZE):
            arr_temp[i] = 1 - arr_temp[i]
        carry = 1
        for i in range(ARRAY_SIZE-1,0,-1):
            total = arr_temp[i]+carry
            arr_temp[i] = total%2
            carry = total//2
    result = 0
    for i in range(1, ARRAY_SIZE):
        if arr_temp[i]==1:
            result += 2**(ARRAY_SIZE-1-i)
    return -result if sign==1 else result