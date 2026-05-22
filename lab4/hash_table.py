
RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LATIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class HashCell:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.u_flag = 0
        self.d_flag = 0
        self.c_flag = 0
        if key is not None:
            self.u_flag = 1

    def is_free(self):
        return self.u_flag == 0

    def is_active(self):
        return self.u_flag == 1 and self.d_flag == 0

    def clear_as_deleted(self):
        self.key = None
        self.value = None
        self.u_flag = 0
        self.d_flag = 1
        self.c_flag = 0


class HashTable:

    def __init__(self, size=20):
        if size <= 0:
            raise ValueError("Размер таблицы должен быть положительным")

        self.size = size
        self.cells = []
        for _ in range(size):
            self.cells.append(HashCell())
        self.count = 0

    def __len__(self):
        return self.count

    def __contains__(self, key):
        return self.search(key) is not None

    def _normalize_key(self, key):
        if not isinstance(key, str):
            raise TypeError("Ключ должен быть строкой")
        normalized_key = key.strip()
        if normalized_key == "":
            raise ValueError("Ключ не должен быть пустым")
        return normalized_key

    def _letter_number(self, char):
        char = char.upper()
        if char in RUSSIAN_ALPHABET:
            return RUSSIAN_ALPHABET.index(char)
        if char in LATIN_ALPHABET:
            return LATIN_ALPHABET.index(char)
        return ord(char)

    def key_value(self, key):
        key = self._normalize_key(key)
        first_number = self._letter_number(key[0])
        if len(key) > 1:
            second_number = self._letter_number(key[1])
        else:
            second_number = 0

        return first_number * len(RUSSIAN_ALPHABET) + second_number

    def hash(self, key):
        return self.key_value(key) % self.size

    def _next_index(self, start_index, step):
        return (start_index + step) % self.size

    def _find_index(self, key):

        key = self._normalize_key(key)
        start_index = self.hash(key)
        for step in range(self.size):
            index = self._next_index(start_index, step)
            cell = self.cells[index]
            if cell.u_flag == 0 and cell.d_flag == 0:
                return None
            if cell.is_active() and cell.key == key:
                return index

        return None

    def create(self, key, value):
        key = self._normalize_key(key)
        if self.count == self.size:
            raise OverflowError("Хеш-таблица заполнена")
        if self._find_index(key) is not None:
            raise KeyError("Такой ключ уже есть в таблице")
        start_index = self.hash(key)
        for step in range(self.size):
            index = self._next_index(start_index, step)
            cell = self.cells[index]

            if cell.is_free():
                cell.key = key
                cell.value = value
                cell.u_flag = 1
                cell.d_flag = 0
                if step > 0:
                    cell.c_flag = 1
                else:
                    cell.c_flag = 0

                self.count += 1
                return index

        raise OverflowError("Не удалось найти свободную ячейку")

    def search(self, key):
        index = self._find_index(key)
        if index is None:
            return None
        return self.cells[index].value

    def update(self, key, new_value):
        index = self._find_index(key)
        if index is None:
            raise KeyError("Ключ не найден")

        self.cells[index].value = new_value

    def delete(self, key):
        index = self._find_index(key)

        if index is None:
            raise KeyError("Ключ не найден")

        self.cells[index].clear_as_deleted()
        self.count -= 1

    def items(self):
        result = []
        for cell in self.cells:
            if cell.is_active():
                result.append((cell.key, cell.value))

        return result

    def table_view(self):
        rows = []
        for index in range(self.size):
            cell = self.cells[index]
            rows.append((index, cell.key, cell.value, cell.u_flag, cell.d_flag, cell.c_flag))

        return rows
