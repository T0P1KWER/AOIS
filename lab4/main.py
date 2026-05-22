from hash_table import HashTable


def print_table(table: HashTable) -> None:

    print("Индекс | Ключ             | Данные                         | U | D | C")
    for row in table.table_view():
        index, key, value, occupied, deleted, collision = row
        key = key or ""
        value = value or ""

        print(
            f"{index:>6} | "
            f"{key:<16} | "
            f"{str(value):<30} | "
            f"{occupied} | {deleted} | {collision}"
        )


def add_elements_from_keyboard(table: HashTable) -> None:
    print("Хеш-таблица создана.")
    print("Вводите ключ и данные для добавления новой записи.")
    print("Чтобы завершить программу, введите exit вместо ключа.\n")

    while True:
        key = input("Введите ключ: ").strip()

        if key.lower() == "exit":
            print("Работа программы завершена.")
            break

        value = input("Введите данные: ").strip()

        try:
            index = table.create(key, value)
            print(f"\nЭлемент добавлен в ячейку с индексом {index}.")
            print("Текущая хеш-таблица:")
            print_table(table)
            print()
        except (ValueError, TypeError, KeyError, OverflowError) as error:
            print(f"Ошибка: {error}\n")


if __name__ == "__main__":
    hash_table = HashTable(size=20)
    add_elements_from_keyboard(hash_table)
