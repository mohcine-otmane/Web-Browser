from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QProgressBar,
                             QHeaderView, QWidget, QMenu, QStyle, QApplication)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

class DownloadItemWidget(QWidget):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.filename = filename
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # File info
        self.name_label = QLabel(filename)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 13px;
            }
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
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
        """)
        
        # Status label
        self.status_label = QLabel("Starting...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                min-width: 80px;
            }
        """)
        
        # Cancel button
        self.cancel_button = QPushButton("✕")
        self.cancel_button.setFixedSize(24, 24)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: #64748b;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ef444420;
                color: #ef4444;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.name_label, 2)
        layout.addWidget(self.progress_bar, 4)
        layout.addWidget(self.status_label, 1)
        layout.addWidget(self.cancel_button)
        
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress < 100:
            self.status_label.setText(f"{progress}%")
        else:
            self.status_label.setText("Completed")
            self.cancel_button.setText("✓")
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 12px;
                    color: #10b981;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #10b98120;
                }
            """)
    
    def set_status(self, status):
        self.status_label.setText(status)
        if status == "Failed":
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #f8fafc;
                }
                QProgressBar::chunk {
                    background-color: #ef4444;
                    border-radius: 3px;
                }
            """)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ef4444;
                    font-size: 12px;
                    min-width: 80px;
                }
            """)

class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setMinimumSize(600, 400)
        
        # Store download items
        self.download_items = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Downloads")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        clear_button = QPushButton("Clear Completed")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                color: #64748b;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #2563eb;
                color: #2563eb;
            }
        """)
        clear_button.clicked.connect(self.clear_completed)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        layout.addLayout(header_layout)
        
        # Downloads container
        self.downloads_layout = QVBoxLayout()
        self.downloads_layout.setSpacing(8)
        
        # Add a placeholder message
        self.placeholder = QLabel("No downloads yet")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                padding: 40px;
            }
        """)
        self.downloads_layout.addWidget(self.placeholder)
        
        # Wrap downloads in a widget with proper styling
        downloads_widget = QWidget()
        downloads_widget.setLayout(self.downloads_layout)
        downloads_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        layout.addWidget(downloads_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_all_button = QPushButton("Cancel All")
        cancel_all_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ef4444;
                border-radius: 6px;
                color: #ef4444;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ef444410;
            }
        """)
        cancel_all_button.clicked.connect(self.cancel_all)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(cancel_all_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
        """)
    
    def add_download(self, download_id, filename):
        """Add a new download to the manager."""
        if self.placeholder.isVisible():
            self.placeholder.hide()
        
        item = DownloadItemWidget(filename)
        self.download_items[download_id] = item
        self.downloads_layout.addWidget(item)
        
        # Connect cancel button
        item.cancel_button.clicked.connect(lambda: self.cancel_download(download_id))
    
    def update_progress(self, download_id, progress):
        """Update the progress of a download."""
        if download_id in self.download_items:
            self.download_items[download_id].update_progress(progress)
    
    def update_status(self, download_id, status):
        """Update the status of a download."""
        if download_id in self.download_items:
            self.download_items[download_id].set_status(status)
    
    def cancel_download(self, download_id):
        """Cancel a specific download."""
        if download_id in self.download_items:
            # Notify controller to cancel the download
            if self.parent() and hasattr(self.parent(), 'controller'):
                self.parent().controller.downloader.cancel_download(download_id)
    
    def cancel_all(self):
        """Cancel all active downloads."""
        if self.parent() and hasattr(self.parent(), 'controller'):
            self.parent().controller.downloader.cancel_all_downloads()
    
    def clear_completed(self):
        """Remove completed downloads from the list."""
        for download_id, item in list(self.download_items.items()):
            if item.status_label.text() in ["Completed", "Failed", "Cancelled"]:
                item.deleteLater()
                del self.download_items[download_id]
        
        if not self.download_items:
            self.placeholder.show()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Hide instead of close to preserve downloads
        self.hide()
        event.ignore() 