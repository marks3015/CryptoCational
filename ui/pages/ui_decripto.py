from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QSlider, QGroupBox,
    QApplication, QSizePolicy, QSplitter, QStackedWidget, QGridLayout,
    QInputDialog, QListView
)

from ui.popups import show_error, show_warning, show_info
from ui.popups.input_popup import get_input_text
from PySide6.QtCore import Qt, Signal
import sys
import os
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.vigenere import decrypt_preserve_format, normalize_text
from core.frequency import calculate_frequencies, get_language_frequencies
from core.attack import estimate_key_length, chi_squared_score
from core.utils import split_text_into_columns, estimate_ic
from core.translator import translator
from core.aes import normalize_key
from core.modes import aes_ecb_decrypt, aes_ctr_decrypt


# Standardized styles
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
QTextEdit, QLineEdit, QComboBox, QSpinBox {
    font-family: 'Roboto Mono', monospace;
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #2F80ED;
    selection-color: white;
}
QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #2F80ED;
}
QTextEdit:read-only, QLineEdit:read-only {
    background-color: #F8FAFC;
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
"""

# COMBOBOX_STYLE removed — now uses INPUT_STYLE for consistency

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
QPushButton:disabled {
    background-color: transparent;
    color: #94A3B8;
    border: 1.5px solid #E2E8F0;
}
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

BUTTON_PURPLE = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #8B5CF6;
    border: 1.5px solid #8B5CF6;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover { background-color: rgba(139, 92, 246, 0.1); }
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


class InteractiveFrequencyAnalyzer(QWidget):
    shift_changed = Signal(int)
    alignment_score = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_shift = 0
        self._observed_freq = None
        self._expected_freq = None
        self._column_text = ""
        self._language = "pt"
        self._best_shift = None
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # Single card with chart + controls
        chart_card = CardWidget()
        
        # Chart
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 8px;")
        self.chart_frame.setMinimumHeight(280)
        chart_inner = QVBoxLayout(self.chart_frame)
        chart_inner.setContentsMargins(8, 8, 8, 8)
        
        self.figure = Figure(figsize=(6.2, 3.0), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)
        chart_inner.addWidget(self.canvas)
        chart_card.main_layout.addWidget(self.chart_frame)
        
        # Spacing between chart and controls
        chart_card.main_layout.addSpacing(16)
        
        # Controls (slider + buttons) inside the same card
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(12)
        
        self.btn_shift_left = QPushButton("<")
        self.btn_shift_left.setFixedSize(44, 44)
        self.btn_shift_left.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_shift_left.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shift_left.clicked.connect(lambda: self._adjust_shift(-1))
        slider_layout.addWidget(self.btn_shift_left)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 25)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.NoTicks)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.setMinimumHeight(24)
        self.slider.setStyleSheet("""
            QSlider {
                background: transparent;
            }
            QSlider::groove:horizontal {
                border: 1px solid #D1D5DB;
                height: 4px;
                background: #E5E7EB;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #6B7280;
                border: 1.5px solid #4B5563;
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #9CA3AF;
                border-radius: 2px;
            }
        """)
        slider_layout.addWidget(self.slider, 1)

        self.btn_shift_right = QPushButton(">")
        self.btn_shift_right.setFixedSize(44, 44)
        self.btn_shift_right.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_shift_right.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shift_right.clicked.connect(lambda: self._adjust_shift(1))
        slider_layout.addWidget(self.btn_shift_right)
        
        chart_card.main_layout.addLayout(slider_layout)
        
        # Confirm button
        chart_card.main_layout.addSpacing(12)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_apply = QPushButton("Confirmar Letra")
        self.btn_apply.setMinimumHeight(44)
        self.btn_apply.setMinimumWidth(200)
        self.btn_apply.setStyleSheet(BUTTON_SUCCESS)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addStretch()
        chart_card.main_layout.addLayout(btn_layout)
        
        root.addWidget(chart_card)

    def _calculate_best_shift(self):
        if not self._observed_freq or not self._expected_freq:
            return 0

        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        best_shift = 0
        best_score = float('inf')
        for shift in range(26):
            shifted = {}
            for i, letter in enumerate(letters):
                cipher_idx = (i + shift) % 26
                cipher_letter = letters[cipher_idx]
                shifted[letter] = self._observed_freq.get(cipher_letter, 0)
            score = chi_squared_score(shifted, self._expected_freq)
            if score < best_score:
                best_score = score
                best_shift = shift
        return best_shift

    def _calculate_alignment_score(self, observed):
        """Score 0-100 based on histogram intersection (overlap area).
        Directly reflects how much the bar charts visually overlap."""
        if not self._expected_freq:
            return 0.0

        overlap = 0.0
        total_expected = 0.0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            obs = observed.get(letter, 0)
            exp = self._expected_freq.get(letter, 0)
            overlap += min(obs, exp)
            total_expected += exp

        if total_expected > 0:
            return (overlap / total_expected) * 100.0
        return 0.0

    def _calculate_best_alignment(self):
        """Find the highest alignment score across all 26 shifts."""
        if not self._observed_freq or not self._expected_freq:
            return 0.0

        best = 0.0
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for shift in range(26):
            shifted = {}
            for i, letter in enumerate(letters):
                cipher_idx = (i + shift) % 26
                shifted[letter] = self._observed_freq.get(letters[cipher_idx], 0)
            score = self._calculate_alignment_score(shifted)
            if score > best:
                best = score
        return best

    def set_column_data(self, column_text, language="pt", initial_shift=None):
        self._column_text = column_text
        self._language = language
        self._observed_freq = calculate_frequencies(column_text)
        try:
            self._expected_freq = get_language_frequencies(language)
        except Exception:
            self._expected_freq = get_language_frequencies("pt")

        if initial_shift is not None:
            self._current_shift = initial_shift % 26
        else:
            self._current_shift = 0

        self.slider.blockSignals(True)
        self.slider.setValue(self._current_shift)
        self.slider.blockSignals(False)

        self._best_shift = self._calculate_best_shift()
        self._best_alignment_score = self._calculate_best_alignment()
        self._update_chart()

    def _adjust_shift(self, delta):
        new_shift = self._current_shift + delta
        if 0 <= new_shift <= 25:
            self.slider.setValue(new_shift)

    def _on_slider_changed(self, value):
        self._current_shift = value
        self._update_chart()
        self.shift_changed.emit(value)

    def _shift_to_letter(self, shift):
        return chr((shift % 26) + ord('A'))

    def _update_chart(self):
        if not self._observed_freq or not self._expected_freq:
            return

        shifted_observed = {}
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i, letter in enumerate(letters):
            cipher_idx = (i + self._current_shift) % 26
            cipher_letter = letters[cipher_idx]
            shifted_observed[letter] = self._observed_freq.get(cipher_letter, 0)

        x = np.arange(26)
        observed_values = [shifted_observed[l] for l in letters]
        expected_values = [self._expected_freq.get(l, 0) for l in letters]

        # Check if current shift is the best alignment
        score = self._calculate_alignment_score(shifted_observed)
        is_best = hasattr(self, '_best_alignment_score') and score >= self._best_alignment_score - 0.1
        obs_edge = '#22C55E' if is_best else '#374151'
        obs_lw = 1.5 if is_best else 1.2

        self.ax.clear()
        width = 0.55
        self.ax.bar(x, expected_values, width, label='Esperada', 
                   color='none', edgecolor='#9CA3AF', linewidth=1.0, zorder=1)
        self.ax.bar(x, observed_values, width, label='Observada', 
                   color='none', edgecolor=obs_edge, linewidth=obs_lw, zorder=2)

        for i, (obs, exp) in enumerate(zip(observed_values, expected_values)):
            if obs > 1 and exp > 1 and abs(obs - exp) < 3:
                self.ax.bar(x[i], max(obs, exp), width, color='#D1D5DB', alpha=0.3, edgecolor='none', zorder=0)

        self.ax.set_xlabel('Letra', fontsize=8, color='#6B7280')
        self.ax.set_ylabel('Freq. (%)', fontsize=8, color='#6B7280')
        self.ax.set_title(f'Shift: {self._current_shift} ({self._shift_to_letter(self._current_shift)})',
                         fontsize=10, fontweight='bold', color='#1F2937')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(list(letters), fontsize=7, color='#6B7280')
        self.ax.tick_params(axis='y', labelsize=7, colors='#6B7280')
        self.ax.legend(loc='upper right', fontsize=7, framealpha=0.5, edgecolor='#D1D5DB')
        self.ax.grid(True, alpha=0.15, axis='y', linestyle='--', color='#9CA3AF')
        self.ax.set_facecolor('#FAFAFA')
        for spine in self.ax.spines.values():
            spine.set_color('#D1D5DB')
            spine.set_linewidth(0.5)

        max_val = max(max(observed_values), max(expected_values)) if observed_values and expected_values else 5
        self.ax.set_ylim(0, max(max_val * 1.2, 5))

        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()
        self.alignment_score.emit(score)

    def get_current_shift(self):
        return self._current_shift

    def connect_apply_button(self, callback):
        self.btn_apply.clicked.connect(callback)


class DecriptoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ciphertext_original = ""
        self._ciphertext_normalized = ""
        self._key_length = 8
        self._current_column = 0
        self._columns = []
        self._key_letters = ['?'] * 20
        self._confirmed = [False] * 20
        self.setup_ui()
        translator.language_changed.connect(self.retranslate_ui)

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8f8f8;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Internal stack for navigation: Home -> Sub-pages
        self.decripto_stack = QStackedWidget()

        # Page 0: Home (selection)
        self.home_widget = QWidget()
        self._setup_home_page()
        self.decripto_stack.addWidget(self.home_widget)

        # Page 1: Vigenère Frequency Analysis
        self.vigenere_widget = QWidget()
        self._setup_vigenere_page()
        self.decripto_stack.addWidget(self.vigenere_widget)

        # Page 2: AES Decryption
        self.aes_widget = QWidget()
        self._setup_aes_page()
        self.decripto_stack.addWidget(self.aes_widget)

        main_layout.addWidget(self.decripto_stack)

    def _setup_home_page(self):
        layout = QVBoxLayout(self.home_widget)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top stretch to push content to center vertically
        layout.addStretch(1)

        # Title
        self.home_title = QLabel(translator.get("decripto_home_title", "Decifração"))
        self.home_title.setStyleSheet("font-family: 'Roboto Mono', monospace; font-size: 32px; font-weight: bold; color: #333333;")
        self.home_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.home_title)

        # Subtitle
        self.home_subtitle = QLabel(translator.get("decripto_home_subtitle", "Selecione um método de decifração"))
        self.home_subtitle.setStyleSheet("font-family: 'Roboto Mono', monospace; font-size: 14px; color: #6B7280;")
        self.home_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.home_subtitle)

        layout.addSpacing(40)

        # Buttons grid
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button 1: Vigenère
        self.btn_vigenere = QPushButton(translator.get("decripto_tab_vigenere", "Análise Manual de Frequência"))
        self.btn_vigenere.setMinimumHeight(120)
        self.btn_vigenere.setMinimumWidth(280)
        self.btn_vigenere.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_vigenere.setStyleSheet(BUTTON_PRIMARY + """
            QPushButton {
                font-size: 15px;
                border-width: 2px;
            }
        """)
        self.btn_vigenere.clicked.connect(lambda: self.decripto_stack.setCurrentIndex(1))
        buttons_layout.addWidget(self.btn_vigenere)

        # Button 2: AES
        self.btn_aes_decrypt = QPushButton(translator.get("decripto_tab_aes", "Decifração AES"))
        self.btn_aes_decrypt.setMinimumHeight(120)
        self.btn_aes_decrypt.setMinimumWidth(280)
        self.btn_aes_decrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aes_decrypt.setStyleSheet(BUTTON_DANGER + """
            QPushButton {
                font-size: 15px;
                border-width: 2px;
            }
        """)
        self.btn_aes_decrypt.clicked.connect(lambda: self.decripto_stack.setCurrentIndex(2))
        buttons_layout.addWidget(self.btn_aes_decrypt)

        layout.addLayout(buttons_layout)

        # Bottom stretch to keep content centered
        layout.addStretch(1)

    def _setup_vigenere_page(self):
        layout = QVBoxLayout(self.vigenere_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(8)

        self.left_panel = self._create_left_panel()
        self.center_panel = self._create_center_panel()
        self.right_panel = self._create_right_panel()

        self.left_panel.setMinimumWidth(200)
        self.center_panel.setMinimumWidth(400)
        self.right_panel.setMinimumWidth(200)

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.center_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setSizes([220, 640, 220])
        layout.addWidget(self.splitter, 1)

    def _setup_aes_page(self):
        layout = QVBoxLayout(self.aes_widget)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)

        # Grid
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setColumnStretch(1, 1)
        grid.setColumnMinimumWidth(0, 340)

        # Config Card
        self.aes_config_card = CardWidget(translator.get("config_label", "Configurações"))

        self.aes_mode_label_d = QLabel(translator.get("aes_mode_label"))
        self.aes_mode_label_d.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.aes_config_card.main_layout.addWidget(self.aes_mode_label_d)

        self.aes_mode_combo_d = QComboBox()
        self.aes_mode_combo_d.addItem(translator.get("aes_mode_ecb"), "ecb")
        self.aes_mode_combo_d.addItem(translator.get("aes_mode_ctr"), "ctr")
        self.aes_mode_combo_d.setFixedHeight(40)
        self.aes_mode_combo_d.setStyleSheet(INPUT_STYLE)
        self.aes_config_card.main_layout.addWidget(self.aes_mode_combo_d)
        self.aes_config_card.main_layout.addSpacing(8)

        self.aes_rounds_label_d = QLabel(translator.get("aes_rounds_label"))
        self.aes_rounds_label_d.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.aes_config_card.main_layout.addWidget(self.aes_rounds_label_d)

        self.aes_rounds_spin_d = QSpinBox()
        self.aes_rounds_spin_d.setRange(1, 13)
        self.aes_rounds_spin_d.setValue(10)
        self.aes_rounds_spin_d.setFixedHeight(40)
        self.aes_rounds_spin_d.setStyleSheet(INPUT_STYLE)
        self.aes_config_card.main_layout.addWidget(self.aes_rounds_spin_d)
        self.aes_config_card.main_layout.addSpacing(8)

        self.aes_key_label_d = QLabel(translator.get("aes_key_label"))
        self.aes_key_label_d.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.aes_config_card.main_layout.addWidget(self.aes_key_label_d)

        self.aes_key_input_d = QLineEdit()
        self.aes_key_input_d.setPlaceholderText(translator.get("aes_key_placeholder"))
        self.aes_key_input_d.setFixedHeight(40)
        self.aes_key_input_d.setStyleSheet(INPUT_STYLE)
        self.aes_config_card.main_layout.addWidget(self.aes_key_input_d)
        self.aes_config_card.main_layout.addStretch()

        grid.addWidget(self.aes_config_card, 0, 0)

        # Input Card
        self.aes_input_card = CardWidget(translator.get("decripto_aes_input", "Ciphertext (Hex)"))
        self.aes_text_input_d = QTextEdit()
        self.aes_text_input_d.setPlaceholderText(translator.get("aes_input_placeholder"))
        self.aes_text_input_d.setMinimumHeight(120)
        self.aes_text_input_d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.aes_text_input_d.setStyleSheet(INPUT_STYLE)
        self.aes_input_card.main_layout.addWidget(self.aes_text_input_d)
        grid.addWidget(self.aes_input_card, 0, 1)

        # Action Button (row 1, col 0) - positioned directly below config card
        self.aes_btn_decrypt = QPushButton(translator.get("aes_btn_decrypt"))
        self.aes_btn_decrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aes_btn_decrypt.setMinimumHeight(44)
        self.aes_btn_decrypt.setStyleSheet(BUTTON_PRIMARY)
        self.aes_btn_decrypt.clicked.connect(self._decrypt_aes)
        
        btn_wrapper = QWidget()
        btn_wrapper_layout = QVBoxLayout(btn_wrapper)
        btn_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        btn_wrapper_layout.addWidget(self.aes_btn_decrypt)
        btn_wrapper_layout.addStretch()
        grid.addWidget(btn_wrapper, 1, 0)

        # Output Card
        self.aes_output_card = CardWidget(translator.get("decrypted_text", "Texto Decifrado"))
        self.aes_text_output_d = QTextEdit()
        self.aes_text_output_d.setReadOnly(True)
        self.aes_text_output_d.setMinimumHeight(120)
        self.aes_text_output_d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.aes_text_output_d.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 13px; }")
        self.aes_output_card.main_layout.addWidget(self.aes_text_output_d)

        self.aes_btn_copy_d = QPushButton(translator.get("aes_btn_copy"))
        self.aes_btn_copy_d.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aes_btn_copy_d.setMinimumHeight(38)
        self.aes_btn_copy_d.setStyleSheet(BUTTON_PRIMARY)
        self.aes_btn_copy_d.clicked.connect(self._copy_aes_result)
        self.aes_output_card.main_layout.addWidget(self.aes_btn_copy_d)

        grid.addWidget(self.aes_output_card, 1, 1)
        grid.setRowStretch(2, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def _decrypt_aes(self):
        raw = self.aes_text_input_d.toPlainText().strip()
        key_text = self.aes_key_input_d.text().strip()

        if not raw:
            show_warning(self, translator.get("aes_msg_no_text"))
            return
        if not key_text:
            show_warning(self, translator.get("aes_msg_no_key"))
            return

        key = normalize_key(key_text)
        mode = self.aes_mode_combo_d.currentData()
        rounds = self.aes_rounds_spin_d.value()

        try:
            data = bytes.fromhex(raw.replace(' ', '').replace('\n', ''))
        except ValueError:
            show_warning(self, "Formato hexadecimal inválido")
            return

        try:
            if mode == "ecb":
                result = aes_ecb_decrypt(data, key, rounds)
            else:
                if len(data) < 16:
                    show_warning(self, translator.get("aes_msg_ctr_short"))
                    return
                iv = data[:16]
                ciphertext = data[16:]
                result = aes_ctr_decrypt(ciphertext, key, rounds, iv)
            try:
                text = result.decode('utf-8')
                self.aes_text_output_d.setPlainText(text)
            except UnicodeDecodeError:
                self.aes_text_output_d.setPlainText(result.hex())
        except Exception as e:
            show_error(self, str(e))

    def _copy_aes_result(self):
        text = self.aes_text_output_d.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def _create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Cryptogram Card
        self.cripto_card = CardWidget(translator.get("crypto_text", "Criptograma"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(translator.get("input_placeholder", "Cole o texto cifrado aqui..."))
        self.input_text.setMinimumHeight(100)
        self.input_text.setMaximumHeight(180)
        self.input_text.setStyleSheet(INPUT_STYLE + "QTextEdit { font-family: 'Roboto Mono', Consolas, monospace; font-size: 13px; }")
        self.cripto_card.main_layout.addWidget(self.input_text)
        layout.addWidget(self.cripto_card)

        # Configuration Card
        self.config_card = CardWidget(translator.get("config_label", "Configurações"))
        self.config_card.main_layout.setSpacing(4)
        
        # Language
        self.lang_label = QLabel(translator.get("config_lang", "Idioma"))
        self.lang_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.config_card.main_layout.addWidget(self.lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("Português", "pt")
        self.language_combo.addItem("Inglês", "en")
        self.language_combo.setFixedHeight(42)
        self.language_combo.setStyleSheet(INPUT_STYLE)
        # Style the dropdown list directly to avoid black rectangle
        combo_view = QListView()
        combo_view.setStyleSheet("""
            QListView {
                background-color: #FFFFFF;
                color: #1F2937;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                selection-background-color: #2F80ED;
                selection-color: white;
                padding: 4px;
                font-family: 'Roboto Mono', monospace;
                outline: none;
            }
            QListView::item {
                padding: 6px 12px;
            }
            QListView::item:hover {
                background-color: #F1F5F9;
            }
        """)
        self.language_combo.setView(combo_view)
        self.config_card.main_layout.addWidget(self.language_combo)
        
        # Separation between sections
        self.config_card.main_layout.addSpacing(16)
        
        # Key size
        self.key_label_ui = QLabel(translator.get("config_key_size", "Tamanho da chave"))
        self.key_label_ui.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.config_card.main_layout.addWidget(self.key_label_ui)
        
        self.key_length_spin = QSpinBox()
        self.key_length_spin.setRange(1, 20)
        self.key_length_spin.setValue(8)
        self.key_length_spin.setFixedHeight(42)
        self.key_length_spin.valueChanged.connect(self._on_keylength_changed)
        self.key_length_spin.setStyleSheet(INPUT_STYLE + """
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                border: none;
            }
        """)
        self.config_card.main_layout.addWidget(self.key_length_spin)
        
        # Separation before buttons
        self.config_card.main_layout.addSpacing(20)
        
        self.btn_estimate = QPushButton(translator.get("btn_estimate_size", "Estimar Tamanho"))
        self.btn_estimate.setMinimumHeight(38)
        self.btn_estimate.setStyleSheet(BUTTON_PURPLE)
        self.btn_estimate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_estimate.clicked.connect(self._estimate_key_length)
        self.config_card.main_layout.addWidget(self.btn_estimate)
        
        self.config_card.main_layout.addSpacing(8)

        self.btn_start = QPushButton(translator.get("btn_start_analysis", "Iniciar Análise"))
        self.btn_start.setMinimumHeight(38)
        self.btn_start.setStyleSheet(BUTTON_SUCCESS)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self._start_analysis)
        self.config_card.main_layout.addWidget(self.btn_start)
        
        layout.addWidget(self.config_card)

        # Key Card
        self.key_card = CardWidget(translator.get("key_display_label", "Chave"))
        
        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setPlaceholderText("????????")
        self.key_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_display.setMinimumHeight(50)
        self.key_display.setStyleSheet(INPUT_STYLE + "QLineEdit { font-family: 'Roboto Mono', Consolas, monospace; font-size: 18px; font-weight: 700; letter-spacing: 4px; }")
        self.key_card.main_layout.addWidget(self.key_display)

        self.btn_edit_key = QPushButton(translator.get("btn_edit_key", "Editar Chave"))
        self.btn_edit_key.setMinimumHeight(38)
        self.btn_edit_key.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_edit_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_key.clicked.connect(self._edit_key)
        self.key_card.main_layout.addWidget(self.btn_edit_key)
        
        layout.addWidget(self.key_card)
        layout.addStretch()
        
        return panel

    def _create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header Card
        header_card = CardWidget()
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        self.interactive_title = QLabel(translator.get("interactive_analysis", "Análise Interativa"))
        self.interactive_title.setStyleSheet("font-family: 'Roboto Mono', monospace; font-size: 15px; font-weight: 700; color: #1F2937; background-color: transparent;")
        header_layout.addWidget(self.interactive_title)
        header_layout.addStretch()

        self.btn_prev_col = QPushButton(translator.get("btn_prev", "< Anterior"))
        self.btn_prev_col.setMinimumHeight(40)
        self.btn_prev_col.setEnabled(False)
        self.btn_prev_col.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_prev_col.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev_col.clicked.connect(self._prev_column)
        header_layout.addWidget(self.btn_prev_col)

        self.column_label = QLabel(translator.get("col_label", curr="1", total="8").format(curr="1", total="8"))
        self.column_label.setStyleSheet("font-family: 'Roboto Mono', monospace; font-weight: 700; color: #1F2937; padding: 0 8px; background-color: transparent;")
        header_layout.addWidget(self.column_label)

        self.btn_next_col = QPushButton(translator.get("btn_next", "Próxima >"))
        self.btn_next_col.setMinimumHeight(40)
        self.btn_next_col.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_next_col.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next_col.clicked.connect(self._next_column)
        header_layout.addWidget(self.btn_next_col)

        header_card.main_layout.addLayout(header_layout)
        layout.addWidget(header_card)

        # Analyzer
        self.analyzer = InteractiveFrequencyAnalyzer()
        self.analyzer.shift_changed.connect(self._on_shift_changed)
        self.analyzer.alignment_score.connect(self._on_alignment_score_changed)
        self.analyzer.connect_apply_button(self._confirm_current_letter)
        layout.addWidget(self.analyzer, 1)

        return panel

    def _create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Decrypted Text Card
        self.result_card = CardWidget(translator.get("decrypted_text", "Texto Decifrado"))
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(140)
        self.output_text.setStyleSheet(INPUT_STYLE + "QTextEdit { font-family: 'Roboto Mono', Consolas, monospace; font-size: 13px; }")
        self.result_card.main_layout.addWidget(self.output_text)

        self.btn_copy = QPushButton(translator.get("btn_copy", "Copiar Resultado"))
        self.btn_copy.setMinimumHeight(38)
        self.btn_copy.setStyleSheet(BUTTON_PRIMARY)
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self._copy_result)
        self.result_card.main_layout.addWidget(self.btn_copy)
        
        layout.addWidget(self.result_card)

        # Statistics Card
        self.stats_card = CardWidget("Estatísticas")
        
        self.ic_label = QLabel(translator.get("stats_ic_none", "IC desta coluna: --"))
        self.ic_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.stats_card.main_layout.addWidget(self.ic_label)

        self.match_label = QLabel(translator.get("stats_alignment", "Alinhamento: --%").format(score="--"))
        self.match_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.stats_card.main_layout.addWidget(self.match_label)

        self.legibility_label = QLabel(translator.get("stats_legibility", "Legibilidade: --%").format(score="--"))
        self.legibility_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 13px; background-color: transparent;")
        self.stats_card.main_layout.addWidget(self.legibility_label)
        
        layout.addWidget(self.stats_card)
        layout.addStretch()

        return panel

    def retranslate_ui(self, lang_code=None):
        self.cripto_card.title_label.setText(translator.get("crypto_text"))
        self.config_card.title_label.setText(translator.get("config_label"))
        self.key_card.title_label.setText(translator.get("key_display_label"))
        self.result_card.title_label.setText(translator.get("decrypted_text"))
        self.stats_card.title_label.setText(translator.get("stats_label", "Estatísticas"))
        self.lang_label.setText(translator.get("config_lang"))
        self.key_label_ui.setText(translator.get("config_key_size"))
        self.btn_estimate.setText(translator.get("btn_estimate_size"))
        self.btn_start.setText(translator.get("btn_start_analysis"))
        self.btn_edit_key.setText(translator.get("btn_edit_key"))
        self.interactive_title.setText(translator.get("interactive_analysis"))
        self.btn_prev_col.setText(translator.get("btn_prev"))
        self.btn_next_col.setText(translator.get("btn_next"))
        self.btn_copy.setText(translator.get("btn_copy"))
        self.input_text.setPlaceholderText(translator.get("input_placeholder"))
        self.analyzer.btn_apply.setText(translator.get("btn_confirm_letter"))
        self.column_label.setText(translator.get("col_label").format(curr=self._current_column + 1, total=self._key_length))

        # Home page translations
        self.home_title.setText(translator.get("decripto_home_title", "Decifração"))
        self.home_subtitle.setText(translator.get("decripto_home_subtitle", "Selecione um método de decifração"))
        self.btn_vigenere.setText(translator.get("decripto_tab_vigenere", "Análise Manual de Frequência"))
        self.btn_aes_decrypt.setText(translator.get("decripto_tab_aes", "Decifração AES"))

        # AES page translations
        if hasattr(self, 'aes_config_card'):
            self.aes_config_card.title_label.setText(translator.get("config_label", "Configurações"))
            self.aes_mode_label_d.setText(translator.get("aes_mode_label"))
            self.aes_rounds_label_d.setText(translator.get("aes_rounds_label"))
            self.aes_key_label_d.setText(translator.get("aes_key_label"))
            self.aes_key_input_d.setPlaceholderText(translator.get("aes_key_placeholder"))
            self.aes_input_card.title_label.setText(translator.get("decripto_aes_input", "Ciphertext (Hex)"))
            self.aes_text_input_d.setPlaceholderText(translator.get("aes_input_placeholder"))
            self.aes_btn_decrypt.setText(translator.get("aes_btn_decrypt"))
            self.aes_output_card.title_label.setText(translator.get("decrypted_text", "Texto Decifrado"))
            self.aes_btn_copy_d.setText(translator.get("aes_btn_copy"))

        # Dynamic translation of runtime statistics based on initialization
        if not hasattr(self, '_ciphertext_original') or not self._ciphertext_original:
            self.ic_label.setText(translator.get("stats_ic_none", "IC desta coluna: --"))
            self.match_label.setText(translator.get("stats_alignment", "Alinhamento: {score}%").format(score="--"))
            self.legibility_label.setText(translator.get("stats_legibility", "Legibilidade: {score}%").format(score="--"))
        else:
            self._update_column_ui()
            # Restore shift rendering translations smoothly
            shift = self.analyzer.get_current_shift() if hasattr(self.analyzer, 'get_current_shift') else 0
            self._on_shift_changed(shift)
            self._decrypt_and_show()

    def _on_keylength_changed(self, value):
        self._key_length = value
        self._update_key_display()

    def _estimate_key_length(self):
        text = normalize_text(self.input_text.toPlainText())
        if not text:
            show_warning(self, translator.get("warn_insert_crypto", "Insira um criptograma primeiro."))
            return

        try:
            results = estimate_key_length(text, max_length=12, language='pt')
            if results:
                best = results[0][0]
                self.key_length_spin.setValue(best)
                msg = translator.get("msg_probable_sizes", "Tamanhos mais prováveis:\n\n")
                for length, score in results[:3]:
                    pct = f"{score:.0%}"
                    msg += translator.get("msg_key_size_pct", "  Chave {length}:  {pct}\n").format(length=length, pct=pct)
                show_info(self, msg)
        except Exception as e:
            show_error(self, str(e))

    def _start_analysis(self):
        original = self.input_text.toPlainText()
        normalized = normalize_text(original)
        if not normalized:
            show_warning(self, translator.get("warn_insert_crypto", "Insira um criptograma primeiro."))
            return

        self._ciphertext_original = original
        self._ciphertext_normalized = normalized
        self._key_length = self.key_length_spin.value()
        self._columns = split_text_into_columns(normalized, self._key_length)
        self._key_letters = ['?'] * self._key_length
        self._confirmed = [False] * self._key_length
        self._current_column = 0

        self._update_column_ui()
        self._update_key_display()
        self._decrypt_and_show()

        show_info(
            self,
            translator.get("info_crypto_divided", "Criptograma dividido em {num} colunas.\n\nUse os controles para ajustar o shift de cada coluna.").format(num=self._key_length)
        )

    def _update_column_ui(self):
        if not self._columns or self._current_column >= len(self._columns):
            return

        col_text = self._columns[self._current_column]
        language = self.language_combo.currentData()

        initial_shift = 0
        if self._confirmed[self._current_column]:
            initial_shift = ord(self._key_letters[self._current_column]) - ord('A')

        self.analyzer.set_column_data(col_text, language, initial_shift)
        self.column_label.setText(translator.get("col_label", "Coluna {curr} de {total}").format(curr=self._current_column + 1, total=self._key_length))
        self.btn_prev_col.setEnabled(self._current_column > 0)
        self.btn_next_col.setEnabled(self._current_column < self._key_length - 1)

        self._update_column_statistics(col_text)

    def _update_column_statistics(self, col_text):
        if len(col_text) > 1:
            ic = estimate_ic(col_text)
            self.ic_label.setText(translator.get("stats_ic", "IC desta coluna: {ic}").format(ic=f"{ic:.4f}"))
        else:
            self.ic_label.setText(translator.get("stats_ic_none", "IC desta coluna: --"))

    def _on_shift_changed(self, shift):
        letter = chr((shift % 26) + ord('A'))
        self._key_letters[self._current_column] = letter
        self._update_key_display()
        self._decrypt_and_show()

        # Directly compute alignment for current column/shift (histogram intersection)
        if self._columns and self._current_column < len(self._columns):
            col_text = self._columns[self._current_column]
            observed = calculate_frequencies(col_text)
            language = self.language_combo.currentData()
            try:
                expected = get_language_frequencies(language)
            except Exception:
                expected = get_language_frequencies("pt")

            letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            shifted = {}
            for i, l in enumerate(letters):
                cipher_idx = (i + shift) % 26
                shifted[l] = observed.get(letters[cipher_idx], 0)

            overlap = 0.0
            total_expected = 0.0
            for l in letters:
                overlap += min(shifted.get(l, 0), expected.get(l, 0))
                total_expected += expected.get(l, 0)
            score = (overlap / total_expected) * 100.0 if total_expected > 0 else 0.0
            self.match_label.setText(translator.get("stats_alignment", "Alinhamento: {score}%").format(score=f"{score:.1f}"))

    def _on_alignment_score_changed(self, score):
        self.match_label.setText(translator.get("stats_alignment", "Alinhamento: {score}%").format(score=f"{score:.1f}"))

    def _confirm_current_letter(self):
        shift = self.analyzer.get_current_shift()
        letter = chr((shift % 26) + ord('A'))
        self._key_letters[self._current_column] = letter
        self._confirmed[self._current_column] = True
        self._update_column_ui()
        self._update_key_display()

        if self._current_column < self._key_length - 1:
            self._next_column()

    def _prev_column(self):
        if self._current_column > 0:
            self._current_column -= 1
            self._update_column_ui()

    def _next_column(self):
        if self._current_column < self._key_length - 1:
            self._current_column += 1
            self._update_column_ui()

    def _update_key_display(self):
        self.key_display.setText(''.join(self._key_letters[:self._key_length]))

    def _decrypt_and_show(self):
        if not self._ciphertext_original:
            return

        key = ''.join(self._key_letters[:self._key_length])
        try:
            decrypted = decrypt_preserve_format(self._ciphertext_original, key)
            self.output_text.setPlainText(decrypted)
            self._update_statistics(decrypted)
        except Exception:
            pass

    def _update_statistics(self, decrypted_text):
        normalized = normalize_text(decrypted_text)
        if len(normalized) > 1:
            try:
                language = self.language_combo.currentData()

                # Legibility via IC (Index of Coincidence)
                ic = estimate_ic(normalized)
                # Portuguese IC ≈ 0.0745, English IC ≈ 0.0667, random ≈ 0.0385
                expected_ic = 0.0745 if language == 'pt' else 0.0667
                random_ic = 0.0385
                if expected_ic > random_ic:
                    legibility = max(0.0, min(100.0, (ic - random_ic) / (expected_ic - random_ic) * 100.0))
                else:
                    legibility = 0.0
                self.legibility_label.setText(translator.get("stats_legibility", "Legibilidade: {score}%").format(score=f"{legibility:.1f}"))
            except Exception:
                self.legibility_label.setText(translator.get("stats_legibility", "Legibilidade: --%").format(score="--"))
        else:
            self.legibility_label.setText(translator.get("stats_legibility", "Legibilidade: --%").format(score="--"))

    def _edit_key(self):
        current = ''.join(self._key_letters[:self._key_length])
        new_key, ok = get_input_text(self, translator.get("btn_edit_key", "Editar Chave"), translator.get("edit_key_prompt", "Digite a chave completa:"), default_text=current)
        if ok and new_key:
            new_key = new_key.upper()[:self._key_length]
            for i, char in enumerate(new_key):
                if char.isalpha():
                    self._key_letters[i] = char
                    self._confirmed[i] = True
            self._update_key_display()
            self._decrypt_and_show()
            self._update_column_ui()

    def _copy_result(self):
        result = self.output_text.toPlainText()
        if result:
            QApplication.clipboard().setText(result)
            show_info(self, "Texto copiado para a área de transferência!")
