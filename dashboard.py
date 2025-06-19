from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QStackedWidget, QGridLayout, QPushButton
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
import sys
import requests

from services.rss_fetcher import fetch_islamic_rss
from services.hijri_calendar_custom import HijriCalendarWidget



class Dashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(1024, 600)
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: #f4f7fe;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_news)
        self.refresh_timer.start(300000)

    def create_nav_button(self, text, icon, is_active=False):
        btn = QPushButton(f"{icon}  {text}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(45)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#ffffff' if is_active else 'transparent'};
                color: {'#2d3748' if is_active else '#a0aec0'};
                border: none;
                border-radius: 12px;
                padding-left: 20px;
                text-align: left;
                font-weight: 500;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: #edf2f7;
                color: #2d3748;
            }}
        """)
        return btn

    def init_ui(self):
        self.content_widget = QWidget()
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #f4f7fe; border-right: 1px solid #e2e8f0;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 30, 20, 20)
        left_layout.setSpacing(15)

        title = QLabel("🏛️ Mahal Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3748; margin-bottom: 20px;")
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
        content_layout.addWidget(left_widget, stretch=2)

        # Center Panel
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_widget.setStyleSheet("background-color: #f4f7fe;")

        # Top Split Panel
        central_top = QWidget()
        central_top_layout = QHBoxLayout(central_top)
        central_top_layout.setContentsMargins(10, 0, 10, 10)
        central_top_layout.setSpacing(15)

        # Stats Panel
        stats_widget = QWidget()
        stats_main_layout = QVBoxLayout(stats_widget)
        stats_main_layout.setContentsMargins(10, 10, 10, 10)
        stats_main_layout.setSpacing(15)

        top_info_widget = QWidget()
        top_info_widget = QWidget()
        top_info_layout = QHBoxLayout(top_info_widget)
        top_info_layout.setContentsMargins(0, 0, 0, 0)
        top_info_layout.setSpacing(6)  # Small space between logo and text
        top_info_layout.setAlignment(Qt.AlignLeft)  # Ensure all items hug the left side

        # Logo on the left
        logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png")
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setFixedSize(100, 100)
        logo_label.setAlignment(Qt.AlignVCenter)

        # Arabic text next to logo (not right-aligned globally)
        name_label = QLabel("إرشاد الإسلام")
        name_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2d3748;
            font-family: 'Noto Sans Arabic', 'Amiri', 'Scheherazade', 'Segoe UI', 'Arial';
        """)
        name_label.setLayoutDirection(Qt.RightToLeft)
        name_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        name_label.setFixedHeight(100)  # Align with logo
        name_label.setContentsMargins(0, 0, 0, 0)

        # Add logo and name to layout (they'll stick to the left together)
        top_info_layout.addWidget(logo_label)
        top_info_layout.addWidget(name_label)


        bottom_stats_widget = QWidget()
        bottom_stats_layout = QGridLayout(bottom_stats_widget)
        bottom_stats_layout.setSpacing(15)

        stats = [
            ("📊 Total Sales", "$1k", "#FFE3E3"),
            ("📄 Total Order", "300", "#FFF6DA"),
            ("👨‍👩‍👧 Total Families", "235", "#E4F7D2"),
            ("🧍 Members", "1294", "#D6F0FF"),
            ("📅 Events", "4", "#F4E1FF"),
            ("📄 Requests", "12", "#FFEBDA"),
        ]

        for i, (label, value, bg_color) in enumerate(stats):
            card = QWidget()
            card.setFixedSize(210, 150)
            card.setStyleSheet(f"background-color: {bg_color}; border-radius: 18px;")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            card_layout.setSpacing(5)

            icon_label = QLabel(label.split()[0])
            icon_label.setStyleSheet("font-size: 24px;")
            card_layout.addWidget(icon_label)

            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1F1F1F;")
            card_layout.addWidget(value_label)

            subtitle_label = QLabel(" ".join(label.split()[1:]))
            subtitle_label.setStyleSheet("font-size: 13px; color: #5C5C5C;")
            card_layout.addWidget(subtitle_label)

            card_layout.addStretch()
            bottom_stats_layout.addWidget(card, i // 3, i % 3)

        stats_main_layout.addWidget(top_info_widget, stretch=1)
        stats_main_layout.addWidget(bottom_stats_widget, stretch=4)

 

# Outer calendar section with blue/light background
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        calendar_layout.setContentsMargins(10, 10, 10, 10)
        calendar_layout.setSpacing(0)
        calendar_widget.setStyleSheet("background-color: #f4f7fe;")  # Or your panel color

        # Inner white rounded square panel
        white_panel = QWidget()
        white_panel.setFixedSize(350, 380)
        white_panel.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
        """)

        # Calendar inside the white panel
        calendar = HijriCalendarWidget()
        calendar.setStyleSheet("background: transparent; border-radius: 16px;")  # Optional
        calendar_layout_inner = QVBoxLayout(white_panel)
        calendar_layout_inner.setContentsMargins(10, 10, 10, 10)
        calendar_layout_inner.setAlignment(Qt.AlignTop)
        calendar_layout_inner.addWidget(calendar)

        # Add some space at top of the calendar section
        calendar_layout.setAlignment(Qt.AlignTop)
        calendar_layout.addSpacing(10)
        calendar_layout.addWidget(white_panel, alignment=Qt.AlignTop)



        # Add to layout with stretch
        central_top_layout.addWidget(stats_widget, stretch=4)
        central_top_layout.addWidget(calendar_widget, stretch=2)


        # News Section
        self.central_bottom_container = QScrollArea()
        self.central_bottom_container.setWidgetResizable(True)
        self.central_bottom_container.setStyleSheet("""
            QScrollArea {
                background-color: #f4f7fe;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.central_bottom = QWidget()
        self.central_bottom.setStyleSheet("background-color: #f4f7fe;")
        self.central_bottom_layout = QVBoxLayout(self.central_bottom)
        self.central_bottom_layout.setContentsMargins(10, 10, 10, 10)
        self.central_bottom_layout.setSpacing(8)

        self.central_bottom_container.setWidget(self.central_bottom)

        # News wrapper with fixed heading
        news_wrapper = QWidget()
        news_wrapper_layout = QVBoxLayout(news_wrapper)
        news_wrapper_layout.setContentsMargins(10, 10, 10, 10)
        news_wrapper_layout.setSpacing(8)

        self.news_heading = QLabel("<h2 style='color:#D62828;'>📢 News Daily</h2>")
        self.news_heading.setStyleSheet("margin-bottom: 5px;")
        news_wrapper_layout.addWidget(self.news_heading)
        news_wrapper_layout.addWidget(self.central_bottom_container)

        center_layout.addWidget(central_top, stretch=4)
        center_layout.addWidget(news_wrapper, stretch=2)
        content_layout.addWidget(center_widget, stretch=6)

        # Right Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        right_widget.setStyleSheet("background-color: #E6F0FF;")
        right_layout.addWidget(QLabel("Right Panel"))
        content_layout.addWidget(right_widget, stretch=2)

        # Scroll Area for Main Layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(self.content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        self.load_news()

    def load_news(self):
        for i in reversed(range(self.central_bottom_layout.count())):
            widget = self.central_bottom_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        news_articles = fetch_islamic_rss()
        if news_articles:
            for article in news_articles[:15]:
                title = article.get("title", "No Title")
                description = article.get("description", "")
                url = article.get("url", "")
                image_url = article.get("image")

                article_widget = QWidget()
                article_layout = QVBoxLayout(article_widget)
                article_layout.setSpacing(8)
                article_layout.setContentsMargins(10, 10, 10, 10)

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
                            article_layout.addWidget(image_label)
                    except Exception as e:
                        print(f"Failed to load image: {image_url}\n{e}")

                html = f"""
                    <div style="margin-bottom: 12px;">
                        <span style="color:#D62828; font-weight:bold;">➔</span>
                        <b>{title}</b><br>
                        {description}<br>
                        <a href='{url}' style='color:#0077cc;'>Read more</a>
                    </div>
                """
                label = QLabel(html)
                label.setOpenExternalLinks(True)
                label.setWordWrap(True)
                article_layout.addWidget(label)

                self.central_bottom_layout.addWidget(article_widget)
        else:
            self.central_bottom_layout.addWidget(QLabel("Failed to load news."))



