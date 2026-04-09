from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QFileDialog, QApplication, QSizePolicy,
    QGridLayout
)
from PySide6.QtCore import Qt
import os
from core.translator import translator
from core.vigenere import encrypt_preserve_format, validate_key
from ui.popups import show_error, show_warning, show_info

# Styles identical to decryption for visual standardization
CARD_STYLE = """
QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
"""

SECTION_TITLE_STYLE = """
font-family: 'Roboto Mono', monospace;
font-size: 14px;
font-weight: 700;
color: #1F2937;
padding: 0;
background-color: transparent;
"""

INPUT_STYLE = """
QTextEdit, QLineEdit, QComboBox {
    font-family: 'Roboto Mono', monospace;
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #2F80ED;
    selection-color: white;
}
QTextEdit:focus, QLineEdit:focus, QComboBox:focus {
    border: 2px solid #2F80ED;
}
QTextEdit:read-only, QLineEdit:read-only {
    background-color: #F8FAFC;
    color: #4B5563;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: url(assets/icons/down_arrow.svg);
    width: 16px;
    height: 16px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    selection-background-color: #F1F5F9;
    selection-color: #1F2937;
}
"""

BUTTON_NEUTRAL = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #334155;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(203, 213, 225, 0.15); }
"""

BUTTON_PRIMARY = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #2F80ED;
    border: 1.5px solid #2F80ED;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(47, 128, 237, 0.1); }
"""

BUTTON_SUCCESS = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #10B981;
    border: 1.5px solid #10B981;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(16, 185, 129, 0.1); }
"""

BUTTON_WARNING = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #D97706;
    border: 1.5px solid #F59E0B;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(245, 158, 11, 0.1); }
"""

BUTTON_DANGER = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #DC2626;
    border: 1.5px solid #EF4444;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(239, 68, 68, 0.1); }
"""

class CardWidget(QFrame):
    """Standardized card widget with title and content"""
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(CARD_STYLE)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(SECTION_TITLE_STYLE)
            self.main_layout.addWidget(self.title_label)

class CriptoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        translator.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        self.header = QLabel(translator.get("cripto_title"))
        self.header.setStyleSheet("color: #333333; font-size: 24px; font-weight: bold; font-family: 'Roboto Mono', monospace;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Main Grid Container for perfect alignment
        content_grid = QGridLayout()
        content_grid.setSpacing(20)
        content_grid.setColumnStretch(1, 1) # Right side stretches
        content_grid.setColumnMinimumWidth(0, 380) # Left side fixed
        
        # Row 0, Col 1: Data Input (Main)
        self.input_card = CardWidget(translator.get("input_text", "Texto a Criptografar"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(translator.get("input_placeholder", "Digite ou cole seu texto aqui..."))
        self.text_input.setMinimumHeight(150)
        self.text_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.input_card.main_layout.addWidget(self.text_input)
        content_grid.addWidget(self.input_card, 0, 1)
        
        # Row 0, Col 0: Configuration (Side)
        self.config_card = CardWidget(translator.get("config_label", "Configurações"))
        self.btn_select_file = QPushButton(translator.get("cripto_file_btn", "Selecionar Arquivo .TXT"))
        self.btn_select_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_file.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_select_file.clicked.connect(self._load_file)
        self.config_card.main_layout.addWidget(self.btn_select_file)
        self.config_card.main_layout.addSpacing(8)
        
        self.algo_label = QLabel(translator.get("cripto_algorithm", "Método de Criptografia"))
        self.algo_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.config_card.main_layout.addWidget(self.algo_label)
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItem("Vigenère", "vigenere")
        self.algo_combo.setFixedHeight(40)
        self.algo_combo.setStyleSheet(INPUT_STYLE)
        self.config_card.main_layout.addWidget(self.algo_combo)
        
        self.config_card.main_layout.addSpacing(8)
        
        self.key_label = QLabel(translator.get("key_label", "Chave"))
        self.key_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.config_card.main_layout.addWidget(self.key_label)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(translator.get("key_placeholder", "Digite a chave..."))
        self.key_input.setFixedHeight(40)
        self.key_input.setStyleSheet(INPUT_STYLE)
        self.config_card.main_layout.addWidget(self.key_input)
        self.config_card.main_layout.addStretch()
        
        content_grid.addWidget(self.config_card, 0, 0)
        
        # Row 1, Col 0: Action Button
        self.btn_encrypt = QPushButton(translator.get("btn_encrypt_action", "Criptografar"))
        self.btn_encrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_encrypt.setMinimumHeight(44)
        self.btn_encrypt.setStyleSheet(BUTTON_DANGER)
        self.btn_encrypt.clicked.connect(self._encrypt_text)
        
        # Wrap the button in a widget so it doesn't stretch alone in the grid
        btn_wrapper = QWidget()
        btn_wrapper_layout = QVBoxLayout(btn_wrapper)
        btn_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        btn_wrapper_layout.addWidget(self.btn_encrypt)
        btn_wrapper_layout.addStretch()
        
        content_grid.addWidget(btn_wrapper, 1, 0)
        
        # Row 1, Col 1: Output Result
        self.output_card = CardWidget(translator.get("result_label", "Resultado"))
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setMinimumHeight(150)
        self.text_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_output.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 13px; }")
        self.output_card.main_layout.addWidget(self.text_output)
        
        self.btn_copy = QPushButton(translator.get("btn_copy", "Copiar"))
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setMinimumHeight(38)
        self.btn_copy.setStyleSheet(BUTTON_PRIMARY)
        self.btn_copy.clicked.connect(self._copy_result)
        self.output_card.main_layout.addWidget(self.btn_copy)
        
        content_grid.addWidget(self.output_card, 1, 1)
        
        # Add Stretch at the bottom
        content_grid.setRowStretch(2, 1)
        
        main_layout.addLayout(content_grid)
        
        self.setStyleSheet("background-color: #f8f8f8;")

    def _load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translator.get("cripto_file_btn", "Selecionar Arquivo .TXT"),
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_input.setPlainText(content)
            except Exception as e:
                show_error(self, str(e), translator.get("popup_text_empty"))
                
    def _encrypt_text(self):
        raw_text = self.text_input.toPlainText().strip()
        raw_key = self.key_input.text().strip()
        
        if not raw_text:
            show_warning(self, translator.get("msg_no_text", "The text to encrypt cannot be empty."))
            return
            
        if not raw_key:
            show_warning(self, translator.get("msg_no_key", "The key cannot be empty or contain numbers."))
            return
            
        try:
            validate_key(raw_key) # Raises OSError/ValueError if the key contains numbers etc.
        except Exception:
            show_warning(self, translator.get("msg_no_key", "The key cannot be empty or contain numbers."))
            return
            
        algo = self.algo_combo.currentData()
        if algo == "vigenere":
            result = encrypt_preserve_format(raw_text, raw_key)
            self.text_output.setPlainText(result)
        else:
            show_info(self, "Algoritmo Não Suportado / Unsupported Algorithm")

    def _copy_result(self):
        result_text = self.text_output.toPlainText()
        if result_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(result_text)

    def retranslate_ui(self, lang_code=None):
        self.header.setText(translator.get("cripto_title"))
        self.input_card.title_label.setText(translator.get("input_text", "Texto a Criptografar"))
        self.btn_select_file.setText(translator.get("cripto_file_btn", "Selecionar Arquivo .TXT"))
        self.text_input.setPlaceholderText(translator.get("input_placeholder", "Digite ou cole seu texto aqui... Ou faça o upload de um arquivo ao lado."))
        self.config_card.title_label.setText(translator.get("config_label", "Configurações"))
        self.algo_label.setText(translator.get("cripto_algorithm", "Método de Criptografia"))
        self.key_label.setText(translator.get("key_label", "Chave"))
        self.key_input.setPlaceholderText(translator.get("key_placeholder", "Digite a chave..."))
        self.btn_encrypt.setText(translator.get("btn_encrypt_action", "Criptografar"))
        self.output_card.title_label.setText(translator.get("result_label", "Resultado"))
        self.btn_copy.setText(translator.get("btn_copy", "Copiar"))
