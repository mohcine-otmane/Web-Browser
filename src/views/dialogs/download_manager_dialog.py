from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QProgressBar)
from PySide6.QtCore import Qt

class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Manager")
        self.setMinimumSize(600, 400)
        
        # Apply modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e6f2fa;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #f8f8f8;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                color: #444444;
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
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create downloads table
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(4)
        self.downloads_table.setHorizontalHeaderLabels(["Filename", "Progress", "Status", "Actions"])
        self.downloads_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.downloads_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.downloads_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.downloads_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.downloads_table.setColumnWidth(1, 150)  # Progress column
        self.downloads_table.setColumnWidth(2, 100)  # Status column
        self.downloads_table.setColumnWidth(3, 100)  # Actions column
        layout.addWidget(self.downloads_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.clear_finished_button = QPushButton("Clear Finished")
        self.cancel_all_button = QPushButton("Cancel All")
        self.close_button = QPushButton("Close")
        
        button_layout.addWidget(self.clear_finished_button)
        button_layout.addWidget(self.cancel_all_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.clear_finished_button.clicked.connect(self.clear_finished_downloads)
        self.cancel_all_button.clicked.connect(self.cancel_all_downloads)
        self.close_button.clicked.connect(self.close)
        
        # Store download rows
        self.download_rows = {}
    
    def add_download(self, download_id: int, filename: str):
        """Add a new download to the table."""
        row = self.downloads_table.rowCount()
        self.downloads_table.insertRow(row)
        
        # Filename
        filename_item = QTableWidgetItem(filename)
        filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
        self.downloads_table.setItem(row, 0, filename_item)
        
        # Progress
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        self.downloads_table.setCellWidget(row, 1, progress_bar)
        
        # Status
        status_item = QTableWidgetItem("Starting...")
        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        self.downloads_table.setItem(row, 2, status_item)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.cancel_download(download_id))
        self.downloads_table.setCellWidget(row, 3, cancel_button)
        
        # Store row information
        self.download_rows[download_id] = {
            'row': row,
            'progress_bar': progress_bar,
            'cancel_button': cancel_button
        }
    
    def update_progress(self, download_id: int, progress: int):
        """Update the progress of a download."""
        if download_id in self.download_rows:
            row_info = self.download_rows[download_id]
            row_info['progress_bar'].setValue(progress)
            self.downloads_table.item(row_info['row'], 2).setText(f"{progress}%")
    
    def update_status(self, download_id: int, status: str):
        """Update the status of a download."""
        if download_id in self.download_rows:
            row_info = self.download_rows[download_id]
            self.downloads_table.item(row_info['row'], 2).setText(status)
            
            # Disable cancel button if download is finished
            if status in ["Completed", "Cancelled", "Failed"]:
                row_info['cancel_button'].setEnabled(False)
    
    def clear_finished_downloads(self):
        """Remove completed, cancelled, or failed downloads from the table."""
        rows_to_remove = []
        for download_id, row_info in self.download_rows.items():
            status = self.downloads_table.item(row_info['row'], 2).text()
            if status in ["Completed", "Cancelled", "Failed"]:
                rows_to_remove.append((download_id, row_info['row']))
        
        # Remove rows in reverse order to maintain correct indices
        for download_id, row in sorted(rows_to_remove, key=lambda x: x[1], reverse=True):
            self.downloads_table.removeRow(row)
            del self.download_rows[download_id]
            
            # Update row numbers for remaining downloads
            for info in self.download_rows.values():
                if info['row'] > row:
                    info['row'] -= 1
    
    def cancel_download(self, download_id: int):
        """Signal that a download should be cancelled."""
        if hasattr(self.parent(), 'controller'):
            self.parent().controller.downloader.cancel_download(download_id)
    
    def cancel_all_downloads(self):
        """Signal that all downloads should be cancelled."""
        if hasattr(self.parent(), 'controller'):
            self.parent().controller.downloader.cancel_all_downloads() 