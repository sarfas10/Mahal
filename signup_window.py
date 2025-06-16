# signup_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from firebase_api import firebase_register



class SignupWindow(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Signup")
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: white;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setStyleSheet("background-color: #FFEFE6;")
        left_widget.setMinimumWidth(600)

        image = QLabel()
        pixmap = QPixmap("skeleton.png")
        image.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
        image.setAlignment(Qt.AlignCenter)

        headline = QLabel("Join the community!")
        headline.setFont(QFont("Segoe UI", 18, QFont.Bold))
        headline.setAlignment(Qt.AlignCenter)

        subtext = QLabel("Create your account and start managing your events effortlessly.")
        subtext.setAlignment(Qt.AlignCenter)
        subtext.setWordWrap(True)

        left_layout.addStretch()
        left_layout.addWidget(image)
        left_layout.addSpacing(20)
        left_layout.addWidget(headline)
        left_layout.addWidget(subtext)
        left_layout.addStretch()

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setSpacing(20)

        welcome_label = QLabel("Create Account")
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

        title_label = QLabel("Sign up to continue")
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

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setFixedHeight(40)
        self.confirm_input.setStyleSheet(input_style)

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C1D57; color: white;
                border-radius: 5px; padding: 10px;
            }
            QPushButton:hover {
                background-color: #8B2F75;
            }
        """)
        register_btn.setFixedHeight(40)
        register_btn.clicked.connect(self.handle_signup)

        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet("color: #6C1D57; border: none; background: transparent;")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.back_to_login)

        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_layout.addWidget(back_btn)
        back_layout.addStretch()

        form_layout.addWidget(title_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_input)
        form_layout.addWidget(register_btn)
        form_layout.addSpacing(10)
        form_layout.addLayout(back_layout)

        right_layout.addWidget(form_container)
        right_layout.addStretch()

        main_layout.addWidget(left_widget, 6)
        main_layout.addWidget(right_widget, 4)

    def handle_signup(self):
        from login_window import LoginWindow
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not email or not password or not confirm:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Password Error", "Passwords do not match.")
            return

        try:
            firebase_register(email, password)
            QMessageBox.information(self, "Success", "Registration successful!")
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Registration Failed", str(e))

    def back_to_login(self):
        self.stack.setCurrentIndex(0)
