#import pygame

from gameparts.parts import EquipmentItem, EquipmentCatalog, RentalService
#from gameparts.exceptions import ...

def main():
    running = True

    print('Добро пожаловать в сервис аренды туристического снаряжения!')

    catalog = EquipmentCatalog()
    rental_service = RentalService()

    while running:
        print('Выберите действие:')
        menu = int(input('1. Посмотреть каталог туристического снаряжения\n' \
        '2. Найти нужное снаряжение\n'
        '3. Предложить аренду туристического снаряжения\n'
        '4. Посмотреть список забронированного снаряжения\n' \
        '5. Выход из сервиса\n'))
        match menu:
            case 1:
                available_items = catalog.show_available()
                if available_items:
                    print("\nДоступное снаряжение:")
                    for item in available_items:
                        print(f'- {item.name}: {item.price_per_day} руб/день')
                    input_str = input('Вы можете открыть карточку любого товара. Для этого введите его название: ')
                    if input_str != '':
                        found_item = catalog.find_item(input_str)
                        if found_item:
                            for item in found_item:
                                print(item)
                        else:
                            print('Товар не найден')
                else:
                    print('Сейчас нет доступного снаряжения, но вы можете первым его добавить')

            case 2:
                needed_item = input('Введите название искомого снаряжения: ')
                found_item = catalog.find_item(needed_item)
                if found_item:
                    for item in found_item:
                        print(item)
                # функция бронирования
                
            case 3:
                name = input('Введите название снаряжения: ')
                price = int(input('Введите цену, руб/день: '))
                deposit_input = int(input('Введите сумму залога (необязательно), руб: '))
                deposit = int(deposit_input) if deposit_input.strip() != '' else 0
                description_input = input('Введите описание(необязательно): ')
                description = description_input if description_input != '' else ' '
                new_item = EquipmentItem(name, price, deposit, description)
                catalog.add_equip_item(new_item)
                print('Ваше предложение добавлено!')
            case 4:
                print('Забронированные товары:')
                if rental_service.booked_items:
                    for item in rental_service.booked_items:
                        print(f'- {item.name}: {item.price_per_day} руб/день')
                    days = int(input('Введите количество дней для расчета стоимости: '))
                    total_price = rental_service.full_rent_price(days)
                    print(f'Общая стоимость: {total_price} руб')
                else:
                    print('Нет забронированных товаров')
            case 5:
                running = False
            case _:
                print('Введена неверная команда')


if __name__ == '__main__':
    main()
