from .exceptions import WrongPasswordError, UserNotFoundError, LoginExistsError


class User:
    '''Класс для описания пользователя'''

    def __init__(self, full_name, tel, login, password, id = 0):
        self.full_name = full_name
        self.tel = tel
        self.login = login
        self.password = password
        self.id = id
        self.offers = []
        
    @staticmethod
    def hide_password(password):
        # Скрытие пароля пользователя.
        return '*' * len(password)
    
    def check_password(self, input_password):
        # Проверка введенного пароля.
        if input_password == self.password:
            return True
        raise WrongPasswordError()
    
    def change_info(self, field, new_value, old_password=None):
        # Изменение информации о пользователе.
        old_login = self.login

        if field.lower() == 'пароль' and old_password:
            if not self.check_password(old_password):
                raise WrongPasswordError()
            self.password = new_value
        elif field.lower() == 'логин' and old_password:
            if not self.check_password(old_password):
                raise WrongPasswordError()
            self.login = new_value
        elif field.lower() == 'фио':
            self.full_name = new_value
        elif field.lower() == 'телефон':
            self.tel = new_value

        self._update_user_in_file(old_login)

        if field.lower() == 'логин':
            self._update_login_in_equipment_file(old_login, new_value)


    def _update_user_in_file(self, search_login=None):
        # Обновление информации о пользователе в файле.
        search_login = search_login or self.login

        try:
            with open('users.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open('users.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    data = line.strip().split('|')
                    if len(data) >= 4 and data[2] == search_login:
                        f.write(self.to_string() + '\n')
                    else:
                        f.write(line)
        except Exception as e:
            print(f"Ошибка обновления пользователя в файле: {e}")

    def add_user_offers(self, item):
        # Добавление нового снаряжения.
        self.offers.append(item)

    def get_user_offers(self):
        # Вывод предложений пользователя.
        return self.offers

    def to_string(self):
        # Формирование записи о пользователе.
        return f'{self.full_name}|{self.tel}|{self.login}|{self.password}|{self.id}'

    @classmethod
    def from_string(cls, line):
        # Формирование объекта из строки.
        data = line.strip().split('|')
        return cls(data[0], data[1], data[2], data[3], int(data[4]))
    
    def save_user_to_file(self):
        # Передача нового пользователя в файл.
        try:
            with open('users.txt', 'a', encoding='utf-8') as f:
                f.write(self.to_string() + '\n')
        except Exception as e:
            print(f"Ошибка сохранения пользователя: {e}")
    
    def _update_login_in_equipment_file(self, old_login, new_login):
        # Обновление логина во всех связанных записях экипировки
        try:
            with open('equipment.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open('equipment.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    data = line.strip().split('|')
                    if len(data) >= 7: 
                        if data[5] == old_login:
                            data[5] = new_login
                        if len(data) > 6 and data[6] == old_login:
                            data[6] = new_login
                        
                        updated_line = '|'.join(data) + '\n'
                        f.write(updated_line)
                    else:
                        f.write(line)
        except Exception as e:
            print(f"Ошибка обновления логина в файле экипировки: {e}")

    def __str__(self):
        return f'ФИО: {self.full_name}\nТелефон: {self.tel}\nЛогин: {self.login}\nПароль: {self.hide_password(self.password)}'


class Users:
    '''Класс для хранения клиентов'''

    def __init__(self):
        self.users = []
        self.next_id = 1
        self.load_users()

    def add_user(self, full_name, tel, login, password):
        # Добавление нового пользователя.
        if any(user.login == login for user in self.users):
            raise LoginExistsError()
        
        if len(password) < 4:
            return False, 'Пароль должен содержать не менее 4 символов'

        new_user = User(full_name, tel, login, password, self.next_id)           
        self.users.append(new_user)
        self.next_id += 1
        new_user.save_user_to_file()

    def find_user(self, login):
        # Поиск пользователя по логину.
        for user in self.users:
            if user.login == login:
                return user
        return None
            
    def user_authentication(self, login, password):
        # Аутентификация пользователя.
        user = self.find_user(login)
        if not user:
            raise UserNotFoundError()

        if user.check_password(password):
            return user
        
        raise WrongPasswordError()
    
    def check_duplicate(self, full_name, tel):
        # Проверка пользователя на дубликат.
        for user in self.users:
            if user.full_name == full_name and user.tel == tel:
                return True
            return False
            
    def load_users(self):
        # Извлечение пользователей из файла
        try:
            with open('users.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    user = User.from_string(line)
                    self.users.append(user)
                    if user.id >= self.next_id:
                        self.next_id = user.id + 1
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")


class EquipmentItem:
    """Класс для описания конкретного предмета экипировки"""

    def __init__(self, name, price_per_day, deposit=0, product_description=' ', status='available', owner=None, booked_by=None):
        self.name = name
        self.product_description = product_description
        self.price_per_day = price_per_day
        self.deposit = deposit
        self.status = status
        self.owner = owner
        self.booked_by = booked_by

    def change_info_item(self, field, new_value):
        # Изменение информации о предмете экипировки.
        if field.lower() in 'название':
            self.name = new_value
        elif field.lower() in 'описание':
            self.product_description = new_value
        elif field.lower() in 'цена':
            self.price_per_day = new_value
        elif field.lower() in 'залог':
            self.deposit = new_value
        self._update_item_in_file()
    
    def _update_item_in_file(self):
        # Обновление информации о пользователе в файле.
        try:
            with open('equipment.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()

            with open('equipment.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    data = line.strip().split('|')
                    if len(data) >= 1 and data[0] == self.name:
                        f.write(self.to_string() + '\n')
                    else:
                        f.write(line)
        except Exception as e:
            print(f'Ошибка обновления предмета в файле: {e}')

    def to_string(self):
        # Преобразование информации об экипировке в запись. 
        owner_login = self.owner.login if self.owner else 'None'
        booked_by_login = self.booked_by.login if self.booked_by else 'None'
        return f'{self.name}|{self.product_description}|{self.price_per_day}|{self.deposit}|{self.status}|{owner_login}|{booked_by_login}'

    @classmethod
    def from_string(cls, line, users_list):
        # Формирование объекта из строки.
        data = line.strip().split('|')
        owner = None
        booked_by = None
        
        if data[5] != "None":
            owner = users_list.find_user(data[5])
        if len(data) > 6 and data[6] != "None": 
            booked_by = users_list.find_user(data[6])
        
        return cls(data[0], int(data[2]), int(data[3]), data[1], data[4], owner, booked_by)

    def save_to_file(self):
        # Запись предмета в файл.
        try:
            with open('equipment.txt', 'a', encoding='utf-8') as f:
                f.write(self.to_string() + '\n')
        except Exception as e:
            print(f"Ошибка сохранения предмета: {e}")

    def __str__(self):
        return f'{self.name}\nЦена: {self.price_per_day} руб/день\nЗалог: {self.deposit} руб.\nОписание: {self.product_description if self.product_description != "" else "отсутствует"}\n'


class EquipmentCatalog:
    """Класс для описания каталога и работе с ним"""

    def __init__(self, users_list):
        self.equip_items = []
        self.users_list = users_list
        self.load_equipment()

    def add_equip_item(self, item):
        # Добавление нового предмета в файл.
        self.equip_items.append(item)
        item.save_to_file()
    
    def find_item(self, input_str):
        # Поиск предмета экипировки в каталоге.
        found_items = []
        for item in self.equip_items:
            if input_str.lower() in item.name.lower() and item.status == 'available':
                found_items.append(item)
        return found_items
    
    def find_user_offers(self, user):
        # Вывод всех предложений пользователя.
        return [item for item in self.equip_items if item.owner == user]
    
    def show_available(self):
        # Вывод всех доступных предметов экипировки.
        available_items = []
        for item in self.equip_items:
            if item.status == 'available':
                available_items.append(item)
        return available_items
    
    def remove_item(self, item):
        # Удаление объявления о сдаче предмета экипировки.
        if item in self.equip_items:
            self.equip_items.remove(item)
            self._remove_item_from_file(item)

    def _remove_item_from_file(self, item):
        # Удаление предмета экипировки из файла
        try:
            with open('equipment.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open('equipment.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    data = line.strip().split('|')
                    if len(data) >= 1 and data[0] != item.name: 
                        f.write(line)
        except Exception as e:
            print(f"Ошибка удаления предмета из файла: {e}")
    
    def load_equipment(self):
        # Загрузка всех предметов из файла.
        try:
            with open('equipment.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    item = EquipmentItem.from_string(line, self.users_list)
                    self.equip_items.append(item)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Ошибка загрузки оборудования: {e}")
    

class RentalService:
    """Класс для управления бронированием"""

    def __init__(self, users_list):
        self.users_list = users_list

    def book_item(self, item, user):
        # Бронирование предмета экипировки.
        if item.status == 'available':
            item.status = 'booked'
            item.booked_by = user
            item._update_item_in_file()

    def get_user_bookings(self, user, catalog):
        # Получение списка забронированных пользователем товаров
        user_bookings = []
        for item in catalog.equip_items:
            if item.booked_by == user and item.status == 'booked':
                user_bookings.append(item)
        return user_bookings
    
    def remove_booking_by_item(self, item, user):
        # Удаление бронирования по объекту предмета
        if item.booked_by == user and item.status == 'booked':
            item.status = 'available'
            item.booked_by = None 
            item._update_item_in_file()
            return True  
        return False

    def full_rent_price(self, days, user, catalog): 
        # Расчет полной стоимости аренды забронированной экипировки.
        full_price = 0
        user_bookings = self.get_user_bookings(user, catalog)
        
        for item in user_bookings:
            full_price += self.count_price(item, days)
        return full_price

    def count_price(self, item, days):
        return item.price_per_day * days + item.deposit
