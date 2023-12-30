from PyQt6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QFont,
    QPixmap,
)
import requests
import re
import logging
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt

from jparty.style import MyLabel, CARDPAL
from jparty.constants import DEFAULT_CONFIG
from jparty.utils import get_base_path
import threading
import time

class QuestionWidget(QWidget):
    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.question = question
        self.setAutoFillBackground(True)
        self.main_layout = QVBoxLayout()

        # Read the config.json file
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        # Question text
        self.question_label = MyLabel(question.text.upper(), self.startFontSize, self)
        self.question_label.setFont(QFont("ITC_ Korinna"))
        self.main_layout.addWidget(self.question_label)
        self.main_layout.setContentsMargins(0, 50, 0, 50)

        if question.video_link is not None:
            logging.info(f"QUESTION HAS VIDEO, LOADING VIDEO: {question.video_link}")
            yt_regex = r'https:\/\/youtu\.be\/([a-zA-Z0-9\-_]+)\?.*t=([0-9]+)'
            yt_match = re.match(yt_regex, question.video_link)
            video_url = None
            if yt_match:
                yt_id = yt_match.group(1)
                yt_time = yt_match.group(2)
                video_url = f"video.html?v={yt_id}&t={yt_time}"
            else:
                yt_regex_no_time = r'https:\/\/youtu\.be\/([a-zA-Z0-9\-_]+)'
                yt_match_no_time = re.match(yt_regex_no_time, question.video_link)
                if yt_match_no_time:
                    yt_id = yt_match_no_time.group(1)
                    video_url = f"video.html?v={yt_id}"
            if video_url:
                # Embed youtube clip video
                self.web_view = QWebEngineView()
                url = f"http://localhost:8081/{video_url}"
                logging.info(f"loading url: {url}")
                self.web_view.load(QUrl(url))
                self.web_view.page().settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
                # Resize web_view to be half the height of the screen. Scale width relatively
                self.web_view.setFixedHeight(self.height() * 12)
                self.web_view.setFixedWidth(self.width() * 7)
                # Center the web_view horizontally and vertically
                self.main_layout.addWidget(self.web_view, alignment=Qt.AlignmentFlag.AlignCenter)

                # self.setLayout(self.main_layout)

                def end_video(main_layout, web_view):
                    time.sleep(10)
                    main_layout.removeWidget(web_view)
                    web_view.deleteLater()

                thread = threading.Thread(target=end_video, args=(self.main_layout, self.web_view,))
                thread.start()

        elif question.image_link is not None:
            logging.info(f"question has image: {question.image_link}")
            if question.image_content is None:
                try:
                    request = requests.get(question.image_link, timeout=1)
                    question.image_content = request.content
                    logging.info(f"loaded image: {question.image_link}")
                except requests.exceptions.RequestException as e:
                    logging.info(f"failed to load image: {question.image_link}")
            
            logging.info(f"question has image content: {question.image_content}")
            if question.image_content is not None and b"html" in question.image_content.lower():
                question.image_content = None

            disable_images = self.config.get('showtextwithimages', DEFAULT_CONFIG['showtextwithimages']) == 'Only show text'

            if not disable_images and question.image_content is not None and b"Not Found" not in question.image_content:
                self.image = QPixmap()
                self.image.loadFromData(question.image_content)
                
                if self.config.get('showtextwithimages', DEFAULT_CONFIG['showtextwithimages']) == 'Show both':
                    # Show both text and image
                    self.image = self.image.scaledToHeight(self.height() * 12)

                    # Create a QLabel for the image
                    self.image_label = MyLabel("", self.startFontSize, self)
                    self.image_label.setPixmap(self.image)
                    self.main_layout.addWidget(self.image_label)
                elif self.config.get('showtextwithimages', DEFAULT_CONFIG['showtextwithimages']) == 'Only show image':
                    # Show image only
                    self.image = self.image.scaledToWidth(self.width() * 12)
                    self.question_label.setPixmap(self.image)

        self.setLayout(self.main_layout)

        self.setPalette(CARDPAL)
        self.show()

    def startFontSize(self):
        return self.width() * 0.05


class HostQuestionWidget(QuestionWidget):
    def __init__(self, question, parent=None):
        super().__init__(question, parent)

        self.question_label.setText(question.text)
        self.main_layout.setStretchFactor(self.question_label, 6)
        self.main_layout.addSpacing(self.main_layout.contentsMargins().top())
        self.answer_label = MyLabel(question.answer, self.startFontSize, self)
        self.answer_label.setFont(QFont("ITC_ Korinna"))
        self.main_layout.addWidget(self.answer_label, 1)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(QColor("white")))
        line_y = self.main_layout.itemAt(1).geometry().top()
        qp.drawLine(0, line_y, self.width(), line_y)


class DailyDoubleWidget(QuestionWidget):
    def __init__(self, question, parent=None):
        super().__init__(question, parent)
        self.question_label.setVisible(False)
        if hasattr(self, 'image_label'):
            self.image_label.setVisible(False)

        self.dd_label = MyLabel("DAILY<br/>DOUBLE!", self.startDDFontSize, self)
        self.main_layout.replaceWidget(self.question_label, self.dd_label)

    def startDDFontSize(self):
        return self.width() * 0.2

    def show_question(self):
        self.main_layout.replaceWidget(self.dd_label, self.question_label)
        self.dd_label.deleteLater()
        self.dd_label = None
        self.question_label.setVisible(True)
        if hasattr(self, 'image_label'):
            self.image_label.setVisible(True)


class HostDailyDoubleWidget(HostQuestionWidget, DailyDoubleWidget):
    def __init__(self, question, parent=None):
        super().__init__(question, parent)
        self.answer_label.setVisible(False)

        self.main_layout.setStretchFactor(self.dd_label, 6)
        self.hint_label = MyLabel(
            "Click the player below who found the Daily Double",
            self.startFontSize,
            self,
        )
        self.main_layout.replaceWidget(self.answer_label, self.hint_label)
        self.main_layout.setStretchFactor(self.hint_label, 1)

    def show_question(self):
        super().show_question()
        self.main_layout.replaceWidget(self.hint_label, self.answer_label)
        self.hint_label.deleteLater()
        self.hint_label = None
        self.answer_label.setVisible(True)


class FinalJeopardyWidget(QuestionWidget):
    def __init__(self, question, parent=None):
        super().__init__(question, parent)
        self.question_label.setVisible(False)

        self.category_label = MyLabel(
            question.category, self.startCategoryFontSize, self
        )
        self.main_layout.replaceWidget(self.question_label, self.category_label)

    def startCategoryFontSize(self):
        return self.width() * 0.1

    def show_question(self):
        self.main_layout.replaceWidget(self.category_label, self.question_label)
        self.category_label.deleteLater()
        self.category_label = None
        self.question_label.setVisible(True)


class HostFinalJeopardyWidget(FinalJeopardyWidget, HostQuestionWidget):
    def __init__(self, question, parent):
        super().__init__(question, parent)
        self.answer_label.setVisible(False)

        self.main_layout.setStretchFactor(self.question_label, 6)
        self.hint_label = MyLabel(
            "Waiting for all players to wager...", self.startFontSize, self
        )
        self.main_layout.replaceWidget(self.answer_label, self.hint_label)
        self.main_layout.setStretchFactor(self.hint_label, 1)

    def hide_hint(self):
        self.hint_label.setVisible(True)

    def show_question(self):
        super().show_question()
        self.main_layout.replaceWidget(self.hint_label, self.answer_label)
        self.hint_label.deleteLater()
        self.hint_label = None
        self.answer_label.setVisible(True)
