# hijri_calendar.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCalendarWidget
from PyQt5.QtCore import QDate
from hijridate import Gregorian

class HijriCalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Calendar UI
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)

        # Hijri date display
        self.hijri_label = QLabel()
        self.hijri_label.setStyleSheet("font-size: 14px; color: #333; padding: 4px;")
        layout.addWidget(self.hijri_label)

        self.calendar.selectionChanged.connect(self.update_hijri_date)
        self.update_hijri_date()

    def update_hijri_date(self):
        qdate = self.calendar.selectedDate()
        g_date = Gregorian(qdate.year(), qdate.month(), qdate.day())
        h_date = g_date.to_hijri()
        self.hijri_label.setText(f"🗓 Hijri: {h_date.day} {h_date.month_name()} {h_date.year} AH")
