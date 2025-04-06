from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import QSettings
import json

class AddBookmarkDialog(QDialog):
    def __init__(self, url, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bookmark")
        self.setMinimumWidth(400)
        
        # Apply modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #444444;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                min-height: 25px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton[text="Cancel"] {
                background-color: #ffffff;
                color: #444444;
                border: 1px solid #e0e0e0;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #f8f8f8;
                border-color: #d0d0d0;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setText(title)
        layout.addRow("Title:", self.title_edit)
        
        # URL
        self.url_edit = QLineEdit()
        self.url_edit.setText(url)
        self.url_edit.setReadOnly(True)
        layout.addRow("URL:", self.url_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        layout.addRow("", button_layout)
    
    def save_bookmark(self):
        title = self.title_edit.text().strip()
        url = self.url_edit.text().strip()
        
        if not title or not url:
            return False
        
        settings = QSettings()
        bookmarks = json.loads(settings.value("bookmarks", "{}"))
        bookmarks[title] = url
        settings.setValue("bookmarks", json.dumps(bookmarks))
        
        return True 