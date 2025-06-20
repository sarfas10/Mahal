# hijri_calendar_dynamic.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QApplication, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
import sys
from hijridate import Hijri, Gregorian
import datetime
import requests
import json
from typing import List, Dict, Set


class ImportantDatesLoader(QThread):
    """Thread for loading important dates to avoid blocking UI"""
    dates_loaded = pyqtSignal(dict)
    
    
    def __init__(self, year, month):
        super().__init__()
        self.year = year
        self.month = month
    
    def run(self):
        """Load important dates from multiple sources"""
        important_dates = {}
        
        # Method 1: Load from Islamic calendar API
        try:
            api_dates = self.fetch_from_api(self.year, self.month)
            important_dates.update(api_dates)
        except Exception as e:
            print(f"API fetch failed: {e}")
        
        # Method 2: Load predefined important dates
        predefined_dates = self.get_predefined_dates(self.year, self.month)
        important_dates.update(predefined_dates)
        
        # Method 3: Calculate astronomical events
        astronomical_dates = self.calculate_astronomical_events(self.year, self.month)
        important_dates.update(astronomical_dates)
        
        self.dates_loaded.emit(important_dates)
    
    def fetch_from_api(self, year: int, month: int) -> Dict[int, List[str]]:
        """Fetch important dates from Islamic calendar API"""
        important_dates = {}
        
        # Using Aladhan API for Islamic calendar events
        try:
            # Get the Gregorian equivalent to fetch events
            hijri_start = Hijri(year, month, 1)
            greg_start = hijri_start.to_gregorian()
            
            # Fetch events for the month
            url = f"http://api.aladhan.com/v1/calendar/{greg_start.year}/{greg_start.month}"
            params = {
                'method': 2,  # ISNA method
                'adjustment': 0
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                for day_data in data.get('data', []):
                    hijri_info = day_data.get('date', {}).get('hijri', {})
                    greg_info = day_data.get('date', {}).get('gregorian', {})
                    
                    if hijri_info.get('month', {}).get('number') == month:
                        day = int(hijri_info.get('day', 0))
                        
                        # Check for special events
                        events = []
                        
                        # Prayer times indicate important days
                        if day_data.get('timings'):
                            # Check for Friday (Jummah)
                            if greg_info.get('weekday', {}).get('en') == 'Friday':
                                events.append('Jummah')
                        
                        # Add holidays if mentioned
                        hijri_holidays = hijri_info.get('holidays', [])
                        if hijri_holidays:
                            events.extend(hijri_holidays)
                        
                        if events:
                            important_dates[day] = events
                            
        except Exception as e:
            print(f"API error: {e}")
            
        return important_dates
    
    def get_predefined_dates(self, year: int, month: int) -> Dict[int, List[str]]:
        """Get predefined important Islamic dates"""
        important_dates = {}
        
        # Important dates by month (Hijri calendar)
        monthly_events = {
            1: {  # Muharram
                1: ["New Year"],
                10: ["Ashura"],
                11: ["Day after Ashura"]
            },
            2: {  # Safar
                # Usually no major events, but can add regional ones
            },
            3: {  # Rabi' al-Awwal
                12: ["Mawlid al-Nabi (Sunni)"],
                17: ["Mawlid al-Nabi (Shia)"]
            },
            4: {  # Rabi' al-Thani
                # Add any regional events
            },
            5: {  # Jumada al-Awwal
                # Add any regional events
            },
            6: {  # Jumada al-Thani
                # Add any regional events
            },
            7: {  # Rajab
                27: ["Isra and Mi'raj"]
            },
            8: {  # Sha'ban
                15: ["Laylat al-Bara'ah"]
            },
            9: {  # Ramadan
                1: ["Start of Ramadan"],
                21: ["Laylat al-Qadr (possible)"],
                23: ["Laylat al-Qadr (possible)"],
                25: ["Laylat al-Qadr (possible)"],
                27: ["Laylat al-Qadr (most likely)"],
                29: ["Laylat al-Qadr (possible)"]
            },
            10: {  # Shawwal
                1: ["Eid al-Fitr"]
            },
            11: {  # Dhu al-Qi'dah
                # Hajj preparation month
            },
            12: {  # Dhu al-Hijjah
                8: ["Hajj begins"],
                9: ["Day of Arafah"],
                10: ["Eid al-Adha"],
                11: ["Eid al-Adha (2nd day)"],
                12: ["Eid al-Adha (3rd day)"],
                13: ["Eid al-Adha (4th day)"]
            }
        }
        
        if month in monthly_events:
            for day, events in monthly_events[month].items():
                important_dates[day] = events
        
        return important_dates
    
    def calculate_astronomical_events(self, year: int, month: int) -> Dict[int, List[str]]:
        """Calculate astronomical events like new moons, full moons"""
        important_dates = {}
        
        # For simplicity, marking approximate dates
        # In a real implementation, you'd use astronomical calculations
        
        # New moon is typically around day 1 of Hijri month
        important_dates[1] = important_dates.get(1, []) + ["New Moon"]
        
        # Full moon is typically around day 14-15 of Hijri month
        full_moon_day = 14
        important_dates[full_moon_day] = important_dates.get(full_moon_day, []) + ["Full Moon"]
        
        return important_dates

class DayLabel(QLabel):
    def __init__(self, day, is_today=False, events=None):
        super().__init__(str(day))
        self.day = day
        self.is_today = is_today
        self.events = events or []
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 12))
        self.setFixedSize(40, 40)
        self.update_style()
        
        # Set tooltip for events
        
        

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
        if self.events:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Different colors for different types of events
            if any("Eid" in event for event in self.events):
                dot_color = QColor("#ff6b6b")  # Red for Eid
            elif any("Ramadan" in event or "Laylat" in event for event in self.events):
                dot_color = QColor("#4ecdc4")  # Teal for Ramadan/Night events
            elif any("Mawlid" in event for event in self.events):
                dot_color = QColor("#45b7d1")  # Blue for Mawlid
            else:
                dot_color = QColor("#7a60ff")  # Purple for other events
            
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

        self.important_dates = {}  # Will be populated dynamically
        self.loader_thread = None

        self.prev_btn.clicked.connect(self.prev_month)
        self.next_btn.clicked.connect(self.next_month)

        self.load_important_dates()

    def load_important_dates(self):
        """Load important dates for current month"""
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.terminate()
        
        self.loader_thread = ImportantDatesLoader(self.selected_year, self.selected_month)
        self.loader_thread.dates_loaded.connect(self.on_important_dates_loaded)
        self.loader_thread.start()
        
        # Update calendar with current data (if any)
        self.update_calendar()

    def on_important_dates_loaded(self, important_dates):
        """Handle loaded important dates"""
        self.important_dates = important_dates
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
            events = self.important_dates.get(day, [])
            label = DayLabel(day, is_today=is_today, events=events)
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
        self.load_important_dates()

    def next_month(self):
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        self.load_important_dates()


