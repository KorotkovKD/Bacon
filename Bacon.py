import os

def xor_digits(digits: list[bool], dig1:int, dig2: int) -> bool:
    ''' Вычисляет бит переноса.'''
    if digits[dig1] == digits[dig2]:
        return False
    return True


def shift_number(number: list[bool], c: bool) -> list[bool]:
    '''Получает новое число из старого путём сдвига с переносом.'''
    new_number = list(number)
    for i in range(3, -1, -1):
        new_number[i+1] = new_number[i]
    new_number[0] = c
    return new_number


def create_dict(ALPHABET: tuple[str], table: list[list[bool]], mode: str) -> dict:
    '''Создает таблицу переводами между и символами и числами.'''
    dct = {}
    if mode == 'enc':
        for i in range(31):
            dct[ALPHABET[i]] = table[i]
        return dct
    for i in range(31):
        a = transform_l_to_n(table[i])
        # Преобразование двоичного числа в десятичное для индексации.
        dct[a] = ALPHABET[i]
    return dct


def get_key() -> list:
    '''Считывает ключ из файла'''
    file_key_name = input('Введите имя файла с ключём (он будет удалён после обработки):\n')
    File_key = check_file(file_key_name, 'r+')
    if not File_key:
        return[]
    key: str = ''
    key = File_key.read()
    if len(key) < 9:
        print('Неверная длина ключа.\n')
        key = ''
    File_key.seek(0)
    File_key.write(" " * len(key))
    File_key.close()
    os.remove(file_key_name)
    key_list =[]
    if key:
        key_list: list = process_key(key)
        key = ' ' * 9
    return key_list


def process_key(key_str: str) -> list:
    '''Преобразует ключ из строки в нужные типы данных,
       проверяя его корректность.
       Символы 1-5: Начальное число таблицы в двоичном виде;
       Символы 6-7: Номера разрядов двоичных чисел слева,
                    участвующих в операции XOR;
       Символ 8: Смещение таблицы чисел по горизонтали;
       Символ 9: Смещение текста сообщения по горизонтали.'''
    NUMBERS = ('1', '2', '3', '4')
    key_list = []
    start_number = []
    for i in range(5):
        if key_str[i] == '1':
            start_number.append(True)
        elif key_str[i] == '0':
            start_number.append(False)
        else:
            print('Неверное стартовое число.\n')
            start_number = [False, False, False, False, False]
            key_str = ' ' * 9 
            return key_list
    if True not in start_number:
        print('Небезопасное стартовое число (00000).\n')
        key_str = ' ' * 9 
        return key_list
    key_list.append(start_number)
    start_number = [False, False, False, False, False]
    for i in range(5, 7):
        if key_str[i] in NUMBERS:
            key_list.append(int(key_str[i]))
        else:
            print('Неверные XOR-разряды числа.\n')
            key_str = ' ' * 9
            key_list = []
            return key_list
    if not ((4 in key_list) and ((2 in key_list) or (1 in key_list))):
            print('Небезопасные XOR-разряды числа (введите (4, 1) или (4, 2)).\n')
            key_str = ' ' * 9
            key_list = []
            return key_list
    for i in range(7, 9):
        if key_str[i] in NUMBERS:
            key_list.append(int(key_str[i]))
        else:
            print('Неверное смещение текста или шифра.\n')
            key_str = ' ' * 9
            key_list = []
            return key_list
    key_str = ' ' * 9
    return key_list


def create_table(key_list: list) -> list:
    '''Создаёт таблицу чисел.'''
    table = []
    tmp:list = key_list[0]
    xor_dig1: int = key_list[1]
    xor_dig2: int = key_list[2]
    table_shift: int = key_list[3]
    key_list = [ ' ', ' ', ' ', ' ']
    for _ in range(31):
        enc_code = list(tmp)
        enc_code = shift_table(enc_code, table_shift)
        table.append(enc_code)
        tmp = generate_new_number(tmp, xor_dig1, xor_dig2)
    enc_code = [ ' ', ' ', ' ', ' ', ' ']
    tmp = [ ' ', ' ', ' ', ' ', ' ']
    return table


def generate_new_number(number: list,
                 xor_dig1: int,
                 xor_dig2: int,
                 ) -> list:
    ''' Получает следующее число таблицы чисел из текущего.'''
    c: bool = xor_digits(number, xor_dig1, xor_dig2)
    new_number = shift_number(number, c)
    return new_number


def shift_table(number:list[bool], shift: int) -> list[bool]:
    '''Смещает таблицу чисел по горизонтали.'''
    tmp: list[bool] = list(number)
    for i in range(5):
        j = i + shift
        if j > 4:
            j -= 5
        number[j] = tmp[i]
    tmp = [False, False, False, False, False]
    return number


def choose_mode() -> str:
    '''Выбор между режимами зашифровки и расшифровки.'''
    mode: str = ''
    while True:
        mode = input('Введите "enc" для зашифровки, '
                    '"dec" для зашифровки, '
                    '"exit" для прекращения операции:\n')
        if (mode == 'enc') or (mode == 'dec'):
            break
        if (mode == 'exit'):
            mode = ''
            break
        print('Неверный ввод.')
        mode = ''
    return mode


def encrypt_message(message: str, dct: dict) -> list:
    '''Зашифровывает сообщение'''
    message = message.lower()
    encrypted_message = []
    for i in message:
        if i in dct:
            for j in dct[i]:
                encrypted_message.append(j)
    message = ''
    return encrypted_message


def integrate_message(encoded_message: list[bool],
                      text: str,
                      text_shift: int,
                      table: list[list[bool]] 
                      ) -> str:
    '''Вставляет зашифрованное сообщение в текст.'''
    generated_number = []
    # Преобразование текста в строчный для облегчения проверок.
    text = text.lower()
    tmp = list(text)
    text = ''
    j = 0
    shift = 0
    text_len = len(tmp)
    for i in range(5):
        # Вычисление числа для генерации псевдо случайного числа.
        generated_number.append(encoded_message[len(encoded_message)//2 + i])
    # Генерирует псевдо случайные биты для заполнения области смещения.
    generated_number = generate_number(generated_number, table)
    temp_number = list(generated_number)
    while shift < text_shift:
    # Смещение в тексте с заполнением мусором.
        while not tmp[j].islower():
            j += 1
            if j == text_len:
                return ''
        shift += 1
        if  temp_number.pop():
            tmp[j] = tmp[j].upper()
        j += 1
        if j == text_len:
            return '' 
    for i in encoded_message:
    # Вставка в текст зашифрованного сообщения
        while not tmp[j].islower():
            j += 1
            if j == text_len:
                return ''
        if i:
            tmp[j] = tmp[j].upper()
        j += 1
        if j == text_len:
            return ''
    generated_number = []
    for i in range(5):
    # Вычисление числа для генерации псевдо случайного числа.
        generated_number.append(encoded_message[-1 - 1])
    temp_number = list(generated_number)
    while j != text_len:
    # Заполнение остатка текста мусором.
        if not temp_number:
            generated_number = generate_number(generated_number, table)
            temp_number = list(generated_number)
        if temp_number.pop():
            tmp[j] = tmp[j].upper()
        j += 1
    for i in tmp:
    # Собирание модифицированного текста в одну строку.
        text += i
    return text


def decrypt_message(text: str, dct: dict, text_shift: int) -> str:
    '''Расшифровывает сообщение.'''
    decrypted_message: str = ''
    character = []
    shift = 0
    char:str = ''
    tmp = list(text)
    text = ''
    while shift < text_shift:
        # Цикл сдвига в тексте.
        if tmp:
            char = tmp.pop(0)
            if char.islower() or char.isupper():
                shift += 1
        else:
            return '' 
    for i in tmp:
        if len(character) == 5:
            # Преобразует набор считаных значений в десятичное число.
            code = transform_l_to_n(character)
            character = []
            if code != 0:
            # Сопоставление десятичного числа символу в словаре и 
            # добавление его к тексту сообщения.
                decrypted_message += dct[code]
        # Преобразование текста в биты шифра
        if i.islower():
            character.append(False)
        if i.isupper():
            character.append(True)
    return decrypted_message


def transform_l_to_n(number_l: list) -> int:
    '''Преобразует число из list[bool] в int.'''
    number:int = 0
    digit_mult:int = 16
    for i in number_l:
        if i:
            number += digit_mult
        digit_mult //= 2
    return number


def generate_number(number: list[bool],
                    table: list[list: bool]
                    ) -> list[bool]:
    '''
    Генерирут псевдослучайное число на основе предыдущего
    и таблицы чисел.
    '''
    indx: int
    for i in range(31):
        if table[i] == number:
            indx = i
            break
    offset: int = transform_l_to_n(number)
    if offset == 31:
        offset -= 1
    i = indx + offset
    if i >= 31:
        i -= 31
    new_number = table[i]
    return new_number


def encrypt(dct: dict, text_shift: int, table: list) -> None:
    '''Управляет зашифровкой сообщений.'''
    message = get_message()
    if not message:
        print('Сообщение не было прочитано с файла')
        return
    encrypted_message = encrypt_message(message, dct)
    message = ' ' * len(message)
    text_file = get_text('enc')
    if not text_file:
        return
    integrated_message = integrate_message(encrypted_message, text_file[1], text_shift, table)
    encrypted_message = ' ' * len(encrypted_message)
    if not integrated_message:
        print('Ошибка шифрования. Предоставленный текст слишком мал.\n')
        return
    write_file(integrated_message, text_file[0])
    return


def check_file(file_name: str, mode: str):
    '''Обрабатывает открытие файлов.'''
    File = None
    try:
        File = open(file_name, mode)
    except IOError:
        print('Не получилось открыть файл:', file_name)
        if File:
            File.close()
        File = None
    finally:
        return File


def get_message() -> str:
    '''Загружает сообщение для зашифровки.'''
    file_message_name = input('Введте имя файла с пересылаемым сообщением '
                              '(Он будет удалён после прочтения):\n') 
    File_message = check_file(file_message_name, 'r+')
    if not File_message:
        return ''
    message: str = ''
    message = File_message.read()
    File_message.seek(0)
    File_message.write(" " * len(message))
    File_message.close()
    os.remove(file_message_name)
    return message


def get_text(mode: str) -> list[str]:
    '''Загружает открытый текст.'''
    file_text_name = input('Введте имя файла с текстом, используемым для'
                           'пересылки сообщения (удаляется при декодировании):\n')
    File_text = check_file(file_text_name, 'r+')
    if not File_text:
        return []
    text_file = []
    text_file.append(file_text_name)
    text: str = ''
    text = File_text.read()
    if mode == 'dec':
        File_text.seek(0)
        File_text.write('' * len(text))
        File_text.close()
        os.remove(file_text_name)
    File_text.close()
    text_file.append(text)
    return text_file


def write_file(text: str, file_output_name = '') -> None:
    '''Записывает полученный результат в файл.'''
    if not file_output_name:
        file_output_name = input('Введите имя файла для записи сообщения:\n')
    File_output = check_file(file_output_name, 'w')
    if not File_output:
        return
    File_output.write(text)
    File_output.close()
    text = ' ' * len(text)
    return


def decrypt(dct: dict, text_shift: int) -> None:
    '''Обрабатывает дешифровку и передачу сообщения.'''
    text_file = get_text('dec')
    if not text_file:
        return
    decrypted_message = decrypt_message(text_file[1], dct, text_shift)
    if not decrypted_message:
        print('В тексте не содержалось зашифрованной информации.')
    write_file(decrypted_message)
    decrypted_message = ' ' * len(decrypted_message)
    return


def main() -> None:
    mode: str = choose_mode()
    if not mode:
        return
    key_list: list = get_key()
    if not key_list:
        return
    ALPHABET = ('а', 'б', 'в', 'г', 'д', 'е', 'ж',
                'з', 'и', 'й', 'к', 'л', 'м', 'н',
                'о', 'п', 'р', 'с', 'т', 'у', 'ф',
                'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы',
                'э', 'ю', 'я')
    text_shift: int = key_list.pop()
    table = create_table(key_list)
    key_list = [' ', ' ',' ',' ']
    dct = create_dict(ALPHABET, table, mode)
    if mode == 'enc':
        encrypt(dct, text_shift, table)
    else:
        decrypt(dct, text_shift)
    text_shift = 0
    table.clear()
    dct.clear()
    return


main()