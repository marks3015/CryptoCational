import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                               QFrame, QSizePolicy, QSpacerItem, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap

from ui.pages.ui_cripto import CriptoPage
from ui.pages.ui_decripto import DecriptoPage
from ui.pages.ui_home import HomePage
from ui.pages.ui_settings import SettingsPage
from ui.pages.ui_aes import AESPage
from ui.pages.ui_rsa import RSAPage
from core.translator import translator
from core.utils import get_resource_path




class UI_MainWindow:
    def __init__(self, version="v1.1.0"):
        self.version = version
        
        # Navigation button styles
        self._btn_default_style = """
            QPushButton {
                font-family: 'Roboto Mono', monospace;
                font-size: 12px;
                text-align: left;
                background-color: transparent;
                border: none;
                min-width: 50px;
                min-height: 50px;
                padding: 10px;
                border-left: 4px solid transparent;
                color: #555555;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 0.12);
                border-left: 4px solid rgba(80, 80, 80, 0.4);
            }
        """
        self._btn_active_style = """
            QPushButton {
                font-family: 'Roboto Mono', monospace;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                background-color: rgba(80, 80, 80, 0.18);
                border: none;
                min-width: 50px;
                min-height: 50px;
                padding: 10px;
                border-left: 4px solid #505050;
                color: #333333;
            }
        """
    
    def setup_ui(self, parent):
        self.parent = parent
        if not parent.objectName():
            parent.setObjectName("MainWindow")
        
        # Set initial parameters
        parent.resize(1200, 720)
        parent.setMinimumSize(1200, 720)
        
        # Remove title bar
        parent.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        parent.setWindowIcon(QIcon(get_resource_path("assets/images/logo.png")))
        
        # Create parent widget
        self.central_frame = QFrame()
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_frame)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Side menu
        self.left_menu = QFrame()
        self.left_menu.setStyleSheet("background-color: #f0f0f0")
        self.left_menu.setMinimumWidth(60)
        self.left_menu.setMaximumWidth(60)
        
        # Side menu layout
        self.left_menu_layout = QVBoxLayout(self.left_menu)
        self.left_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_layout.setSpacing(0)
        
        # Top frame of side menu
        self.left_menu_top_frame = QFrame()
        self.left_menu_top_frame.setMinimumHeight(50)
        
        # Top frame layout of side menu
        self.left_menu_top_layout = QVBoxLayout(self.left_menu_top_frame)
        self.left_menu_top_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_top_layout.setSpacing(0)
        
        # Top frame buttons with icons
        icon_size = QPixmap(24, 24).scaledToHeight(24, Qt.TransformationMode.SmoothTransformation).size()
        
        self.toggle_btn = QPushButton(" Menu")
        self.toggle_btn.setIcon(QIcon(get_resource_path("assets/icons/menu.svg")))
        self.toggle_btn.setIconSize(icon_size)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(self._btn_default_style)
        
        self.btn_home = QPushButton(" Home")
        self.btn_home.setIcon(QIcon(get_resource_path("assets/icons/home.svg")))
        self.btn_home.setIconSize(icon_size)
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_home.setStyleSheet(self._btn_active_style)
        
        self.btn_cripto = QPushButton(" Criptografar")
        self.btn_cripto.setIcon(QIcon(get_resource_path("assets/icons/lock.svg")))
        self.btn_cripto.setIconSize(icon_size)
        self.btn_cripto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cripto.setStyleSheet(self._btn_default_style)
        
        self.btn_decripto = QPushButton(" Descriptografar")
        self.btn_decripto.setIcon(QIcon(get_resource_path("assets/icons/unlock.svg")))
        self.btn_decripto.setIconSize(icon_size)
        self.btn_decripto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_decripto.setStyleSheet(self._btn_default_style)
        
        self.btn_aes = QPushButton(" AES")
        self.btn_aes.setIcon(QIcon(get_resource_path("assets/icons/shield.svg")))
        self.btn_aes.setIconSize(icon_size)
        self.btn_aes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aes.setStyleSheet(self._btn_default_style)

        self.btn_rsa = QPushButton(" RSA-OAEP")
        self.btn_rsa.setIcon(QIcon(get_resource_path("assets/icons/rsa.svg")))
        self.btn_rsa.setIconSize(icon_size)
        self.btn_rsa.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rsa.setStyleSheet(self._btn_default_style)
        
        # Add top frame buttons
        self.left_menu_top_layout.addWidget(self.toggle_btn)
        self.left_menu_top_layout.addWidget(self.btn_home)
        self.left_menu_top_layout.addWidget(self.btn_cripto)
        self.left_menu_top_layout.addWidget(self.btn_decripto)
        self.left_menu_top_layout.addWidget(self.btn_aes)
        self.left_menu_top_layout.addWidget(self.btn_rsa)
        
        # Menu spacer
        self.left_menu_spacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        
        # Bottom frame of side menu
        self.left_menu_bottom_frame = QFrame()
        self.left_menu_bottom_frame.setMinimumHeight(50)
        
        # Bottom frame layout of side menu
        self.left_menu_bottom_layout = QVBoxLayout(self.left_menu_bottom_frame)
        self.left_menu_bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_bottom_layout.setSpacing(0)
        
        # Settings button
        self.btn_settings = QPushButton(translator.get("menu_settings"))
        self.btn_settings.setIcon(QIcon(get_resource_path("assets/icons/settings.svg")))
        self.btn_settings.setIconSize(icon_size)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet(self._btn_default_style)
        
        # Add bottom frame buttons
        self.left_menu_bottom_layout.addWidget(self.btn_settings)
        
        # Add: Top frame, spacer, bottom frame
        self.left_menu_layout.addWidget(self.left_menu_top_frame)
        self.left_menu_layout.addItem(self.left_menu_spacer)
        self.left_menu_layout.addWidget(self.left_menu_bottom_frame)
        
        # Content area
        self.content = QFrame()
        self.content.setStyleSheet("background-color: #f8f8f8")
        
        # Content layout
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Top bar
        self.top_bar = QFrame()
        self.top_bar.setMinimumHeight(40)
        self.top_bar.setMaximumHeight(40)
        self.top_bar.setStyleSheet("background-color: #f8f8f8;")
        
        # Top bar layout
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.top_bar_layout.setSpacing(8)
        
        # App icon
        app_icon_size = QPixmap(20, 20).scaledToHeight(20, Qt.TransformationMode.SmoothTransformation).size()
        self.lbl_icon = QLabel()
        self.lbl_icon.setPixmap(QIcon(get_resource_path("assets/images/logo.png")).pixmap(app_icon_size))
        self.lbl_icon.setMaximumWidth(30)
        
        self.lbl_title = QLabel("CryptoCational - Home")
        self.lbl_title.setStyleSheet(
            "font-family: 'Roboto Mono', monospace; font-size: 16px; color: #333333; font-weight: bold;"
        )
        
        top_button_style = """
        QPushButton {
            background-color: transparent; 
            border: none;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        }
        """
        
        close_button_style = """
        QPushButton {
            background-color: transparent; 
            border: none;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #E81123;
            border-radius: 4px;
        }
        """
        
        control_icon_size = QPixmap(16, 16).scaledToHeight(16, Qt.TransformationMode.SmoothTransformation).size()
        
        # Control buttons
        self.btn_minimize = QPushButton()
        self.btn_minimize.setIcon(QIcon(get_resource_path("assets/icons/minimize.svg")))
        self.btn_minimize.setIconSize(control_icon_size)
        self.btn_minimize.setFixedSize(30, 30)
        self.btn_minimize.setStyleSheet(top_button_style)
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.clicked.connect(parent.showMinimized)
        
        self.btn_maximize = QPushButton()
        self.btn_maximize.setIcon(QIcon(get_resource_path("assets/icons/maximize.svg")))
        self.btn_maximize.setIconSize(control_icon_size)
        self.btn_maximize.setFixedSize(30, 30)
        self.btn_maximize.setStyleSheet(top_button_style)
        self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_maximize.clicked.connect(self.toggle_maximize_restore)
        
        self.btn_close = QPushButton()
        self.btn_close.setIcon(QIcon(get_resource_path("assets/icons/close.svg")))
        self.btn_close.setIconSize(control_icon_size)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet(close_button_style)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(parent.close)
        
        self.top_spacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        
        # Add icon, title, and buttons to the top bar
        self.top_bar_layout.addWidget(self.lbl_icon)
        self.top_bar_layout.addWidget(self.lbl_title)
        self.top_bar_layout.addItem(self.top_spacer)
        self.top_bar_layout.addWidget(self.btn_minimize)
        self.top_bar_layout.addWidget(self.btn_maximize)
        self.top_bar_layout.addWidget(self.btn_close)
        
        # Application pages stack
        self.pages = QStackedWidget()
        
        self.home = HomePage()
        self.cripto = CriptoPage()
        self.decripto = DecriptoPage()
        self.aes = AESPage()
        self.settings = SettingsPage(version=self.version)
        self.rsa = RSAPage()
        
        self.pages.addWidget(self.home)       # 0
        self.pages.addWidget(self.cripto)     # 1
        self.pages.addWidget(self.decripto)   # 2
        self.pages.addWidget(self.aes)        # 3
        self.pages.addWidget(self.settings)   # 4
        self.pages.addWidget(self.rsa)        # 5
        
        # Bottom bar
        self.bottom_bar = QFrame()
        self.bottom_bar.setMinimumHeight(40)
        self.bottom_bar.setMaximumHeight(40)
        self.bottom_bar.setStyleSheet("background-color: #f8f8f8;")
        
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.bottom_bar_layout.setSpacing(10)
        
        self.bottom_label_right = QLabel(f"CryptoCational | {self.version}")
        self.bottom_label_right.setStyleSheet(
            "font-family: 'Roboto Mono', monospace; font-size: 12px; color: #666666;"
        )
        
        self.bottom_spacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        
        self.bottom_bar_layout.addItem(self.bottom_spacer)
        self.bottom_bar_layout.addWidget(self.bottom_label_right)
        
        # Add widgets to content layout
        self.content_layout.addWidget(self.top_bar)
        self.content_layout.addWidget(self.pages)
        self.content_layout.addWidget(self.bottom_bar)
        
        self.main_layout.addWidget(self.left_menu)
        self.main_layout.addWidget(self.content)
        
        parent.setCentralWidget(self.central_frame)
    
    def set_active_button(self, active_btn):
        """Applies active style to the clicked button and resets the others"""
        nav_buttons = [self.btn_home, self.btn_cripto, self.btn_decripto, self.btn_aes, self.btn_settings, self.btn_rsa]
        for btn in nav_buttons:
            if btn is active_btn:
                btn.setStyleSheet(self._btn_active_style)
            else:
                btn.setStyleSheet(self._btn_default_style)
    
    def update_label_title(self, title: str):
        """Updates the title"""
        self.lbl_title.setText(title)
    
    def toggle_maximize_restore(self):
        parent = self.central_frame.parentWidget()
        icon_size = QPixmap(16, 16).scaledToHeight(16, Qt.TransformationMode.SmoothTransformation).size()
        if parent.isMaximized():
            parent.showNormal()
            self.btn_maximize.setIcon(QIcon(get_resource_path("assets/icons/maximize.svg")))
        else:
            parent.showMaximized()
            self.btn_maximize.setIcon(QIcon(get_resource_path("assets/icons/restore.svg")))
        self.btn_maximize.setIconSize(icon_size)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)
        
        # Connect buttons
        self.ui.toggle_btn.clicked.connect(self.toggle_menu)
        self.ui.btn_home.clicked.connect(lambda: self.switch_tab(0))
        self.ui.btn_cripto.clicked.connect(lambda: self.switch_tab(1))
        self.ui.btn_decripto.clicked.connect(lambda: self.switch_tab(2))
        self.ui.btn_aes.clicked.connect(lambda: self.switch_tab(3))
        self.ui.btn_settings.clicked.connect(lambda: self.switch_tab(4))
        self.ui.btn_rsa.clicked.connect(lambda: self.switch_tab(5))
        
        # Connect home page buttons
        self.ui.home.btn_cripto.clicked.connect(lambda: self.switch_tab(1))
        self.ui.home.btn_decripto.clicked.connect(lambda: self.switch_tab(2))
        self.ui.home.btn_instrucoes.clicked.connect(self.goto_instructions)
        
        # Connect to translator
        translator.language_changed.connect(self.retranslate_ui)
        
        # Variables for window movement
        self.drag_pos = None
        
        # Allow moving window by top bar
        self.ui.top_bar.mousePressEvent = self.top_bar_mouse_press
        self.ui.top_bar.mouseMoveEvent = self.top_bar_mouse_move
        
        # Menu state
        self.menu_expanded = False
        
        # Initialize menu correctly at startup
        self._update_menu_texts()
    
    def _update_menu_texts(self):
        """Updates button texts based on menu state"""
        if self.menu_expanded:
            self.ui.toggle_btn.setText(translator.get("menu_toggle"))
            self.ui.btn_home.setText(translator.get("menu_home"))
            self.ui.btn_cripto.setText(translator.get("menu_encrypt"))
            self.ui.btn_decripto.setText(translator.get("menu_decrypt"))
            self.ui.btn_aes.setText(translator.get("menu_aes"))
            self.ui.btn_settings.setText(translator.get("menu_settings"))
            self.ui.btn_rsa.setText(translator.get("menu_rsa"))
        else:
            self.ui.toggle_btn.setText("")
            self.ui.btn_home.setText("")
            self.ui.btn_cripto.setText("")
            self.ui.btn_decripto.setText("")
            self.ui.btn_aes.setText("")
            self.ui.btn_settings.setText("")
            self.ui.btn_rsa.setText("")
            
    def retranslate_ui(self, lang_code=None):
        self._update_menu_texts()
        titles = [
            translator.get("app_title_home"), 
            translator.get("app_title_encrypt"), 
            translator.get("app_title_decrypt"), 
            translator.get("app_title_aes"),
            translator.get("app_title_settings"),
            translator.get("app_title_rsa"),
        ]
        curr_index = self.ui.pages.currentIndex()
        if 0 <= curr_index < len(titles):
            self.ui.update_label_title(titles[curr_index])
    
    def toggle_menu(self):
        """Expands or collapses the side menu"""
        self.menu_expanded = not self.menu_expanded
        
        target_width = 220 if self.menu_expanded else 60
        
        self.animation = QPropertyAnimation(self.ui.left_menu, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.ui.left_menu.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        self.ui.left_menu.setMaximumWidth(target_width)
        
        # Update button texts
        self._update_menu_texts()
    
    def switch_tab(self, index):
        """Changes active page"""
        self.ui.pages.setCurrentIndex(index)
        
        # Reset sub-pages to home when navigating to Decripto
        if index == 2 and hasattr(self.ui.decripto, 'decripto_stack'):
            self.ui.decripto.decripto_stack.setCurrentIndex(0)

        # Reset RSA page to home when navigating to it
        if index == 5 and hasattr(self.ui.rsa, 'stack'):
            self.ui.rsa.stack.setCurrentIndex(0)
        
        # Update active button
        buttons = [
            self.ui.btn_home, self.ui.btn_cripto, self.ui.btn_decripto,
            self.ui.btn_aes, self.ui.btn_settings, self.ui.btn_rsa,
        ]
        self.ui.set_active_button(buttons[index])
        
        # Update title
        titles = [
            translator.get("app_title_home"), 
            translator.get("app_title_encrypt"), 
            translator.get("app_title_decrypt"), 
            translator.get("app_title_aes"),
            translator.get("app_title_settings"),
            translator.get("app_title_rsa"),
        ]
        self.ui.update_label_title(titles[index])
    
    def goto_instructions(self):
        """Redirects directly to the settings instructions sub-tab"""
        self.switch_tab(4)
        self.ui.settings._switch_tab(2)

    def top_bar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
    
    def top_bar_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPosition().toPoint()


def main():
    # Fix para mostrar ícone no Taskbar do Windows
    if sys.platform == "win32":
        import ctypes
        myappid = u'cryptocational.interface.vigenere.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set default font
    font = QFont("Roboto Mono", 10)
    font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
