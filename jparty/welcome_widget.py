from PyQt6.QtGui import (
    QPainter,
    QBrush,
    QImage,
    QFont,
    QPalette,
    QPixmap,
    QColor, 
)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QMessageBox,
    QLabel,
    QDialog,
    QComboBox,
    QPushButton,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal

import qrcode
import time
from threading import Thread
import logging
import json
import os
import sys

from jparty.version import version
from jparty.retrieve import get_game, get_random_game
from jparty.utils import resource_path, add_shadow, DynamicLabel, DynamicButton
from jparty.helpmsg import helpmsg
from jparty.style import WINDOWPAL
from jparty.constants import DEFAULT_CONFIG


class Image(qrcode.image.base.BaseImage):
    """QR code image widget"""

    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QImage(size, size, QImage.Format.Format_RGB16)
        self._image.fill(WINDOWPAL.color(QPalette.ColorRole.Window))

    def pixmap(self):
        return QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size,
            self.box_size,
            Qt.GlobalColor.black,
        )

    def save(self, stream, kind=None):
        pass


class StartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QPixmap(resource_path("icon.png"))
        self.icon_label = DynamicLabel("", 0, self)

        add_shadow(self, radius=0.2)
        self.setPalette(WINDOWPAL)

        self.icon_layout = QHBoxLayout()
        self.icon_layout.addStretch()
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addStretch()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(WINDOWPAL.color(QPalette.ColorRole.Window)))
        qp.drawRect(self.rect())

    def resizeEvent(self, event):
        icon_size = self.icon_label.height()
        self.icon_label.setPixmap(
            self.icon.scaled(
                icon_size,
                icon_size,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.icon_label.setMaximumWidth(icon_size)


class Welcome(StartWidget):
    gameid_trigger = pyqtSignal(str)
    summary_trigger = pyqtSignal(str)

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.title_font = QFont()
        self.title_font.setBold(True)

        self.title_label = DynamicLabel("JParty!", lambda: self.height() * 0.1, self)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_label = DynamicLabel(
            f"version {version}", lambda: self.height() * 0.03
        )
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("QLabel { color : grey}")

        select_layout = QHBoxLayout()

        template_url = "https://docs.google.com/spreadsheets/d/1_vBBsWn-EVc7npamLnOKHs34Mc2iAmd9hOGSzxHQX0Y/edit#gid=0"
        gameid_text = f'Game ID (from J-Archive URL)<br>or <a href="{template_url}">GSheet ID for custom game</a>'
        self.gameid_label = DynamicLabel(gameid_text, lambda: self.height() * 0.1, self)
        self.gameid_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.gameid_label.setOpenExternalLinks(True)

        self.textbox = QLineEdit(self)
        self.textbox.textChanged.connect(self.show_summary)
        f = self.textbox.font()
        self.textbox.setFont(f)

        button_layout = QVBoxLayout()
        self.start_button = DynamicButton("Start!", self)
        self.start_button.clicked.connect(self.game.start_game)
        self.start_button.setEnabled(False)

        self.rand_button = DynamicButton("Random", self)
        self.rand_button.clicked.connect(self.random)

        button_layout.addWidget(self.start_button, 10)
        button_layout.addStretch(1)
        button_layout.addWidget(self.rand_button, 10)

        select_layout.addStretch(5)
        select_layout.addWidget(self.gameid_label, 40)
        select_layout.addStretch(2)
        select_layout.addWidget(self.textbox, 40)
        select_layout.addStretch(2)
        select_layout.addLayout(button_layout, 20)
        select_layout.addStretch(5)

        self.summary_label = DynamicLabel("", lambda: self.height() * 0.04, self)
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.quit_button = DynamicButton("Quit", self)
        self.quit_button.clicked.connect(self.game.close)

        self.help_button = DynamicButton("Show help", self)
        self.help_button.clicked.connect(self.show_help)

        self.settings_button = DynamicButton("Settings", self)
        self.settings_button.clicked.connect(self.show_settings)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch(5)
        footer_layout.addWidget(self.quit_button, 3)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.help_button, 3)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.settings_button, 3)
        footer_layout.addStretch(5)

        main_layout.addStretch(3)
        main_layout.addLayout(self.icon_layout, 6)
        main_layout.addWidget(self.title_label, 3)
        main_layout.addWidget(self.version_label, 1)
        main_layout.addStretch(1)
        main_layout.addLayout(select_layout, 5)
        main_layout.addStretch(1)
        main_layout.addWidget(self.summary_label, 5)
        main_layout.addLayout(footer_layout, 3)
        main_layout.addStretch(3)

        self.gameid_trigger.connect(self.set_gameid)
        self.summary_trigger.connect(self.set_summary)

        self.setLayout(main_layout)

        self.show()

    def show_help(self):
        logging.info("Showing help")
        msgbox = QMessageBox(
            QMessageBox.Icon.NoIcon,
            "JParty Help",
            helpmsg,
            QMessageBox.StandardButton.Ok,
            self,
        )
        msgbox.exec()

    def show_settings(self):
        logging.info("Showing settings")
        settings_menu = SettingsMenu(self)
        settings_menu.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        textbox_height = int(self.gameid_label.height() * 0.8)
        self.textbox.setMinimumSize(QSize(0, textbox_height))
        f = self.textbox.font()
        f.setPixelSize(int(textbox_height * 0.9))
        self.textbox.setFont(f)

    def __random(self):
        while True:
            game_id = get_random_game()
            logging.info(f"GAMEID {game_id}")
            self.game.data = get_game(game_id)
            if self.game.valid_game():
                break
            else:
                time.sleep(0.25)

        self.gameid_trigger.emit(str(game_id))
        self.summary_trigger.emit(self.game.data.date + "\n" + self.game.data.comments)

    def random(self, checked):
        self.summary_trigger.emit("Loading...")
        t = Thread(target=self.__random)
        t.start()

    def __show_summary(self):
        game_id = self.textbox.text()
        try:
            self.game.data = get_game(game_id)
            if self.game.valid_game():
                self.summary_trigger.emit(
                    self.game.data.date + "\n" + self.game.data.comments
                )
            else:
                self.summary_trigger.emit("Game has blank questions")

        except Exception:
            self.summary_trigger.emit("Cannot get game")

        self.check_start()

    def set_summary(self, text):
        self.summary_label.setText(text)

    def set_gameid(self, text):
        self.textbox.setText(text)

    def show_summary(self, text=None):
        self.summary_trigger.emit("Loading...")
        t = Thread(target=self.__show_summary)
        t.start()

        self.check_start()

    def check_start(self):
        if self.game.startable():
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def restart(self):
        self.show_summary(self)


class QRWidget(StartWidget):
    def __init__(self, host, parent=None):
        super().__init__(parent)

        self.font = QFont()
        self.font.setPointSize(30)

        main_layout = QVBoxLayout()

        self.hint_label = DynamicLabel("Scan for Buzzer:", self.start_fontsize, self)
        self.hint_label.setFont(self.font)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.qrlabel = QLabel(self)
        self.qrlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.url = "http://" + host
        self.url_label = DynamicLabel(self.url, self.start_fontsize, self)
        self.url_label.setFont(self.font)
        self.url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)
        main_layout.addLayout(self.icon_layout, 5)
        main_layout.addWidget(self.hint_label, 2)
        main_layout.addWidget(self.qrlabel, 5)
        main_layout.addWidget(self.url_label, 2)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.show()

    def start_fontsize(self):
        return 0.1 * self.width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.qrlabel.setPixmap(
            qrcode.make(
                self.url, image_factory=Image, box_size=max(self.height() / 50, 1)
            ).pixmap()
        )

    def restart(self):
        pass

class SettingsMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Read the current theme from the configuration file
        with open('config.json', 'r') as f:
            config = json.load(f)

        current_theme = config.get('theme', DEFAULT_CONFIG['theme'])
        current_showtextwithimages = config.get('showtextwithimages', DEFAULT_CONFIG['showtextwithimages'])
        current_earlybuzztimeout = config.get('earlybuzztimeout', DEFAULT_CONFIG['earlybuzztimeout'])
        current_allownegative = config.get('allownegative', DEFAULT_CONFIG['allownegative'])
        current_allownegativeinfinal = config.get('allownegativeinfinal', DEFAULT_CONFIG['allownegativeinfinal'])

        self.setWindowTitle("Settings")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout()

        # Add info about theme change auto-restarting the game
        settings_info = QLabel("Theme change auto-restarts the game.", self)
        settings_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_info.setFixedWidth(self.width())
        palette = settings_info.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(128, 128, 128))
        settings_info.setPalette(palette)
        settings_info_layout = QHBoxLayout()

        # Add a label for the "Theme" section
        theme_label = QLabel("Theme:", self)

        # Add a combo box for theme selection
        self.theme_combobox = QComboBox(self)
        self.theme_combobox.addItem("Default")
        self.theme_combobox.addItem("Christmas")
        self.theme_combobox.addItem("EightiesSynthwave")
        self.theme_combobox.setCurrentText(current_theme)

        # Set the font to bold and text color to white
        font = self.theme_combobox.font()
        font.setBold(True)
        self.theme_combobox.setFont(font)
        palette = self.theme_combobox.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.theme_combobox.setPalette(palette)

        # Add a white border around the dropdown menu
        self.theme_combobox.setStyleSheet("QComboBox { border: 2px solid white; }")

        # Create a horizontal layout for the label and combo box
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combobox)

        # Add a label for the "showtextwithimages" section
        showtextwithimages_label = QLabel("Question display mode:", self)

        # Add a combo box for showtextwithimages selection
        self.showtextwithimages_combobox = QComboBox(self)
        self.showtextwithimages_combobox.addItem("Only show text")
        self.showtextwithimages_combobox.addItem("Only show image")
        self.showtextwithimages_combobox.addItem("Show both")
        self.showtextwithimages_combobox.setCurrentText(current_showtextwithimages)

        # Set the font to bold and text color to white
        font = self.showtextwithimages_combobox.font()
        font.setBold(True)
        self.showtextwithimages_combobox.setFont(font)
        palette = self.showtextwithimages_combobox.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.showtextwithimages_combobox.setPalette(palette)

        # Add a white border around the dropdown menu
        self.showtextwithimages_combobox.setStyleSheet("QComboBox { border: 2px solid white; }")

        # Create a horizontal layout for the label and combo box
        showtextwithimages_layout = QHBoxLayout()
        showtextwithimages_layout.addWidget(showtextwithimages_label)
        showtextwithimages_layout.addWidget(self.showtextwithimages_combobox)

        # Add a label for the "earlybuzztimeout" section
        earlybuzztimeout_label = QLabel("Early buzz timeout (ms):", self)

        # Add a combo box for earlybuzztimeout selection
        self.earlybuzztimeout_combobox = QLineEdit(self)
        self.earlybuzztimeout_combobox.setText(str(current_earlybuzztimeout))

        # Set the font to bold and text color to white
        font = self.earlybuzztimeout_combobox.font()
        font.setBold(True)
        self.earlybuzztimeout_combobox.setFont(font)
        palette = self.earlybuzztimeout_combobox.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.earlybuzztimeout_combobox.setPalette(palette)

        # Add a white border around the dropdown menu
        self.earlybuzztimeout_combobox.setStyleSheet("QComboBox { border: 2px solid white; }")

        # Create a horizontal layout for the label and combo box
        earlybuzztimeout_layout = QHBoxLayout()
        earlybuzztimeout_layout.addWidget(earlybuzztimeout_label)
        earlybuzztimeout_layout.addWidget(self.earlybuzztimeout_combobox)

        # Add a label for the "allownegative" section
        allownegative_label = QLabel("Allow Negatives:", self)

        # Add a combo box for allownegative selection
        self.allownegative_combobox = QComboBox(self)
        self.allownegative_combobox.addItem("True")
        self.allownegative_combobox.addItem("False")
        self.allownegative_combobox.setCurrentText(current_allownegative)

        # Set the font to bold and text color to white
        font = self.allownegative_combobox.font()
        font.setBold(True)
        self.allownegative_combobox.setFont(font)
        palette = self.allownegative_combobox.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.allownegative_combobox.setPalette(palette)

        # Add a white border around the dropdown menu
        self.allownegative_combobox.setStyleSheet("QComboBox { border: 2px solid white; }")

        # Create a horizontal layout for the label and combo box
        allownegative_layout = QHBoxLayout()
        allownegative_layout.addWidget(allownegative_label)
        allownegative_layout.addWidget(self.allownegative_combobox)

        # Add a label for the "allownegativeinfinal" section
        allownegativeinfinal_label = QLabel("Allow Negative Score In Final Jeopardy:", self)

        # Add a combo box for allownegativeinfinal selection
        self.allownegativeinfinal_combobox = QComboBox(self)
        self.allownegativeinfinal_combobox.addItem("True")
        self.allownegativeinfinal_combobox.addItem("False")
        self.allownegativeinfinal_combobox.setCurrentText(current_allownegativeinfinal)

        # Set the font to bold and text color to white
        font = self.allownegativeinfinal_combobox.font()
        font.setBold(True)
        self.allownegativeinfinal_combobox.setFont(font)
        palette = self.allownegativeinfinal_combobox.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.allownegativeinfinal_combobox.setPalette(palette)

        # Add a white border around the dropdown menu
        self.allownegativeinfinal_combobox.setStyleSheet("QComboBox { border: 2px solid white; }")

        # Create a horizontal layout for the label and combo box
        allownegativeinfinal_layout = QHBoxLayout()
        allownegativeinfinal_layout.addWidget(allownegativeinfinal_label)
        allownegativeinfinal_layout.addWidget(self.allownegativeinfinal_combobox)

        # Add the horizontal layouts to the main layout
        layout.addLayout(settings_info_layout)
        layout.addSpacing(20)
        layout.addLayout(theme_layout)
        layout.addLayout(showtextwithimages_layout)
        layout.addLayout(earlybuzztimeout_layout)
        layout.addLayout(allownegative_layout)
        layout.addLayout(allownegativeinfinal_layout)

        # Add space before the Apply button
        layout.addSpacing(10)

        # Add an "Apply" button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.save_settings)  # Connect the button's clicked signal to the save_settings method
        self.apply_button.setStyleSheet("QPushButton { border: 2px solid black; }")
        self.apply_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.apply_button.setMinimumSize(100, 30)
        layout.addWidget(self.apply_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Add space after the Apply button
        layout.addSpacing(10)

        # Set the font to bold for all widgets in the layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                font = widget.font()
                font.setBold(True)
                widget.setFont(font)

        self.setLayout(layout)

    def save_settings(self):
        logging.info("save_settings method called")  # Debugging line
        new_settings = {}
        requires_restart = False

        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Theme setting
        old_theme = config.get('theme', 'default')
        theme = self.theme_combobox.currentText()
        if theme != old_theme:
            requires_restart = True

        # Show text with images setting
        showtextwithimages = self.showtextwithimages_combobox.currentText()

        # Early buzz timeout setting
        earlybuzztimeout = int(self.earlybuzztimeout_combobox.text())

        # Show allow negative setting
        allownegative = self.allownegative_combobox.currentText()

        # Show allow negative in final setting
        allownegativeinfinal = self.allownegativeinfinal_combobox.currentText()

        # Save config
        logging.info("Saving settings...")
        with open('config.json', 'w') as f:
            json.dump({
                'theme': theme,
                'showtextwithimages': showtextwithimages,
                'earlybuzztimeout': earlybuzztimeout,
                'allownegative': allownegative,
                'allownegativeinfinal': allownegativeinfinal
            }, f)

        if requires_restart:
            # Restart the application
            os.execv(sys.executable, ['python'] + sys.argv)
        self.accept()  # Close the dialog