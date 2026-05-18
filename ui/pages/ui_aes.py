from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QFileDialog, QApplication,
    QSizePolicy, QGridLayout, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
import os
import hashlib

from core.translator import translator
from core.aes import normalize_key
from core.modes import (
    aes_ecb_encrypt, aes_ecb_decrypt,
    aes_ctr_encrypt, aes_ctr_decrypt,
    aes_ecb_encrypt_visual, aes_ctr_encrypt_visual,
)
from core.bmp_utils import (
    image_to_bmp_raw,
    extract_bmp_header_and_pixels,
    rebuild_bmp,
)
from ui.popups import show_error, show_warning, show_info

# ─────────────────────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────────────────────
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
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px;
    border: none;
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


class SelfieTestWorker(QThread):
    """
    Worker thread that encrypts BMP pixel data for multiple AES configs.
    
    Signals:
        result_ready(str, int, bytes, str, bytes): mode, rounds, display_bytes, hash_hex, save_bytes
        error_occurred(str, str, str): mode, rounds, error_msg
        all_done(): emitted when all configs are processed
    """
    result_ready = Signal(str, int, bytes, str, bytes)
    error_occurred = Signal(str, str, str)
    all_done = Signal()

    def __init__(self, bmp_pixels: bytes, key: bytes, bmp_header: bytes, parent=None):
        super().__init__(parent)
        self.bmp_pixels = bmp_pixels
        self.key = key
        self.bmp_header = bmp_header
        self._running = True

    def run(self):
        configs = [
            ("ecb", 3), ("ecb", 5), ("ecb", 9), ("ecb", 13),
            ("ctr", 3), ("ctr", 5), ("ctr", 9), ("ctr", 13),
        ]
        for mode, rounds in configs:
            if not self._running:
                break
            try:
                if mode == "ecb":
                    ct = aes_ecb_encrypt_visual(self.bmp_pixels, self.key, rounds)
                    # Truncate PKCS#7 padding so BMP dimensions stay valid
                    display_bytes = ct[:len(self.bmp_pixels)]
                    save_bytes = ct
                else:
                    ct, iv = aes_ctr_encrypt_visual(self.bmp_pixels, self.key, rounds)
                    display_bytes = ct
                    save_bytes = iv + ct

                h = hashlib.sha256(save_bytes).hexdigest()
                self.result_ready.emit(mode, rounds, display_bytes, h, save_bytes)
            except Exception as e:
                self.error_occurred.emit(mode, rounds, str(e))
        self.all_done.emit()

    def stop(self):
        self._running = False


class AESPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selfie_path = None
        self._selfie_data = None
        self._selfie_bmp = None
        self._bmp_header = None
        self._bmp_pixels = None
        self._test_results = {}
        self._worker = None
        self.setup_ui()
        translator.language_changed.connect(self.retranslate_ui)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        self.header = QLabel(translator.get("aes_title"))
        self.header.setStyleSheet("color: #333333; font-size: 24px; font-weight: bold; font-family: 'Roboto Mono', monospace;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)

        # ── Selfie Tests Section ──
        self._setup_selfie_ui(scroll_layout)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        self.setStyleSheet("background-color: #f8f8f8;")

    def _setup_selfie_ui(self, scroll_layout):
        # Selfie Card
        self.selfie_card = CardWidget(translator.get("aes_selfie_title", "Testes com Selfie"))

        # Key input
        key_layout = QHBoxLayout()
        key_layout.setSpacing(12)
        key_label = QLabel(translator.get("aes_key_label", "Chave"))
        key_label.setStyleSheet(SECTION_TITLE_STYLE)
        key_layout.addWidget(key_label)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(translator.get("aes_key_placeholder", "Digite a chave (texto simples)"))
        self.key_input.setStyleSheet(INPUT_STYLE)
        self.key_input.setMinimumHeight(40)
        key_layout.addWidget(self.key_input)
        self.selfie_card.main_layout.addLayout(key_layout)

        # Selfie controls
        selfie_ctrl = QHBoxLayout()
        selfie_ctrl.setSpacing(12)

        self.btn_select_selfie = QPushButton(translator.get("aes_selfie_select"))
        self.btn_select_selfie.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_selfie.setMinimumHeight(40)
        self.btn_select_selfie.setStyleSheet(BUTTON_NEUTRAL)
        self.btn_select_selfie.clicked.connect(self._select_selfie)
        selfie_ctrl.addWidget(self.btn_select_selfie)

        self.btn_run_tests = QPushButton(translator.get("aes_selfie_run_tests"))
        self.btn_run_tests.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run_tests.setMinimumHeight(40)
        self.btn_run_tests.setStyleSheet(BUTTON_SUCCESS)
        self.btn_run_tests.clicked.connect(self._run_selfie_tests)
        selfie_ctrl.addWidget(self.btn_run_tests)

        selfie_ctrl.addStretch()
        self.selfie_card.main_layout.addLayout(selfie_ctrl)

        # Original image preview
        self.original_preview_label = QLabel(translator.get("aes_selfie_none", "Nenhuma imagem selecionada"))
        self.original_preview_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #6B7280; font-size: 12px;")
        self.original_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_preview_label.setMinimumHeight(120)
        self.selfie_card.main_layout.addWidget(self.original_preview_label)

        # Results grid (8 cards: 4 ECB + 4 CTR)
        results_grid = QGridLayout()
        results_grid.setSpacing(16)
        results_grid.setColumnStretch(0, 1)
        results_grid.setColumnStretch(1, 1)
        results_grid.setColumnStretch(2, 1)
        results_grid.setColumnStretch(3, 1)

        self.result_cards = {}
        test_configs = [
            ("ecb", 3), ("ecb", 5), ("ecb", 9), ("ecb", 13),
            ("ctr", 3), ("ctr", 5), ("ctr", 9), ("ctr", 13),
        ]

        for idx, (mode, rounds) in enumerate(test_configs):
            card = self._create_result_card(mode, rounds)
            self.result_cards[(mode, rounds)] = card
            row = 0 if idx < 4 else 1
            col = idx % 4
            results_grid.addWidget(card, row, col)

        self.selfie_card.main_layout.addLayout(results_grid)
        scroll_layout.addWidget(self.selfie_card)
        scroll_layout.addStretch()

    def _create_result_card(self, mode, rounds):
        key = f"aes_test_{mode}_{rounds}"
        title = translator.get(key, f"{mode.upper()} - {rounds} rodadas")
        card = CardWidget(title)
        card.setMinimumHeight(260)

        img_label = QLabel(translator.get("aes_waiting_test", "Aguardando teste..."))
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setMinimumHeight(140)
        img_label.setStyleSheet("background-color: #F1F5F9; border-radius: 8px; font-family: 'Roboto Mono', monospace; color: #6B7280; font-size: 11px;")
        card.main_layout.addWidget(img_label)
        card.img_label = img_label

        hash_label = QLabel(f"{translator.get('aes_hash_label', 'Hash SHA-256:')} --")
        hash_label.setStyleSheet("font-family: 'Roboto Mono', monospace; color: #4B5563; font-size: 10px;")
        hash_label.setWordWrap(True)
        card.main_layout.addWidget(hash_label)
        card.hash_label = hash_label

        btn_save = QPushButton(translator.get("aes_save_btn"))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setMinimumHeight(32)
        btn_save.setStyleSheet(BUTTON_PRIMARY)
        btn_save.clicked.connect(lambda checked, m=mode, r=rounds: self._save_result(m, r))
        btn_save.setEnabled(False)
        card.main_layout.addWidget(btn_save)
        card.btn_save = btn_save

        return card

    # ── Helpers ──
    def _get_key(self):
        text = self.key_input.text().strip()
        if not text:
            show_warning(self, translator.get("aes_msg_no_key"))
            return None
        return normalize_key(text)

    def _select_selfie(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            translator.get("aes_selfie_select"),
            "",
            translator.get("aes_file_filter_img")
        )
        if path:
            try:
                with open(path, 'rb') as f:
                    self._selfie_data = f.read()
                self._selfie_path = path

                # Converte para BMP 24-bit raw 512x512 para testes visuais rápidos
                self._selfie_bmp = image_to_bmp_raw(self._selfie_data, 512, 512)
                self._bmp_header, self._bmp_pixels = extract_bmp_header_and_pixels(self._selfie_bmp)

                self._test_results.clear()
                self._show_original_preview()
                self._clear_result_cards()
            except Exception as e:
                show_error(self, str(e))

    def _show_original_preview(self):
        pixmap = QPixmap()
        if pixmap.loadFromData(self._selfie_bmp):
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.original_preview_label.setPixmap(pixmap)
            self.original_preview_label.setText("")
        else:
            self.original_preview_label.setText(translator.get("aes_selfie_error", "Erro ao carregar preview"))

    def _clear_result_cards(self):
        for card in self.result_cards.values():
            card.img_label.setText(translator.get("aes_waiting_test", "Aguardando teste..."))
            card.img_label.setPixmap(QPixmap())
            card.hash_label.setText(f"{translator.get('aes_hash_label', 'Hash SHA-256:')} --")
            card.btn_save.setEnabled(False)

    # ── Selfie Tests ──
    def _run_selfie_tests(self):
        if not self._bmp_pixels:
            show_warning(self, translator.get("aes_msg_no_selfie", "Selecione uma selfie primeiro."))
            return

        key = self._get_key()
        if key is None:
            return

        # Limpa resultados anteriores e desabilita controles
        self._test_results.clear()
        self._clear_result_cards()
        self.btn_run_tests.setEnabled(False)
        self.btn_select_selfie.setEnabled(False)

        self._worker = SelfieTestWorker(self._bmp_pixels, key, self._bmp_header, self)
        self._worker.result_ready.connect(self._on_worker_result)
        self._worker.error_occurred.connect(self._on_worker_error)
        self._worker.all_done.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_result(self, mode, rounds, display_bytes, hash_hex, save_bytes):
        # Store display_bytes so we can save the visual BMP/PNG later
        self._test_results[(mode, rounds)] = (display_bytes, hash_hex)
        self._display_result_card(mode, rounds, display_bytes, hash_hex)

    def _on_worker_error(self, mode, rounds, msg):
        card = self.result_cards[(mode, rounds)]
        card.img_label.setText(f"Erro: {msg}")
        card.hash_label.setText(f"{translator.get('aes_hash_label', 'Hash SHA-256:')} --")
        card.btn_save.setEnabled(False)

    def _on_worker_finished(self):
        self.btn_run_tests.setEnabled(True)
        self.btn_select_selfie.setEnabled(True)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def _display_result_card(self, mode, rounds, display_bytes, hash_hex):
        card = self.result_cards[(mode, rounds)]

        # Reconstrói BMP válido com header original + pixels criptografados
        bmp_bytes = rebuild_bmp(self._bmp_header, display_bytes)

        pixmap = QPixmap()
        if pixmap.loadFromData(bmp_bytes):
            pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            card.img_label.setPixmap(pixmap)
            card.img_label.setText("")
        else:
            card.img_label.setText(translator.get("aes_preview_na", "Preview não disponível"))
            card.img_label.setPixmap(QPixmap())

        card.hash_label.setText(f"{translator.get('aes_hash_label', 'Hash SHA-256:')} {hash_hex[:32]}...")
        card.btn_save.setEnabled(True)

    def _save_result(self, mode, rounds):
        if (mode, rounds) not in self._test_results:
            return
        display_bytes, _ = self._test_results[(mode, rounds)]

        # Rebuild the visual BMP that is shown on screen
        bmp_bytes = rebuild_bmp(self._bmp_header, display_bytes)

        pixmap = QPixmap()
        if not pixmap.loadFromData(bmp_bytes):
            show_error(self, "Não foi possível carregar a imagem para salvar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Salvar {mode.upper()} {rounds} rodadas",
            f"selfie_{mode}_{rounds}r.png",
            translator.get("aes_file_filter_img")
        )
        if path:
            try:
                # Ensure the file has a .png extension for the save dialog
                # but QFileDialog already enforces it via the filter
                if not path.lower().endswith('.png'):
                    path += '.png'
                pixmap.save(path, "PNG")
                show_info(self, f"{translator.get('aes_saved_to', 'Salvo em:')} {path}")
            except Exception as e:
                show_error(self, str(e))

    # ── Retranslate ──
    def retranslate_ui(self, lang_code=None):
        self.header.setText(translator.get("aes_title"))

        # Selfie section
        self.selfie_card.title_label.setText(translator.get("aes_selfie_title"))
        self.btn_select_selfie.setText(translator.get("aes_selfie_select"))
        self.btn_run_tests.setText(translator.get("aes_selfie_run_tests"))
        if not self._selfie_data:
            self.original_preview_label.setText(translator.get("aes_selfie_none", "Nenhuma imagem selecionada"))

        # Result cards
        for (mode, rounds), card in self.result_cards.items():
            key = f"aes_test_{mode}_{rounds}"
            card.title_label.setText(translator.get(key))
            card.btn_save.setText(translator.get("aes_save_btn"))
            if (mode, rounds) not in self._test_results:
                card.img_label.setText(translator.get("aes_waiting_test", "Aguardando teste..."))
                card.hash_label.setText(f"{translator.get('aes_hash_label', 'Hash SHA-256:')} --")
