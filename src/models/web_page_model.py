from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtCore import QUrl
from config.settings import USER_AGENTS
import random

class WebPageModel(QWebEnginePage):
    def __init__(self, profile=None, parent=None):
        super().__init__(profile or QWebEngineProfile.defaultProfile(), parent)
        self.browser = None
        self.last_error = None
        self.last_request_time = 0
        self.min_request_delay = 3.0
        
        # Set up profile
        self.setup_profile()
        
        # Configure settings
        self.setup_settings()
        
        # Set up proxy
        self.setup_proxy()
    
    def setup_profile(self):
        profile = self.profile()
        profile.setHttpUserAgent(self.get_random_user_agent())
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
    
    def setup_settings(self):
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.NavigateOnDropEnabled, True)
    
    def setup_proxy(self):
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
    
    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)
    
    def certificateError(self, certificateError):
        if self.browser:
            self.browser.show_status_message("SSL Certificate Error")
        return True
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.browser:
            self.browser.show_status_message(f"JavaScript: {message}")
    
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            if self.browser:
                self.browser.navigate_to_url(url)
                return False
        return True
    
    def createWindow(self, _type):
        if self.browser:
            new_tab = self.browser.new_tab()
            return new_tab.web_page
        return None
    
    def modify_google_search_url(self, url):
        params = {
            "client": random.choice(["firefox-b-d", "chrome-b-d", "safari-b-d"]),
            "source": random.choice(["hp", "web", "desktop"]),
            "ei": f"random{random.randint(1000, 9999)}",
            "oq": "",
            "gs_lp": "",
            "ved": f"0ahUKEw{random.randint(1000, 9999)}",
            "uact": random.randint(1, 5),
            "tbs": random.choice(["", "qdr:h", "qdr:d", "qdr:w", "qdr:m"]),
            "safe": random.choice(["active", "off"]),
            "pws": random.choice(["0", "1"]),
            "gws_rd": random.choice(["cr", "ssl"]),
            "hl": random.choice(["en", "en-US", "en-GB"]),
            "gl": random.choice(["us", "gb", "ca", "au"]),
            "num": random.choice(["10", "20", "30"]),
            "start": str(random.randint(0, 100)),
            "filter": random.choice(["0", "1"]),
            "nfpr": random.choice(["0", "1"]),
            "complete": random.choice(["0", "1"]),
            "newwindow": random.choice(["0", "1"]),
            "tbm": random.choice(["", "isch", "vid", "nws"]),
            "tbo": random.choice(["0", "1"]),
            "tbs": random.choice(["", "qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]),
            "sourceid": random.choice(["chrome", "firefox", "safari"]),
            "ie": "UTF-8",
            "oe": "UTF-8"
        }
        
        url_str = url.toString()
        for key, value in params.items():
            if f"{key}=" not in url_str:
                url_str += f"&{key}={value}"
        
        return QUrl(url_str)
    
    def handleError(self, error):
        self.last_error = error
        return super().handleError(error) 