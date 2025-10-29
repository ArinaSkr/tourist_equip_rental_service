import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QListWidget, QMessageBox, QTabWidget,
                            QGroupBox, QFormLayout, QSpinBox, QStackedWidget,
                            QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Импортируем ваши классы
from gameparts.parts import Users, EquipmentItem, EquipmentCatalog, RentalService
from gameparts.exceptions import WrongPasswordError, UserNotFoundError, LoginExistsError

class LoginWindow(QWidget):
    """Окно входа и регистрации"""
    
    login_success = pyqtSignal(object)  # Сигнал об успешном входе
    
    def __init__(self, users_system):
        super().__init__()
        self.users = users_system
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Добро пожаловать в EQUIPlease!")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #355262; margin: 20px;")
        layout.addWidget(title)
        
        subtitle = QLabel("- сервис аренды туристического снаряжения -")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #c0c0c0; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Форма входа
        login_group = QGroupBox("Вход в систему")
        login_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        login_layout = QFormLayout()
        
        self.login_input = QLineEdit()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_layout.addRow("Логин:", self.login_input)
        login_layout.addRow("Пароль:", self.password_input)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        login_btn = QPushButton("Войти")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #355262;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1B5B7E;
            }
        """)
        login_btn.clicked.connect(self.login)
        
        layout.addWidget(login_btn)
        
        # Разделитель
        separator = QLabel("или")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #c0c0c0; margin: 10px;")
        layout.addWidget(separator)
        
        # Кнопка регистрации
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
        """)
        register_btn.clicked.connect(self.show_registration)
        
        layout.addWidget(register_btn)
        self.setLayout(layout)
        
    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        try:
            user = self.users.user_authentication(login, password)
            self.login_success.emit(user)
        except UserNotFoundError:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден")
        except WrongPasswordError:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль")
            
    def show_registration(self):
        dialog = RegistrationDialog(self.users, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user = dialog.get_created_user()
            if user:
                self.login_success.emit(user)

class RegistrationDialog(QDialog):
    """Диалог регистрации"""
    
    def __init__(self, users_system, parent=None):
        super().__init__(parent)
        self.users = users_system
        self.created_user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Регистрация")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Форма регистрации
        form_group = QGroupBox("Регистрация нового пользователя")
        form_layout = QFormLayout()
        
        self.full_name_input = QLineEdit()
        self.tel_input = QLineEdit()
        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("ФИО:", self.full_name_input)
        form_layout.addRow("Телефон:", self.tel_input)
        form_layout.addRow("Логин:", self.login_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("Подтвердите пароль:", self.confirm_password_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.register)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def register(self):
        # Получаем данные из полей
        full_name = self.full_name_input.text().strip()
        tel = self.tel_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Проверки
        if not all([full_name, tel, login, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
            
        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать не менее 4 символов")
            return
            
        # Проверка на дубликат
        duplicate = self.users.check_duplicate(full_name, tel)
        if duplicate:
            reply = QMessageBox.question(
                self, 
                "Пользователь существует", 
                "Пользователь с такими данными уже существует. Хотите войти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # TODO: Переход к входу
                pass
            return
            
        # Проверка логина
        if self.users.find_user(login):
            QMessageBox.warning(self, "Ошибка", "Этот логин уже занят")
            return
            
        try:
            self.users.add_user(full_name, tel, login, password)
            user = self.users.find_user(login)
            
            self.created_user = user
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.accept()
        except LoginExistsError:
            QMessageBox.warning(self, "Ошибка", "Этот логин уже занят")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка регистрации: {e}")
            
    def get_created_user(self):
        return self.created_user

class EditProfileDialog(QDialog):
    """Диалог редактирования профиля"""
    
    profile_updated = pyqtSignal()  # Сигнал об обновлении профиля
    
    def __init__(self, user, users_system, parent=None):
        super().__init__(parent)
        self.user = user
        self.users = users_system
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Редактирование профиля")
        self.setModal(True)
        self.resize(450, 400)
        
        layout = QVBoxLayout()
        
        # Форма редактирования
        form_group = QGroupBox("Редактировать данные")
        form_layout = QFormLayout()
        
        self.full_name_input = QLineEdit(self.user.full_name)
        self.tel_input = QLineEdit(self.user.tel)
        self.login_input = QLineEdit(self.user.login)
        
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("ФИО:", self.full_name_input)
        form_layout.addRow("Телефон:", self.tel_input)
        form_layout.addRow("Логин:", self.login_input)
        form_layout.addRow("Текущий пароль:", self.current_password_input)
        form_layout.addRow("Новый пароль:", self.new_password_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_changes)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def save_changes(self):
        new_full_name = self.full_name_input.text().strip()
        new_tel = self.tel_input.text().strip()
        new_login = self.login_input.text().strip()
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        
        changes_made = False
        
        try:
            # Изменение ФИО
            if new_full_name and new_full_name != self.user.full_name:
                self.user.change_info("фио", new_full_name)
                changes_made = True
                
            # Изменение телефона
            if new_tel and new_tel != self.user.tel:
                self.user.change_info("телефон", new_tel)
                changes_made = True
                
            # Изменение логина
            if new_login and new_login != self.user.login:
                if self.users.find_user(new_login) and new_login != self.user.login:
                    QMessageBox.warning(self, "Ошибка", "Этот логин уже занят")
                    return
                if not current_password:
                    QMessageBox.warning(self, "Ошибка", "Для смены логина нужен текущий пароль")
                    return
                self.user.change_info("логин", new_login, old_password=current_password)
                changes_made = True
                
            # Изменение пароля
            if new_password:
                if not current_password:
                    QMessageBox.warning(self, "Ошибка", "Для смены пароля нужен текущий пароль")
                    return
                if len(new_password) < 4:
                    QMessageBox.warning(self, "Ошибка", "Пароль должен содержать не менее 4 символов")
                    return
                self.user.change_info("пароль", new_password, old_password=current_password)
                changes_made = True
                
            if changes_made:
                self.profile_updated.emit()
                QMessageBox.information(self, "Успех", "Изменения сохранены!")
                self.accept()
            else:
                QMessageBox.information(self, "Информация", "Изменений не было")
                
        except WrongPasswordError:
            QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")


class AddOfferDialog(QDialog):
    """Диалог добавления нового предложения"""
    
    offer_added = pyqtSignal()  # Сигнал о добавлении предложения
    
    def __init__(self, user, catalog_system, parent=None):
        super().__init__(parent)
        self.user = user
        self.catalog = catalog_system
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Добавить предложение")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Форма добавления
        form_group = QGroupBox("Добавить снаряжение в аренду")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        
        self.price_input = QSpinBox()
        self.price_input.setRange(1, 100000)
        self.price_input.setValue(100)
        
        self.deposit_input = QSpinBox()
        self.deposit_input.setRange(0, 100000)
        self.deposit_input.setValue(0)
        
        self.description_input = QTextEdit()
        
        form_layout.addRow("Название*:", self.name_input)
        form_layout.addRow("Цена, руб/день*:", self.price_input)
        form_layout.addRow("Залог, руб:", self.deposit_input)
        form_layout.addRow("Описание:", self.description_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.add_offer)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def add_offer(self):
        name = self.name_input.text().strip()
        price = self.price_input.value()
        deposit = self.deposit_input.value()
        description = self.description_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название снаряжения")
            return
            
        # Создаем новый предмет
        new_item = EquipmentItem(
            name=name,
            price_per_day=price,
            deposit=deposit,
            product_description=description if description else "описание отсутствует",
            owner=self.user
        )
        
        # Добавляем в каталог
        self.catalog.add_equip_item(new_item)
        self.user.add_user_offers(new_item)
        
        self.offer_added.emit()
        QMessageBox.information(self, "Успех", "Предложение добавлено!")
        self.accept()


class ManageOfferDialog(QDialog):
    """Диалог управления предложением"""
    
    offer_updated = pyqtSignal()
    
    def __init__(self, item, catalog_system, parent=None):
        super().__init__(parent)
        self.item = item
        self.catalog = catalog_system
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Управление: {self.item.name}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Текущая информация
        info_group = QGroupBox("Текущая информация")
        info_layout = QFormLayout()
        
        info_text = QTextEdit()
        info_text.setPlainText(str(self.item))
        info_text.setReadOnly(True)
        info_layout.addRow(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Форма редактирования
        edit_group = QGroupBox("Редактировать")
        edit_layout = QFormLayout()
        
        self.name_input = QLineEdit(self.item.name)
        self.price_input = QSpinBox()
        self.price_input.setRange(1, 100000)
        self.price_input.setValue(self.item.price_per_day)
        
        self.deposit_input = QSpinBox()
        self.deposit_input.setRange(0, 100000)
        self.deposit_input.setValue(self.item.deposit)
        
        self.description_input = QTextEdit()
        self.description_input.setPlainText(self.item.product_description)
        self.description_input.setMaximumHeight(80)
        
        edit_layout.addRow("Название:", self.name_input)
        edit_layout.addRow("Цена в день:", self.price_input)
        edit_layout.addRow("Залог:", self.deposit_input)
        edit_layout.addRow("Описание:", self.description_input)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Кнопки действий
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить изменения")
        save_btn.clicked.connect(self.save_changes)
        
        delete_btn = QPushButton("Удалить предложение")
        delete_btn.setStyleSheet(" color: red; ")
        delete_btn.clicked.connect(self.delete_offer)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def save_changes(self):
        new_name = self.name_input.text().strip()
        new_price = self.price_input.value()
        new_deposit = self.deposit_input.value()
        new_description = self.description_input.toPlainText().strip()
        
        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
            
        # Применяем изменения
        if new_name != self.item.name:
            self.item.change_info_item("название", new_name)
            
        if new_price != self.item.price_per_day:
            self.item.change_info_item("цена", new_price)
            
        if new_deposit != self.item.deposit:
            self.item.change_info_item("залог", new_deposit)
            
        if new_description != self.item.product_description:
            self.item.change_info_item("описание", new_description)
            
        self.offer_updated.emit()
        QMessageBox.information(self, "Успех", "Изменения сохранены!")
        
    def delete_offer(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить предложение '{self.item.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.catalog.remove_item(self.item)
            self.offer_updated.emit()
            QMessageBox.information(self, "Успех", "Предложение удалено")
            self.accept()


class MainWindow(QMainWindow):
    """Главное окно приложения после входа"""
    
    def __init__(self, user, users_system, catalog_system, rental_system):
        super().__init__()
        self.user = user
        self.users = users_system
        self.catalog = catalog_system
        self.rental = rental_system
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"EQUIPlease - Добро пожаловать, {self.user.login}!")
        self.setGeometry(100, 100, 1000, 700)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # Вкладка 1: Каталог снаряжения
        self.catalog_tab = self.create_catalog_tab()
        self.tabs.addTab(self.catalog_tab, "Каталог")
        
        # Вкладка 2: Профиль
        self.profile_tab = self.create_profile_tab()
        self.tabs.addTab(self.profile_tab, "Профиль")
        
        # Вкладка 3: Мои предложения
        self.offers_tab = self.create_offers_tab()
        self.tabs.addTab(self.offers_tab, "Мои предложения")
        
        # Вкладка 4: Бронирования
        self.bookings_tab = self.create_bookings_tab()
        self.tabs.addTab(self.bookings_tab, "Бронирования")
        
        self.setCentralWidget(self.tabs)
        
    def create_catalog_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Доступное снаряжение")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #355262; margin: 10px;")
        layout.addWidget(title)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Найти...")
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_equipment)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Список снаряжения
        self.equipment_list = QListWidget()
        self.equipment_list.itemDoubleClicked.connect(self.show_equipment_details)
        layout.addWidget(self.equipment_list)
        
        # Обновляем список
        self.update_equipment_list()
        
        widget.setLayout(layout)
        return widget
        
    def create_profile_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Профиль")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #355262; margin: 10px;")
        layout.addWidget(title)

        # Информация о пользователе
        info_group = QGroupBox()
        info_layout = QFormLayout()
        
        self.profile_display = QTextEdit()
        self.profile_display.setReadOnly(True)
        self.profile_display.setPlainText(str(self.user))
        self.profile_display.setStyleSheet("font-size: 14px;")
        
        info_layout.addRow(self.profile_display)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Кнопка редактирования
        edit_btn = QPushButton("Редактировать профиль")
        edit_btn.clicked.connect(self.edit_profile)
        layout.addWidget(edit_btn)
        
        widget.setLayout(layout)
        return widget
        
    def create_offers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Мои предложения")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #355262; margin: 10px;")
        layout.addWidget(title)
        
        self.offers_list = QListWidget()
        self.offers_list.setStyleSheet("font-size: 14px;")
        self.offers_list.itemDoubleClicked.connect(self.show_offer_details)
        layout.addWidget(self.offers_list)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить предложение")
        add_btn.clicked.connect(self.add_offer)
        edit_btn = QPushButton("Редактировать выбранное")
        edit_btn.clicked.connect(lambda: self.show_offer_details(self.offers_list.currentItem()))
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        
        layout.addLayout(btn_layout)
        
        self.update_offers_list()
        
        widget.setLayout(layout)
        return widget
        
    def create_bookings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Мои бронирования")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #355262; margin: 10px;")
        layout.addWidget(title)

        # Расчет стоимости
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Дни:"))
        self.days_input = QSpinBox()
        self.days_input.setRange(1, 365)
        self.days_input.setValue(1)
        cost_layout.addWidget(self.days_input)
        
        calc_btn = QPushButton("Рассчитать стоимость")
        calc_btn.clicked.connect(self.calculate_cost)
        cost_layout.addWidget(calc_btn)
        
        self.cost_label = QLabel("Общая стоимость: 0 руб")
        cost_layout.addWidget(self.cost_label)
        
        layout.addLayout(cost_layout)
        
        self.bookings_list = QListWidget()
        self.bookings_list.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.bookings_list)
        
        delete_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить выбранное бронирование")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d7d7d7;
                color: red;
                border: none;
                padding: 8px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        delete_btn.clicked.connect(self.remove_booking)
        delete_layout.addWidget(delete_btn)
        layout.addLayout(delete_layout)

        self.update_bookings_list()
        
        widget.setLayout(layout)
        return widget
        
    def update_equipment_list(self):
        """Обновление списка доступного снаряжения"""
        self.equipment_list.clear()
        self.equipment_list.setStyleSheet("font-size: 14px;")
        available_items = self.catalog.show_available()
        
        for item in available_items:
            list_item = QListWidgetItem(
                f"{item.name} - {item.price_per_day} руб/день"
            )
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.equipment_list.addItem(list_item)
            
    def update_offers_list(self):
        """Обновление списка предложений пользователя"""
        self.offers_list.clear()
        self.offers_list.setStyleSheet("font-size: 14px;")
        user_offers = self.catalog.find_user_offers(self.user)
        
        for item in user_offers:
            list_item = QListWidgetItem(
                f"{item.name} - {item.price_per_day} руб/день"
            )
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.offers_list.addItem(list_item)
            
    def update_bookings_list(self):
        """Обновление списка бронирований"""
        self.bookings_list.clear()
        self.bookings_list.setStyleSheet("font-size: 14px;")
        user_bookings = self.rental.get_user_bookings(self.user, self.catalog)
        
        for i, item in enumerate(user_bookings, 1):
            list_item = QListWidgetItem(
                f"{i}. {item.name} - {item.price_per_day} руб/день"
            )
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.bookings_list.addItem(list_item)
            
    def search_equipment(self):
        """Поиск снаряжения"""
        search_text = self.search_input.text().strip()
        if search_text:
            found_items = self.catalog.find_item(search_text)
            self.equipment_list.clear()
            for item in found_items:
                list_item = QListWidgetItem(
                    f"{item.name} - {item.price_per_day} руб/день"
                )
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.equipment_list.addItem(list_item)
        else:
            self.update_equipment_list()
            
    def show_equipment_details(self, item):
        """Показать детали снаряжения"""
        equipment = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            equipment.name,
            f"{equipment}\nХотите забронировать этот товар?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.rental.book_item(equipment, self.user)
            QMessageBox.information(self, "Успех", "Товар забронирован!")
            self.update_equipment_list()
            self.update_bookings_list()
        
    def edit_profile(self):
        """Редактирование профиля"""
        dialog = EditProfileDialog(self.user, self.users, self)
        dialog.profile_updated.connect(self.update_profile_display)
        dialog.exec()

    def update_profile_display(self):
        """Обновление отображения профиля"""
        self.profile_display.setPlainText(str(self.user))
        
    def add_offer(self):
        """Добавление нового предложения"""
        dialog = AddOfferDialog(self.user, self.catalog, self)
        dialog.offer_added.connect(self.update_offers_list)
        dialog.exec()

    def show_offer_details(self, item):
        """Показать детали предложения для редактирования"""
        if item:
            equipment = item.data(Qt.ItemDataRole.UserRole)
            dialog = ManageOfferDialog(equipment, self.catalog, self)
            dialog.offer_updated.connect(self.update_offers_list)
            dialog.exec()

    def calculate_cost(self):
        """Расчет стоимости бронирований"""
        days = self.days_input.value()
        total_price = self.rental.full_rent_price(days, self.user, self.catalog)
        self.cost_label.setText(f"Общая стоимость: {total_price} руб")

    def remove_booking(self):
        """Удаление выбранного бронирования"""
        current_item = self.bookings_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование для удаления")
            return
            
        equipment = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить бронирование '{equipment.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.rental.remove_booking_by_item(equipment, self.user):
                QMessageBox.information(self, "Успех", f"Бронирование '{equipment.name}' удалено")
                self.update_bookings_list()
                self.update_equipment_list()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить бронирование")

class EQUIPleaseApp(QWidget):
    """Главное приложение"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация систем
        self.users = Users()
        self.catalog = EquipmentCatalog(self.users)
        self.rental = RentalService(self.users)
        
        self.current_user = None
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # Создаем stacked widget для переключения между окнами
        self.stacked_widget = QStackedWidget()
        
        # Окно входа
        self.login_window = LoginWindow(self.users)
        self.login_window.login_success.connect(self.on_login_success)
        
        self.stacked_widget.addWidget(self.login_window)
        
        self.layout.addWidget(self.stacked_widget)
        self.setLayout(self.layout)
        
        self.setWindowTitle("EQUIPlease")
        self.resize(500, 400)
        
    def on_login_success(self, user):
        """Обработка успешного входа"""
        self.current_user = user
        self.show_main_window()
        
    def show_main_window(self):
        """Показать главное окно"""
        self.main_window = MainWindow(
            self.current_user, 
            self.users, 
            self.catalog, 
            self.rental
        )
        self.stacked_widget.addWidget(self.main_window)
        self.stacked_widget.setCurrentIndex(1)
        
        # Обновляем размер окна
        self.resize(700, 500)

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль
    app.setStyle('Fusion')
    
    window = EQUIPleaseApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
