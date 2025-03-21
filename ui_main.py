import os
import mimetypes
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFrame, 
    QFileDialog, QMessageBox, QApplication, QScrollArea
)
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
import time

from helpers import get_file_extension, format_conversion_message
from convertapi_cli import convert_file, get_available_formats

class DropArea(QFrame):
    """Custom widget to handle drag and drop operations for files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setAcceptDrops(True)
        self.setMinimumSize(200, 100)
        
        # Layout
        layout = QVBoxLayout()
        
        # Label for instructions
        self.label = QLabel("Drag & Drop<br>Here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Add "Or click to choose file" text
        self.click_label = QLabel("Or click to chose file")
        self.click_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.click_label.setStyleSheet("color: #3498db; margin-top: 10px;")
        layout.addWidget(self.click_label)
        
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle when a drag enters the widget area."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle when a file is dropped into the widget."""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            # Get the first URL (assuming single file drop)
            url = mime_data.urls()[0]
            file_path = url.toLocalFile()
            
            # Emit signal to parent to handle the file
            self.parent().handle_file_selected(file_path)
            
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worder-Wonder Converter")
        self.resize(600, 400)  # Set initial size
        self.current_file_path = None
        self.file_format = None
        self.setup_ui()
        
    def setup_ui(self):
        # Create a central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Main layout split into left and right
        
        # Clear any previous messages
        self.messages = []
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Drop area (also clickable to choose file)
        self.drop_area = DropArea(self)
        self.drop_area.mousePressEvent = lambda event: self.choose_file()
        left_layout.addWidget(self.drop_area)
        
        # Add "or" label between drop area and button
        or_label = QLabel(" ")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(or_label)
        
        # Choose file button
        choose_file_btn = QPushButton("Choose File")
        choose_file_btn.clicked.connect(self.choose_file)
        left_layout.addWidget(choose_file_btn)
        
        left_panel.setLayout(left_layout)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Message area (chatbox style)
        self.message_area = QFrame()
        self.message_area.setObjectName("messageArea")
        self.message_area.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        message_layout = QVBoxLayout()
        
        # Messages will be displayed here in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.message_box = QLabel()
        self.message_box.setObjectName("messageBox")
        self.message_box.setWordWrap(True)
        self.message_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.message_box.setMinimumHeight(150)
        self.message_box.setTextFormat(Qt.TextFormat.RichText)
        
        scroll_area.setWidget(self.message_box)
        message_layout.addWidget(scroll_area)
        
        self.message_area.setLayout(message_layout)
        right_layout.addWidget(self.message_area)
        
        # Format selection section
        format_section = QWidget()
        format_layout = QHBoxLayout()
        
        format_label = QLabel("Choose file format to convert:")
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.setEnabled(False)  # Disable until a file is selected
        format_layout.addWidget(self.format_combo)
        
        format_section.setLayout(format_layout)
        right_layout.addWidget(format_section)
        
        # Convert button
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setObjectName("convert_btn")
        self.convert_btn.clicked.connect(self.convert_file)
        self.convert_btn.setEnabled(False)  # Disable until a file is selected
        right_layout.addWidget(self.convert_btn)
        
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)  # 1/3 of width
        main_layout.addWidget(right_panel, 2)  # 2/3 of width
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def choose_file(self):
        """Open a file dialog to choose a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose File", "", "All Files (*.*)"
        )
        
        if file_path:
            self.handle_file_selected(file_path)
    
    def handle_file_selected(self, file_path):
        """Process the selected file."""
        self.current_file_path = file_path
        self.file_format = get_file_extension(file_path)
        
        # Update UI with file information
        file_name = os.path.basename(file_path)
        file_format_display = self.file_format[1:] if self.file_format.startswith('.') else self.file_format
        
        # Add file information to message box
        self.add_message(f"<b>File:</b> {file_name}")
        self.add_message(f"<b>Detected file format:</b> {file_format_display}")
        
        # Get available conversion formats
        available_formats = get_available_formats(self.file_format)
        
        # Clear and update the format combo box
        self.format_combo.clear()
        if available_formats:
            self.format_combo.addItems(available_formats)
            self.format_combo.setEnabled(True)
            self.convert_btn.setEnabled(True)
            self.add_message("<b>Ready to convert.</b> Select a format and click Convert.")
        else:
            self.format_combo.setEnabled(False)
            self.convert_btn.setEnabled(False)
            self.add_message("<b>No conversion formats available</b> for this file type.")
    
    def add_message(self, message):
        """Add a message to the message box."""
        current_text = self.message_box.text()
        timestamp = ""  # You can add a timestamp if desired: f"<span class='timestamp'>{time.strftime('%H:%M:%S')}</span> "
        
        if current_text:
            # Add new message below existing ones
            new_text = f"{current_text}<div class='message'>{timestamp}{message}</div>"
        else:
            new_text = f"<div class='message'>{timestamp}{message}</div>"
        self.message_box.setText(new_text)
        
        # Ensure the most recent message is visible
        QApplication.processEvents()
    
    def convert_file(self):
        """Convert the file to the selected format."""
        if not self.current_file_path or not self.format_combo.currentText():
            return
        
        target_format = self.format_combo.currentText()
        
        # Update UI to show conversion is in progress
        self.add_message("<b>Converting...</b> Please wait.")
        self.convert_btn.setEnabled(False)
        
        # Perform the conversion
        result = convert_file(self.current_file_path, target_format)
        
        # Display result
        message = format_conversion_message(self.current_file_path, result)
        self.add_message(f"<b>Conversion complete:</b> {message}")
        
        # Re-enable the convert button
        self.convert_btn.setEnabled(True)