from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import QSettings
import json

class AddBookmarkDialog(QDialog):
    def __init__(self, url, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bookmark")
        self.setMinimumWidth(400)
        self.setObjectName("AddBookmarkDialog")
        
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