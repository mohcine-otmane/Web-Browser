from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QSpinBox, QPushButton, QLabel)
from PySide6.QtCore import QSettings, QStandardPaths
import os

class CacheSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cache Settings")
        self.setMinimumWidth(400)
        self.setObjectName("CacheSettingsDialog")
        
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