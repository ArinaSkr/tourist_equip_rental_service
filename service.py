import getpass

from gameparts.parts import User, Users, EquipmentItem, EquipmentCatalog, RentalService
from gameparts.exceptions import WrongPasswordError, UserNotFoundError, LoginExistsError


def get_password_input(prompt='Введите пароль: '):
    # Функция для скрытия ввода пароля
    return getpass.getpass(prompt)

def main():
    running = True

    users = Users()
    catalog = EquipmentCatalog(users)
    rental_service = RentalService(users)

    print('Добро пожаловать в сервис аренды туристического снаряжения EQUIPlease!')

    actual_user = None
    while actual_user is None:
        choice = input('У вас уже есть аккаунт? (да/нет):').lower()
        print('-' * 10)
        match choice:
            case 'да':
                try:
                    login = input('Введите логин: ')
                    password = get_password_input('Введите пароль: ')
                    user = users.user_authentication(login, password)
                    actual_user = user
                except (WrongPasswordError, UserNotFoundError) as e:
                    print(f"Ошибка: {e}")
            case 'нет':
                while actual_user is None:
                    print('Регистрация пользователя')
                    user_full_name = input('Введите ФИО: ')
                    user_tel = input('Введите телефон: ')
                    if users.check_duplicate(user_full_name, user_tel):
                        choice = input('Пользователь с такими данными уже существует. Хотите войти? (да/нет): ')
                        if choice.lower() == 'да':
                            login = input('Введите логин: ')
                            password = get_password_input('Введите пароль: ')
                            users.user_aunthentication(login, password)
                        else:
                            print('Пожалуйста, используйте другие данные.')
                            continue
                    user_login = input('Придумайте логин: ')
                    if users.find_user(user_login):
                        print('Этот логин уже занят. Придумайте другой.')
                        continue
                    user_password = get_password_input('Введите пароль(не менее 4 символов): ')
                    try:
                        user = users.add_user(user_full_name, user_tel, user_login, user_password)
                        actual_user = user
                        break
                    except LoginExistsError as e:
                        print(f"Ошибка: {e}")

    while running:
        print('-' * 10)
        print('Выберите действие - введите номер:')
        try:
            menu = int(input(
            '1. Посмотреть каталог туристического снаряжения\n' 
            '2. Посмотреть профиль\n' 
            '3. Предложить аренду туристического снаряжения\n' 
            '4. Посмотреть список забронированного снаряжения\n' 
            '5. Посмотреть список моих предложений\n'
            '6. Выход из сервиса\n'
            ))
        except ValueError:
            print('Пожалуйста, введите число от 1 до 6')
            continue
        print('-' * 10)
        match menu:
            case 1:
                available_items = catalog.show_available()
                if available_items:
                    print("\nДоступное для бронирования снаряжение:")
                    for item in available_items:
                        print(f'- {item.name}: {item.price_per_day} руб/день')
                    input_str = input('Вы можете открыть карточку любого товара. Для этого введите его название: ')
                    if input_str != '':
                        found_item = catalog.find_item(input_str)
                        if found_item:
                            for item in found_item:
                                print(item)
                                book_choice = input('Хотите забронировать этот товар? (да/нет):')
                                if book_choice.lower() in 'да':
                                    rental_service.book_item(item, actual_user)
                                    print('Успешно забронироавно!')
                                    break
                        else:
                            print('Товар не найден')
                else:
                    print('Сейчас нет доступного снаряжения, но вы можете первым его добавить')

            case 2:
                print(f'Ваш профиль: \n{actual_user}')
                choice_change = input('Хотите изменить информацию? (да/нет): ')
                if choice_change.lower() in 'да':
                    what_change = input('Какую информацию хотите изменить?(ФИО, телефон, логин, пароль): ')
                    if what_change.lower() in ['фио', 'телефон']:
                        new_value = input('Введите новое значение: ')
                        try:
                            actual_user.change_info(what_change, new_value)
                        except Exception as e:
                            print(f"Ошибка: {e}")
                    elif what_change.lower() == 'логин':
                        old_password = get_password_input('Введите пароль для подтверждения: ')
                        new_login = input('Введите новый логин: ')
                        if users.find_user(new_login):
                            print('Этот логин уже занят')
                        else:
                            try:
                                actual_user.change_info('логин', new_login, old_password=old_password)
                            except WrongPasswordError as e:
                                print(f"Ошибка: {e}")
                    elif what_change == 'пароль':
                        old_password = get_password_input('Введите текущий пароль: ')
                        new_password = get_password_input('Введите новый пароль: ')
                        try:
                            actual_user.change_info('пароль', new_password, old_password=old_password)
                        except WrongPasswordError as e:
                            print(f"Ошибка: {e}")
            case 3:
                name = input('Введите название снаряжения: ')
                try:
                    price = int(input('Введите цену, руб/день: '))
                    if price <= 0:
                        print('Цена должна быть положительной')
                        continue
                except ValueError:
                    print('Цена должна быть числом')
                    continue
                deposit_input = input('Введите сумму залога (необязательно), руб: ')
                try:
                    deposit = int(deposit_input) if deposit_input.strip() != '' else 0
                except ValueError:
                    print('Залог должен быть числом. Установлен 0.')
                    deposit = 0
                description_input = input('Введите описание(необязательно): ')
                description = description_input if description_input != '' else 'описание отсутствует'
                new_item = EquipmentItem(name, price, deposit, description, owner=actual_user)
                catalog.add_equip_item(new_item)
                actual_user.add_user_offers(new_item)
                print('Ваше предложение добавлено!')

            case 4:
                user_bookings = rental_service.get_user_bookings(actual_user, catalog)
                if user_bookings:
                    print('Забронированное снаряжение:')
                    for i, item in enumerate(user_bookings, 1):
                        print(f'{i}. {item.name}: {item.price_per_day} руб/день')
                    
                    calc_choice = input('\nХотите посчитать общую стоимость? (да/нет): ')
                    if calc_choice.lower() in 'да':
                        try:
                            days = int(input('Введите количество дней для расчета стоимости: '))
                            total_price = rental_service.full_rent_price(days, actual_user, catalog)
                            print(f'Общая стоимость: {total_price} руб')
                        except ValueError:
                            print('Количество дней должно быть числом')
                    
                    change_choice = input('\nХотите изменить список? (да/нет): ')
                    if change_choice.lower() in 'да':
                        try:
                            item_number = int(input('Введите номер товара для удаления (или 0 для отмены): '))
                            if item_number == 0:
                                continue
                            elif 1 <= item_number <= len(user_bookings):
                                item_to_remove = user_bookings[item_number - 1]
                                if rental_service.remove_booking_by_item(item_to_remove, actual_user):
                                    print(f'Товар "{item_to_remove.name}" удален из бронирований')
                                else:
                                    print('Не удалось удалить товар')
                            else:
                                print('Неверный номер товара')
                        except ValueError:
                            print('Пожалуйста, введите число')
                else:
                    print('Нет забронированных товаров')

            case 5:
                while True:
                    user_offers = catalog.find_user_offers(actual_user)
                    if user_offers:
                        print('Ваши предложения: ')
                        for item in user_offers:
                            print(f'- {item.name}: {item.price_per_day} руб/день')
                        choice_change_item = input('Если хотите отредактировать/удалить объявление о снаряжении, введите его название: ')
                        if choice_change_item.strip() == '':
                            break
                        target_item = None
                        for item in user_offers:
                            if item.name.lower() == choice_change_item.lower():
                                target_item = item
                                break
                        if target_item:
                            action_item = input('Что хотите сделать? (удалить/изменить/назад): ')
                            if action_item.lower() == 'удалить':
                                if catalog.remove_item(target_item):
                                    actual_user.offers.remove(target_item)
                                    print('Объявление удалено')
                            elif action_item.lower() == 'изменить':
                                what_change = input('Какую информацию хотите изменить?(название, описание, цена, залог): ').lower()
                                if what_change in ['название', 'описание', 'цена', 'залог']:
                                    new_value = input('Введите новое значение: ')
                                    if what_change in ['цена', 'залог']:
                                        try:
                                            new_value = int(new_value)
                                        except ValueError:
                                            print('Значение должно быть числом')
                                            continue
                                    target_item.change_info_item(what_change, new_value)
                                    print('Изменения сохранены')
                            elif action_item == 'назад':
                                continue
                            else:
                                print('Неизвестное действие')
                        else:
                            print('Товар не найден среди ваших предложений')
                    else:
                        print('У вас пока нет объявлений')
                        break
            case 6:
                running = False
                print('До новых встреч!')
            case _:
                print('Введена неверная команда')


if __name__ == '__main__':
    main()
