from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QStackedWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt, QSize
import sys

class Dashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Dashboard")
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: white;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

    def init_ui(self):
        # Scrollable content widget
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Give the scrollable widget a reasonable minimum size
        content_widget.setMinimumWidth(1200)  # You can tweak this
        content_widget.setMinimumHeight(600)

        # LEFT PANEL
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_widget.setStyleSheet("background-color: #FFEFE6;")
        left_label = QLabel("Left Panel")
        left_layout.addWidget(left_label)
        content_layout.addWidget(left_widget, stretch=2)

        # CENTER PANEL
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_widget.setStyleSheet("background-color: #F4F4F4;")

        # Top Half
        central_top = QWidget()
        central_top.setStyleSheet("background-color: #DFFFD6;")
        central_top_layout = QVBoxLayout(central_top)
        central_top_layout.setContentsMargins(10, 10, 10, 10)
        central_top_label = QLabel("Central Top")
        central_top_layout.addWidget(central_top_label)

        # Bottom Half
        central_bottom = QWidget()
        central_bottom.setStyleSheet("background-color: #FFFAD6;")
        central_bottom_layout = QVBoxLayout(central_bottom)
        central_bottom_layout.setContentsMargins(10, 10, 10, 10)
        central_bottom_label = QLabel("Central Bottom")
        central_bottom_layout.addWidget(central_bottom_label)

        center_layout.addWidget(central_top, stretch=4)
        center_layout.addWidget(central_bottom, stretch=2)
        content_layout.addWidget(center_widget, stretch=6)

        # RIGHT PANEL
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_widget.setStyleSheet("background-color: #E6F0FF;")
        right_label = QLabel("Right Panel")
        right_layout.addWidget(right_label)
        content_layout.addWidget(right_widget, stretch=2)

        # SCROLL AREA
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(content_widget)

        # Set layout of the Dashboard
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stack = QStackedWidget()
    dashboard = Dashboard(stack)
    dashboard.show()
    sys.exit(app.exec_())
