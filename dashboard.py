from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QByteArray, QUrl
import requests
from io import BytesIO


from services.rss_fetcher import fetch_islamic_rss
import sys
from PyQt5.QtGui import QPixmap

class Dashboard(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(1024, 600)
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; background-color: white;")
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)

        # Auto-refresh every 5 minutes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_news)
        self.refresh_timer.start(300000)  # 5 minutes

    def init_ui(self):
        self.content_widget = QWidget()
        content_layout = QHBoxLayout(self.content_widget)
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
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_widget.setStyleSheet("background-color: #F4F4F4;")

        # Top Half
        central_top = QWidget()
        central_top_layout = QVBoxLayout(central_top)
        central_top_layout.setContentsMargins(10, 10, 10, 10)
        central_top_layout.setSpacing(10)
        central_top.setStyleSheet("background-color: #DFFFD6;")
        central_top_layout.addWidget(QLabel("Central Top"))

        # Bottom Half (News)
        self.central_bottom_container = QScrollArea()
        self.central_bottom_container.setWidgetResizable(True)
        self.central_bottom_container.setStyleSheet("""
            QScrollArea {
                background-color: #FFFAD6;
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
        self.central_bottom_layout = QVBoxLayout(self.central_bottom)
        self.central_bottom_layout.setContentsMargins(10, 10, 10, 10)
        self.central_bottom_layout.setSpacing(8)

        self.news_heading = QLabel("<h2 style='color:#D62828;'>📢 News Daily</h2>")
        self.news_heading.setStyleSheet("margin-bottom: 15px;")
        self.central_bottom_layout.addWidget(self.news_heading)

        self.central_bottom_container.setWidget(self.central_bottom)
        center_layout.addWidget(central_top, stretch=4)
        center_layout.addWidget(self.central_bottom_container, stretch=2)
        content_layout.addWidget(center_widget, stretch=6)

        # RIGHT PANEL
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        right_widget.setStyleSheet("background-color: #E6F0FF;")
        right_layout.addWidget(QLabel("Right Panel"))
        content_layout.addWidget(right_widget, stretch=2)

        # Main layout
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
    # Clear previous content
        for i in reversed(range(self.central_bottom_layout.count())):
            widget = self.central_bottom_layout.itemAt(i).widget()
            if widget is not None and widget != self.news_heading:
                widget.setParent(None)

    # Add heading again
        self.central_bottom_layout.addWidget(self.news_heading)

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

                # If image is available, show it
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

                # News text
                html = f"""
                    <div style="margin-bottom: 12px;">
                        <span style="color:#D62828; font-weight:bold;">➤</span>
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stack = QStackedWidget()
    dashboard = Dashboard(stack)
    dashboard.show()
    sys.exit(app.exec_())
