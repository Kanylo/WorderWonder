import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from ui_main import MainWindow
from convertapi_cli import check_api_status

def load_stylesheet(path):
    """Load and return the content of a QSS stylesheet file."""
    if not os.path.exists(path):
        return ""
    
    with open(path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application name and organization
    app.setApplicationName("Worder-Wonder")
    app.setOrganizationName("Worder-Wonder Team")
    
    # Set application icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Load stylesheet if available
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
    if os.path.exists(style_path):
        app.setStyleSheet(load_stylesheet(style_path))
    
    # Check if ConvertAPI CLI is available
    if not check_api_status():
        QMessageBox.warning(
            None, 
            "API Not Available", 
            "The ConvertAPI CLI tool is not available or not configured correctly. "
            "Some functionality may be limited."
        )
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())