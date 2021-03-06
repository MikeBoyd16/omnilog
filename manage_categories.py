import sys
import os
import json
import datetime
from manage_fields import *
from select_category import *
from add_item import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image


class ManageCategories(QDialog):
    def __init__(self, category_names, category_icon_paths):
        super().__init__()
        self.row = -1

        # Set this window to always be on top when visible
        self.setModal(True)

        # Initialize category variables
        self.category_names = category_names

        # Initialize icon variables
        self.category_icon_paths = category_icon_paths
        self.original_icon_path = ""
        self.new_icon_path = ""
        self.icon_width = 0
        self.icon_height = 0

        # initialize window variables
        self.frame_length = 250
        self.horizontal_position = 0
        self.vertical_position = 375
        self.init_widgets()
        self.init_window()
        self.init_layout()
        self.init_styles()
        self.init_categories()

    def init_window(self):
        """Initializes the window and its dimensions"""
        self.setFixedSize(270, self.frame_length)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.init_center_position()

    def init_layout(self):
        """Initializes the layout and arranges the widgets in the proper order."""
        self.layouts = {"main_layout": QVBoxLayout(), "header_layout": QHBoxLayout(), "controls_layout": QHBoxLayout(),
                        "fields_layout": QGridLayout(), "submit_layout": QVBoxLayout()}

        # Add the header to the header layout
        self.layouts["header_layout"].addWidget(self.header)
        self.header.setAlignment(Qt.AlignCenter)

        # Add the add and remove category buttons to the controls layout
        self.layouts["controls_layout"].addWidget(self.buttons["add_category"])
        self.layouts["controls_layout"].addWidget(self.buttons["remove_category"])
        self.layouts["controls_layout"].setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Format the fields layout
        self.layouts["fields_layout"].setSizeConstraint(QLayout.SetFixedSize)
        self.layouts["fields_layout"].setAlignment(Qt.AlignCenter)

        # Add the OK button to the submit layout
        self.layouts["submit_layout"].addWidget(self.buttons["ok"])
        self.layouts["submit_layout"].setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.layouts["submit_layout"].addStretch(1)

        # Add all layouts and spacers to the main layout and set margins and spacing
        for layout in self.layouts:
            if layout == "fields_layout":
                self.layouts["main_layout"].addWidget(self.top_line)
            elif layout == "submit_layout":
                self.layouts["main_layout"].addWidget(self.bottom_line)
            if layout != "main_layout":
                self.layouts["main_layout"].addLayout(self.layouts[layout])
            self.layouts[layout].setContentsMargins(10, 10, 10, 10)
            self.layouts[layout].setSpacing(15)

        # Set the main layout as the window's layout
        self.setLayout(self.layouts["main_layout"])

    def init_widgets(self):
        """Initializes widgets and their properties"""

        # Initialize the header
        self.header = QLabel("Manage Categories")

        # Initialize, format, and set the event for all buttons
        self.buttons = {"add_category": QPushButton(), "remove_category": QPushButton(), "ok": QPushButton()}
        for button in self.buttons:
            button_text = button.replace("_", " ").title().rsplit(' ', 1)[0]
            self.buttons[button].setText("  " + button_text)
            self.buttons[button].setFixedSize(QSize(100, 35))
        for button in self.buttons:
            button_method = getattr(self, button)
            self.buttons[button].clicked.connect(button_method)

        # Initialize the top separator
        self.top_line = QFrame()
        self.top_line.setFrameShape(QFrame.HLine)
        self.top_line_shadow = QGraphicsDropShadowEffect()
        self.top_line_shadow.setBlurRadius(7.0)
        self.top_line_shadow.setOffset(2.3)
        self.top_line.setGraphicsEffect(self.top_line_shadow)

        # Initialize the bottom separator
        self.bottom_line = QFrame()
        self.bottom_line.setFrameShape(QFrame.HLine)
        self.bottom_line_shadow = QGraphicsDropShadowEffect()
        self.bottom_line_shadow.setBlurRadius(7.0)
        self.bottom_line_shadow.setOffset(-2.3)
        self.bottom_line.setGraphicsEffect(self.bottom_line_shadow)

        # Initialize empty category field and button data structures
        self.category_fields = {}
        self.category_buttons = {}

    def init_styles(self):
        """Sets the stylesheet properties for widgets"""
        self.setPalette(QPalette(QColor("#f3ffbd")))
        self.setStyleSheet("""
            .QLabel {
                font-weight: bold;
                font-size: 24px;
                color: #247ba0;
            }
            .QPushButton {
                background-color: #247ba0;
                border: 1px solid #8CBDAF;
                font-weight: bold;
                font-size: 12px;
                color: #f3ffbd;
                width: 40px;
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

    def init_categories(self):
        for idx in range(len(self.category_names)):
            self.update_frame_length("increase")
            key = str(idx)
            self.row += 1

            self.category_fields[key] = QLineEdit()
            self.category_fields[key].setText(str(self.category_names[key]))
            self.category_fields[key].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.category_fields[key].textChanged.connect(self.set_icon_status)
            self.layouts["fields_layout"].addWidget(self.category_fields[key], idx, 0, 1, 1)

            self.category_buttons[key] = QPushButton()
            if key in self.category_icon_paths:
                self.category_buttons[key].setIcon(QIcon(self.category_icon_paths[key]))
            else:
                self.category_buttons[key].setText("Icon")
            self.category_buttons[key].setIconSize(QSize(30, 30))
            self.category_buttons[key].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.category_buttons[key].clicked.connect(self.set_icon)
            self.set_icon_status()
            self.layouts["fields_layout"].addWidget(self.category_buttons[key], idx, 1, 1, 1)

        # If there are fewer than four categories, populate the window with additional empty category fields.
        while self.row < 3:
            self.add_category()

    def init_center_position(self):
        """Positions the window in the center of the screen"""
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.horizontal_position = frame_geometry.left()
        self.move(self.horizontal_position, self.vertical_position)

    def add_category(self):
        """Adds a new field where a category can be entered"""
        self.update_frame_length("increase")
        self.row += 1
        key = str(self.row)

        self.category_fields[key] = QLineEdit()
        if self.row < len(self.category_names):
            self.category_fields[key].setText(str(self.category_names[key]))
        else:
            self.category_fields[key].setPlaceholderText("Enter a category name")
        self.category_fields[key].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.category_fields[key].textChanged.connect(self.set_icon_status)
        self.layouts["fields_layout"].addWidget(self.category_fields[key], self.row, 0, 1, 1)

        self.category_buttons[key] = QPushButton()
        if self.row < len(self.category_icon_paths):
            self.category_buttons[key].setIcon(QIcon(self.category_icon_paths[key]))
            self.category_buttons[key].setIconSize(QSize(30, 30))
        else:
            self.category_buttons[key].setText("Icon")
        self.category_buttons[key].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.category_buttons[key].clicked.connect(self.set_icon)
        self.set_icon_status()
        self.layouts["fields_layout"].addWidget(self.category_buttons[key], self.row, 1, 1, 1)

    def remove_category(self):
        """Removes an existing field where a category could be entered"""
        if self.row >= 0:
            key = str(self.row)
            self.category_fields[key].setParent(None)
            del(self.category_fields[key])
            self.category_buttons[key].setParent(None)
            del(self.category_buttons[key])

            if key in self.category_icon_paths:
                os.remove(self.category_icon_paths[key])
                del(self.category_icon_paths[key])
            if key in self.category_names:
                del(self.category_names[key])

            self.row -= 1
            self.update_frame_length("decrease")

    def set_icon_status(self):
        """Enables/disables combo buttons based on the field combo selection"""
        for idx in range(self.row + 1):
            key = str(idx)
            if self.category_fields[key].text():
                self.category_buttons[key].setEnabled(True)
                self.category_buttons[key].setStyleSheet("""
                                    .QPushButton {background-color: #247ba0;}
                                    .QPushButton:hover {background-color: #8CBDAF;}
                                """)
            else:
                self.category_buttons[key].setEnabled(False)
                self.category_buttons[key].setStyleSheet(".QPushButton {background-color: #D7E7EE;}")

            self.update_icon_name(key)

    def set_icon(self):
        """Sets the icon for a particular category"""
        current_button = self.sender()
        current_row = ((self.layouts["fields_layout"].indexOf(current_button) + 1) // 2) - 1
        key = str(current_row)

        icon_file = QFileDialog.getOpenFileName(self, "Open Image", "c:\\", "Image Files (*.png *.jpg *.bmp)")
        self.original_icon_path = icon_file[0]
        if self.original_icon_path:
            icon = QPixmap(self.original_icon_path)
            self.icon_width = QPixmap.width(icon)
            self.icon_height = QPixmap.height(icon)

            # Calculate the icon's aspect ratio
            width_ratio = 1.0
            height_ratio = 1.0
            if self.icon_width > self.icon_height:
                width_ratio = self.icon_width / self.icon_height
            else:
                height_ratio = self.icon_height / self.icon_width

            # Reduce icon dimensions to be less than or equal to 35
            while self.icon_width > 35 or self.icon_height > 35:
                self.icon_width -= width_ratio
                self.icon_height -= height_ratio

            # Convert icon dimensions back to integers
            self.icon_width = int(self.icon_width)
            self.icon_height = int(self.icon_height)

            # Set the scaled dimensions of the icon to fit the container
            icon = icon.scaled(self.icon_width, self.icon_height, Qt.KeepAspectRatio)

            # Create a new icon path and save it at that location
            self.new_icon_path = "images/category-icons/" + str(self.category_fields[key].text()) + ".jpg"
            self.category_icon_paths[key] = self.new_icon_path
            self.save_icon()

            # Add the icon to the container
            current_button.setText("")
            current_button.setIcon(QIcon(icon))

    def save_icon(self):
        """Copies an icon to the program directory and saves the path to the category record"""

        # Create an icon image object from the original icon path
        icon = Image.open(self.original_icon_path)

        # Resize the icon
        icon_resized = icon.resize((self.icon_width, self.icon_height), Image.ANTIALIAS)

        # Save the image as a new file at the new image path location
        icon_resized.save(self.new_icon_path, 'JPEG', quality=90)

    def update_icon_name(self, key):
        """Updates the icon file name when the name of the category field changes"""
        if key in self.category_icon_paths:
            category_name = str(self.category_fields[key].text())
            icon_path = "images/category-icons/" + category_name + ".jpg"
            if category_name is not '' and icon_path not in self.category_icon_paths[key]:
                os.rename(self.category_icon_paths[key], icon_path)
                self.category_icon_paths[key] = icon_path
                self.category_buttons[key].setIcon(QIcon(self.category_icon_paths[key]))

    def update_frame_length(self, change_type):
        """Increases or decreases the length and height of the frame"""
        if change_type == "increase":
            self.frame_length += 65
            self.vertical_position -= 30
        elif change_type == "decrease":
            self.frame_length -= 65
            self.vertical_position += 30
        else:
            raise ValueError("An invalid value was entered for the type of change in frame height.")

        self.setFixedHeight(self.frame_length)
        self.move(self.horizontal_position, self.vertical_position)

    def ok(self):
        """Updates catalog categories and returns focus to the main window"""
        self.category_names = {}
        temp_category_icon_paths = {}
        category_count = 0
        for idx in range(len(self.category_fields)):
            key = str(idx)
            if self.category_fields[key].text():
                self.category_names[str(category_count)] = self.category_fields[key].text()
                if key in self.category_icon_paths:
                    temp_category_icon_paths[str(category_count)] = self.category_icon_paths[key]
                category_count += 1
        self.category_icon_paths = temp_category_icon_paths
        self.hide()
