from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel)
from PySide6.QtCore import QSettings, QStandardPaths
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setMinimumWidth(400)
        
        # Apply modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #444444;
            }
            QLineEdit, QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
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
        
        # Home page setting
        self.home_page_edit = QLineEdit()
        layout.addRow("Home Page:", self.home_page_edit)
        
        # Search engine setting
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "DuckDuckGo", "Bing"])
        layout.addRow("Search Engine:", self.search_engine)
        
        # Downloads location
        self.download_path = QLineEdit()
        self.download_path.setReadOnly(True)
        layout.addRow("Downloads Location:", self.download_path)
        
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
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        settings = QSettings()
        self.home_page_edit.setText(settings.value("home_page", "https://www.bing.com"))
        self.search_engine.setCurrentText(settings.value("search_engine", "Bing"))
        self.download_path.setText(settings.value("download_path", QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)))
    
    def save_settings(self):
        settings = QSettings()
        settings.setValue("home_page", self.home_page_edit.text())
        settings.setValue("search_engine", self.search_engine.currentText())
        settings.setValue("download_path", self.download_path.text()) 