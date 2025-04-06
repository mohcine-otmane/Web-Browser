from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton,
                             QLabel)
from PySide6.QtCore import QSettings, Qt
import json
import os

class BookmarksDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
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
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f2fa;
                color: #0078d4;
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
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search bookmarks...")
        layout.addWidget(self.search_edit)
        
        # Bookmarks list
        self.bookmarks_list = QListWidget()
        layout.addWidget(self.bookmarks_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        delete_button = QPushButton("Delete")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)
        
        delete_button.clicked.connect(self.delete_selected)
        cancel_button.clicked.connect(self.reject)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.search_edit.textChanged.connect(self.filter_bookmarks)
        
        # Load bookmarks
        self.load_bookmarks()
    
    def load_bookmarks(self):
        settings = QSettings()
        bookmarks = json.loads(settings.value("bookmarks", "{}"))
        
        self.bookmarks_list.clear()
        for title, url in bookmarks.items():
            item = QListWidgetItem(f"{title}\n{url}")
            item.setData(Qt.UserRole, url)
            self.bookmarks_list.addItem(item)
    
    def filter_bookmarks(self, text):
        for i in range(self.bookmarks_list.count()):
            item = self.bookmarks_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def delete_selected(self):
        selected_items = self.bookmarks_list.selectedItems()
        if not selected_items:
            return
        
        settings = QSettings()
        bookmarks = json.loads(settings.value("bookmarks", "{}"))
        
        for item in selected_items:
            title = item.text().split('\n')[0]
            if title in bookmarks:
                del bookmarks[title]
        
        settings.setValue("bookmarks", json.dumps(bookmarks))
        self.load_bookmarks() 