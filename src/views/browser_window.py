import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QToolBar,
                              QLineEdit, QTabWidget, QStatusBar, QPushButton,
                              QMenuBar, QMenu, QDialog, QMessageBox)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QUrl, QSize
from config.settings import STYLE_SETTINGS
from models.browser_model import BrowserModel
from views.tab_view import TabView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEngineProfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.browser_controller import BrowserController

class BrowserWindow(QMainWindow):
    def __init__(self, controller: 'BrowserController'):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Web Browser")
        self.setMinimumSize(1024, 768)
        
        # Define color scheme
        colors = {
            'primary': '#2563eb',  # Modern blue
            'primary_hover': '#1d4ed8',
            'primary_pressed': '#1e40af',
            'background': '#ffffff',
            'surface': '#f8fafc',
            'border': '#e2e8f0',
            'text': '#1e293b',
            'text_secondary': '#64748b',
            'accent': '#f59e0b',
            'danger': '#ef4444',
            'success': '#10b981'
        }
        
        # Apply modern style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['background']};
            }}
            QToolBar {{
                background-color: {colors['surface']};
                border-bottom: 1px solid {colors['border']};
                spacing: 10px;
                padding: 10px;
            }}
            QToolButton, QPushButton[flat="true"] {{
                background-color: transparent;
                border: none;
                padding: 8px;
                min-width: 36px;
                min-height: 36px;
                border-radius: 8px;
                font-size: 16px;
                color: {colors['text']};
            }}
            QToolButton:hover, QPushButton[flat="true"]:hover {{
                background-color: {colors['primary']}20;
                color: {colors['primary']};
            }}
            QToolButton:pressed, QPushButton[flat="true"]:pressed {{
                background-color: {colors['primary']}30;
            }}
            QLineEdit {{
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {colors['background']};
                min-height: 36px;
                selection-background-color: {colors['primary']};
                selection-color: white;
                color: {colors['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors['primary']};
                background-color: {colors['background']};
            }}
            QLineEdit::placeholder {{
                color: {colors['text_secondary']};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                background-color: {colors['background']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 4px;
                color: {colors['text_secondary']};
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['background']};
                border-bottom: 2px solid {colors['primary']};
                color: {colors['primary']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {colors['primary']}10;
                color: {colors['text']};
            }}
            QStatusBar {{
                background-color: {colors['surface']};
                border-top: 1px solid {colors['border']};
                color: {colors['text_secondary']};
                padding: 6px;
                font-size: 12px;
            }}
            QMenuBar {{
                background-color: {colors['surface']};
                border-bottom: 1px solid {colors['border']};
                padding: 6px;
            }}
            QMenuBar::item {{
                padding: 8px 16px;
                color: {colors['text']};
                font-size: 13px;
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background-color: {colors['primary']}20;
                color: {colors['primary']};
            }}
            QMenu {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                color: {colors['text']};
                font-size: 13px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {colors['primary']}20;
                color: {colors['primary']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 80px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary_pressed']};
            }}
            QPushButton[text="Cancel"] {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
            }}
            QPushButton[text="Cancel"]:hover {{
                background-color: {colors['surface']};
                border-color: {colors['text_secondary']};
            }}
            
            /* Navigation Buttons */
            #nav_button {{
                font-family: system-ui;
                font-size: 18px;
                min-width: 36px;
                min-height: 36px;
                border-radius: 8px;
                background-color: transparent;
                color: {colors['text']};
            }}
            #nav_button:hover {{
                background-color: {colors['primary']}20;
                color: {colors['primary']};
            }}
            #nav_button:pressed {{
                background-color: {colors['primary']}30;
            }}
            
            /* Special Buttons */
            #bookmarks_button {{
                color: {colors['accent']};
            }}
            #downloads_button {{
                color: {colors['primary']};
            }}
        """)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # Create menus
        self.create_menus()
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Navigation buttons with modern icons
        back_button = QPushButton("←")
        back_button.setObjectName("nav_button")
        back_button.setToolTip("Back")
        back_button.setFixedSize(36, 36)
        back_button.clicked.connect(self.controller.back)
        
        forward_button = QPushButton("→")
        forward_button.setObjectName("nav_button")
        forward_button.setToolTip("Forward")
        forward_button.setFixedSize(36, 36)
        forward_button.clicked.connect(self.controller.forward)
        
        refresh_button = QPushButton("↻")
        refresh_button.setObjectName("nav_button")
        refresh_button.setToolTip("Refresh")
        refresh_button.setFixedSize(36, 36)
        refresh_button.clicked.connect(self.controller.refresh)
        
        home_button = QPushButton("⌂")
        home_button.setObjectName("nav_button")
        home_button.setToolTip("Home")
        home_button.setFixedSize(36, 36)
        home_button.clicked.connect(self.controller.go_home)
        
        # URL bar with modern style
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search term...")
        self.url_bar.returnPressed.connect(self.handle_url_entered)
        
        # Go button
        go_button = QPushButton("→")
        go_button.setObjectName("nav_button")
        go_button.setFixedSize(36, 36)
        go_button.clicked.connect(self.handle_url_entered)
        
        # Bookmarks button
        bookmarks_button = QPushButton("★")
        bookmarks_button.setObjectName("bookmarks_button")
        bookmarks_button.setToolTip("Bookmarks")
        bookmarks_button.setFixedSize(36, 36)
        bookmarks_button.clicked.connect(self.controller.show_bookmarks)
        
        # Downloads button
        downloads_button = QPushButton("↓")
        downloads_button.setObjectName("downloads_button")
        downloads_button.setToolTip("Downloads")
        downloads_button.setFixedSize(36, 36)
        downloads_button.clicked.connect(self.controller.show_download_manager)
        
        # Add widgets to toolbar with proper spacing
        self.toolbar.addWidget(back_button)
        self.toolbar.addWidget(forward_button)
        self.toolbar.addWidget(refresh_button)
        self.toolbar.addWidget(home_button)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.url_bar)
        self.toolbar.addWidget(go_button)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(bookmarks_button)
        self.toolbar.addWidget(downloads_button)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.controller.close_tab)
        self.tab_widget.currentChanged.connect(self.controller.tab_changed)
        layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def create_menus(self):
        # File menu
        file_menu = self.menu_bar.addMenu("File")
        new_tab_action = file_menu.addAction("New Tab")
        new_tab_action.triggered.connect(self.controller.new_tab)
        
        # Bookmarks menu
        bookmarks_menu = self.menu_bar.addMenu("Bookmarks")
        add_bookmark_action = bookmarks_menu.addAction("Add Bookmark")
        show_bookmarks_action = bookmarks_menu.addAction("Show Bookmarks")
        add_bookmark_action.triggered.connect(self.controller.add_bookmark)
        show_bookmarks_action.triggered.connect(self.controller.show_bookmarks)
        
        # Settings menu
        settings_menu = self.menu_bar.addMenu("Settings")
        browser_settings_action = settings_menu.addAction("Browser Settings")
        cache_settings_action = settings_menu.addAction("Cache Settings")
        proxy_settings_action = settings_menu.addAction("Proxy Settings")
        browser_settings_action.triggered.connect(self.controller.show_settings)
        cache_settings_action.triggered.connect(self.controller.show_cache_settings)
        proxy_settings_action.triggered.connect(self.controller.show_proxy_settings)
    
    def handle_url_entered(self):
        url = self.url_bar.text().strip()
        if url:
            self.controller.navigate_to_url(url)
    
    def setup_connections(self):
        # Connect download handler to the profile
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.controller.handle_download)
    
    def add_new_tab(self, url=None):
        tab = TabView(self.controller)
        index = self.tab_widget.addTab(tab, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        
        if url:
            tab.web_view.setUrl(QUrl(url))
        
        return tab
    
    def get_current_tab(self):
        return self.tab_widget.currentWidget()
    
    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
    
    def update_tab_title(self, tab, title):
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, title)
    
    def show_status_message(self, message, timeout=3000):
        self.status_bar.showMessage(message, timeout)
    
    def update_settings(self, settings):
        # Update any settings that affect the UI
        pass
    
    def update_bookmarks(self, bookmarks):
        # Update bookmarks menu
        pass 