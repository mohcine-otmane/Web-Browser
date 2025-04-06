import sys
import os
from PySide6.QtWidgets import QApplication
from controllers.browser_controller import BrowserController
from views.browser_window import BrowserWindow
from config.settings import WEBENGINE_FLAGS, ENV_SETTINGS

def main():
    # Set environment variables
    for key, value in ENV_SETTINGS.items():
        os.environ[key] = value
    
    # Set WebEngine flags
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(WEBENGINE_FLAGS)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create controller first
    controller = BrowserController()
    
    # Create view and set it in controller
    view = BrowserWindow(controller)
    controller.set_view(view)
    
    # Show the window
    view.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 