class User:
    '''Класс для описание пользователя'''

    def __init__(self, full_name, tel, login, password, id = 0):
        self.fullname = full_name
        self.tel = tel
        self.login = login
        self.password = password
        self.offers = []
        
    @staticmethod
    def hide_password(password):
        # функция для скрытия пароля пользователя
        return '*' * len(password)
    
    def check_password(self, input_password):
        return True if input_password == self.password else raise WrongPassswordError
    
    def change_info(self, field, new_value, old_password=None):
        # функция для изменения информации о пользователе
        if field.lower() == 'пароль' and old_password:
            if not self.check_password(old_password):
                return 'Пароль неверный'
            self.password = new_value
        elif field.lower() == 'логин' and old_password:
            if not self.check_password(old_password):
                return 'Пароль неверный'
            self.login = new_value
        elif field.lower() == 'фио':
            self.full_name = new_value
        elif field.lower() == 'телефон':
            self.tel = new_value

    def add_user_offers(self, item):
        #with open(users_offers) as file
        self.offers.append(item)

    def get_user_offers(self):
        return self.offers

    def __str__(self):
        return f'ФИО: {self.fullname}\nТелефон: {self.tel}\nЛогин: {self.login}\nПароль: {self.hide_password(self.password)}'


class Users:
    '''Класс для хранения клиентов'''

    def __init__(self):
        self.users = []

    def add_user(self, full_name, tel, login, password):
        
        if any(user.login == login for user in self.users):
            return False, 'Логин уже существует'
        
        if len(password) < 4:
            return False, 'Пароль должен содержать не менее 4 символов'

        new_user = User(full_name, tel, login, password)            
        self.users.append(new_user)

    def find_user(self, login):
        for user in self.users:
            if user.login == login:
                return user
            
    def user_aunthentication(self, login, password):
        user = self.find_user
        if user and user.check_password(password):
            return True
        return raise WrongPasswordError
    
    def check_duplicate(self, full_name, tel):
        for user in self.users:
            if user.full_name == full_name and user.tel == tel:
                return True
            else:
                return False


class EquipmentItem:
    """Класс для описания конкретного предмета экипировки"""

    def __init__(self, name, price_per_day, deposit=0, product_description=' ', status='available', owner = None):
        self.name = name
        self.product_description = product_description
        self.price_per_day = price_per_day
        self.deposit = deposit
        self.status = status
        self.owner = owner

    def change_info_item(self, field, new_value):
        # функция для изменения информации о пользователе
        if field.lower() in 'название':
            self.name = new_value
        elif field.lower() in 'описание':
            self.product_description = new_value
        elif field.lower() in 'цена':
            self.price_per_day = new_value
        elif field.lower() in 'залог':
            self.deposit = new_value

    def __str__(self):
        return f'{self.name}\n \
        Цена: {self.price_per_day} руб/день\n \
        Залог: {self.deposit} руб.\n \
        Описание: {self.product_description if self.product_description != '' else 'отсутствует'}\n'



class EquipmentCatalog:
    """Класс для описания каталога и работе с ним"""

    def __init__(self):
        self.equip_items = []

    def add_equip_item(self, item):
        self.equip_items.append(item)
    
    def find_item(self, input_str):
        found_items = []
        for item in self.equip_items:
            if input_str.lower() in item.name.lower() and item.status == 'available':
                found_items.append(item)
        return found_items
    
    def find_user_offers(self, user):
        return [item for item in self.equip_items if item.owner == user]
    
    def show_available(self):
        available_items = []
        for item in self.equip_items:
            if item.status == 'available':
                available_items.append(item)
        return available_items
    
    def remove_item(self, item):
        if item in self.equip_items:
            self.equip_items.remove(item)
    

class RentalService:
    """Класс для управления бронированием"""

    def __init__(self):
        self.booked_items = []

    def book_item(self, item, user):
        if item.status == 'available':
            item.status = 'booked'
            booking = {'item': item, 'user': user, 'days': 0}
            self.booked_items.append(item)

    def get_user_bookings(self, item, user):
        return [booking for booking in self.booked_items if booking['user'] == user]
    
    def remove_booking(self, item, user):
        for booking in self.booked_items:
            if booking['item'].name.lower() == item_name.lower() and booking['user'] == user:
                booking['item'].status = 'available'
                self.booked_items.remove(booking)

    def full_rent_price(self, days):
        full_price = 0
        for booking in self.booked_items:
            booking['days'] = days
            full_price += self.count_price(booking['item'], days)
        return full_price

    def count_price(self, item, days):
        return item.price_per_day * days + item.deposit
