from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QProgressBar, QFileDialog)
from PySide6.QtCore import QSettings, QStandardPaths, QUrl
import os
import re

class DownloadDialog(QDialog):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download")
        self.setMinimumWidth(500)
        
        # Store URL and parse suggested filename
        self.url = url
        self.url_obj = QUrl(url)
        self.suggested_filename = self.sanitize_filename(os.path.basename(self.url_obj.path()))
        if not self.suggested_filename:
            self.suggested_filename = "download"
        
        # Apply modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #1e293b;
                font-size: 13px;
            }
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                background-color: #ffffff;
                min-height: 36px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
            QLineEdit:disabled {
                background-color: #f8fafc;
                color: #64748b;
            }
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                text-align: center;
                background-color: #f8fafc;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 100px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton[text="Cancel"] {
                background-color: #ffffff;
                color: #1e293b;
                border: 2px solid #e2e8f0;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
            QPushButton[text="Browse..."] {
                background-color: #ffffff;
                color: #2563eb;
                border: 2px solid #2563eb;
                min-width: 80px;
            }
            QPushButton[text="Browse..."]:hover {
                background-color: #2563eb10;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # URL
        url_label = QLabel("URL:")
        url_label.setStyleSheet("font-weight: bold;")
        self.url_edit = QLineEdit()
        self.url_edit.setText(url)
        self.url_edit.setReadOnly(True)
        layout.addRow(url_label, self.url_edit)
        
        # Filename
        filename_label = QLabel("Filename:")
        filename_label.setStyleSheet("font-weight: bold;")
        self.filename_edit = QLineEdit()
        self.filename_edit.setText(self.suggested_filename)
        layout.addRow(filename_label, self.filename_edit)
        
        # Save location
        location_label = QLabel("Save Location:")
        location_label.setStyleSheet("font-weight: bold;")
        location_layout = QHBoxLayout()
        
        self.location_edit = QLineEdit()
        self.location_edit.setText(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_location)
        
        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(browse_button)
        layout.addRow(location_label, location_layout)
        
        # Progress bar
        progress_label = QLabel("Progress:")
        progress_label.setStyleSheet("font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addRow(progress_label, self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        ok_button = QPushButton("Download")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)
        
        layout.addRow("", button_layout)
    
    def sanitize_filename(self, filename):
        """Clean filename to be safe for saving."""
        # Remove any path components and get just the filename
        filename = os.path.basename(filename)
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = "".join(char for char in filename if ord(char) >= 32)
        
        # Limit length (Windows has a 255 character limit)
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
            
        return filename.strip() or "download"
    
    def browse_location(self):
        """Open file dialog to choose save location."""
        current_dir = self.location_edit.text()
        if not os.path.exists(current_dir):
            current_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            os.path.join(current_dir, self.filename_edit.text()),
            "All Files (*.*)"
        )
        
        if file_path:
            # Update both location and filename
            self.location_edit.setText(os.path.dirname(file_path))
            self.filename_edit.setText(os.path.basename(file_path))
    
    def validate_and_accept(self):
        """Validate the save path before accepting."""
        try:
            save_path = self.get_save_path()
            save_dir = os.path.dirname(save_path)
            
            # Create directory if it doesn't exist
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Check write permissions
            if not os.access(save_dir, os.W_OK):
                raise PermissionError(f"No write permission for directory: {save_dir}")
            
            # Check if file exists
            if os.path.exists(save_path):
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "File Exists",
                    "The file already exists. Do you want to replace it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            self.accept()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot save file: {str(e)}"
            )
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def set_default_path(self, path):
        """Set the default download path and filename."""
        self.location_edit.setText(os.path.dirname(path))
        self.filename_edit.setText(self.sanitize_filename(os.path.basename(path)))
    
    def get_save_path(self):
        """Get the full save path for the download."""
        save_dir = self.location_edit.text()
        if not save_dir:
            save_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        
        filename = self.sanitize_filename(self.filename_edit.text())
        return os.path.join(save_dir, filename) 