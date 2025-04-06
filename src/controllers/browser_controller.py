import os
import json
from PySide6.QtCore import QObject, QUrl, QStandardPaths, QSettings, Qt, Signal
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton)
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest, QWebEnginePage
from models.browser_model import BrowserModel
from views.dialogs import (SettingsDialog, CacheSettingsDialog, ProxyDialog, 
                         BookmarksDialog, AddBookmarkDialog, DownloadDialog,
                         DownloadManagerDialog)
from typing import TYPE_CHECKING
from .file_downloader import FileDownloader

if TYPE_CHECKING:
    from views.browser_window import BrowserWindow
    from views.tab_view import TabView

class BrowserController(QObject):
    def __init__(self):
        super().__init__()
        self.model = BrowserModel()
        self.view = None  # Will be set after BrowserWindow is created
        self.settings = self.load_settings()
        self.bookmarks = self.load_bookmarks()
        
        # Create file downloader
        self.downloader = FileDownloader(self)
        self.downloader.download_progress.connect(self._on_download_progress)
        self.downloader.download_finished.connect(self._on_download_finished)
        self.downloader.download_error.connect(self._on_download_error)
        
        # Create download manager dialog
        self.download_manager = None
        
        # Setup cache
        self.setup_cache()
        
        # Apply proxy settings
        self.apply_proxy_settings()
    
    def set_view(self, view: 'BrowserWindow'):
        self.view = view
        # Add initial tab after view is set
        self.new_tab()
    
    def setup_cache(self):
        # Get or create cache directory
        cache_path = self.settings.get("cache_path", 
            os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "web_browser"))
        os.makedirs(cache_path, exist_ok=True)
        
        # Setup cache settings
        cache_size = self.settings.get("cache_size", 100) * 1024 * 1024  # Convert MB to bytes
        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath(cache_path)
        profile.setHttpCacheMaximumSize(cache_size)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
    
    def update_cache_settings(self):
        cache_path = self.settings.get("cache_path", 
            os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "web_browser"))
        cache_size = self.settings.get("cache_size", 100) * 1024 * 1024
        
        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath(cache_path)
        profile.setHttpCacheMaximumSize(cache_size)
    
    def load_settings(self):
        try:
            with open("browser_settings.json", "r") as f:
                settings = json.load(f)
        except:
            settings = {
                "home_page": "https://www.bing.com",
                "search_engine": "Bing",
                "download_path": QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
                "cache_size": 100,
                "cache_path": os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "web_browser")
            }
        return settings
    
    def load_bookmarks(self):
        try:
            with open("bookmarks.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_bookmarks(self):
        with open("bookmarks.json", "w") as f:
            json.dump(self.bookmarks, f)
    
    def show(self):
        self.view.show()
    
    def new_tab(self, url=None):
        if not url and self.settings:
            url = self.settings["home_page"]
        return self.view.add_new_tab(url)
    
    def close_tab(self, index):
        if self.view.tab_widget.count() > 1:
            self.view.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self.view, "Cannot Close Tab", "You must have at least one tab open.")
    
    def tab_changed(self, index):
        if index >= 0:
            current_tab = self.view.tab_widget.widget(index)
            self.view.update_url_bar(current_tab.web_view.url())
    
    def update_tab_title(self, tab, title):
        self.view.update_tab_title(tab, title)
    
    def update_tab_url(self, tab, url):
        self.view.update_url_bar(url)
        self.model.set_url(url.toString())
    
    def back(self):
        current_tab = self.view.get_current_tab()
        if current_tab and current_tab.web_view.history().canGoBack():
            current_tab.web_view.back()
    
    def forward(self):
        current_tab = self.view.get_current_tab()
        if current_tab and current_tab.web_view.history().canGoForward():
            current_tab.web_view.forward()
    
    def refresh(self):
        current_tab = self.view.get_current_tab()
        if current_tab:
            current_tab.web_view.reload()
    
    def go_home(self):
        if self.settings:
            self.navigate_to_url(self.settings["home_page"])
    
    def navigate_to_url(self, url):
        current_tab = self.view.get_current_tab()
        if current_tab:
            if isinstance(url, str):
                url = QUrl.fromUserInput(url)
            current_tab.web_view.setUrl(url)
    
    def update_url(self, url):
        self.model.set_url(url)
    
    def load_started(self):
        self.view.status_bar.showMessage("Loading...")
    
    def show_status_message(self, message, timeout=3000):
        self.view.status_bar.showMessage(message, timeout)
    
    def show_settings(self):
        dialog = SettingsDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            dialog.save_settings()
            self.settings = self.load_settings()
            self.update_cache_settings()
    
    def show_cache_settings(self):
        dialog = CacheSettingsDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            dialog.save_settings()
            self.update_cache_settings()
    
    def show_proxy_settings(self):
        dialog = ProxyDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            dialog.save_settings()
            self.apply_proxy_settings()
    
    def show_bookmarks(self):
        dialog = BookmarksDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            self.bookmarks = self.load_bookmarks()
    
    def add_bookmark(self):
        current_tab = self.view.get_current_tab()
        if current_tab:
            dialog = AddBookmarkDialog(current_tab.web_view.url().toString(), 
                                     current_tab.web_view.title(), self.view)
            if dialog.exec() == QDialog.Accepted:
                if dialog.save_bookmark():
                    self.bookmarks = self.load_bookmarks()
                    self.view.status_bar.showMessage("Bookmark added!", 3000)
    
    def show_download_manager(self):
        """Show the download manager dialog."""
        if not self.download_manager:
            self.download_manager = DownloadManagerDialog(self.view)
        self.download_manager.show()
    
    def handle_download(self, download: QWebEngineDownloadRequest):
        try:
            # Get the download URL and suggested filename
            url = download.url().toString()
            suggested_filename = download.suggestedFileName()
            if not suggested_filename:
                suggested_filename = "download"
            
            # Create download dialog
            dialog = DownloadDialog(url, self.view)
            if dialog.exec() != QDialog.Accepted:
                download.cancel()
                return
            
            # Get the selected save path
            save_path = dialog.get_save_path()
            if not save_path:
                download.cancel()
                dialog.close()
                return
            
            # Show download manager if not visible
            self.show_download_manager()
            
            # Add download to manager
            self.download_manager.add_download(download.id(), os.path.basename(save_path))
            
            # Start the download using our FileDownloader
            self.downloader.start_download(download, save_path, dialog)
            
        except Exception as e:
            error_msg = f"Failed to start download: {str(e)}"
            QMessageBox.critical(
                self.view,
                "Download Error",
                error_msg
            )
            self.view.show_status_message(error_msg)
            if download:
                download.cancel()
            if 'dialog' in locals():
                dialog.close()
    
    def _on_download_progress(self, filename: str, progress: int):
        """Handle download progress updates."""
        self.view.show_status_message(f"Downloading {filename}: {progress}%")
        if self.download_manager:
            for download_id, info in self.downloader.active_downloads.items():
                if info['filename'] == filename:
                    self.download_manager.update_progress(download_id, progress)
                    break
    
    def _on_download_finished(self, filename: str, success: bool):
        """Handle download completion."""
        status = "Completed" if success else "Cancelled"
        self.view.show_status_message(f"Download {status.lower()}: {filename}")
        if self.download_manager:
            for download_id, info in self.downloader.active_downloads.items():
                if info['filename'] == filename:
                    self.download_manager.update_status(download_id, status)
                    break
    
    def _on_download_error(self, filename: str, error: str):
        """Handle download errors."""
        error_msg = f"Download error ({filename}): {error}"
        self.view.show_status_message(error_msg)
        QMessageBox.critical(
            self.view,
            "Download Error",
            error_msg
        )
        if self.download_manager:
            for download_id, info in self.downloader.active_downloads.items():
                if info['filename'] == filename:
                    self.download_manager.update_status(download_id, "Failed")
                    break
    
    def get_current_tab(self):
        return self.view.get_current_tab()
    
    def navigate(self):
        url = self.view.url_bar.text().strip()
        if not url:
            return
        
        try:
            if not url.startswith(('http://', 'https://')):
                if '.' in url:
                    url = 'https://' + url
                else:
                    # Use selected search engine
                    search_engine = self.settings.get("search_engine", "Bing")
                    if search_engine == "Google":
                        url = f'https://www.google.com/search?q={url}'
                    elif search_engine == "DuckDuckGo":
                        url = f'https://duckduckgo.com/?q={url}'
                    else:  # Bing
                        url = f'https://www.bing.com/search?q={url}'
            
            # Create QUrl with relaxed parsing
            qurl = QUrl.fromUserInput(url)
            self.navigate_to_url(qurl)
        except Exception as e:
            self.view.status_bar.showMessage(f"Error loading page: {str(e)}", 3000)
    
    def apply_proxy_settings(self):
        settings = QSettings()
        proxy_type = settings.value("proxy/type", "No Proxy")
        
        if proxy_type == "No Proxy":
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
            return
        
        proxy = QNetworkProxy()
        if proxy_type == "HTTP":
            proxy.setType(QNetworkProxy.HttpProxy)
        else:
            proxy.setType(QNetworkProxy.Socks5Proxy)
        
        proxy.setHostName(settings.value("proxy/host", ""))
        proxy.setPort(int(settings.value("proxy/port", "0")))
        
        if settings.value("proxy/use_auth", False, type=bool):
            proxy.setUser(settings.value("proxy/username", ""))
            proxy.setPassword(settings.value("proxy/password", ""))
        
        QNetworkProxy.setApplicationProxy(proxy) 