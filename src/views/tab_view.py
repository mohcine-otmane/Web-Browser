from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from models.web_page_model import WebPageModel

class TabView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.web_view = QWebEngineView()
        self.web_page = WebPageModel()
        self.web_page.browser = controller
        self.web_view.setPage(self.web_page)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def setup_connections(self):
        self.web_view.titleChanged.connect(self.handle_title_changed)
        self.web_view.urlChanged.connect(self.handle_url_changed)
        self.web_view.loadFinished.connect(self.handle_load_finished)
    
    def load_url(self, url):
        self.web_view.setUrl(QUrl(url))
    
    def handle_title_changed(self, title):
        if self.controller:
            self.controller.update_tab_title(self, title)
    
    def handle_url_changed(self, url):
        if self.controller:
            self.controller.update_tab_url(self, url)
    
    def handle_load_finished(self, success):
        if self.controller:
            if success:
                self.controller.show_status_message("Page loaded successfully")
            else:
                error = self.web_page.last_error
                if error:
                    self.controller.show_status_message(f"Error loading page: {error.errorString()}")
    
    def back(self):
        self.web_view.back()
    
    def forward(self):
        self.web_view.forward()
    
    def reload(self):
        self.web_view.reload()
    
    def stop(self):
        self.web_view.stop() 