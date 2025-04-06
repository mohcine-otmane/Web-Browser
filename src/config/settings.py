import os
from PySide6.QtCore import QStandardPaths

# Browser Settings
DEFAULT_SETTINGS = {
    "home_page": "https://www.bing.com",
    "search_engine": "Bing",
    "download_path": QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
    "cache_size": 100,
    "cache_path": os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "web_browser")
}

# WebEngine Settings
WEBENGINE_FLAGS = [
    "--disable-gpu",
    "--disable-gpu-compositing",
    "--disable-gpu-rasterization",
    "--disable-gpu-sandbox",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
    "--disable-web-security",
    "--allow-insecure-localhost",
    "--disable-features=UseSkiaRenderer,UseVulkan",
    "--no-sandbox",
    "--disable-web-security",
    "--disable-proxy-service",
    "--no-proxy-server",
    "--host-resolver-rules='MAP * ~NOTFOUND, EXCLUDE localhost'",
    "--process-per-site"
]

# Environment Settings
ENV_SETTINGS = {
    "QT_QUICK_BACKEND": "software",
    "QT_OPENGL": "software",
    "QTWEBENGINE_DISABLE_GPU_PROCESS": "1",
    "QTWEBENGINE_DISABLE_SANDBOX": "1"
}

# Style Settings
STYLE_SETTINGS = """
    QMainWindow {
        background-color: #f0f0f0;
    }
    QToolBar {
        background-color: #ffffff;
        border-bottom: 1px solid #e0e0e0;
        padding: 5px;
        spacing: 5px;
    }
    QPushButton {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 30px;
        color: #444444;
    }
    QPushButton:hover {
        background-color: #f8f8f8;
        border-color: #d0d0d0;
    }
    QPushButton:pressed {
        background-color: #e8e8e8;
    }
    QLineEdit {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 5px;
        background-color: #ffffff;
        selection-background-color: #0078d4;
    }
    QLineEdit:focus {
        border-color: #0078d4;
    }
    QTabWidget::pane {
        border: none;
        background-color: #ffffff;
    }
    QTabBar::tab {
        background-color: #f8f8f8;
        border: 1px solid #e0e0e0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 12px;
        margin-right: 2px;
        color: #666666;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #0078d4;
        border-bottom: 2px solid #0078d4;
    }
    QTabBar::tab:hover:!selected {
        background-color: #f0f0f0;
        color: #444444;
    }
"""

# User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

DEFAULT_HOME_PAGE = "https://www.google.com"
DEFAULT_SEARCH_ENGINE = "https://www.google.com/search?q=" 