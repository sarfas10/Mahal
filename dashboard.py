from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QStackedWidget, QGridLayout, QPushButton, QSizePolicy
)

from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
import sys
import requests

from services.rss_fetcher import fetch_islamic_rss
from services.hijri_calendar_custom import HijriCalendarWidget
from services.adhan_api import fetch_adhan_times

class NotificationItem:
    """Data class for notification items"""
    def __init__(self, title, message, timestamp, notification_type="info", is_read=False):
        self.title = title
        self.message = message
        self.timestamp = timestamp
        self.notification_type = notification_type  # "info", "warning", "success", "error"
        self.is_read = is_read
        self.id = id(self)  # Simple ID based on object identity


class NotificationWidget(QWidget):
    """Widget to display notifications with mark as read functionality"""
    
    def __init__(self):
        super().__init__()
        self.notifications = []
        self.setStyleSheet("background-color: transparent;")
        self.init_ui()
        self.load_sample_notifications()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(8)
        
        # Header with title and mark all as read button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # Title
        title = QLabel("🔔 Notifications")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #323130;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Mark all as read button
        self.mark_all_read_btn = QPushButton("Mark all as read")
        self.mark_all_read_btn.setFont(QFont("Segoe UI", 9))
        self.mark_all_read_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 212, 0.1);
                color: #0078d4;
                border: 1px solid rgba(0, 120, 212, 0.3);
                border-radius: 6px;
                padding: 4px 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 212, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 212, 0.3);
            }
        """)
        self.mark_all_read_btn.clicked.connect(self.mark_all_as_read)
        header_layout.addWidget(self.mark_all_read_btn)
        
        self.layout.addLayout(header_layout)
        
        # Scroll area for notifications
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.15);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(6)
        
        self.scroll_area.setWidget(self.notifications_widget)
        self.layout.addWidget(self.scroll_area)
        
    def load_sample_notifications(self):
        """Load sample notifications for demonstration"""
        sample_notifications = [
            NotificationItem(
                "New Member Registration",
                "Ahmad Hassan has registered as a new member",
                datetime.now() - timedelta(minutes=5),
                "success"
            ),
            NotificationItem(
                "Payment Received",
                "Monthly contribution received from Family ID: 1234",
                datetime.now() - timedelta(hours=2),
                "info"
            ),
            NotificationItem(
                "Upcoming Event",
                "Quran recitation competition tomorrow at 7 PM",
                datetime.now() - timedelta(hours=4),
                "warning"
            ),
            NotificationItem(
                "Maintenance Alert",
                "Water tank cleaning scheduled for this Friday",
                datetime.now() - timedelta(days=1),
                "info"
            ),
            NotificationItem(
                "Document Expiry",
                "Certificate renewal required for 3 members",
                datetime.now() - timedelta(days=2),
                "error"
            ),
            NotificationItem(
                "Meeting Reminder",
                "Monthly committee meeting on Sunday at 10 AM",
                datetime.now() - timedelta(days=3),
                "warning"
            ),
            NotificationItem(
                "Donation Received",
                "Zakat donation of $500 received from anonymous donor",
                datetime.now() - timedelta(days=4),
                "success",
                True  # This one is read
            ),
            NotificationItem(
                "System Update",
                "Management system updated to version 2.1.0",
                datetime.now() - timedelta(days=5),
                "info",
                True  # This one is read
            ),
        ]
        
        self.notifications = sample_notifications
        self.update_notifications_display()
        
    def update_notifications_display(self):
        """Update the notifications display"""
        # Clear existing items
        for i in reversed(range(self.notifications_layout.count())):
            widget = self.notifications_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        if not self.notifications:
            no_notifications = QLabel("No notifications")
            no_notifications.setStyleSheet("color: #605e5c; font-style: italic; padding: 20px;")
            no_notifications.setAlignment(Qt.AlignCenter)
            self.notifications_layout.addWidget(no_notifications)
            return
        
        # Sort notifications by timestamp (newest first)
        sorted_notifications = sorted(self.notifications, key=lambda x: x.timestamp, reverse=True)
        
        for notification in sorted_notifications:
            notification_widget = self.create_notification_widget(notification)
            self.notifications_layout.addWidget(notification_widget)
        
        # Add stretch to push items to top
        self.notifications_layout.addStretch()
        
        # Update button state
        unread_count = sum(1 for n in self.notifications if not n.is_read)
        self.mark_all_read_btn.setEnabled(unread_count > 0)
        
    def create_notification_widget(self, notification):
        """Create a widget for a single notification"""
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Different opacity for read/unread
        opacity = "0.6" if notification.is_read else "1.0"
        border_left = self.get_notification_color(notification.notification_type)
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 255, 255, {opacity});
                border-radius: 8px;
                border-left: 3px solid {border_left};
                margin: 1px;
            }}
            QWidget:hover {{
                background-color: rgba(255, 255, 255, 1.0);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Header with icon, title, and timestamp
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        # Icon and title
        
        title_text = f" {notification.title}"
        if not notification.is_read:
            title_text += " •"  # Unread indicator
            
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {'#323130' if not notification.is_read else '#605e5c'};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Timestamp
        time_str = self.format_timestamp(notification.timestamp)
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: #605e5c;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(notification.message)
        message_label.setFont(QFont("Segoe UI", 9))
        message_label.setStyleSheet(f"color: {'#323130' if not notification.is_read else '#605e5c'}; padding-left: 20px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        outer_layout.addWidget(card)
        # Click to mark as read
        if not notification.is_read:
            outer.mousePressEvent = lambda event, n=notification: self.mark_as_read(n)
            outer.setCursor(Qt.PointingHandCursor)
        
        return outer
    
    
    
    def get_notification_color(self, notification_type):
        """Get color for notification type"""
        colors = {
            "info": "#0078d4",
            "success": "#107c10",
            "warning": "#ff8c00",
            "error": "#d13438"
        }
        return colors.get(notification_type, "#0078d4")
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def mark_as_read(self, notification):
        """Mark a single notification as read"""
        notification.is_read = True
        self.update_notifications_display()
    
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification.is_read = True
        self.update_notifications_display()
    
    def add_notification(self, notification):
        """Add a new notification"""
        self.notifications.append(notification)
        self.update_notifications_display()



class ImportantDatesDisplay(QWidget):
    """Widget to display important dates for the current month"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(3)  # Reduced from 5 to 3
        
        # Title
        title = QLabel("📅 Important Dates")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #323130; margin-bottom: 3px;")  # Reduced from 5px to 3px
        self.layout.addWidget(title)
        
        # Scroll area for dates
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.15);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.dates_widget = QWidget()
        self.dates_layout = QVBoxLayout(self.dates_widget)
        self.dates_layout.setContentsMargins(0, 0, 0, 0)
        self.dates_layout.setSpacing(2)  # Reduced from 3 to 2
        
        self.scroll_area.setWidget(self.dates_widget)
        self.layout.addWidget(self.scroll_area)
        
    def update_dates(self, important_dates, month_name):
        """Update the display with new important dates"""
        # Clear existing items
        for i in reversed(range(self.dates_layout.count())):
            widget = self.dates_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        if not important_dates:
            no_events = QLabel("No special events this month")
            no_events.setStyleSheet("color: #605e5c; font-style: italic; padding: 10px;")
            no_events.setAlignment(Qt.AlignCenter)
            self.dates_layout.addWidget(no_events)
            return
        
        # Sort dates by day
        sorted_dates = sorted(important_dates.items())
        
        for day, events in sorted_dates:
            date_widget = self.create_date_widget(day, events, month_name)
            self.dates_layout.addWidget(date_widget)
        
        # Add stretch to push items to top
        self.dates_layout.addStretch()
    
    def create_date_widget(self, day, events, month_name):
        """Create a widget for a single date with its events"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 1);
                border-radius: 8px;
                margin: 1px;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 1);
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)  # Reduced vertical margins from 6 to 4
        layout.setSpacing(1)  # Reduced from 2 to 1
        
        # Date header
        date_label = QLabel(f"{day} {month_name}")
        date_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        date_label.setStyleSheet("color: #323130;")
        layout.addWidget(date_label)
        
        # Events
        for event in events:
            event_label = QLabel(f"• {event}")
            event_label.setFont(QFont("Segoe UI", 9))
            
            # Color code events
            if any(word in event.lower() for word in ['eid', 'عيد']):
                color = "#d13438"  # Red for Eid
            elif any(word in event.lower() for word in ['ramadan', 'رمضان', 'laylat', 'ليلة']):
                color = "#107c10"  # Green for Ramadan/special nights
            elif any(word in event.lower() for word in ['mawlid', 'مولد']):
                color = "#0078d4"  # Blue for Mawlid
            elif any(word in event.lower() for word in ['ashura', 'عاشوراء']):
                color = "#8764b8"  # Purple for Ashura
            elif any(word in event.lower() for word in ['jummah', 'جمعة', 'friday']):
                color = "#107c10"  # Green for Jummah
            else:
                color = "#605e5c"  # Gray for other events
            
            event_label.setStyleSheet(f"color: {color}; padding-left: 5px;")
            event_label.setWordWrap(True)
            layout.addWidget(event_label)
        
        return widget


class EnhancedHijriCalendarWidget(HijriCalendarWidget):
    """Enhanced calendar widget that emits signals when dates change"""
    dates_updated = pyqtSignal(dict, str)  # important_dates, month_name
    
    def __init__(self):
        super().__init__()
        
    def on_important_dates_loaded(self, important_dates):
        """Override to emit signal when dates are loaded"""
        super().on_important_dates_loaded(important_dates)
        # Get current month name
        from hijridate import Hijri
        h = Hijri(self.selected_year, self.selected_month, 1)
        month_name = h.month_name("en")
        # Emit signal with dates and month name
        self.dates_updated.emit(important_dates, month_name)
    
    def update_calendar(self):
        """Override to emit signal when calendar updates"""
        super().update_calendar()
        # Emit signal even if dates haven't changed
        from hijridate import Hijri
        h = Hijri(self.selected_year, self.selected_month, 1)
        month_name = h.month_name("en")
        self.dates_updated.emit(self.important_dates, month_name)


class AdhanTimesRow(QWidget):
    """Widget to display Adhan times in a horizontal row"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 0, 0, 0)
        self.layout.setSpacing(25)  # Reduced from 12 to 8
        
        # Get adhan times
        adhan_times = fetch_adhan_times()
        next_prayer = 'Asr'  # TODO: Replace with dynamic logic
        
        icons = {
            "Fajr": "🌅",
            "Dhuhr": "☀️",
            "Asr": "🌇",
            "Maghrib": "🌆",
            "Isha": "🌌",
        }
        
        for prayer, time in adhan_times.items():
            is_next = (prayer == next_prayer)
            card = self.create_adhan_card(prayer, time, icons.get(prayer, "🕋"), is_next)
            self.layout.addWidget(card)
        
        self.layout.addStretch()
    
    def create_adhan_card(self, prayer, time, icon, is_next):
        """Create a single adhan time card"""
        card = QWidget()
        card.setFixedSize(140, 80)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {'rgba(0, 120, 212, 0.1)' if is_next else 'rgba(255, 255, 255, 0.9)'};
                border-radius: 12px;
            }}
            QWidget:hover {{
                background-color: {'rgba(0, 120, 212, 0.15)' if is_next else 'rgba(255, 255, 255, 1.0)'};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        # Icon and prayer name
        top_layout = QHBoxLayout()
        top_layout.setSpacing(4)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 12))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")
        
        name_label = QLabel(prayer)
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        name_label.setStyleSheet("color: #323130;background-color: transparent;")
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(name_label)
        top_layout.addStretch()
        
        # Time
        time_label = QLabel(time)
        time_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        time_label.setStyleSheet(f"""
            color: {'#0078d4' if is_next else '#323130'};
            padding: 2px 6px;
            border-radius: 6px;
            background-color: transparent;
        """)
        time_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(top_layout)
        layout.addWidget(time_label)
        layout.addStretch()
        
        return card

class Dashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(1024, 800)
        # Windows 11 theme colors
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
                background-color: #fafafa;
                color: #323130;
            }
        """)
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_news)
        self.refresh_timer.start(300000)

    def create_nav_button(self, text, icon, is_active=False):
        btn = QPushButton(f"{icon}  {text}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(48)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'rgba(255, 255, 255, 0.9)' if is_active else 'transparent'};
                color: {'#323130' if is_active else '#605e5c'};
                border-radius: 8px;
                padding-left: 16px;
                text-align: left;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.8);
                color: #323130;
            }}
        """)
        return btn

    def init_ui(self):
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top horizontal layout: Sidebar + Main Left Panel + Calendar Right Panel
        top_horizontal_layout = QHBoxLayout()
        top_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        top_horizontal_layout.setSpacing(0)

        # Sidebar
        left_widget = QWidget()
        left_widget.setFixedWidth(300)
        left_widget.setStyleSheet("""
            background-color: #f3f2f1;
            border-right: 1px solid #e1dfdd;
        """)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 24, 20, 20)
        left_layout.setSpacing(12)

        title = QLabel("🏛️ Mahal Management")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #323130;
            margin-bottom: 16px;
        """)
        left_layout.addWidget(title)

        menu_items = [
            ("Admin Panel", "🛠️", True),
            ("Finance Tracking", "💰", False),
            ("Member Management", "👥", False),
            ("Asset Management", "📦", False),
            ("Academics", "🎓", False),
            ("Certificate Management", "📜", False),
        ]

        for label, icon, active in menu_items:
            btn = self.create_nav_button(label, icon, active)
            left_layout.addWidget(btn)

        left_layout.addStretch()
        top_horizontal_layout.addWidget(left_widget)

        # Main Left Panel (Logo, Title, Adhan Times, Stats)
        main_left_panel = QWidget()
        main_left_layout = QVBoxLayout(main_left_panel)
        main_left_layout.setContentsMargins(24, 24, 24, 24)
        main_left_layout.setSpacing(16)
        main_left_panel.setStyleSheet("background-color: #fafafa;")

        # Logo and Name Row
        logo_name_widget = QWidget()
        logo_name_layout = QHBoxLayout(logo_name_widget)
        logo_name_layout.setContentsMargins(0, 0, 0, 0)
        logo_name_layout.setSpacing(16)
        logo_name_layout.setAlignment(Qt.AlignLeft)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setFixedSize(80, 80)
        logo_label.setAlignment(Qt.AlignVCenter)

        # Arabic text
        name_label = QLabel("إرشاد الإسلام")
        name_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #323130;
            font-family: 'Noto Sans Arabic', 'Amiri', 'Scheherazade', 'Segoe UI', 'Arial';
        """)
        name_label.setLayoutDirection(Qt.RightToLeft)
        name_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        name_label.setFixedHeight(80)

        logo_name_layout.addWidget(logo_label)
        logo_name_layout.addWidget(name_label)
        logo_name_layout.addStretch()

        # Adhan Times Section
        adhan_section = QWidget()
        adhan_section_layout = QVBoxLayout(adhan_section)
        adhan_section_layout.setContentsMargins(0, 0, 0, 0)
        adhan_section_layout.setSpacing(8)

        
        self.adhan_times_widget = AdhanTimesRow()
        adhan_section_layout.addWidget(self.adhan_times_widget)

        # Stats Section
        stats_section = QWidget()
        stats_section_layout = QVBoxLayout(stats_section)
        stats_section_layout.setContentsMargins(0, 0, 0, 0)
        stats_section_layout.setSpacing(8)

        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(12)

        stats = [
            ("📊 Total Sales", "$1k"),
            ("📄 Total Order", "300"),
            ("👨‍👩‍👧 Total Families", "235"),
            ("🧍 Members", "1294"),
            ("📅 Events", "4"),
            ("📄 Requests", "12"),
        ]

        for i, (label, value) in enumerate(stats):
            card = QWidget()
            card.setObjectName("statCard")
            card.setFixedSize(180, 110)
            card.setStyleSheet(f"""
                QWidget#statCard {{
                    background-color: #ace6f5;
                    border-radius: 12px;
                }}
                QWidget {{
                    background-color: #ace6f5;
                  
                    
                }}
                
            """)


            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            card_layout.setSpacing(4)

            icon_label = QLabel(label.split()[0])
            icon_label.setStyleSheet("font-size: 18px;")
            card_layout.addWidget(icon_label)

            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #323130;")
            card_layout.addWidget(value_label)

            subtitle_label = QLabel(" ".join(label.split()[1:]))
            subtitle_label.setStyleSheet("font-size: 11px; color: #605e5c;")
            card_layout.addWidget(subtitle_label)

            card_layout.addStretch()
            stats_layout.addWidget(card, i // 3, i % 3)

        
        stats_section_layout.addWidget(stats_widget)

        # Add all sections to main left panel
        main_left_layout.addWidget(logo_name_widget)
        main_left_layout.addWidget(adhan_section)
        main_left_layout.addWidget(stats_section)
        main_left_layout.addStretch()

        # Calendar Right Panel
        calendar_panel = QWidget()
        calendar_panel.setFixedWidth(380)
        calendar_panel.setStyleSheet("""
            background-color: #fafafa;
            
        """)
        calendar_layout = QVBoxLayout(calendar_panel)
        calendar_layout.setContentsMargins(24, 24, 24, 24)
        calendar_layout.setSpacing(0)

        # White panel container for calendar
        white_panel = QWidget()
        white_panel.setStyleSheet("""
            background-color: #ace6f5;
            border-radius: 12px;
        """)

        # Layout for calendar and events inside white panel
        calendar_layout_inner = QVBoxLayout(white_panel)
        calendar_layout_inner.setContentsMargins(16, 16, 16, 16)
        calendar_layout_inner.setSpacing(8)

        # Enhanced Calendar
        self.calendar = EnhancedHijriCalendarWidget()
        self.calendar.setStyleSheet("background: transparent; border-radius: 8px;")
        self.calendar.setMaximumHeight(300)
        calendar_layout_inner.addWidget(self.calendar)

        # Important Dates Display
        self.important_dates_display = ImportantDatesDisplay()
        calendar_layout_inner.addWidget(self.important_dates_display, stretch=1)

        # Connect calendar to dates display
        self.calendar.dates_updated.connect(self.important_dates_display.update_dates)

        calendar_layout.addWidget(white_panel, stretch=1)




        # Add panels to top horizontal layout
        top_horizontal_layout.addWidget(main_left_panel, stretch=1)
        top_horizontal_layout.addWidget(calendar_panel)

# === Notifications Panel ===
        notification_panel = QWidget()
        notification_panel.setObjectName("NotificationPanel")
        notification_panel.setFixedWidth(380)
        notification_panel.setStyleSheet("""
            QWidget#NotificationPanel {
                background-color: #ffffff;
                border: 3 solid #769ea8;
                border-radius: 0px;
            }
        """)

        notification_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        notification_layout = QVBoxLayout(notification_panel)
        notification_layout.setContentsMargins(16, 16, 16, 16)
        notification_layout.setSpacing(8)

        self.notification_widget = NotificationWidget()
        notification_panel.setFixedHeight(calendar_panel.height())
        notification_layout.addWidget(self.notification_widget)


        top_horizontal_layout.addWidget(notification_panel)


        # News Section (Full Width but respecting sidebar)
        news_section = QWidget()
        news_section.setStyleSheet("background-color: #fafafa;")
        news_section_layout = QHBoxLayout(news_section)
        news_section_layout.setContentsMargins(0, 0, 0, 0)
        news_section_layout.setSpacing(0)
        
        # Add spacer for sidebar width
        sidebar_spacer = QWidget()
        sidebar_spacer.setFixedWidth(300)  # Same width as sidebar
        sidebar_spacer.setStyleSheet("background-color: #f3f2f1; border-right: 1px solid #e1dfdd;")
        news_section_layout.addWidget(sidebar_spacer)
        
        # News content area
        news_content = QWidget()
        news_content_layout = QVBoxLayout(news_content)
        news_content_layout.setContentsMargins(24, 0, 24, 24)
        news_content_layout.setSpacing(8)

        # News heading
        self.news_heading = QLabel("📢 News Daily")
        self.news_heading.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #323130;
            margin-bottom: 6px;
        """)
        news_content_layout.addWidget(self.news_heading)

        # News scroll area
        self.news_scroll_area = QScrollArea()
        self.news_scroll_area.setWidgetResizable(True)
        self.news_scroll_area.setMinimumHeight(400)
        self.news_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.05);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.news_container = QWidget()
        self.news_container.setStyleSheet("background-color: transparent;")
        self.news_layout = QVBoxLayout(self.news_container)
        self.news_layout.setContentsMargins(0, 0, 0, 0)
        self.news_layout.setSpacing(8)

        self.news_scroll_area.setWidget(self.news_container)
        news_content_layout.addWidget(self.news_scroll_area)
        
        # Add news content to news section
        news_section_layout.addWidget(news_content)

        # Add sections to main layout
        content_layout.addLayout(top_horizontal_layout, stretch=4)
        content_layout.addWidget(news_section, stretch=1)

        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(self.content_widget)

        main_layout_outer = QVBoxLayout(self)
        main_layout_outer.setContentsMargins(0, 0, 0, 0)
        main_layout_outer.addWidget(scroll_area)

        self.load_news()

    def load_news(self):
        # Clear existing news items
        for i in reversed(range(self.news_layout.count())):
            widget = self.news_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        news_articles = fetch_islamic_rss()
        if news_articles:
            for article in news_articles[:12]:
                title = article.get("title", "No Title")
                description = article.get("description", "")
                url = article.get("url", "")
                image_url = article.get("image")

                article_widget = QWidget()
                article_widget.setStyleSheet("""
                    QWidget {
                        background-color: rgba(255, 255, 255, 0.9);
                        border-radius: 12px;
                        padding: 16px;
                    }
                    QWidget:hover {
                        background-color: rgba(255, 255, 255, 1.0);
                    }
                """)
                article_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
                
                article_layout = QVBoxLayout(article_widget)
                article_layout.setSpacing(6)
                article_layout.setContentsMargins(16, 12, 16, 12)

                if image_url:
                    try:
                        response = requests.get(image_url, timeout=5)
                        if response.status_code == 200:
                            pixmap = QPixmap()
                            pixmap.loadFromData(response.content)
                            pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
                            image_label = QLabel()
                            image_label.setPixmap(pixmap)
                            image_label.setAlignment(Qt.AlignCenter)
                            image_label.setStyleSheet("border-radius: 8px;")
                            article_layout.addWidget(image_label)
                    except Exception as e:
                        print(f"Failed to load image: {image_url}\n{e}")

                html = f"""
                    <div style="margin-bottom: 8px;">
                        <h3 style="color: #323130; margin-bottom: 6px; font-weight: 600;">{title}</h3>
                        <p style="color: #605e5c; margin-bottom: 6px; line-height: 1.4;">{description}</p>
                        <a href='{url}' style='color: #0078d4; text-decoration: none; font-weight: 500;'>Read more →</a>
                    </div>
                """
                label = QLabel(html)
                label.setOpenExternalLinks(True)
                label.setWordWrap(True)
                article_layout.addWidget(label)

                self.news_layout.addWidget(article_widget)
        else:
            error_label = QLabel("Failed to load news.")
            error_label.setStyleSheet("color: #605e5c; font-style: italic; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            self.news_layout.addWidget(error_label)