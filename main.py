from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle

# Батьківський клас
class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)
    
# Клас де зберігаємо ім'я
class Name(Field):
    pass

# Клас де зберігаємо номер телефону 
class Phone(Field):
    @Field.value.setter
    def value(self, value):
        # Проходмо валідацію. Якщо  номер не цифри або довжина менше 10
        if not str(value).isdigit() or len(str(value)) != 10:
            print("Помилка: Невірний формат телефону!")
            super(Phone, self.__class__).value.fset(self, None)
        else:
            super(Phone, self.__class__).value.fset(self, value)

    def __str__(self):
        return str(self.value)
    
# Клас для створення дати народження    
class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        # Проходмо валідацію. Якщо дата народження у форматі DD.MM.YYYY
        date_pattern = re.compile(r'^\d{2}\.\d{2}.\d{4}$')
        if date_pattern.match(value):
            super(Birthday, self.__class__).value.fset(self, value)
        else:
            print("Помилка: Невірний формат дати народження (DD.MM.YYYY)!")
            super(Birthday, self.__class__).value.fset(self, None)
# Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів. Відповідає за логіку додавання/видалення/редагування
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
    # Додадємо номер
    def add_phone(self, phone):
        phone = Phone(phone)
        if phone.value is not None:  # Додаємо телефон тільки якщо він відповідає критеріям
            self.phones.append(phone)
            return True
        else:
            return False
    # Видаляємо номер
    def del_phone(self, phone):
        self.phones = [i for i in self.phones if i.value != phone]
    # Знаходимо номер
    def find_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                return i
        return None
    # Редагуємо номер
    def change_phone(self, old_phone, new_phone):
        for i in self.phones:
            if i.value == old_phone:
                i.value = new_phone
                return True
        print(f"Помилка: Телефонний номер {old_phone} не знайдено.")
        return False

    def __str__(self):
        birthday_str = f", дата народження: {self.birthday}" if self.birthday else ""
        return f"Ім'я контакта: {self.name.value}, телефон: {'; '.join(i.value for i in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        if record.name.value in self.data:
            existing_record = self.data[record.name.value]
            for phone in record.phones:
                if phone not in existing_record.phones:
                    existing_record.phones.append(phone)
        else:
            self.data[record.name.value] = record
    # Видаляємо номер
    def delete(self, name):
        records_to_delete = [record for record in self.data.values() if record.name.value == name]
        for record in records_to_delete:
            del self.data[record.name.value]
    # Знаходимо номер
    def find(self, query):
        matching_records = []
        
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                matching_records.append(record)
            else:
                for phone in record.phones:
                    if query in str(phone.value):
                        matching_records.append(record)
                        break
        return matching_records
    # Метод для ітерації по записам
    def iterator(self, n):
        records = list(self.data.values())
        while records:
            for record in records[:n]:
                print(record)
            records = records[n:]
    
    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())
# Ввод команд та збереження в файл
def command_handler():
    try:
        with open("data_file.bin", "rb") as f:
            main_address_book = pickle.load(f)
    except FileNotFoundError:
        main_address_book = AddressBook()

    print("Command List")
    print("1. add [name] [phone] [birthday](по бажанню) - додавання номеру телефону до адресної книги;")
    print("2. change [name] [phone] - змінює номер телефону контакту;")
    print("3. find [name] - знаходить телефон за буквою в імені або цифрою в номері телефона;")
    print("4. show all - показує всі контакти в адресній книзі;")
    print("5. del [name] - видаляє всі данні для імені;")
    print("6. exit, close, good bye - вихід CLI-bot")

    while True:
        command = input("Введіть команду: ").lower().strip()
        command_parts = command.split(' ')

        if command_parts[0] == "add":
            if len(command_parts) > 2:
                name = command_parts[1]
                phone = command_parts[2]
                birthday = command_parts[3] if len(command_parts) > 3 else None
                record = Record(name, birthday)
                if record.add_phone(phone):  # Перевіряємо, чи додано телефон
                    main_address_book.add_record(record)
                    print(f"Запис {name} додано.")
            else:
                print("Введить ім'я та номер телефону")
        
        elif command_parts[0] == "del":
            if len(command_parts) == 2:
                name = command_parts[1]
                if name in main_address_book.data:
                    del main_address_book.data[name]
                    print(f"Запис {name} видалено.")        
                else:
                    print(f"Помилка: Запис з ім'ям {name} не знайдено.")
            else:
                print("Введить ім'я")
                
        elif command_parts[0] == "change":
            if len(command_parts) == 4:
                name = command_parts[1]
                old_phone = command_parts[2]
                new_phone = command_parts[3]
                if name in main_address_book.data:
                    record = main_address_book.data[name]
                    if record.change_phone(old_phone, new_phone):
                        print(f"Телефонний номер {old_phone} змінено на {new_phone}.")
                    else:
                        print(f"Помилка: Телефонний номер {old_phone} не знайдено.")
                else:
                    print(f"Помилка: Запис з ім'ям {name} не знайдено.")
            else:
                print("Введіть ім'я, старий та новий номери телефону")

        elif command_parts[0] == "find" and len(command_parts) > 1:
            query = command_parts[1]
            matching_records = main_address_book.find(query)
    
            if matching_records:
                for record in matching_records:
                    print(record)
            else:
                print(f"Записів, які відповідають запиту '{query}', не знайдено.")
        
        
        elif command == "show all":
            if main_address_book.data:
                print(main_address_book)
            else:
                print("Записів нема")
        
        elif command == "exit" or command == "close" or command == "good bye":
            with open("data_file.bin", "wb") as file:
                pickle.dump(main_address_book, file)
            print("Good bye!")
            break
        else:
            print(f"Невідома команда. '{command}'")

if __name__ == "__main__":
    command_handler()