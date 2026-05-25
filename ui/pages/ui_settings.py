from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                               QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox,
                               QPushButton, QStackedWidget, QScrollArea, QLineEdit)
from PySide6.QtCore import Qt
from core.translator import translator

class SettingsPage(QWidget):
    def __init__(self, parent=None, version="v1.1.0"):
        super().__init__(parent)
        self.version = version
        self.instruction_sections = []
        self.setup_ui()
        translator.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        # Layout principal da pagina Settings
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)
        
        # === MENU LATERAL DE OPCOES ===
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(200)
        self.left_panel.setStyleSheet("background-color: transparent;")
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Titulo do Menu
        self.title_label = QLabel(translator.get("settings_title"))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Roboto Mono', monospace; color: #333333; margin-bottom: 20px;")
        left_layout.addWidget(self.title_label)
        
        self.btn_general = self._create_tab_button(translator.get("settings_tab_general", "Geral"))
        self.btn_license = self._create_tab_button(translator.get("settings_tab_license", "Licença"))
        self.btn_instructions = self._create_tab_button(translator.get("settings_tab_instructions", "Instruções"))
        
        left_layout.addWidget(self.btn_general)
        left_layout.addWidget(self.btn_license)
        left_layout.addWidget(self.btn_instructions)
        left_layout.addStretch()
        
        # Conectar botoes as abas
        self.btn_general.clicked.connect(lambda: self._switch_tab(0))
        self.btn_license.clicked.connect(lambda: self._switch_tab(1))
        self.btn_instructions.clicked.connect(lambda: self._switch_tab(2))
        
        # === CONTEUDO (PAGINAS) ===
        # Wrap the stack in a QFrame to preserve rounded borders clipping correctly
        self.card_wrapper = QFrame()
        self.card_wrapper.setObjectName("SettingsCard")
        self.card_wrapper.setStyleSheet("""
            #SettingsCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #000000;
            }
        """)
        wrapper_layout = QVBoxLayout(self.card_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")
        wrapper_layout.addWidget(self.content_stack)

        # Criando abas
        self.tab_general = self._setup_general_tab()
        self.tab_license = self._setup_license_tab()
        self.tab_instructions = self._setup_instructions_tab()
        
        self.content_stack.addWidget(self.tab_general)
        self.content_stack.addWidget(self.tab_license)
        self.content_stack.addWidget(self.tab_instructions)
        
        # Montar master layout
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.card_wrapper)
        self.setStyleSheet("background-color: #f8f8f8;")
        
        self._switch_tab(0)

    def _create_tab_button(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                font-family: 'Roboto Mono', monospace;
                font-size: 14px;
                text-align: left;
                background-color: transparent;
                border: none;
                padding: 12px 10px;
                border-left: 3px solid transparent;
                color: #555555;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            QPushButton:checked {
                font-weight: bold;
                border-left: 3px solid #333333;
                background-color: rgba(0, 0, 0, 0.08);
                color: #333333;
            }
        """)
        btn.setCheckable(True)
        return btn

    def _switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)
        self.btn_general.setChecked(index == 0)
        self.btn_license.setChecked(index == 1)
        self.btn_instructions.setChecked(index == 2)

    def _setup_general_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Lang section
        self.lang_label = QLabel(translator.get("settings_lang"))
        self.lang_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; font-family: 'Roboto Mono', monospace;")
        layout.addWidget(self.lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(translator.get("settings_lang_pt"), "pt")
        self.lang_combo.addItem(translator.get("settings_lang_en"), "en")
        
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Roboto Mono', monospace;
                font-size: 14px;
                color: #1F2937;
            }
            QComboBox:hover {
                border: 1px solid #2F80ED;
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
        """)
        self.lang_combo.setFixedHeight(45)
        
        idx = self.lang_combo.findData(translator.get_language())
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
            
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        layout.addWidget(self.lang_combo)
        
        # Version section
        self.version_label = QLabel(translator.get("settings_version", "Versão do Sistema"))
        self.version_label.setStyleSheet("color: #555555; font-size: 16px; font-weight: bold; font-family: 'Roboto Mono', monospace; margin-top: 10px;")
        layout.addWidget(self.version_label)
        
        version_input = QLineEdit()
        version_input.setText(self.version)
        version_input.setReadOnly(True)
        version_input.setFixedHeight(45)
        version_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Roboto Mono', monospace;
                font-size: 14px;
                color: #4B5563;
            }
        """)
        layout.addWidget(version_input)
        layout.addStretch()
        return tab

    def _setup_license_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(48, 48, 48, 48)
        self.lic_label = QLabel(translator.get("settings_tab_license_content", "Licença do aplicativo não definida."))
        self.lic_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #555555; font-size: 14px;")
        layout.addWidget(self.lic_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return tab

    def _setup_instructions_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QScrollBar:vertical { border: none; background-color: #F0F0F0; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background-color: #CCCCCC; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background-color: #AAAAAA; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(19, 19, 19, 19)
        content_layout.setSpacing(24)
        
        self.inst_main_title = QLabel(translator.get("inst_title", "Instruções de Uso"))
        self.inst_main_title.setStyleSheet("color: #333333; font-size: 24px; font-weight: bold; font-family: 'Roboto Mono', monospace;")
        content_layout.addWidget(self.inst_main_title)
        
        self._add_instruction_section(content_layout, "inst_sec1_title", "Sobre o CryptoCational", 
                          "inst_sec1_body", "O CryptoCational é uma ferramenta projetada para criptografar, descriptografar e analisar textos utilizando a clássica Cifra de Vigenère.")
        self._add_instruction_section(content_layout, "inst_sec2_title", "Como Criptografar", 
                          "inst_sec2_body", "1. Na aba 'Criptografar', digite ou cole o texto que deseja proteger.\n2. Insira a Chave (apenas letras).\n3. Clique em 'Criptografar'.")
        self._add_instruction_section(content_layout, "inst_sec3_title", "Como Descriptografar (Texto Simples)", 
                          "inst_sec3_body", "Se você já sabe a chave, vá à aba 'Descriptografar', cole o texto cifrado, insira a chave correta e clique em 'Descriptografar'.")
        self._add_instruction_section(content_layout, "inst_sec4_title", "Análise de Frequência (Quebra da Cifra)", 
                          "inst_sec4_body", "Caso não possua a chave, você pode tentar descobri-la:\n\n1. Insira o texto cifrado.\n2. Clique em 'Estimar Tamanho'.")
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        return tab
        
    def _add_instruction_section(self, layout, title_key, default_title, body_key, default_body):
        title = QLabel(translator.get(title_key, default_title))
        title.setStyleSheet("color: #2D3748; font-size: 18px; font-weight: bold; font-family: 'Roboto Mono', monospace; margin-top: 10px;")
        
        body = QLabel(translator.get(body_key, default_body))
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setStyleSheet("color: #4A5568; font-size: 14px; line-height: 1.6; font-family: 'Roboto', sans-serif;")
        
        layout.addWidget(title)
        layout.addWidget(body)
        self.instruction_sections.append((title, body, title_key, default_title, body_key, default_body))

    def _on_language_changed(self, index):
        lang_code = self.lang_combo.itemData(index)
        translator.set_language(lang_code)
        
    def retranslate_ui(self, lang_code):
        self.title_label.setText(translator.get("settings_title"))
        self.btn_general.setText(translator.get("settings_tab_general", "Geral"))
        self.btn_license.setText(translator.get("settings_tab_license", "Licença"))
        self.btn_instructions.setText(translator.get("settings_tab_instructions", "Instruções"))
        
        self.lang_label.setText(translator.get("settings_lang"))
        self.version_label.setText(translator.get("settings_version", "Versão do Sistema"))
        
        self.lic_label.setText(translator.get("settings_tab_license_content", "Licença do aplicativo não definida."))
        
        self.inst_main_title.setText(translator.get("inst_title", "Instruções de Uso"))
        for title, body, title_key, def_title, body_key, def_body in self.instruction_sections:
            title.setText(translator.get(title_key, def_title))
            body.setText(translator.get(body_key, def_body))
        
        self.lang_combo.blockSignals(True)
        self.lang_combo.setItemText(0, translator.get("settings_lang_pt"))
        self.lang_combo.setItemText(1, translator.get("settings_lang_en"))
        self.lang_combo.blockSignals(False)
