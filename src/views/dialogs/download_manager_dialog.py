from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QProgressBar,
                             QHeaderView, QWidget, QMenu, QStyle, QApplication)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

class DownloadItemWidget(QWidget):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.setObjectName("download_item")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # File info
        self.name_label = QLabel(filename)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        
        # Status label
        self.status_label = QLabel("Starting...")
        
        # Cancel button
        self.cancel_button = QPushButton("✕")
        self.cancel_button.setFixedSize(24, 24)
        
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
    
    def set_status(self, status):
        self.status_label.setText(status)
        if status == "Failed":
            pass

class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setMinimumSize(600, 400)
        self.setObjectName("DownloadManagerDialog")
        
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
        
        clear_button = QPushButton("Clear Completed")
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
        self.downloads_layout.addWidget(self.placeholder)
        
        # Wrap downloads in a widget
        downloads_widget = QWidget()
        downloads_widget.setLayout(self.downloads_layout)
        
        layout.addWidget(downloads_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_all_button = QPushButton("Cancel All")
        cancel_all_button.clicked.connect(self.cancel_all)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(cancel_all_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
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