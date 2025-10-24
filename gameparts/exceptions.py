class WrongPasswordError(Exception):
    """Исключение для неверного пароля"""

    def __str__(self):
        return "Введен неверный пароль"


class UserNotFoundError(Exception):
    """Исключение для отсутствующего пользователя"""

    def __str__(self):
        return "Пользователь не найден"


class LoginExistsError(Exception):
    """Исключение для существующего логина"""

    def __str__(self):
        return "Введенный логин уже существует"
