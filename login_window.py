# login_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt
from services.firebase_api import firebase_login
from signup_window import SignupWindow


class LoginWindow(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Login")
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: white;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setStyleSheet("background-color: #FFEFE6;")
        left_widget.setMinimumWidth(600)

        image = QLabel()
        pixmap = QPixmap("Assets/logo.png")
        image.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
        image.setAlignment(Qt.AlignCenter)

        headline = QLabel("Turn your ideas into reality.")
        headline.setFont(QFont("Segoe UI", 18, QFont.Bold))
        headline.setAlignment(Qt.AlignCenter)

        subtext = QLabel("Start for free and get attractive offers from the community.")
        subtext.setAlignment(Qt.AlignCenter)
        subtext.setWordWrap(True)

        left_layout.addStretch()
        left_layout.addWidget(image)
        left_layout.addSpacing(20)
        left_layout.addWidget(headline)
        left_layout.addWidget(subtext)
        left_layout.addStretch()

        # Right Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setSpacing(20)

        welcome_label = QLabel("Welcome back!")
        welcome_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 42px; color: #000000;")
        welcome_label.setMinimumHeight(100)
        right_layout.addWidget(welcome_label)
        right_layout.addStretch()

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(50, 40, 50, 40)
        form_layout.setSpacing(15)

        title_label = QLabel("Login to your Account")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; color: #000000;")

        input_style = """
            QLineEdit {
                border: 1.5px solid black;
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #6C1D57;
                outline: none;
            }
        """

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet(input_style)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(input_style)

        remember_me = QCheckBox("Remember Me")
        remember_me.setStyleSheet("margin-left: 5px;")

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C1D57; color: white;
                border-radius: 5px; padding: 10px;
            }
            QPushButton:hover {
                background-color: #8B2F75;
            }
        """)
        login_btn.setFixedHeight(40)
        login_btn.clicked.connect(self.handle_login)

        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet("color: #6C1D57; border: none; background: transparent; text-align: left;")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setFixedWidth(150)

        create_acc_label = QLabel("Not Registered Yet?")
        create_acc_btn = QPushButton("Create an account")
        create_acc_btn.setStyleSheet("color: #6C1D57; border: none; background: transparent;")
        create_acc_btn.setCursor(Qt.PointingHandCursor)
        create_acc_btn.clicked.connect(self.open_signup)

        create_layout = QHBoxLayout()
        create_layout.addStretch()
        create_layout.addWidget(create_acc_label)
        create_layout.addWidget(create_acc_btn)
        create_layout.addStretch()

        form_layout.addWidget(title_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(remember_me)
        form_layout.addWidget(login_btn)
        form_layout.addWidget(forgot_btn, alignment=Qt.AlignRight)
        form_layout.addSpacing(20)
        form_layout.addLayout(create_layout)

        right_layout.addWidget(form_container)
        right_layout.addStretch()

        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 4)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please fill all fields.")
            return
        try:
            user = firebase_login(email, password)
            QMessageBox.information(self, "Success", "Login successful!")
            print("Logged in:", user["email"])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_signup(self):
        self.stack.setCurrentIndex(1)
