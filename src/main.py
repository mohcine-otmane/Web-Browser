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
    # Basic environment setup
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--no-sandbox "
        "--disable-gpu-compositing "
        "--use-angle=d3d11 "  # Force ANGLE with D3D11
        "--enable-features=UseOzonePlatform "
        "--ozone-platform=windows "
        "--in-process-gpu "
        "--disable-gpu-process-crash-limit "
        "--disable-features=PreloadMediaEngagementData,AutoplayIgnoreWebAudio "
        "--no-first-run"
    )
    
    # Set Qt specific flags
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    # Modern DPI handling (replacement for deprecated attributes)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def main():
    try:
        # Setup environment first
        setup_environment()
        
        # Log startup sequence
        logger.info("Starting browser application...")
        
        # Create application
        app = QApplication(sys.argv)
        logger.info("QApplication created successfully")
        
        # Initialize WebEngine profile
        try:
            profile = QWebEngineProfile.defaultProfile()
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            logger.info("WebEngine profile initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebEngine profile: {e}")
            return 1
        
        # Create controller
        try:
            controller = BrowserController()
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