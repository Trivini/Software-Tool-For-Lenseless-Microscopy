import sys, os
import numpy as np
from datetime import datetime, timedelta
import hashlib
import platform
import subprocess
import cv2
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton, QMessageBox,
    QTextEdit, QFileDialog, QInputDialog, QListWidget, QDateTimeEdit,QGroupBox,QSpinBox,QDateEdit, QComboBox, QWidget, QDialogButtonBox, QFrame, QToolButton
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from PyQt5.QtGui import QPixmap, QPalette, QBrush, QResizeEvent,QIcon, QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QDateTime, QDate, QSize
import os

# Constants for file storage
USER_FILE = "users.txt"
HISTORY_FILE = "login_history.txt"
ORG_FILE = "orgs.txt"
ACTIVATION_FILE = os.path.join("data", "activation.dat")



# -- Role Selection Dialog --------------------------------------------------
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


ONE_DAY_KEY_HASH = "09537a467b353929f4d1a1cb879037920d61452fd713bdc2127ecb022bb267fc"  # TRIAL-1234-5678-9ABC
LIFETIME_KEY_HASH = "6453f3928e2063efe8ea40949f1137eec230fb05f12cf974f3397d57f5f90ff0"  # FULL-ABCD-EFGH-1234

def hash_key(key):
    """Hash the activation key using SHA-256"""
    return hashlib.sha256(key.encode()).hexdigest()

def check_activation():
    """Check if the software is activated"""
    if not os.path.exists(ACTIVATION_FILE):
        return False, None
    
    try:
        with open(ACTIVATION_FILE, 'r') as f:
            data = json.load(f)
            
        # Verify the activation data
        if 'type' not in data or 'expires' not in data:
            return False, None
        
        # Check if it's a lifetime activation
        if data['type'] == 'lifetime':
            return True, 'lifetime'
        
        # Check if the trial period is still valid
        if data['type'] == 'trial':
            # Parse expiration date
            expiry_date = datetime.fromisoformat(data['expires'])
            if datetime.now() < expiry_date:
                return True, 'trial'
            else:
                return False, 'expired'
    except Exception as e:
        print(f"Error checking activation: {e}")
        return False, None

class ActivationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Activation")
        self.resize(450, 280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Set styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#infoLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                selection-background-color: #e5e5e5;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton#activateButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                min-height: 40px;
            }
            QPushButton#activateButton:hover {
                background-color: #2980b9;
            }
            QFrame#separator {
                background-color: #e0e0e0;
                max-height: 1px;
                margin: 15px 0;
            }
        """)
        
        # Create UI
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title section
        title_label = QLabel("Software Activation Required")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Info section
        info_label = QLabel("Please enter your activation key to continue using this software.")
        info_label.setObjectName("infoLabel")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)
        
        # Key input section
        key_layout = QFormLayout()
        key_layout.setVerticalSpacing(15)
        
        key_label = QLabel("Activation Key:")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        
        key_layout.addRow(key_label, self.key_input)
        main_layout.addLayout(key_layout)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setObjectName("activateButton")
        self.activate_btn.setMinimumWidth(150)
        self.activate_btn.clicked.connect(self.activate_software)
        
        button_layout.addWidget(self.activate_btn)
        main_layout.addLayout(button_layout)
        
        # Add stretches for better layout
        main_layout.addStretch(1)
    
    def activate_software(self):
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "Activation Failed", "Please enter a valid activation key.")
            return
        
        # Hash the entered key
        key_hash = hash_key(key)
        print(key_hash)
        # Check against known keys
        if key_hash == LIFETIME_KEY_HASH:
            self.save_activation('lifetime')
            QMessageBox.information(self, "Activation Successful", 
                                  "Thank you! Your software has been activated with a lifetime license.")
            self.accept()
        elif key_hash == ONE_DAY_KEY_HASH:
            self.save_activation('trial')
            QMessageBox.information(self, "Activation Successful", 
                                  "Thank you! Your software has been activated for a 1-day trial.")
            self.accept()
        else:
            QMessageBox.critical(self, "Activation Failed", 
                               "The activation key you entered is invalid. Please try again.")
    
    def save_activation(self, activation_type):
        """Save the activation information"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(ACTIVATION_FILE), exist_ok=True)
        
        data = {
            'type': activation_type,
            'activated_at': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(days=1)).isoformat() if activation_type == 'trial' else None
        }
        
        with open(ACTIVATION_FILE, 'w') as f:
            json.dump(data, f)


class WelcomeDialog(QDialog):
    def __init__(self, logo_path=None):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.resize(450, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Store logo path
        self.logo_path = "saglo.jpeg" 
        
        # Set modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            QLabel#logoLabel {
                margin-bottom: 15px;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#subtitleLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
            QPushButton {
                padding: 14px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                min-width: 160px;
            }
            QPushButton#adminButton {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton#adminButton:hover {
                background-color: #2980b9;
            }
            QPushButton#userButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
            }
            QPushButton#userButton:hover {
                background-color: #d6dbdf;
            }
            QFrame#separator {
                background-color: #e0e0e0;
                max-height: 1px;
                margin: 15px 0;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(10)
        
        # Logo section
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # App logo
        logo_label = QLabel()
        logo_label.setObjectName("logoLabel")
        logo_label.setFixedSize(80, 80)
        logo_label.setScaledContents(True)
        logo_label.setPixmap(self.get_app_logo())
        logo_layout.addWidget(logo_label)
        
        main_layout.addLayout(logo_layout)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Title and subtitle
        title_label = QLabel("Welcome to the System")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Please select your login type to continue")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        
        # Add separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Admin button with icon
        admin_btn = QPushButton("Administrator")
        admin_btn.setObjectName("adminButton")
        admin_btn.setIcon(self.get_icon("admin"))
        admin_btn.setIconSize(QSize(20, 20))
        admin_btn.clicked.connect(lambda: self.select("admin"))
        
        # User button with icon
        user_btn = QPushButton("Standard User")
        user_btn.setObjectName("userButton")
        user_btn.setIcon(self.get_icon("user"))
        user_btn.setIconSize(QSize(20, 20))
        user_btn.clicked.connect(lambda: self.select("user"))
        
        buttons_layout.addWidget(admin_btn)
        buttons_layout.addWidget(user_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Add version info at bottom
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignRight)
        version_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        main_layout.addWidget(version_label)
        
        self.role = None

    def get_app_logo(self):
        """Load the application logo from file."""
        try:
            # Use the provided logo path or default to a placeholder
            if self.logo_path and os.path.exists(self.logo_path):
                return QPixmap(self.logo_path)
            else:
                print("Logo path not provided or file not found.")
                return self.create_placeholder_logo()
        except Exception as e:
            # Fallback in case the image can't be loaded
            print(f"Error loading logo: {e}")
            return self.create_placeholder_logo()
    
    def create_placeholder_logo(self):
        """Create a placeholder logo if the actual logo can't be loaded."""
        pixmap = QPixmap(80, 80)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a rounded rectangle background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#3498db")))
        painter.drawRoundedRect(0, 0, 80, 80, 16, 16)
        
        # Draw text
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "A")
        
        painter.end()
        return pixmap
        
    def get_icon(self, icon_type):
        # In a real application, you would use actual icon files
        # This is a placeholder that creates icons from the system
        if icon_type == "admin":
            return QIcon.fromTheme("user-admin", QIcon.fromTheme("system-users"))
        else:
            return QIcon.fromTheme("user", QIcon.fromTheme("system-user"))
    
    def select(self, role):
        self.role = role
        self.accept()


class BaseLoginDialog(QDialog):
    """Base class for login dialogs with shared functionality"""
    def __init__(self, title, logo_path, accent_color, hover_color):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(400, 450)
        # Remove help button from title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.logo_path = logo_path
        self.accent_color = accent_color
        self.hover_color = hover_color
        
        # Apply styling
        self.setStyleSheet(self.get_stylesheet())
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout with proper margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Logo section
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # App logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(100, 100)
        self.logo_label.setScaledContents(True)
        
        # Load logo image
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            self.logo_label.setPixmap(pixmap)
        
        logo_layout.addWidget(self.logo_label)
        main_layout.addLayout(logo_layout)
        
        # Title section
        title_label = QLabel(self.windowTitle().replace("🔐 ", "").replace("👤 ", ""))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)
        
        # Form layout
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(15, 25, 15, 25)
        form_layout.setVerticalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        self.user = QLineEdit()
        self.user.setObjectName("inputField")
        self.user.setPlaceholderText("Enter your username")
        
        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        self.pw = QLineEdit()
        self.pw.setObjectName("inputField")
        self.pw.setEchoMode(QLineEdit.Password)
        self.pw.setPlaceholderText("Enter your password")
        
        form_layout.addRow(username_label, self.user)
        form_layout.addRow(password_label, self.pw)
        
        main_layout.addWidget(form_container)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setMinimumWidth(150)
        self.login_btn.clicked.connect(self.check)
        
        button_layout.addWidget(self.login_btn)
        main_layout.addLayout(button_layout)
        
        # Add stretches to make form appear centered
        main_layout.insertStretch(0, 1)
        main_layout.addStretch(1)
        
    def get_stylesheet(self):
        return f"""
            QDialog {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }}
            
            QLabel#titleLabel {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            
            QLabel#fieldLabel {{
                font-size: 14px;
                font-weight: 600;
                color: #4a6572;
            }}
            
            QFrame#separator {{
                background-color: #e0e0e0;
                max-height: 1px;
                margin: 10px 0;
            }}
            
            QFrame#formContainer {{
                background-color: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }}
            
            QLineEdit#inputField {{
                padding: 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                selection-background-color: #e5e5e5;
            }}
            
            QLineEdit#inputField:focus {{
                border: 1px solid {self.accent_color};
            }}
            
            QPushButton#loginButton {{
                background-color: {self.accent_color};
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                margin-top: 15px;
                min-height: 40px;
            }}
            
            QPushButton#loginButton:hover {{
                background-color: {self.hover_color};
            }}
        """
    
    def check(self):
        # This method should be implemented by subclasses
        pass


class AdminLoginDialog(BaseLoginDialog):
    def __init__(self, logo_path="saglo.jpeg"):
        super().__init__("Admin Login", logo_path, "#3498db", "#2980b9")
        
        # Set admin-specific placeholder text
        self.user.setPlaceholderText("Enter admin username")
        self.pw.setPlaceholderText("Enter admin password")
        
        # Set icon for admin
        if QIcon.hasThemeIcon("user-admin"):
            self.login_btn.setIcon(QIcon.fromTheme("user-admin"))
    
    def check(self):
        if self.user.text() == "admin" and self.pw.text() == "password":
            # Ensure the directory exists
            os.makedirs(os.path.dirname(HISTORY_FILE) if os.path.dirname(HISTORY_FILE) else '.', exist_ok=True)
            with open(HISTORY_FILE, "a") as f:
                f.write(f"admin @ {datetime.now().isoformat()}\n")
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                "Authentication Failed", 
                "Invalid admin credentials. Please try again."
            )



class UserLoginDialog(BaseLoginDialog):
    def __init__(self, logo_path="saglo.png"):
        super().__init__("User Login", logo_path, "#2ecc71", "#27ae60")
        
        # Set user-specific placeholder text
        self.user.setPlaceholderText("Enter your username")
        self.pw.setPlaceholderText("Enter your password")
        
        # Add a register hint
        hint = QLabel("Don't have an account? Please contact your administrator.")
        hint.setObjectName("hintLabel")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-top: 10px;")
        self.layout().addWidget(hint)
        
        # Set icon for user
        if QIcon.hasThemeIcon("user"):
            self.login_btn.setIcon(QIcon.fromTheme("user"))
    
    def check(self):
        users = {}
        if os.path.exists(USER_FILE):
            with open(USER_FILE) as f:
                for line in f:
                    if ',' in line:
                        u, p = line.strip().split(',')
                        users[u] = p
        
        if self.user.text() in users and users[self.user.text()] == self.pw.text():
            # Ensure the directory exists
            os.makedirs(os.path.dirname(HISTORY_FILE) if os.path.dirname(HISTORY_FILE) else '.', exist_ok=True)
            with open(HISTORY_FILE, "a") as f:
                f.write(f"{self.user.text()} @ {datetime.now().isoformat()}\n")
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                "Authentication Failed", 
                "Invalid user credentials. Please try again."
            )


# -- User Management Dialog ------------------------------------------------
class ManageUsersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Users")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        
        # Custom buttons
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete")
        self.close_btn = QPushButton("Close")
        self.delete_btn.clicked.connect(self.delete_user)
        self.close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        self.load_users()

    def load_users(self):
        self.list_widget.clear()
        if os.path.exists(USER_FILE):
            with open(USER_FILE) as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 1:
                        self.list_widget.addItem(parts[0])

    def delete_user(self):
        selected = self.list_widget.currentItem()
        if selected:
            username = selected.text()
            users = []
            with open(USER_FILE) as f:
                users = [line.strip() for line in f if not line.startswith(username + ',')]
            with open(USER_FILE, 'w') as f:
                f.write("\n".join(users) + "\n")
            self.load_users()
            QMessageBox.information(self, "Deleted", f"User '{username}' deleted")
# -- Report Dialog ----------------------------------------------------------




class ReportDialog(QDialog):
    def __init__(self, image_filename):
        super().__init__()
        self.setWindowTitle("📝 Report Information")
        self.resize(900, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #f7f9fc;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-weight: 500;
            }
            QLineEdit, QSpinBox, QDateEdit, QDateTimeEdit, QComboBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 220px;
                max-width: 250px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #2e86de;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e6bb8;
            }
        """)

        self.data = {}
        self.imgfile = image_filename

        main_layout = QHBoxLayout(self)
        self.software_version = QLineEdit()
        self.software_version.setText("4.0")       # Set your fixed version here
        self.software_version.setReadOnly(True)
        # === Form Section ===
        form_group = QGroupBox("Fill Report Details")
        form_layout = QHBoxLayout()
        form_group.setLayout(form_layout)

        left_form = QFormLayout()
        right_form = QFormLayout()

        # Create all widgets
        self.college_name = QLineEdit()
        self.department = QLineEdit()
        self.user = QLineEdit()
        self.print_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.print_time.setCalendarPopup(True)
        
        self.page_number = QSpinBox(); self.page_number.setMinimum(1)
        self.total_pages = QSpinBox(); self.total_pages.setMinimum(1)

        self.sample_name = QLineEdit()
        self.solvent = QLineEdit()
        self.analysis = QLineEdit()
        self.method = QLineEdit()
        self.plate_material = QLineEdit()
        self.batch_no = QLineEdit()
        self.ar_no = QLineEdit()
        self.equipment_no = QLineEdit()

        self.reviewed_by = QLineEdit()
        self.reviewed_date = QDateEdit(QDate.currentDate())
        self.reviewed_date.setCalendarPopup(True)
        self.analysed_by = QLineEdit()
        self.analysed_date = QDateEdit(QDate.currentDate())
        self.analysed_date.setCalendarPopup(True)
        
        self.status = QComboBox(); self.status.addItems(["Draft", "In Review", "Final"])

        self.image_name = QLineEdit()
        self.image_captured_date = QDateTimeEdit(QDateTime.currentDateTime())
        self.image_captured_date.setCalendarPopup(True)
        self.created_date = QDateTimeEdit(QDateTime.currentDateTime())
        self.created_date.setCalendarPopup(True)
        self.field_name = QLineEdit()
        

        # Split into two vertical form columns
        left_form.addRow("College Name:", self.college_name)
        left_form.addRow("Department:", self.department)
        left_form.addRow("User:", self.user)
        left_form.addRow("Print Time:", self.print_time)
        left_form.addRow("Page Number:", self.page_number)
        left_form.addRow("Total Pages:", self.total_pages)
        left_form.addRow("Sample Name:", self.sample_name)
        left_form.addRow("Solvent:", self.solvent)
        left_form.addRow("Analysis:", self.analysis)
        left_form.addRow("Method:", self.method)
        left_form.addRow("Slide Material:", self.plate_material)
        left_form.addRow("Batch No:", self.batch_no)

        right_form.addRow("A.R No:", self.ar_no)
        right_form.addRow("Equipment No:", self.equipment_no)
        right_form.addRow("Reviewed By:", self.reviewed_by)
        right_form.addRow("Reviewed Date:", self.reviewed_date)
        right_form.addRow("Analysed By:", self.analysed_by)
        right_form.addRow("Analysed Date:", self.analysed_date)
        right_form.addRow("Software Version:", self.software_version)
        right_form.addRow("Status:", self.status)
        right_form.addRow("Image Name:", self.image_name)
        right_form.addRow("Image Captured Date:", self.image_captured_date)
        right_form.addRow("Created Date:", self.created_date)
        right_form.addRow("Magnification:", self.field_name)
        

        self.generate_btn = QPushButton("Generate Report")
        right_form.addRow(self.generate_btn)

        form_layout.addLayout(left_form)
        form_layout.addLayout(right_form)

        main_layout.addWidget(form_group, 3)

        # === Image Section ===
        image_group = QGroupBox("📷 Image Preview")
        image_layout = QVBoxLayout()
        image_layout.setAlignment(Qt.AlignTop)
        image_group.setLayout(image_layout)

        self.img_label = QLabel()
        self.img_label.setFixedSize(280, 280)
        self.img_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.load_image()

        image_layout.addWidget(self.img_label)
        main_layout.addWidget(image_group, 1)

        # Connect generate button
        self.generate_btn.clicked.connect(self.on_generate)

    def load_image(self):
        if self.imgfile and os.path.exists(self.imgfile):
            pixmap = QPixmap(self.imgfile)
            self.img_label.setPixmap(
                pixmap.scaled(
                    self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

    def on_generate(self):
        fields = {
            'college_name': self.college_name.text(),
            'department': self.department.text(),
            'user': self.user.text(),
            'print_time': self.print_time.dateTime().toString(),
            'page_number': self.page_number.value(),
            'total_pages': self.total_pages.value(),
            'sample_name': self.sample_name.text(),
            'solvent': self.solvent.text(),
            'analysis': self.analysis.text(),
            'method': self.method.text(),
            'plate_material': self.plate_material.text(),
            'batch_no': self.batch_no.text(),
            'ar_no': self.ar_no.text(),
            'equipment_no': self.equipment_no.text(),
            'reviewed_by': self.reviewed_by.text(),
            'reviewed_date': self.reviewed_date.date().toString(),
            'analysed_by': self.analysed_by.text(),
            'analysed_date': self.analysed_date.date().toString(),
            'software_version': self.software_version.text(),
            'status': self.status.currentText(),
            'image_name': self.image_name.text(),
            'image_captured_date': self.image_captured_date.dateTime().toString(),
            'created_date': self.created_date.dateTime().toString(),
            'field_name': self.field_name.text(),
            'image': self.imgfile
        }
        for key, val in fields.items():
            if key != 'image' and (val is None or str(val).strip() == ''):
                QMessageBox.warning(self, "Missing Data", f"Please enter {key.replace('_', ' ').title()}")
                return

        self.data = fields
        self.accept()

# -- Main Application Window -------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saglo-holosoft - Lensless Digital Holographic Microscopy Software")
        self.resize(800, 600)
        self.last_bw = None
        self.last_bw_path = None

        # Set background image for the main work area
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.bg_path = os.path.join('images', 'backi.png')  # Background image path
        self.bg_label = QLabel(self.central_widget)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()  # Make sure it's behind all widgets

        self.update_background()

        # Load OpenCV DNN Colorization Model
        model_dir = "model/"
        proto = os.path.join(model_dir, "colorization_deploy_v2.prototxt")
        weights = os.path.join(model_dir, "colorization_release_v2.caffemodel")
        pts = os.path.join(model_dir, "pts_in_hull.npy")
        self.color_net = cv2.dnn.readNetFromCaffe(proto, weights)
        pts_in_hull = np.load(pts)
        class8 = self.color_net.getLayerId("class8_ab")
        conv8 = self.color_net.getLayerId("conv8_313_rh")
        pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
        self.color_net.getLayer(class8).blobs = [pts_in_hull.astype(np.float32)]
        self.color_net.getLayer(conv8).blobs = [np.full((1, 313), 2.606, dtype="float32")]

        # --- Menus ---
        menubar = self.menuBar()

        fileMenu = menubar.addMenu("File")
        openAct = QAction("Open", self)
        openAct.triggered.connect(self.open_pdf)
        fileMenu.addAction(openAct)
        fileMenu.addSeparator()
        exitAct = QAction("Exit", self)
        exitAct.triggered.connect(QApplication.instance().quit)
        fileMenu.addAction(exitAct)

        camMenu = menubar.addMenu("Camera")
        capAct = QAction("Capture Image", self)
        capAct.triggered.connect(self.capture_image)
        camMenu.addAction(capAct)
        uploadAct = QAction("Upload Image", self)
        uploadAct.triggered.connect(self.upload_image)
        camMenu.addAction(uploadAct)

        rptMenu = menubar.addMenu("Reports")
        genAct = QAction("Generate Report", self)
        genAct.triggered.connect(self.generate_report)
        rptMenu.addAction(genAct)

        setMenu = menubar.addMenu("Settings")
        addUserAct = QAction("Add User", self)
        addUserAct.triggered.connect(self.add_user)
        manageUsersAct = QAction("Manage Users", self)
        manageUsersAct.triggered.connect(self.manage_users)
        histAct = QAction("View Login History", self)
        histAct.triggered.connect(self.view_history)
        orgAct = QAction("Add Organization", self)
        orgAct.triggered.connect(self.add_org)
        setMenu.addAction(addUserAct)
        setMenu.addAction(manageUsersAct)
        setMenu.addSeparator()
        setMenu.addAction(histAct)
        setMenu.addAction(orgAct)

        helpMenu = menubar.addMenu("Help")
        aboutAct = QAction("About SagloSoft", self)
        aboutAct.triggered.connect(self.show_about)
        aboutOrg = QAction("About Organizations", self)
        aboutOrg.triggered.connect(self.show_orgs)
        helpMenu.addAction(aboutAct)
        helpMenu.addAction(aboutOrg)

        # Add bottom-left graphical buttons for Settings
        self.init_settings_toolbar()

    def update_background(self):
        pixmap = QPixmap(self.bg_path)
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        self.update_background()

    def init_settings_toolbar(self):
        # Create horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 10)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        # Icons path
        icon_path = "icons"

        # Add horizontal buttons
        buttons = [
            ("adduser.png", self.add_user, "Add User"),
            ("manage.png", self.manage_users, "Manage Users"),
            ("history.png", self.view_history, "Login History"),
            ("org.png", self.add_org, "Add Organization")
        ]

        for icon_file, slot, tooltip in buttons:
            btn = QToolButton()
            btn.setIcon(QIcon(os.path.join(icon_path, icon_file)))
            btn.setIconSize(QSize(36, 36))
            btn.setToolTip(tooltip)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        # Wrap the layout in a QWidget
        toolbar_widget = QWidget(self.central_widget)
        toolbar_widget.setLayout(layout)
        toolbar_widget.setGeometry(10, self.height() - 80, 350, 50)  # increased bottom padding

        toolbar_widget.show()

        self.toolbar_widget = toolbar_widget

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_background()
        if hasattr(self, 'toolbar_widget'):
            self.toolbar_widget.setGeometry(10, self.height() - 80, 350, 50)





    def open_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])


    def update_background(self):
        if os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path).scaled(
                self.central_widget.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(pixmap)
            self.bg_label.resize(self.central_widget.size())

    def show_about(self):
        """Display an image in the About dialog instead of text."""
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        about_img_path = os.path.join('images', 'ver.png')  # Update with your 'About' image path
        if os.path.exists(about_img_path):
            pixmap = QPixmap(about_img_path)
            msg.setIconPixmap(pixmap)
        else:
            msg.setText("App v1.0")
        msg.exec_()

    def capture_image(self):
        # List available cameras
        available_cameras = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap is not None and cap.read()[0]:
                available_cameras.append(i)
                cap.release()

        if not available_cameras:
            QMessageBox.critical(self, "Error", "No cameras found.")
            return

        # Ask user to select camera
        cam_strs = [f"Camera {i}" for i in available_cameras]
        cam_idx, ok = QInputDialog.getItem(self, "Select Camera", "Choose a camera:", cam_strs, 0, False)
        if not ok:
            return

        selected_cam_index = available_cameras[cam_strs.index(cam_idx)]
        cap = cv2.VideoCapture(selected_cam_index)

        if not cap.isOpened():
            QMessageBox.critical(self, "Error", f"Cannot open camera {selected_cam_index}")
            return

        QMessageBox.information(self, "Info", "Press 'c' to capture image, 'q' to quit preview")

        # Show live preview
        while True:
            ret, frame = cap.read()
            if not ret:
                QMessageBox.critical(self, "Error", "Failed to read from camera")
                break

            cv2.imshow('Live Camera - Press c to Capture', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('c'):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"capture_{ts}.png"
                cv2.imwrite(fname, frame)  # Save original color image
                self.last_bw = frame
                self.last_bw_path = fname
                QMessageBox.information(self, "Captured", f"Saved image to {fname}")
                break

            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def upload_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if fname:
            img = cv2.imread(fname, cv2.IMREAD_COLOR)
            if img is None:
                QMessageBox.warning(self, "Error", "Failed to load image.")
                return
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"upload_{ts}.png"
            cv2.imwrite(save_path, img)
            self.last_bw = img
            self.last_bw_path = save_path
            QMessageBox.information(self, "Uploaded", f"Image loaded and saved as {save_path}")

    def generate_report(self):
        if self.last_bw_path is None:
            QMessageBox.warning(self, "No Image", "Capture an image first")
            return

        image = cv2.imread(self.last_bw_path)
        if image is None:
            QMessageBox.critical(self, "Error", f"Failed to load {self.last_bw_path}")
            return

        tmpname = f"reportimg_{os.path.basename(self.last_bw_path)}"
        cv2.imwrite(tmpname, image)

        dlg = ReportDialog(tmpname)
        if not dlg.exec_():
            return
        data = dlg.data

        required_keys = [
            'college_name', 'department', 'user', 'print_time', 'page_number', 'total_pages',
            'sample_name', 'solvent', 'analysis', 'method', 'plate_material',
            'batch_no', 'ar_no', 'equipment_no', 'reviewed_by', 'reviewed_date',
            'analysed_by', 'analysed_date', 'software_version', 'status',
            'image_name', 'image_captured_date', 'created_date', 'field_name'
        ]
        for key in required_keys:
            if key not in data or not str(data[key]).strip():
                QMessageBox.warning(self, "Missing Data", f"Missing required field: {key}")
                return

        from PyQt5.QtWidgets import QFileDialog
        from PIL import Image
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        default_pdf_name = f"Report_{os.path.splitext(os.path.basename(tmpname))[0]}.pdf"
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Save Report As", default_pdf_name, "PDF Files (*.pdf)")

        if not pdf_path:
            QMessageBox.information(self, "Cancelled", "PDF generation was cancelled.")
            return

        if not pdf_path.lower().endswith(".pdf"):
            pdf_path += ".pdf"

        c = canvas.Canvas(pdf_path, pagesize=A4)
        w, h = A4
        margin = 40
        y = h - margin

        # === Draw Header Logo ===
        logo_path = "saglo.jpeg"
        logo_height = 50  # desired height in points
        logo_drawn = False
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, margin, y - logo_height, height=logo_height, preserveAspectRatio=True, mask='auto')
                logo_drawn = True
            except Exception as e:
                QMessageBox.warning(self, "Logo Error", f"Could not load logo: {e}")
        if logo_drawn:
            y -= (logo_height + 10)  # Add spacing below logo
        else:
            y -= 20  # fallback spacing

        def draw_label_value(label, value, x, y, label_width=100):
            c.drawString(x, y, f"{label}:")
            c.drawString(x + label_width, y, value)

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w / 2, y, data['college_name'])
        y -= 20
        c.setFont("Helvetica", 10)
        draw_label_value("Department", data['department'], margin, y)
        draw_label_value("User", data['user'], w / 2, y)
        y -= 15
        draw_label_value("Print Time", data['print_time'], margin, y)
        c.drawRightString(w - margin, y, f"Page {data['page_number']} of 2")
        y -= 15
        c.line(margin, y, w - margin, y)

        # Sample info
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Sample Details:")
        y -= 15
        c.setFont("Helvetica", 10)
        draw_label_value("Sample Name", data['sample_name'], margin, y)
        draw_label_value("Solvent", data['solvent'], w / 2, y)
        y -= 15
        draw_label_value("Analysis", data['analysis'], margin, y)
        draw_label_value("Method", data['method'], w / 2, y)
        y -= 15
        draw_label_value("Slide Material", data['plate_material'], margin, y)
        y -= 15
        draw_label_value("Batch Number", data['batch_no'], margin, y)
        draw_label_value("AR Number", data['ar_no'], w / 2, y)
        y -= 15
        draw_label_value("Equipment Number", data['equipment_no'], margin, y)
        y -= 15
        c.line(margin, y, w - margin, y)

        # Authorization
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Authorization:")
        y -= 15
        c.setFont("Helvetica", 10)
        draw_label_value("Reviewed By", data['reviewed_by'], margin, y)
        draw_label_value("Date", data['reviewed_date'], w / 2, y)
        y -= 15
        draw_label_value("Analysed By", data['analysed_by'], margin, y)
        draw_label_value("Date", data['analysed_date'], w / 2, y)
        y -= 15
        draw_label_value("Software Version", data['software_version'], margin, y)
        draw_label_value("Status", data['status'], w / 2, y)
        y -= 15
        c.line(margin, y, w - margin, y)

        # Image Metadata
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Image Info:")
        y -= 15
        c.setFont("Helvetica", 10)
        draw_label_value("Image Name", data['image_name'], margin, y)
        y -= 15
        draw_label_value("Image Captured Date", data['image_captured_date'], margin, y)
        draw_label_value("Created Date", data['created_date'], w / 2, y)
        y -= 15
        draw_label_value("Magnigication", data['field_name'], margin, y)
        y -= 15
        c.line(margin, y, w - margin, y)

        c.setFont("Helvetica-Oblique", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)  # gray color
        c.drawCentredString(w / 2, 20, "Report generated by SAGLO-Holosoft Software")
        
        # Draw Image with dynamic size and avoid overlap
        try:
            img = Image.open(tmpname)
            img_width, img_height = img.size
            max_width = w - 2 * margin
            aspect_ratio = img_height / img_width
            draw_height = max_width * aspect_ratio

            y -= (draw_height + 20)  # leave 20px spacing

            if y < margin:
                c.showPage()
                y = h - margin - draw_height
            
            c.drawImage(tmpname, margin, y, width=max_width, height=draw_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            QMessageBox.warning(self, "Image Error", f"Failed to add image: {e}")
        y -= 15            
        c.drawRightString(w - margin, y, f"Page 2 of 2")
        # Footer Text
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)  # gray color
        c.drawCentredString(w / 2, 20, "Report generated by SAGLO-Holosoft Software")

        c.showPage()
        c.save()

        try:
            os.remove(tmpname)
        except Exception as e:
            print(f"Warning: Failed to delete temporary file: {e}")

        QMessageBox.information(self, "Report", f"Saved PDF to {pdf_path}")



    def view_history(self):
        if not os.path.exists(HISTORY_FILE):
            txt = "(no history)"
        else:
            with open(HISTORY_FILE) as f:
                txt = f.read()
        dlg = QDialog(self)
        dlg.setWindowTitle("Login History")
        te = QTextEdit(txt, dlg)
        te.setReadOnly(True)
        dlg.resize(400, 300)
        dlg.exec_()

    def add_org(self):
        org, ok = QInputDialog.getText(self, "Add Organization", "Organization Name:")
        if ok and org.strip():
            with open(ORG_FILE, "a") as f:
                f.write(org.strip() + "\n")
            QMessageBox.information(self, "Added", f"{org} added")

    def show_orgs(self):
        if not os.path.exists(ORG_FILE):
            txt = "(none)"
        else:
            with open(ORG_FILE) as f:
                txt = f.read()
        QMessageBox.information(self, "Organizations", txt)

    def add_user(self):
        username, ok1 = QInputDialog.getText(self, "Add User", "Username:")
        pwd, ok2 = QInputDialog.getText(self, "Add User", "Password:", QLineEdit.Password)
        if ok1 and ok2 and username.strip() and pwd.strip():
            with open(USER_FILE, 'a') as f:
                f.write(f"{username.strip()},{pwd.strip()}\n")
            QMessageBox.information(self, "Added", f"User '{username}' added")

    def manage_users(self):
        dlg = ManageUsersDialog()
        dlg.exec_()

# -- Application Entry Point --------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Directly continue with normal login flow (no activation checks)
    welcome = WelcomeDialog()
    if welcome.exec_() == QDialog.Accepted:
        if welcome.role == "admin":
            dialog = AdminLoginDialog()
            if dialog.exec_() == QDialog.Accepted:
                w = MainWindow()
                w.show()
                sys.exit(app.exec_())
        else:
            dialog = UserLoginDialog()
            if dialog.exec_() == QDialog.Accepted:
                w = MainWindow()
                w.show()
                sys.exit(app.exec_())

        if dialog.exec_() == QDialog.Accepted:
            print(f"Successfully logged in as {welcome.role}")
            QMessageBox.information(None, "Login Successful", 
                                  f"You have successfully logged in as {welcome.role}.")
        else:
            print("Login canceled or failed")
    else:
        print("Welcome dialog closed")
