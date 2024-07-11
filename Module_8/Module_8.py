from collections import UserDict
from datetime import datetime,date,timedelta
import pickle


def input_error(function):
    def inner(*args, **kwargs):
        try:return function(*args, **kwargs)
        except ValueError:return 'Enter a valid argument for the command.'
        except IndexError:return 'Enter the argument for the command.'
        except KeyError:return 'There is no such contact.'
        except ValidationFailed: return "The phone number must be 10 digits"
        except DataFormatError: return "Invalid date format. Use DD.MM.YYYY"
        finally: pass
    return inner

@input_error
def parse_input(user_input:str)->tuple:
    cmd,*args=user_input.split()
    cmd=cmd.strip().casefold()
    return cmd,*args

class ValidationFailed(Exception):pass
class DataFormatError(Exception):pass
    

def phone_validation(phone:str):
        if phone.isdigit() and len(phone)==10:return phone
        else: raise ValidationFailed

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):pass

class Phone(Field):
    def __init__(self, value:str):
        if phone_validation(value):self.value=value



class Birthday(Field):
    def __init__(self, value):
        try:self.value=datetime.strptime(value,'%d.%m.%Y').date()
        except ValueError:raise DataFormatError

class Record:
    def __init__(self, name:str):
        name.capitalize()
        self.name = Name(name)
        self.phones = [] #Елементи всередині списку будуть об'єктами Phone
        self.birthday=None

    def add_phone(self, phone:str):
        if phone not in [p.value for p in self.phones]:
            self.phones.append(Phone(phone))
        else:print(f'{phone} already exists')

    def remove_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones = [p for p in self.phones if p.value != phone_obj.value]

    def edit_phone(self, old_phone: str, new_phone: str):
        try:
            index =next(i for i, p in enumerate(self.phones) if p.value == old_phone)
        except StopIteration:
            print(f'{old_phone} does not exist')
            index=None
        if index!=None:self.phones[index] = Phone(new_phone)

    def add_birthday(self,date_birth):self.birthday=Birthday(date_birth)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):return self.data.get(name)

    def get_upcoming_birthdays(self)->list:
        result=[]
        today=date.today()
        for name,birth_date in self.data.items():
            b_date=birth_date.birthday.value.replace(year=today.year)
            if b_date<today:b_date+=timedelta(days=365)
            weekday=b_date.weekday()
            if weekday==5:b_date+=timedelta(days=2)
            if weekday==6:b_date+=timedelta(days=1)
            days_to_birthday=(b_date-today).days
            if days_to_birthday in [*range(8)]:result.append({'name':name,'birthday':b_date})
        return result

    def delete(self, name):
        try: del self.data[name]
        except KeyError: print(f'{name} does not exist')

    def __str__(self) -> str:
        return '\n'.join(str(record) for record in self.data.values())

@input_error
def add_contact(args:list,book:AddressBook):
    if len(args)<2: return "Invalid. Please write add+name+phone(10 digits)"
    name,phone,*_=args
    phone_validation(phone)
    record= book.find(name.capitalize())
    message="Contact updated."
    if record is None:
        record=Record(name.capitalize())
        book.add_record(record)
        message="Contact added"
    if phone:record.add_phone(phone)
    return message

@input_error
def change_contact(args:list,book:AddressBook):
    if len(args)<3: return "Invalid, format should be: name + old phone number + new number "
    name,old,new,*_=args
    record=book.data[name.capitalize()]
    if record:
        record.edit_phone(old,new)
        return 'Contact updated'

@input_error
def show_phone(args:list,book:AddressBook)->str:
    name,*_=args
    return book.data[name.capitalize()]

@input_error
def show_all(book:AddressBook)->str:
    record=book.data.values()
    if not record:return "Contacts list is empty"
    result=''
    for value in record: result+=f'{value}\n'
    return result.strip()

@input_error
def add_birthday(args,book:AddressBook):
    if len(args)<2: return "Wrong format.Use name + birthday data"
    name,birth_data,*_=args
    record=book.data[name.capitalize()]
    record.add_birthday(birth_data)
    return 'Birthday added'

@input_error
def show_birthday(args,book:AddressBook):
    name,*_=args
    record=book.data[name.capitalize()]
    return record.birthday

@input_error
def birthdays(book:AddressBook):
    result=""
    record=book.get_upcoming_birthdays()
    if record:
        for dic in record:
            result+=f"Contact name: {dic['name']}, Greeting date: {datetime.strftime(dic['birthday'],'%d.%m.%Y')}\n"
        return result.strip()
    return "There is no birthdays this week"

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()



def main():
    book=load_data()
    print('Welcome to the assistant bot!')
    while True:
        user_input=input('Enter a comand here please: ')
        cmd,*args=parse_input(user_input)
        
        if cmd in ['exit','close','quit','q']:
            save_data(book)
            print('Good bye')
            break
        elif cmd=='hello':
            print('How can I help you?')
        elif cmd=='add':
            print(add_contact(args,book))
        elif cmd=='change':
            print(change_contact(args,book))
        elif cmd=='all':
            print(show_all(book))
        elif cmd=='phone':
            print(show_phone(args,book))
        elif cmd=='add-birthday':
            print(add_birthday(args,book))
        elif cmd=='show-birthday':
            print(show_birthday(args,book))
        elif cmd=='birthdays':
            print(birthdays(book))
        else:
            print('Invalid command')



if __name__=='__main__':
    main()