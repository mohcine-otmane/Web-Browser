import os
import json
from PySide6.QtCore import QObject, QUrl, QStandardPaths, QSettings, Qt, Signal
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QListWidget, QListWidgetItem, QPushButton)
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest, QWebEnginePage, QWebEngineSettings
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
        # Create model with this controller as parent to ensure proper lifecycle
        self.model = BrowserModel()
        self.model.setParent(self)
        
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
        
        # Setup browser profile
        self.setup_browser_profile()
        
        # Apply proxy settings
        self.apply_proxy_settings()
    
    def get_theme_colors(self):
        """Get the theme colors for the browser UI."""
        return {
            'primary': '#2563eb',
            'primary_hover': '#1d4ed8',
            'primary_pressed': '#1e40af',
            'background': '#ffffff',
            'surface': '#f8fafc',
            'border': '#e2e8f0',
            'text': '#000000',
            'text_secondary': '#000000',
            'accent': '#f59e0b',
            'danger': '#ef4444',
            'success': '#10b981',
            'shadow': 'rgba(0, 0, 0, 0.1)'
        }
    
    def set_view(self, view: 'BrowserWindow'):
        """Set the view and initialize it."""
        self.view = view
        
        # Add initial tab after view is set
        self.new_tab()
        
        # Connect model signals to view using more robust connection
        if self.model:
            try:
                self.model.url_changed.connect(
                    self.view.update_url_bar,
                    type=Qt.QueuedConnection  # Use queued connection
                )
                self.model.title_changed.connect(
                    lambda title: self.view.setWindowTitle(f"{title} - SandFlea"),
                    type=Qt.QueuedConnection
                )
                self.model.status_message.connect(
                    self.view.status_bar.showMessage,
                    type=Qt.QueuedConnection
                )
            except Exception as e:
                print(f"Error connecting signals: {str(e)}")
    
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
    
    def setup_browser_profile(self):
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()
        
        # Basic settings with hardware acceleration disabled
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)  # Disable WebGL
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        
        # Content settings
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
        
        # Custom user agent
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36 "
            "SandFlea/1.0"
        )
    
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
        """Update the URL bar and model with the new URL.
        
        Args:
            tab: The tab being updated
            url: QUrl object or string representing the new URL
        """
        if not self.view:
            return
            
        try:
            # Convert to string if it's a QUrl
            url_str = url.toString() if hasattr(url, 'toString') else str(url)
            
            # Update UI first
            self.view.update_url_bar(url_str)
            
            # Then update model
            if not self.model:
                return
                
            self.model.set_url(url_str)
            
        except RuntimeError as e:
            # Log error but don't crash
            print(f"Error updating URL: {str(e)}")
        except Exception as e:
            print(f"Unexpected error updating URL: {str(e)}")
    
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
    
    def show_status_message(self, message: str, timeout=3000, urgency="normal"):
        """Show a status message with specified urgency level.
        
        Args:
            message: The message to display
            timeout: How long to show the message (in ms)
            urgency: One of "normal", "high", "success"
        """
        if self.view:
            self.view.status_bar.setProperty("urgency", urgency)
            self.view.status_bar.showMessage(message, timeout)
            self.view.status_bar.style().unpolish(self.view.status_bar)
            self.view.status_bar.style().polish(self.view.status_bar)
    
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
    
    def show_error(self, title: str, message: str):
        """Show an error message box."""
        if self.view and not self.view.isHidden():
            self.view.status_bar.showMessage(message, 3000)
            QMessageBox(
                QMessageBox.Critical,
                title,
                message,
                QMessageBox.Ok,
                self.view
            ).exec()
        else:
            QMessageBox(
                QMessageBox.Critical,
                title,
                message,
                QMessageBox.Ok,
                None
            ).exec()
    
    def handle_download(self, download: QWebEngineDownloadRequest):
        try:
            # Get the download URL and suggested filename
            url = download.url().toString()
            suggested_filename = download.suggestedFileName()
            if not suggested_filename:
                suggested_filename = os.path.basename(url) or "download"
            
            # Get default download path from settings
            default_path = self.settings.get("download_path", 
                QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
            
            # Ensure default download directory exists
            try:
                os.makedirs(default_path, exist_ok=True)
            except Exception as e:
                self.show_error("Download Error", f"Failed to create download directory: {str(e)}")
                download.cancel()
                return
            
            # Create download dialog with default path
            dialog = DownloadDialog(url, self.view)
            dialog.set_default_path(os.path.join(default_path, suggested_filename))
            
            if dialog.exec() != QDialog.Accepted:
                download.cancel()
                return
            
            # Get the selected save path
            save_path = dialog.get_save_path()
            if not save_path:
                self.show_error("Download Error", "No save path selected")
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
            self.show_error("Download Error", error_msg)
            if download:
                download.cancel()
            if 'dialog' in locals():
                dialog.close()
    
    def _on_download_progress(self, filename: str, progress: int):
        """Handle download progress updates."""
        self.show_status_message(
            f"Downloading {filename}: {progress}%",
            urgency="normal"
        )
        if self.download_manager:
            for download_id, info in self.downloader.active_downloads.items():
                if info['filename'] == filename:
                    self.download_manager.update_progress(download_id, progress)
                    break
    
    def _on_download_finished(self, filename: str, success: bool):
        """Handle download completion."""
        status = "Completed" if success else "Cancelled"
        urgency = "success" if success else "high"
        self.show_status_message(
            f"Download {status.lower()}: {filename}",
            urgency=urgency
        )
        if self.download_manager:
            for download_id, info in self.downloader.active_downloads.items():
                if info['filename'] == filename:
                    self.download_manager.update_status(download_id, status)
                    break
    
    def _on_download_error(self, filename: str, error: str):
        """Handle download errors."""
        self.show_status_message(
            f"Download failed: {filename}",
            urgency="high"
        )
        self.show_error("Download Error", error)
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
            self.show_status_message(
                f"Error loading page: {str(e)}", 
                3000,
                urgency="high"
            )
    
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