class EquipmentItem:
    """Класс для описания конкретного предмета экипировки"""

    def __init__(self, name, price_per_day, deposit=0, product_description=' ', status='available'):
        self.name = name
        self.product_description = product_description
        self.price_per_day = price_per_day
        self.deposit = deposit
        self.status = status

    def __str__(self):
        return f'{self.name}\nЦена: {self.price_per_day} руб/день\nЗалог:{self.deposit} руб.\n'


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
    
    def show_available(self):
        available_items = []
        for item in self.equip_items:
            if item.status == 'available':
                available_items.append(item)
        return available_items
    

class RentalService:
    """Класс для управления бронированием"""

    def __init__(self):
        self.booked_items = []

    def book_item(self, item):
        item.status = 'booked'
        self.booked_items.append(item)

    def full_rent_price(self, days):
        full_price = 0
        for item in self.booked_items:
            full_price += self.count_price(item, days)
        return full_price

    def count_price(self, item, days):
        return item.price_per_day * days + item.deposit
