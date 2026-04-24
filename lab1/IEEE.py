from utils import ARRAY_SIZE, EXP_BITS, MANTISSA_BITS, EXP_BIAS, print_array

def get_sign_bit(num):
    return 1 if num < 0 else 0

def int_to_binary(n, bits):
    b = [0]*bits
    for i in range(bits-1,-1,-1):
        b[i] = n%2
        n//=2
    return b

def frac_to_binary(frac, max_bits=23):
    bits=[]
    for _ in range(max_bits):
        frac*=2
        bits.append(1 if frac>=1 else 0)
        if frac>=1: frac-=1
    return bits

def decimal_to_ieee754(num):
    bits=[0]*ARRAY_SIZE
    bits[0]=get_sign_bit(num)
    abs_num=-num if num<0 else num
    if abs_num==0: return bits
    int_part=int(abs_num); frac_part=abs_num-int_part
    int_bin=int_to_binary(int_part,32); frac_bin=frac_to_binary(frac_part,32)
    full=int_bin+frac_bin
    first_one=next((i for i,b in enumerate(full) if b==1),None)
    if first_one is None: exponent=0; mantissa=[0]*MANTISSA_BITS
    else:
        exponent=31-first_one if int_part else -(first_one-31)
        mantissa=full[first_one+1:first_one+1+MANTISSA_BITS]
        mantissa+=[0]*(MANTISSA_BITS-len(mantissa))
    exp_bits=int_to_binary(exponent+EXP_BIAS,EXP_BITS)
    bits[1:1+EXP_BITS]=exp_bits
    bits[1+EXP_BITS:]=mantissa
    return bits

def ieee754_to_decimal(bits):
    sign=-1 if bits[0]==1 else 1
    exp=sum(bits[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))-EXP_BIAS
    mantissa=1+sum(bits[1+EXP_BITS+i]*2**-(i+1) for i in range(MANTISSA_BITS))
    return sign*mantissa*(2**exp)

def align_mantissas(m1,m2,e1,e2):
    if e1>e2: shift=e1-e2; m2=[0]*shift+m2[:-shift]; e=e1
    else: shift=e2-e1; m1=[0]*shift+m1[:-shift]; e=e2
    return m1,m2,e

def add_mantissas(m1,m2):
    result=[0]*len(m1); carry=0
    for i in range(len(m1)-1,-1,-1):
        total=m1[i]+m2[i]+carry
        result[i]=total%2; carry=total//2
    return result,carry

def task_6_ieee754_add(num1,num2):
    print("\n--- ЗАДАНИЕ 6: Сложение ---")
    b1,b2=decimal_to_ieee754(num1),decimal_to_ieee754(num2)
    s1,s2=b1[0],b2[0]
    e1=sum(b1[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))
    e2=sum(b2[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))
    m1=[1]+b1[1+EXP_BITS:]; m2=[1]+b2[1+EXP_BITS:]
    m1,m2,e=align_mantissas(m1,m2,e1,e2)
    if s1==s2: mant,_=add_mantissas(m1,m2); sign=s1
    else:
        val1=sum(bit*2**(23-i) for i,bit in enumerate(m1))
        val2=sum(bit*2**(23-i) for i,bit in enumerate(m2))
        if val1>=val2: mant=[a-b for a,b in zip(m1,m2)]; sign=s1
        else: mant=[a-b for a,b in zip(m2,m1)]; sign=s2
    mant=mant[:MANTISSA_BITS]
    result_bits=[sign]+int_to_binary(e,EXP_BITS)+mant
    print("Результат (бин): ", end=""); print_array(result_bits)
    print(f"Результат (дек): {ieee754_to_decimal(result_bits)}")
    return result_bits

def task_6_ieee754_sub(num1,num2): return task_6_ieee754_add(num1,-num2)

def task_6_ieee754_mul(num1,num2):
    print("\n--- ЗАДАНИЕ 6: Умножение ---")
    b1,b2=decimal_to_ieee754(num1),decimal_to_ieee754(num2)
    sign=b1[0]^b2[0]
    e1=sum(b1[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))-EXP_BIAS
    e2=sum(b2[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))-EXP_BIAS
    mant1=1+sum(b1[1+EXP_BITS+i]*2**-(i+1) for i in range(MANTISSA_BITS))
    mant2=1+sum(b2[1+EXP_BITS+i]*2**-(i+1) for i in range(MANTISSA_BITS))
    result=mant1*mant2; exp_res=e1+e2+EXP_BIAS
    frac=result-1; mant_bits=[int(frac*2**i)%2 for i in range(1,MANTISSA_BITS+1)]
    result_bits=[sign]+int_to_binary(exp_res,EXP_BITS)+mant_bits
    print("Результат (бин): ", end=""); print_array(result_bits)
    print(f"Результат (дек): {ieee754_to_decimal(result_bits)}")
    return result_bits

def task_6_ieee754_div(num1,num2):
    print("\n--- ЗАДАНИЕ 6: Деление ---")
    if num2==0: print("Ошибка: деление на 0"); return [0]*ARRAY_SIZE
    b1,b2=decimal_to_ieee754(num1),decimal_to_ieee754(num2)
    sign=b1[0]^b2[0]
    e1=sum(b1[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))-EXP_BIAS
    e2=sum(b2[1+i]*2**(EXP_BITS-1-i) for i in range(EXP_BITS))-EXP_BIAS
    mant1=1+sum(b1[1+EXP_BITS+i]*2**-(i+1) for i in range(MANTISSA_BITS))
    mant2=1+sum(b2[1+EXP_BITS+i]*2**-(i+1) for i in range(MANTISSA_BITS))
    result=mant1/mant2; exp_res=e1-e2+EXP_BIAS
    frac=result-1; mant_bits=[int(frac*2**i)%2 for i in range(1,MANTISSA_BITS+1)]
    result_bits=[sign]+int_to_binary(exp_res,EXP_BITS)+mant_bits
    print("Результат (бин): ", end=""); print_array(result_bits)
    print(f"Результат (дек): {ieee754_to_decimal(result_bits)}")
    return result_bits
