# hijri_calendar_custom.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QApplication, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
import sys
from hijridate import Hijri, Gregorian
import datetime

class DayLabel(QLabel):
    def __init__(self, day, is_today=False, is_important=False):
        super().__init__(str(day))
        self.day = day
        self.is_today = is_today
        self.is_important = is_important
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 12))
        self.setFixedSize(40, 40)
        self.update_style()

    def update_style(self):
        if self.is_today:
            self.setStyleSheet("""
                background-color: #7a60ff;
                color: white;
                border-radius: 20px;
            """)
        else:
            self.setStyleSheet("""
                color: #333;
                background-color: transparent;
            """)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_important:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            dot_color = QColor("#7a60ff")
            painter.setPen(Qt.NoPen)
            painter.setBrush(dot_color)
            painter.drawEllipse(int(self.width() / 2 - 2), int(self.height() - 6), 4, 4)

class HijriCalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f3f1fa; border-radius: 16px;")
        self.setMinimumSize(250, 250)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Top navigation + title
        self.header_layout = QHBoxLayout()
        self.prev_btn = QPushButton("‹")
        self.next_btn = QPushButton("›")
        for btn in (self.prev_btn, self.next_btn):
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("border: none; color: #7a60ff; font-size: 18px;")
        self.month_label = QLabel()
        self.month_label.setFont(QFont("Segoe UI", 14))
        self.month_label.setAlignment(Qt.AlignCenter)
        self.header_layout.addWidget(self.prev_btn)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.month_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.next_btn)
        self.layout.addLayout(self.header_layout)

        # Days of week row
        days_layout = QHBoxLayout()
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(40)
            label.setStyleSheet("color: #666; font-size: 12px;")
            days_layout.addWidget(label)
        self.layout.addLayout(days_layout)

        # Day cells grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(4)
        self.layout.addLayout(self.grid_layout)

        # Get current Hijri date
        today = datetime.date.today()
        self.hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
        self.selected_month = self.hijri_date.month
        self.selected_year = self.hijri_date.year

        self.important_days = [1, 12, 15, 27, 29]  # You can load from an API

        self.prev_btn.clicked.connect(self.prev_month)
        self.next_btn.clicked.connect(self.next_month)

        self.update_calendar()

    def update_calendar(self):
        # Clear previous labels
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Update title
        h = Hijri(self.selected_year, self.selected_month, 1)
        month_name = h.month_name("en")  # Use "ar" for Arabic
        self.month_label.setText(f"{month_name} {self.selected_year}")

        # Determine first day offset
        g = h.to_gregorian()
        weekday = datetime.date(g.year, g.month, g.day).weekday()  # 0 = Mon

        days_in_month = h.month_length()
        today_hijri = Gregorian(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day).to_hijri()

        row, col = 0, weekday
        for day in range(1, days_in_month + 1):
            is_today = (
                day == today_hijri.day and
                self.selected_month == today_hijri.month and
                self.selected_year == today_hijri.year
            )
            is_important = day in self.important_days
            label = DayLabel(day, is_today=is_today, is_important=is_important)
            self.grid_layout.addWidget(label, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def prev_month(self):
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        self.update_calendar()

    def next_month(self):
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        self.update_calendar()


# Run standalone for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HijriCalendarWidget()
    window.show()
    sys.exit(app.exec_())
