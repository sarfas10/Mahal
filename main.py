# main.py
from PyQt5.QtWidgets import QApplication, QStackedWidget
from login_window import LoginWindow
from signup_window import SignupWindow
from dashboard import Dashboard
import sys

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.login_widget = LoginWindow(self)
        self.signup_widget = SignupWindow(self)
        self.dashboard = Dashboard(self)

        self.addWidget(self.login_widget)  # index 0
        self.addWidget(self.signup_widget)  # index 1
        self.addWidget(self.dashboard)  # index 2

        self.setCurrentIndex(2)  # 0 to start with login
        self.setWindowTitle("Mahal Management")
        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec_())
