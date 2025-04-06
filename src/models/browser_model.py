"""
Browser Model
"""

import json
import os
from PySide6.QtCore import QObject, Signal, QStandardPaths
from config.settings import DEFAULT_SETTINGS

class BrowserModel(QObject):
    # Signals
    url_changed = Signal(str)
    title_changed = Signal(str)
    status_message = Signal(str)
    settings_changed = Signal(dict)
    bookmarks_changed = Signal(list)
    
    def __init__(self, parent=None):
        """Initialize the browser model with proper parent ownership."""
        super().__init__(parent)
        self._url = ""
        self._title = ""
        self._settings = DEFAULT_SETTINGS.copy()
        self._bookmarks = []
        self.load_settings()
        self.load_bookmarks()
    
    def set_url(self, url):
        """Set the current URL and emit the change signal."""
        if self._url != url:
            self._url = url
            self.url_changed.emit(url)
    
    def set_title(self, title):
        """Set the current title and emit the change signal."""
        if self._title != title:
            self._title = title
            self.title_changed.emit(title)
    
    def show_status_message(self, message):
        """Show a status message."""
        self.status_message.emit(message)
    
    @property
    def current_url(self):
        """Get the current URL."""
        return self._url
    
    @property
    def current_title(self):
        """Get the current title."""
        return self._title
    
    def load_settings(self):
        # Load settings from QSettings
        settings = QSettings()
        for key, default_value in DEFAULT_SETTINGS.items():
            self._settings[key] = settings.value(key, default_value)
        
        # Ensure download path exists
        os.makedirs(self._settings["download_path"], exist_ok=True)
    
    def save_settings(self):
        # Save settings to QSettings
        settings = QSettings()
        for key, value in self._settings.items():
            settings.setValue(key, value)
        settings.sync()
        self.settings_changed.emit(self._settings)
    
    def update_setting(self, key, value):
        if key in self._settings:
            self._settings[key] = value
            self.save_settings()
    
    def load_bookmarks(self):
        # Load bookmarks from QSettings
        settings = QSettings()
        self._bookmarks = settings.value("bookmarks", [])
    
    def save_bookmarks(self):
        # Save bookmarks to QSettings
        settings = QSettings()
        settings.setValue("bookmarks", self._bookmarks)
        settings.sync()
        self.bookmarks_changed.emit(self._bookmarks)
    
    def add_bookmark(self, title, url):
        # Check if bookmark already exists
        for bookmark in self._bookmarks:
            if bookmark["url"] == url:
                return False
        
        # Add new bookmark
        self._bookmarks.append({
            "title": title,
            "url": url
        })
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, url):
        # Remove bookmark if it exists
        for i, bookmark in enumerate(self._bookmarks):
            if bookmark["url"] == url:
                del self._bookmarks[i]
                self.save_bookmarks()
                return True
        return False
    
    def load_settings(self):
        try:
            with open("browser_settings.json", "r") as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        with open("browser_settings.json", "w") as f:
            json.dump(self._settings, f)
    
    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_bookmarks(self):
        with open("bookmarks.json", "w") as f:
            json.dump(self._bookmarks, f)
    
    def add_bookmark(self, title, url):
        if not any(b["url"] == url for b in self._bookmarks):
            self._bookmarks.append({
                "title": title,
                "url": url
            })
            self.save_bookmarks()
            self.bookmarks_changed.emit(self._bookmarks)
            return True
        return False
    
    def delete_bookmark(self, url):
        self._bookmarks = [b for b in self._bookmarks if b["url"] != url]
        self.save_bookmarks()
        self.bookmarks_changed.emit(self._bookmarks) 