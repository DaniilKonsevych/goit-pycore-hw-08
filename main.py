from collections import UserDict
from datetime import datetime

import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "+rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
	pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Phone number can only consist of 10 digits.")
        
class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            raise ValueError
        except KeyError:
            raise KeyError
        except IndexError:
            raise IndexError
    return wrapper

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def find_phone(self, phone_number):
        if phone_number in self.phones:
            return self

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, phone_number_old, phone_number_new):
        for p in self.phones:
            if p == phone_number_old:
                phone_number_old = Phone(phone_number_new)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    @input_error
    def add_record(self, record : Record):
        self.data[record.name.value] = record

    @input_error
    def find(self, record : Record):
        return self.data.get(record)

    @input_error
    def delete(self, record : Record):
        self.pop(record)

    @input_error
    def birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for key in self.data.keys():

            record = self.find(key)
            record : Record
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)
                birthday = datetime.strftime(birthday_this_year, '%d.%m.%Y')

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                    birthday = datetime.strftime(birthday_this_year, '%d.%m.%Y')

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({"Name": key, "birthday date (this year)": birthday})

        return f"Birthdays in next 7 days: {upcoming_birthdays}"

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message



@input_error
def change_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is not None:
        record = Record(name)
        book.add_record(record)
        message = "Contact updated."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return record

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Birthday added."
    if record is not None:
        if birthday:
            record.add_birthday(birthday)
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return record.birthday

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone(args, book))

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(book.birthdays())

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()