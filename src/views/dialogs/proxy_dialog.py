from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel, QSpinBox)
from PySide6.QtCore import QSettings

class ProxyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Proxy Settings")
        self.setMinimumWidth(400)
        self.setObjectName("ProxyDialog")
        
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Proxy type
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["No Proxy", "HTTP", "SOCKS5"])
        layout.addRow("Proxy Type:", self.proxy_type)
        
        # Host
        self.host_edit = QLineEdit()
        layout.addRow("Host:", self.host_edit)
        
        # Port
        self.port_edit = QSpinBox()
        self.port_edit.setRange(1, 65535)
        layout.addRow("Port:", self.port_edit)
        
        # Username
        self.username_edit = QLineEdit()
        layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        layout.addRow("", button_layout)
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        settings = QSettings()
        self.proxy_type.setCurrentText(settings.value("proxy_type", "No Proxy"))
        self.host_edit.setText(settings.value("proxy_host", ""))
        self.port_edit.setValue(int(settings.value("proxy_port", 0)))
        self.username_edit.setText(settings.value("proxy_username", ""))
        self.password_edit.setText(settings.value("proxy_password", ""))
    
    def save_settings(self):
        settings = QSettings()
        settings.setValue("proxy_type", self.proxy_type.currentText())
        settings.setValue("proxy_host", self.host_edit.text())
        settings.setValue("proxy_port", self.port_edit.value())
        settings.setValue("proxy_username", self.username_edit.text())
        settings.setValue("proxy_password", self.password_edit.text())