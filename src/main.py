import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import Qt, QCoreApplication
from controllers.browser_controller import BrowserController
from views.browser_window import BrowserWindow
from config.settings import WEBENGINE_FLAGS, ENV_SETTINGS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configure environment variables before Qt initialization"""
    # Set High DPI handling first
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    # Configure certificate handling
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--ignore-certificate-errors "
        "--ignore-ssl-errors "
        "--disable-web-security "
        "--no-sandbox "
        "--use-angle=d3d11 "
        "--enable-features=UseOzonePlatform "
        "--ozone-platform=windows "
        "--in-process-gpu"
    )
    
    # WebEngine setup
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

def main():
    try:
        # Setup environment first - before QApplication
        setup_environment()
        
        logger.info("Starting browser application...")
        
        # Create application
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Load and apply QSS stylesheet
        try:
            style_path = os.path.join(os.path.dirname(__file__), "style.qss")
            if os.path.exists(style_path):
                with open(style_path, "r", encoding='utf-8') as f:
                    app.setStyleSheet(f.read())
                logger.info("Custom stylesheet loaded successfully")
            else:
                logger.error(f"Style file not found: {style_path}")
        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")
        
        app.setQuitOnLastWindowClosed(True)
        
        logger.info("QApplication created successfully")
        
        # Initialize WebEngine profile
        try:
            profile = QWebEngineProfile.defaultProfile()
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            logger.info("WebEngine profile initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebEngine profile: {e}")
            return 1
        
        # Create controller and keep reference
        try:
            controller = BrowserController()
            # Keep reference to prevent deletion
            app.controller = controller  
            logger.info("Browser controller created")
        except Exception as e:
            logger.error(f"Failed to create controller: {e}")
            return 1
        
        # Create and show view
        try:
            view = BrowserWindow(controller)
            controller.set_view(view)
            view.show()
            logger.info("Browser window created and shown")
        except Exception as e:
            logger.error(f"Failed to create window: {e}")
            return 1
        
        # Run application
        logger.info("Starting main event loop")
        return app.exec()
    
    except Exception as e:
        logger.error(f"Critical startup error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())