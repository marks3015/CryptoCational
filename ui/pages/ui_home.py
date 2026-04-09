from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                               QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
import os
from PySide6.QtGui import QFont, QPixmap
from core.translator import translator
from core.utils import get_resource_path


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        translator.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)
        
        # Card principal
        card = QFrame()
        card.setObjectName("MainCard")
        card.setStyleSheet("""
            #MainCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #000000;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 48, 48, 48)
        card_layout.setSpacing(32)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo container
        logo_container = QFrame()
        logo_container.setFixedSize(140, 140)
        logo_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_icon = QLabel()
        logo_path = get_resource_path("assets/images/logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_icon.setPixmap(pixmap)
        else:
            logo_icon.setText("Cripto")
            logo_icon.setStyleSheet("font-size: 24px; font-family: 'Roboto Mono', monospace;")
            
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_icon)
        
        card_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Welcome text
        self.welcome = QLabel("CryptoCational")
        self.welcome.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 32px;
                font-weight: 600;
                font-family: 'Roboto Mono', monospace;
                background-color: transparent;
            }
        """)
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.welcome)
        
        self.subtitle = QLabel(translator.get("home_subtitle"))
        self.subtitle.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
                font-family: 'Roboto Mono', monospace;
                background-color: transparent;
            }
        """)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.subtitle)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        
        # Criptografar button
        self.btn_cripto = QPushButton(translator.get("btn_encrypt"))
        self.btn_cripto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cripto.setMinimumHeight(48)
        self.btn_cripto.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4A4A4A;
                border: 1.5px solid #4A4A4A;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Roboto Mono', monospace;
            }
            QPushButton:hover {
                background-color: rgba(74, 74, 74, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(74, 74, 74, 0.15);
            }
        """)
        btn_layout.addWidget(self.btn_cripto)
        
        # Descriptografar button
        self.btn_decripto = QPushButton(translator.get("btn_decrypt"))
        self.btn_decripto.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_decripto.setMinimumHeight(48)
        self.btn_decripto.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                border: 1.5px solid #CCCCCC;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Roboto Mono', monospace;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
                border: 1.5px solid #999999;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.08);
            }
        """)
        btn_layout.addWidget(self.btn_decripto)
        
        # Instrucoes button
        self.btn_instrucoes = QPushButton(translator.get("btn_instructions"))
        self.btn_instrucoes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_instrucoes.setMinimumHeight(48)
        self.btn_instrucoes.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                border: 1.5px solid #4A4A4A;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Roboto Mono', monospace;
            }
            QPushButton:hover {
                background-color: rgba(74, 74, 74, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(74, 74, 74, 0.15);
            }
        """)
        btn_layout.addWidget(self.btn_instrucoes)
        
        card_layout.addLayout(btn_layout)
        
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Background styling
        self.setStyleSheet("background-color: #f8f8f8;")

    def retranslate_ui(self, lang_code=None):
        self.subtitle.setText(translator.get("home_subtitle"))
        self.btn_cripto.setText(translator.get("btn_encrypt"))
        self.btn_decripto.setText(translator.get("btn_decrypt"))
        self.btn_instrucoes.setText(translator.get("btn_instructions"))
