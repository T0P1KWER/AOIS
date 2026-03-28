import binary
import IEEE
import BCD2421

def print_menu():
    print("\n"+"="*50)
    print("ЛАБОРАТОРНАЯ РАБОТА 1 - МЕНЮ")
    print("="*50)
    print("1. Перевод числа из 10 в 2 (прямой/обратный/доп. код)")
    print("2. Сложение в дополнительном коде")
    print("3. Вычитание через сложение")
    print("4. Умножение в прямом коде")
    print("5. Деление в прямом коде (5 знаков)")
    print("6. IEEE-754 (плавающая точка)")
    print("   6.1 - Сложение")
    print("   6.2 - Вычитание")
    print("   6.3 - Умножение")
    print("   6.4 - Деление")
    print("7. 2421 BCD код")
    print("0. Выход")
    print("="*50)

def main():
    while True:
        print_menu()
        choice=input("Выберите задание: ")
        try:
            if choice=='1':
                num=int(input("Введите число: "))
                binary.task_1(num)
            elif choice=='2':
                num1=int(input("Введите первое число: "))
                num2=int(input("Введите второе число: "))
                binary.task_2_addition(num1,num2)
            elif choice=='3':
                num1=int(input("Введите уменьшаемое: "))
                num2=int(input("Введите вычитаемое: "))
                binary.task_3_subtraction(num1,num2)
            elif choice=='4':
                num1=int(input("Введите первое число: "))
                num2=int(input("Введите второе число: "))
                binary.task_4_multiplication(num1,num2)
            elif choice=='5':
                num1=int(input("Введите делимое: "))
                num2=int(input("Введите делитель: "))
                binary.task_5_division(num1,num2)
            elif choice=='6':
                sub=input("Выберите операцию (1-4): ")
                n1=float(input("Введите первое число: "))
                n2=float(input("Введите второе число: "))
                if sub=='1': IEEE.task_6_ieee754_add(n1,n2)
                elif sub=='2': IEEE.task_6_ieee754_sub(n1,n2)
                elif sub=='3': IEEE.task_6_ieee754_mul(n1,n2)
                elif sub=='4': IEEE.task_6_ieee754_div(n1,n2)
                else: print("Неверный выбор!")
            elif choice=='7':
                num1=int(input("Введите первое число: "))
                num2=int(input("Введите второе число: "))
                BCD2421.task_7_bcd_2421_add(num1,num2)
            elif choice=='0':
                print("Выход")
                break
            else: print("Неверный выбор!")
        except ValueError:
            print("Ошибка: введите корректное число!")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__=="__main__":
    main()
#активировать окружение source venv/bin/activate
#запуск тестов pytest tests/test_all.py --cov=. --cov-report=html && open htmlcov/index.html