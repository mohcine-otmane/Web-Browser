"""
SandFlea Browser Package
"""

from .controllers import BrowserController
from .views import BrowserWindow, TabView
from .models import WebPageModel

__all__ = ['BrowserController', 'BrowserWindow', 'TabView', 'WebPageModel']

__version__ = "1.0.0" 