from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QProgressBar)
from PySide6.QtCore import QSettings, QStandardPaths
import os

class DownloadDialog(QDialog):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download")
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
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 4px;
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
        
        # URL
        self.url_edit = QLineEdit()
        self.url_edit.setText(url)
        self.url_edit.setReadOnly(True)
        layout.addRow("URL:", self.url_edit)
        
        # Save location
        self.location_edit = QLineEdit()
        self.location_edit.setText(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        layout.addRow("Save Location:", self.location_edit)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addRow("Progress:", self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        ok_button = QPushButton("Download")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        layout.addRow("", button_layout)
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def get_save_path(self):
        return os.path.join(self.location_edit.text(), os.path.basename(self.url_edit.text())) 