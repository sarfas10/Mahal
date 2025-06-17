from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt
from services.news_fetcher import fetch_islamic_news
from services.rss_fetcher import fetch_islamic_rss

import sys

class Dashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(1024, 600)
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: white;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

    def init_ui(self):
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # LEFT PANEL
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)
        left_widget.setStyleSheet("background-color: #FFEFE6;")
        left_layout.addWidget(QLabel("Left Panel"))
        content_layout.addWidget(left_widget, stretch=2)

        # CENTER PANEL
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)  # No outside margin
        center_layout.setSpacing(0)
        center_widget.setStyleSheet("background-color: #F4F4F4;")

        # Top Half
        central_top = QWidget()
        central_top_layout = QVBoxLayout(central_top)
        central_top_layout.setContentsMargins(10, 10, 10, 10)
        central_top_layout.setSpacing(10)
        central_top.setStyleSheet("background-color: #DFFFD6;")
        central_top_layout.addWidget(QLabel("Central Top"))

        # Bottom Half (Scrollable)
        central_bottom_container = QScrollArea()
        central_bottom_container.setWidgetResizable(True)
        central_bottom_container.setStyleSheet("background-color: #FFFAD6;")

        central_bottom = QWidget()
        central_bottom_layout = QVBoxLayout(central_bottom)
        central_bottom_layout.setContentsMargins(10, 10, 10, 10)
        central_bottom_layout.setSpacing(8)


        news_articles = fetch_islamic_rss()

        if news_articles:
            for article in news_articles[:15]:  # Display up to 15 articles
                title = article.get("title", "No Title")
                description = article.get("description", "")
                url = article.get("url", "")
        
                news_label = QLabel(f"<b>{title}</b><br>{description}<br><a href='{url}' style='color:blue;'>Read more</a>")
                news_label.setOpenExternalLinks(True)
                news_label.setWordWrap(True)
                central_bottom_layout.addWidget(news_label)
        else:
            central_bottom_layout.addWidget(QLabel("Failed to load news."))



        central_bottom_container.setWidget(central_bottom)

        # Assemble center panel
        center_layout.addWidget(central_top, stretch=4)
        center_layout.addWidget(central_bottom_container, stretch=2)
        content_layout.addWidget(center_widget, stretch=6)

        # RIGHT PANEL
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        right_widget.setStyleSheet("background-color: #E6F0FF;")
        right_layout.addWidget(QLabel("Right Panel"))
        content_layout.addWidget(right_widget, stretch=2)

        # Wrap everything in an outer scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stack = QStackedWidget()
    dashboard = Dashboard(stack)
    dashboard.show()
    sys.exit(app.exec_())
