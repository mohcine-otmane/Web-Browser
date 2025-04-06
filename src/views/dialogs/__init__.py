"""
Browser Dialogs Package
"""

from .settings_dialog import SettingsDialog
from .proxy_dialog import ProxyDialog
from .bookmarks_dialog import BookmarksDialog
from .add_bookmark_dialog import AddBookmarkDialog
from .download_dialog import DownloadDialog
from .cache_settings_dialog import CacheSettingsDialog

__all__ = [
    'SettingsDialog',
    'ProxyDialog',
    'BookmarksDialog',
    'AddBookmarkDialog',
    'DownloadDialog',
    'CacheSettingsDialog'
] 