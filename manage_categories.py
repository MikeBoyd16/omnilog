import sys
import json
import datetime
from manage_fields import *
from select_media import *
from add_media import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ManageCategories(QDialog):
    def __init__(self):
        super().__init__()
        self.category_count = 0
        self.init_widgets()
        self.init_window()
        self.init_layout()
        self.init_styles()

    def init_window(self):
        """Initializes the window, its dimensions, and content"""
        self.setWindowTitle("Manage Categories")
        self.setGeometry(100, 100, 250, 500)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.center_window()

    def init_layout(self):
        """Initializes the layout and arranges the widgets in the proper order."""
        self.layouts = {"Main": QVBoxLayout(), "Top": QHBoxLayout(), "Center": QGridLayout(), "Bottom": QVBoxLayout()}
        for layout in self.layouts:
            if layout != "Main":
                self.layouts["Main"].addLayout(self.layouts[layout])
            if layout == "Top":
                self.layouts[layout].addWidget(self.buttons["add_category"])
                self.layouts[layout].addWidget(self.buttons["remove_category"])
                self.layouts[layout].setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            elif layout == "Center":
                self.layouts[layout].setSizeConstraint(QLayout.SetFixedSize)
                self.layouts[layout].setAlignment(Qt.AlignCenter)
            elif layout == "Bottom":
                self.layouts[layout].addWidget(self.buttons["ok"])
                self.layouts[layout].setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
                self.layouts[layout].addStretch(1)
            self.layouts[layout].setContentsMargins(10, 10, 10, 10)
            self.layouts[layout].setSpacing(15)
        self.setLayout(self.layouts["Main"])

    def init_widgets(self):
        """Initializes widgets and their properties"""
        self.buttons = {"add_category": QPushButton(), "remove_category": QPushButton(), "ok": QPushButton()}
        for button in self.buttons:
            button_text = button.replace("_", " ").title().rsplit(' ', 1)[0]
            self.buttons[button].setText("  " + button_text)
            self.buttons[button].setFixedSize(QSize(100, 40))
        for button in self.buttons:
            button_method = getattr(self, button)
            self.buttons[button].clicked.connect(button_method)

        self.category_fields = {}
        self.category_buttons = {}

    def init_styles(self):
        """Sets the stylesheet properties for widgets"""
        self.setPalette(QPalette(QColor("#f3ffbd")))
        self.setStyleSheet("""
            .Self {
                border: 1px solid #000000;
            }
            .QPushButton {
                background-color: #247ba0;
                border: 1px solid #8CBDAF;
                font-weight: bold;
                font-size: 12px;
                color: #f3ffbd;
                height: 50px;
            }
            .QPushButton:hover {
                background-color: #8CBDAF;
            }
            .QLineEdit {
                width: 120px; 
                margin-top: 14px;
                margin-bottom: 14px;
            }
        """)

    def center_window(self):
        """Positions the window in the center of the screen"""
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def add_category(self):
        """Adds a new field where a category can be entered"""
        self.category_count += 1

        self.category_fields[self.category_count] = QLineEdit()
        self.category_fields[self.category_count].setPlaceholderText("Enter a new category")
        self.category_fields[self.category_count].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.layouts["Center"].addWidget(self.category_fields[self.category_count], self.category_count - 1, 0, 1, 1)

        self.category_buttons[self.category_count] = QPushButton("Set Icon")
        self.category_buttons[self.category_count].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.layouts["Center"].addWidget(self.category_buttons[self.category_count], self.category_count - 1, 1, 1, 4)

    def remove_category(self):
        """Removes an existing field where a category could be entered"""
        if self.category_count != 0:
            self.category_fields[self.category_count].setParent(None)
            del(self.category_fields[self.category_count])
            self.category_buttons[self.category_count].setParent(None)
            del(self.category_buttons[self.category_count])
            self.category_count -= 1

    def ok(self):
        """Returns focus to the main window"""
        self.hide()