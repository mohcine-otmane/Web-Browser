from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel)
from PySide6.QtCore import QSettings, QStandardPaths
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setMinimumWidth(400)
        self.setObjectName("SettingsDialog")
        
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