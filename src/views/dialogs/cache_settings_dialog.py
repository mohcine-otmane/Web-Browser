from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QPushButton, QLabel)
from PySide6.QtCore import QSettings, QStandardPaths
import os

class CacheSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cache Settings")
        self.setMinimumWidth(400)
        
        # Apply modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #444444;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                min-height: 25px;
            }
            QLineEdit:focus, QSpinBox:focus {
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
        
        # Cache path
        self.cache_path_edit = QLineEdit()
        self.cache_path_edit.setReadOnly(True)
        layout.addRow("Cache Location:", self.cache_path_edit)
        
        # Cache size
        self.cache_size = QSpinBox()
        self.cache_size.setRange(1, 1000)
        self.cache_size.setSuffix(" MB")
        layout.addRow("Cache Size:", self.cache_size)
        
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
        self.cache_path_edit.setText(settings.value("cache_path", 
            os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "web_browser")))
        self.cache_size.setValue(int(settings.value("cache_size", 100)))
    
    def save_settings(self):
        settings = QSettings()
        settings.setValue("cache_path", self.cache_path_edit.text())
        settings.setValue("cache_size", self.cache_size.value()) 