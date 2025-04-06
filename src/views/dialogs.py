import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QCheckBox, QPushButton,
                             QListWidget, QListWidgetItem, QSpinBox, QLabel)
from PySide6.QtCore import Qt, QSettings

class BaseDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.setMinimumWidth(400)
        # Set dark theme colors
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #4b4b4b;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #4b4b4b;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QListWidget {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #4b4b4b;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4c4f51;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #3c3f41;
                border: 1px solid #4b4b4b;
            }
            QCheckBox::indicator:checked {
                background-color: #4c4f51;
                border: 1px solid #4b4b4b;
            }
        """)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        pass
    
    def load_data(self):
        pass

class SettingsDialog(BaseDialog):
    def setup_ui(self):
        self.setWindowTitle("Browser Settings")
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
    
    def load_data(self):
        settings = self.model.settings
        self.home_page_edit.setText(settings.get("home_page", "https://www.bing.com"))
        self.search_engine.setCurrentText(settings.get("search_engine", "Bing"))
        self.download_path.setText(settings.get("download_path"))
    
    def accept(self):
        self.model.settings.update({
            "home_page": self.home_page_edit.text(),
            "search_engine": self.search_engine.currentText(),
            "download_path": self.download_path.text()
        })
        super().accept()

class CacheSettingsDialog(BaseDialog):
    def setup_ui(self):
        self.setWindowTitle("Cache Settings")
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cache size setting
        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setSuffix(" MB")
        layout.addRow("Maximum Cache Size:", self.cache_size)
        
        # Cache location
        self.cache_path = QLineEdit()
        self.cache_path.setReadOnly(True)
        layout.addRow("Cache Location:", self.cache_path)
        
        # Clear cache button
        clear_cache_button = QPushButton("Clear Cache Now")
        clear_cache_button.clicked.connect(self.clear_cache)
        layout.addRow(clear_cache_button)
        
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
    
    def load_data(self):
        settings = self.model.settings
        self.cache_size.setValue(settings.get("cache_size", 100))
        self.cache_path.setText(settings.get("cache_path"))
    
    def accept(self):
        # Save settings using the model
        self.model.update_setting("cache_size", self.cache_size.value())
        self.model.update_setting("cache_path", self.cache_path.text())
        super().accept()
    
    def clear_cache(self):
        try:
            cache_path = self.cache_path.text()
            if os.path.exists(cache_path):
                for file in os.listdir(cache_path):
                    file_path = os.path.join(cache_path, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                self.parent().show_status_message("Cache cleared successfully!")
            else:
                self.parent().show_status_message("Cache is already empty.")
        except Exception as e:
            self.parent().show_status_message(f"Failed to clear cache: {str(e)}")

class ProxySettingsDialog(BaseDialog):
    def setup_ui(self):
        self.setWindowTitle("Proxy Settings")
        self.setModal(True)
        
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Proxy type
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["No Proxy", "HTTP", "SOCKS5"])
        layout.addRow("Proxy Type:", self.proxy_type)
        
        # Host and port
        self.host_edit = QLineEdit()
        self.port_edit = QLineEdit()
        layout.addRow("Host:", self.host_edit)
        layout.addRow("Port:", self.port_edit)
        
        # Authentication
        self.use_auth = QCheckBox("Use Authentication")
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("", self.use_auth)
        layout.addRow("Username:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        
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
    
    def load_data(self):
        settings = QSettings()
        self.proxy_type.setCurrentText(settings.value("proxy/type", "No Proxy"))
        self.host_edit.setText(settings.value("proxy/host", ""))
        self.port_edit.setText(settings.value("proxy/port", ""))
        self.use_auth.setChecked(settings.value("proxy/use_auth", False, type=bool))
        self.username_edit.setText(settings.value("proxy/username", ""))
        self.password_edit.setText(settings.value("proxy/password", ""))
    
    def accept(self):
        settings = QSettings()
        settings.setValue("proxy/type", self.proxy_type.currentText())
        settings.setValue("proxy/host", self.host_edit.text())
        settings.setValue("proxy/port", self.port_edit.text())
        settings.setValue("proxy/use_auth", self.use_auth.isChecked())
        settings.setValue("proxy/username", self.username_edit.text())
        settings.setValue("proxy/password", self.password_edit.text())
        super().accept()

class BookmarksDialog(BaseDialog):
    def setup_ui(self):
        self.setWindowTitle("Bookmarks")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search bookmarks...")
        layout.addWidget(self.search_box)
        
        # Create list widget
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_bookmark)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Connect search functionality
        self.search_box.textChanged.connect(self.filter_bookmarks)
        
        # Connect double click
        self.list_widget.itemDoubleClicked.connect(self.load_bookmark)
    
    def load_data(self):
        self.list_widget.clear()
        for bookmark in self.model.bookmarks:
            item = QListWidgetItem(f"{bookmark['title']}\n{bookmark['url']}")
            item.setData(Qt.UserRole, bookmark["url"])
            self.list_widget.addItem(item)
    
    def filter_bookmarks(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def delete_bookmark(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            url = current_item.data(Qt.UserRole)
            self.model.delete_bookmark(url)
            self.list_widget.takeItem(self.list_widget.row(current_item))
            self.parent().show_status_message("Bookmark deleted")
    
    def load_bookmark(self, item):
        url = item.data(Qt.UserRole)
        current_tab = self.parent().get_current_tab()
        if current_tab:
            current_tab.load_url(url) 