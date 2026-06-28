"""Página RSA-OAEP — cifragem, decifragem e assinatura digital."""

from __future__ import annotations

import base64
import hashlib
import json
import sys
import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.rsa.keys import generate_keypair
from core.rsa.cipher import rsa_encrypt, rsa_decrypt
from core.rsa.signature import (
    BEGIN_SIGNED_MSG,
    BEGIN_SIGNATURE,
    END_SIGNED_MSG,
    _sign_hash,
    _verify_signature,
)
from core.translator import translator
from ui.popups import show_error, show_warning, show_info

# ---------------------------------------------------------------------------
# Shared styles (same palette as the rest of the app)
# ---------------------------------------------------------------------------

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
QTextEdit, QLineEdit {
    font-family: 'Roboto Mono', monospace;
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #2F80ED;
    selection-color: white;
}
QTextEdit:focus, QLineEdit:focus {
    border: 2px solid #2F80ED;
}
QTextEdit:read-only, QLineEdit:read-only {
    background-color: #F8FAFC;
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
QPushButton:disabled {
    color: #94A3B8;
    border: 1.5px solid #E2E8F0;
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
QPushButton:disabled {
    color: #94A3B8;
    border: 1.5px solid #E2E8F0;
}
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

BUTTON_HOME_RSA = """
QPushButton {
    font-family: 'Roboto Mono', monospace;
    background-color: transparent;
    color: #F59E0B;
    border: 2px solid #F59E0B;
    border-radius: 12px;
    padding: 16px 20px;
    font-weight: 700;
    font-size: 15px;
}
QPushButton:hover { background-color: rgba(245, 158, 11, 0.1); }
"""

INFO_LABEL_STYLE = (
    "font-family: 'Roboto Mono', monospace; "
    "font-size: 12px; color: #6B7280; "
    "background-color: transparent;"
)

WARNING_LABEL_STYLE = (
    "font-family: 'Roboto Mono', monospace; "
    "font-size: 12px; color: #DC2626; "
    "background-color: transparent; font-weight: 600;"
)

STATUS_LABEL_STYLE = (
    "font-family: 'Roboto Mono', monospace; "
    "font-size: 12px; color: #4B5563; "
    "background-color: transparent;"
)


# ---------------------------------------------------------------------------
# Helper widget: Card
# ---------------------------------------------------------------------------

class CardWidget(QFrame):
    def __init__(self, title: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(CARD_STYLE)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(10)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(SECTION_TITLE_STYLE)
            self.main_layout.addWidget(self.title_label)


# ---------------------------------------------------------------------------
# Key serialisation helpers
# ---------------------------------------------------------------------------

def _key_to_json(key: tuple) -> str:
    """Serialises (n, exp) to a JSON string with base64-encoded integers."""
    n, exp = key
    n_b64 = base64.b64encode(n.to_bytes((n.bit_length() + 7) // 8, "big")).decode()
    e_b64 = base64.b64encode(exp.to_bytes((exp.bit_length() + 7) // 8, "big")).decode()
    return json.dumps({"n": n_b64, "exp": e_b64}, indent=2)


def _json_to_key(text: str) -> tuple:
    """Deserialises JSON → (n, exp).  Raises ValueError on invalid input."""
    try:
        data = json.loads(text)
        n = int.from_bytes(base64.b64decode(data["n"]), "big")
        exp = int.from_bytes(base64.b64decode(data["exp"]), "big")
        return (n, exp)
    except Exception as exc:
        raise ValueError(f"Formato de chave inválido: {exc}") from exc


# ---------------------------------------------------------------------------
# Background worker for key generation
# ---------------------------------------------------------------------------

class RSAKeyWorker(QThread):
    """Generates an RSA-2048 key pair without blocking the UI thread."""

    finished = Signal(object, object)   # (public_key, private_key)
    error = Signal(str)

    def run(self):
        try:
            pub, priv = generate_keypair(bits=1024)
            self.finished.emit(pub, priv)
        except Exception as exc:
            self.error.emit(str(exc))


# ---------------------------------------------------------------------------
# RSA Page
# ---------------------------------------------------------------------------

class RSAPage(QWidget):
    # Sub-page indices
    _PAGE_HOME = 0
    _PAGE_KEYGEN = 1
    _PAGE_ENCRYPT = 2
    _PAGE_DECRYPT = 3
    _PAGE_SIGNVERIFY = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: RSAKeyWorker | None = None
        self._setup_ui()
        translator.language_changed.connect(self.retranslate_ui)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setStyleSheet("background-color: #f8f8f8;")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        # Build all sub-pages
        self._home_widget = QWidget()
        self._build_home_page()
        self.stack.addWidget(self._home_widget)      # 0

        self._keygen_widget = QWidget()
        self._build_keygen_page()
        self.stack.addWidget(self._keygen_widget)    # 1

        self._encrypt_widget = QWidget()
        self._build_encrypt_page()
        self.stack.addWidget(self._encrypt_widget)   # 2

        self._decrypt_widget = QWidget()
        self._build_decrypt_page()
        self.stack.addWidget(self._decrypt_widget)   # 3

        self._signverify_widget = QWidget()
        self._build_signverify_page()
        self.stack.addWidget(self._signverify_widget)  # 4

    # ---- helpers ----------------------------------------------------------

    def _nav_bar(self, title_key: str) -> QWidget:
        """Returns a top navigation bar widget with a back button and title."""
        bar = QWidget()
        bar.setStyleSheet("background-color: #f8f8f8;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(12)

        btn_back = QPushButton(translator.get("rsa_btn_back"))
        btn_back.setFixedHeight(36)
        btn_back.setMinimumWidth(80)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(BUTTON_NEUTRAL)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(self._PAGE_HOME))
        layout.addWidget(btn_back)

        lbl = QLabel(translator.get(title_key))
        lbl.setStyleSheet(
            "font-family: 'Roboto Mono', monospace; font-size: 18px; "
            "font-weight: bold; color: #333333; background-color: transparent;"
        )
        layout.addWidget(lbl)
        layout.addStretch()

        # store refs for retranslation
        bar._btn_back = btn_back  # type: ignore[attr-defined]
        bar._lbl_title = lbl       # type: ignore[attr-defined]
        bar._title_key = title_key # type: ignore[attr-defined]
        return bar

    # ---- Home page --------------------------------------------------------

    def _build_home_page(self):
        layout = QVBoxLayout(self._home_widget)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        self._home_title = QLabel(translator.get("rsa_home_title"))
        self._home_title.setStyleSheet(
            "font-family: 'Roboto Mono', monospace; font-size: 32px; "
            "font-weight: bold; color: #333333; background-color: transparent;"
        )
        self._home_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._home_title)

        self._home_subtitle = QLabel(translator.get("rsa_home_subtitle"))
        self._home_subtitle.setStyleSheet(
            "font-family: 'Roboto Mono', monospace; font-size: 14px; "
            "color: #6B7280; background-color: transparent;"
        )
        self._home_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._home_subtitle)

        layout.addSpacing(40)

        # Row 1: Keygen + Encrypt
        row1 = QHBoxLayout()
        row1.setSpacing(30)
        row1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_home_keygen = QPushButton(translator.get("rsa_btn_keygen"))
        self._btn_home_keygen.setMinimumHeight(110)
        self._btn_home_keygen.setMinimumWidth(260)
        self._btn_home_keygen.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_home_keygen.setStyleSheet(BUTTON_HOME_RSA)
        self._btn_home_keygen.clicked.connect(
            lambda: self.stack.setCurrentIndex(self._PAGE_KEYGEN)
        )
        row1.addWidget(self._btn_home_keygen)

        self._btn_home_encrypt = QPushButton(translator.get("rsa_btn_encrypt"))
        self._btn_home_encrypt.setMinimumHeight(110)
        self._btn_home_encrypt.setMinimumWidth(260)
        self._btn_home_encrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_home_encrypt.setStyleSheet(BUTTON_PRIMARY + "QPushButton { font-size: 15px; border-width: 2px; }")
        self._btn_home_encrypt.clicked.connect(
            lambda: self.stack.setCurrentIndex(self._PAGE_ENCRYPT)
        )
        row1.addWidget(self._btn_home_encrypt)

        layout.addLayout(row1)

        # Row 2: Decrypt + Sign/Verify
        row2 = QHBoxLayout()
        row2.setSpacing(30)
        row2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_home_decrypt = QPushButton(translator.get("rsa_btn_decrypt"))
        self._btn_home_decrypt.setMinimumHeight(110)
        self._btn_home_decrypt.setMinimumWidth(260)
        self._btn_home_decrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_home_decrypt.setStyleSheet(BUTTON_DANGER + "QPushButton { font-size: 15px; border-width: 2px; }")
        self._btn_home_decrypt.clicked.connect(
            lambda: self.stack.setCurrentIndex(self._PAGE_DECRYPT)
        )
        row2.addWidget(self._btn_home_decrypt)

        self._btn_home_signverify = QPushButton(translator.get("rsa_btn_sign_verify"))
        self._btn_home_signverify.setMinimumHeight(110)
        self._btn_home_signverify.setMinimumWidth(260)
        self._btn_home_signverify.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_home_signverify.setStyleSheet(BUTTON_SUCCESS + "QPushButton { font-size: 15px; border-width: 2px; }")
        self._btn_home_signverify.clicked.connect(
            lambda: self.stack.setCurrentIndex(self._PAGE_SIGNVERIFY)
        )
        row2.addWidget(self._btn_home_signverify)

        layout.addLayout(row2)

        layout.addStretch(1)

    # ---- Keygen page ------------------------------------------------------

    def _build_keygen_page(self):
        outer = QVBoxLayout(self._keygen_widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self._keygen_navbar = self._nav_bar("rsa_keygen_title")
        outer.addWidget(self._keygen_navbar)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # --- Config card (left) ---
        self._keygen_config_card = CardWidget(translator.get("rsa_keygen_title"))

        self._keygen_info_lbl = QLabel(translator.get("rsa_keygen_info"))
        self._keygen_info_lbl.setStyleSheet(INFO_LABEL_STYLE)
        self._keygen_info_lbl.setWordWrap(True)
        self._keygen_config_card.main_layout.addWidget(self._keygen_info_lbl)

        self._keygen_config_card.main_layout.addSpacing(12)

        self._btn_generate = QPushButton(translator.get("rsa_keygen_btn"))
        self._btn_generate.setMinimumHeight(44)
        self._btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_generate.setStyleSheet(BUTTON_HOME_RSA)
        self._btn_generate.clicked.connect(self._on_generate_keys)
        self._keygen_config_card.main_layout.addWidget(self._btn_generate)

        self._keygen_status_lbl = QLabel("")
        self._keygen_status_lbl.setStyleSheet(STATUS_LABEL_STYLE)
        self._keygen_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._keygen_config_card.main_layout.addWidget(self._keygen_status_lbl)

        self._keygen_config_card.main_layout.addStretch()
        grid.addWidget(self._keygen_config_card, 0, 0, 2, 1)

        # --- Public key card (right top) ---
        self._pubkey_card = CardWidget(translator.get("rsa_pubkey_label"))

        self._pubkey_output = QTextEdit()
        self._pubkey_output.setReadOnly(True)
        self._pubkey_output.setPlaceholderText("—")
        self._pubkey_output.setMinimumHeight(140)
        self._pubkey_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pubkey_output.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._pubkey_card.main_layout.addWidget(self._pubkey_output)

        self._btn_copy_pub = QPushButton(translator.get("rsa_btn_copy_pub"))
        self._btn_copy_pub.setMinimumHeight(38)
        self._btn_copy_pub.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_pub.setStyleSheet(BUTTON_PRIMARY)
        self._btn_copy_pub.clicked.connect(
            lambda: self._copy_to_clipboard(self._pubkey_output.toPlainText())
        )
        self._pubkey_card.main_layout.addWidget(self._btn_copy_pub)
        grid.addWidget(self._pubkey_card, 0, 1)

        # --- Private key card (right bottom) ---
        self._privkey_card = CardWidget(translator.get("rsa_privkey_label"))

        self._privkey_warning_lbl = QLabel(translator.get("rsa_privkey_warning"))
        self._privkey_warning_lbl.setStyleSheet(WARNING_LABEL_STYLE)
        self._privkey_card.main_layout.addWidget(self._privkey_warning_lbl)

        self._privkey_output = QTextEdit()
        self._privkey_output.setReadOnly(True)
        self._privkey_output.setPlaceholderText("—")
        self._privkey_output.setMinimumHeight(140)
        self._privkey_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._privkey_output.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._privkey_card.main_layout.addWidget(self._privkey_output)

        self._btn_copy_priv = QPushButton(translator.get("rsa_btn_copy_priv"))
        self._btn_copy_priv.setMinimumHeight(38)
        self._btn_copy_priv.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_priv.setStyleSheet(BUTTON_DANGER)
        self._btn_copy_priv.clicked.connect(
            lambda: self._copy_to_clipboard(self._privkey_output.toPlainText())
        )
        self._privkey_card.main_layout.addWidget(self._btn_copy_priv)
        grid.addWidget(self._privkey_card, 1, 1)

        outer.addLayout(grid)

    # ---- Encrypt page -----------------------------------------------------

    def _build_encrypt_page(self):
        outer = QVBoxLayout(self._encrypt_widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self._encrypt_navbar = self._nav_bar("rsa_encrypt_title")
        outer.addWidget(self._encrypt_navbar)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 2)
        grid.setRowStretch(2, 1)

        # Plaintext input card
        self._enc_plain_card = CardWidget(translator.get("rsa_plaintext_label"))

        self._enc_plain_limit = QLabel(translator.get("rsa_msg_limit"))
        self._enc_plain_limit.setStyleSheet(INFO_LABEL_STYLE)
        self._enc_plain_card.main_layout.addWidget(self._enc_plain_limit)

        self._enc_plain_input = QTextEdit()
        self._enc_plain_input.setPlaceholderText(translator.get("rsa_plaintext_placeholder"))
        self._enc_plain_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._enc_plain_input.setStyleSheet(INPUT_STYLE)
        self._enc_plain_card.main_layout.addWidget(self._enc_plain_input)
        grid.addWidget(self._enc_plain_card, 0, 0)

        # Public key input card
        self._enc_pubkey_card = CardWidget(translator.get("rsa_pubkey_input_label"))

        self._enc_pubkey_input = QTextEdit()
        self._enc_pubkey_input.setPlaceholderText(translator.get("rsa_pubkey_input_placeholder"))
        self._enc_pubkey_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._enc_pubkey_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._enc_pubkey_card.main_layout.addWidget(self._enc_pubkey_input)
        grid.addWidget(self._enc_pubkey_card, 0, 1)

        # Encrypt button (spans full width)
        btn_row = QWidget()
        btn_row.setStyleSheet("background-color: transparent;")
        btn_row_layout = QHBoxLayout(btn_row)
        btn_row_layout.setContentsMargins(0, 0, 0, 0)

        self._btn_do_encrypt = QPushButton(translator.get("rsa_btn_do_encrypt"))
        self._btn_do_encrypt.setMinimumHeight(44)
        self._btn_do_encrypt.setMinimumWidth(200)
        self._btn_do_encrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_do_encrypt.setStyleSheet(BUTTON_PRIMARY)
        self._btn_do_encrypt.clicked.connect(self._on_encrypt)
        btn_row_layout.addStretch()
        btn_row_layout.addWidget(self._btn_do_encrypt)
        btn_row_layout.addStretch()
        grid.addWidget(btn_row, 1, 0, 1, 2)

        # Ciphertext output card (spans full width)
        self._enc_cipher_card = CardWidget(translator.get("rsa_ciphertext_label"))

        self._enc_cipher_output = QTextEdit()
        self._enc_cipher_output.setReadOnly(True)
        self._enc_cipher_output.setPlaceholderText("—")
        self._enc_cipher_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._enc_cipher_output.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._enc_cipher_card.main_layout.addWidget(self._enc_cipher_output)

        self._btn_copy_cipher = QPushButton(translator.get("rsa_btn_copy_cipher"))
        self._btn_copy_cipher.setMinimumHeight(38)
        self._btn_copy_cipher.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_cipher.setStyleSheet(BUTTON_PRIMARY)
        self._btn_copy_cipher.clicked.connect(
            lambda: self._copy_to_clipboard(self._enc_cipher_output.toPlainText())
        )
        self._enc_cipher_card.main_layout.addWidget(self._btn_copy_cipher)
        grid.addWidget(self._enc_cipher_card, 2, 0, 1, 2)

        outer.addLayout(grid)

    # ---- Decrypt page -----------------------------------------------------

    def _build_decrypt_page(self):
        outer = QVBoxLayout(self._decrypt_widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self._decrypt_navbar = self._nav_bar("rsa_decrypt_title")
        outer.addWidget(self._decrypt_navbar)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 2)
        grid.setRowStretch(2, 1)

        # Ciphertext input card
        self._dec_cipher_card = CardWidget(translator.get("rsa_ciphertext_input_label"))

        self._dec_cipher_input = QTextEdit()
        self._dec_cipher_input.setPlaceholderText(translator.get("rsa_ciphertext_input_placeholder"))
        self._dec_cipher_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._dec_cipher_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._dec_cipher_card.main_layout.addWidget(self._dec_cipher_input)
        grid.addWidget(self._dec_cipher_card, 0, 0)

        # Private key input card
        self._dec_privkey_card = CardWidget(translator.get("rsa_privkey_input_label"))

        self._dec_privkey_input = QTextEdit()
        self._dec_privkey_input.setPlaceholderText(translator.get("rsa_privkey_input_placeholder"))
        self._dec_privkey_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._dec_privkey_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._dec_privkey_card.main_layout.addWidget(self._dec_privkey_input)
        grid.addWidget(self._dec_privkey_card, 0, 1)

        # Decrypt button (spans full width)
        btn_row = QWidget()
        btn_row.setStyleSheet("background-color: transparent;")
        btn_row_layout = QHBoxLayout(btn_row)
        btn_row_layout.setContentsMargins(0, 0, 0, 0)

        self._btn_do_decrypt = QPushButton(translator.get("rsa_btn_do_decrypt"))
        self._btn_do_decrypt.setMinimumHeight(44)
        self._btn_do_decrypt.setMinimumWidth(200)
        self._btn_do_decrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_do_decrypt.setStyleSheet(BUTTON_DANGER)
        self._btn_do_decrypt.clicked.connect(self._on_decrypt)
        btn_row_layout.addStretch()
        btn_row_layout.addWidget(self._btn_do_decrypt)
        btn_row_layout.addStretch()
        grid.addWidget(btn_row, 1, 0, 1, 2)

        # Decrypted output card (spans full width)
        self._dec_plain_card = CardWidget(translator.get("rsa_decrypted_label"))

        self._dec_plain_output = QTextEdit()
        self._dec_plain_output.setReadOnly(True)
        self._dec_plain_output.setPlaceholderText("—")
        self._dec_plain_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._dec_plain_output.setStyleSheet(INPUT_STYLE)
        self._dec_plain_card.main_layout.addWidget(self._dec_plain_output)

        self._btn_copy_decrypted = QPushButton(translator.get("rsa_btn_copy_decrypted"))
        self._btn_copy_decrypted.setMinimumHeight(38)
        self._btn_copy_decrypted.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_decrypted.setStyleSheet(BUTTON_PRIMARY)
        self._btn_copy_decrypted.clicked.connect(
            lambda: self._copy_to_clipboard(self._dec_plain_output.toPlainText())
        )
        self._dec_plain_card.main_layout.addWidget(self._btn_copy_decrypted)
        grid.addWidget(self._dec_plain_card, 2, 0, 1, 2)

        outer.addLayout(grid)

    # ---- Sign / Verify page -----------------------------------------------

    def _build_signverify_page(self):
        outer = QVBoxLayout(self._signverify_widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self._sv_navbar = self._nav_bar("rsa_signverify_title")
        outer.addWidget(self._sv_navbar)

        # Mode toggle row
        mode_row = QHBoxLayout()
        mode_row.setSpacing(12)
        mode_row.setContentsMargins(0, 0, 0, 4)

        self._btn_mode_sign = QPushButton(translator.get("rsa_btn_mode_sign"))
        self._btn_mode_sign.setMinimumHeight(40)
        self._btn_mode_sign.setMinimumWidth(160)
        self._btn_mode_sign.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_mode_sign.setStyleSheet(BUTTON_PRIMARY)   # active initially
        self._btn_mode_sign.clicked.connect(lambda: self._set_sv_mode("sign"))

        self._btn_mode_verify = QPushButton(translator.get("rsa_btn_mode_verify"))
        self._btn_mode_verify.setMinimumHeight(40)
        self._btn_mode_verify.setMinimumWidth(160)
        self._btn_mode_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_mode_verify.setStyleSheet(BUTTON_NEUTRAL)
        self._btn_mode_verify.clicked.connect(lambda: self._set_sv_mode("verify"))

        mode_row.addWidget(self._btn_mode_sign)
        mode_row.addWidget(self._btn_mode_verify)
        mode_row.addStretch()
        outer.addLayout(mode_row)

        # Stacked widget for sign / verify sub-views
        self._sv_stack = QStackedWidget()

        # sign view
        sign_widget = QWidget()
        self._build_sign_view(sign_widget)
        self._sv_stack.addWidget(sign_widget)   # 0

        # verify view
        verify_widget = QWidget()
        self._build_verify_view(verify_widget)
        self._sv_stack.addWidget(verify_widget)  # 1

        outer.addWidget(self._sv_stack)
        self._sv_mode = "sign"

    def _build_sign_view(self, parent: QWidget):
        grid = QGridLayout(parent)
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 2)
        grid.setRowStretch(2, 1)

        # Message input
        self._sign_msg_card = CardWidget(translator.get("rsa_sign_msg_label"))
        self._sign_msg_input = QTextEdit()
        self._sign_msg_input.setPlaceholderText(translator.get("rsa_sign_msg_placeholder"))
        self._sign_msg_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._sign_msg_input.setStyleSheet(INPUT_STYLE)
        self._sign_msg_card.main_layout.addWidget(self._sign_msg_input)
        grid.addWidget(self._sign_msg_card, 0, 0)

        # Private key input
        self._sign_privkey_card = CardWidget(translator.get("rsa_sign_privkey_label"))
        self._sign_privkey_input = QTextEdit()
        self._sign_privkey_input.setPlaceholderText(translator.get("rsa_privkey_input_placeholder"))
        self._sign_privkey_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._sign_privkey_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._sign_privkey_card.main_layout.addWidget(self._sign_privkey_input)
        grid.addWidget(self._sign_privkey_card, 0, 1)

        # Sign button
        btn_row = QWidget()
        btn_row.setStyleSheet("background-color: transparent;")
        brl = QHBoxLayout(btn_row)
        brl.setContentsMargins(0, 0, 0, 0)
        self._btn_do_sign = QPushButton(translator.get("rsa_btn_do_sign"))
        self._btn_do_sign.setMinimumHeight(44)
        self._btn_do_sign.setMinimumWidth(200)
        self._btn_do_sign.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_do_sign.setStyleSheet(BUTTON_SUCCESS)
        self._btn_do_sign.clicked.connect(self._on_sign)
        brl.addStretch()
        brl.addWidget(self._btn_do_sign)
        brl.addStretch()
        grid.addWidget(btn_row, 1, 0, 1, 2)

        # Signed document output
        self._sign_doc_card = CardWidget(translator.get("rsa_signed_doc_label"))
        self._sign_doc_output = QTextEdit()
        self._sign_doc_output.setReadOnly(True)
        self._sign_doc_output.setPlaceholderText("—")
        self._sign_doc_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._sign_doc_output.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._sign_doc_card.main_layout.addWidget(self._sign_doc_output)

        self._btn_copy_signed = QPushButton(translator.get("rsa_btn_copy_signed"))
        self._btn_copy_signed.setMinimumHeight(38)
        self._btn_copy_signed.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_signed.setStyleSheet(BUTTON_PRIMARY)
        self._btn_copy_signed.clicked.connect(
            lambda: self._copy_to_clipboard(self._sign_doc_output.toPlainText())
        )
        self._sign_doc_card.main_layout.addWidget(self._btn_copy_signed)
        grid.addWidget(self._sign_doc_card, 2, 0, 1, 2)

    def _build_verify_view(self, parent: QWidget):
        grid = QGridLayout(parent)
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 2)
        grid.setRowStretch(2, 1)

        # Signed document input
        self._verify_doc_card = CardWidget(translator.get("rsa_verify_doc_label"))
        self._verify_doc_input = QTextEdit()
        self._verify_doc_input.setPlaceholderText(translator.get("rsa_verify_doc_placeholder"))
        self._verify_doc_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._verify_doc_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._verify_doc_card.main_layout.addWidget(self._verify_doc_input)
        grid.addWidget(self._verify_doc_card, 0, 0)

        # Public key input
        self._verify_pubkey_card = CardWidget(translator.get("rsa_verify_pubkey_label"))
        self._verify_pubkey_input = QTextEdit()
        self._verify_pubkey_input.setPlaceholderText(translator.get("rsa_pubkey_input_placeholder"))
        self._verify_pubkey_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._verify_pubkey_input.setStyleSheet(INPUT_STYLE + "QTextEdit { font-size: 11px; }")
        self._verify_pubkey_card.main_layout.addWidget(self._verify_pubkey_input)
        grid.addWidget(self._verify_pubkey_card, 0, 1)

        # Verify button
        btn_row = QWidget()
        btn_row.setStyleSheet("background-color: transparent;")
        brl = QHBoxLayout(btn_row)
        brl.setContentsMargins(0, 0, 0, 0)
        self._btn_do_verify = QPushButton(translator.get("rsa_btn_do_verify"))
        self._btn_do_verify.setMinimumHeight(44)
        self._btn_do_verify.setMinimumWidth(200)
        self._btn_do_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_do_verify.setStyleSheet(BUTTON_SUCCESS)
        self._btn_do_verify.clicked.connect(self._on_verify)
        brl.addStretch()
        brl.addWidget(self._btn_do_verify)
        brl.addStretch()
        grid.addWidget(btn_row, 1, 0, 1, 2)

        # Result output
        self._verify_result_card = CardWidget(translator.get("rsa_verify_result_label"))
        self._verify_result_output = QTextEdit()
        self._verify_result_output.setReadOnly(True)
        self._verify_result_output.setPlaceholderText("—")
        self._verify_result_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._verify_result_output.setStyleSheet(INPUT_STYLE)
        self._verify_result_card.main_layout.addWidget(self._verify_result_output)
        grid.addWidget(self._verify_result_card, 2, 0, 1, 2)

    # ------------------------------------------------------------------
    # Logic handlers
    # ------------------------------------------------------------------

    def _set_sv_mode(self, mode: str):
        self._sv_mode = mode
        if mode == "sign":
            self._btn_mode_sign.setStyleSheet(BUTTON_PRIMARY)
            self._btn_mode_verify.setStyleSheet(BUTTON_NEUTRAL)
            self._sv_stack.setCurrentIndex(0)
        else:
            self._btn_mode_sign.setStyleSheet(BUTTON_NEUTRAL)
            self._btn_mode_verify.setStyleSheet(BUTTON_PRIMARY)
            self._sv_stack.setCurrentIndex(1)

    # ---- Key generation ---------------------------------------------------

    def _on_generate_keys(self):
        self._btn_generate.setEnabled(False)
        self._keygen_status_lbl.setText(translator.get("rsa_keygen_generating"))
        self._pubkey_output.setPlainText("")
        self._privkey_output.setPlainText("")

        self._worker = RSAKeyWorker()
        self._worker.finished.connect(self._on_keys_ready)
        self._worker.error.connect(self._on_keygen_error)
        self._worker.start()

    def _on_keys_ready(self, pub_key: tuple, priv_key: tuple):
        self._btn_generate.setEnabled(True)
        self._keygen_status_lbl.setText(translator.get("rsa_keygen_done"))
        self._pubkey_output.setPlainText(_key_to_json(pub_key))
        self._privkey_output.setPlainText(_key_to_json(priv_key))

    def _on_keygen_error(self, msg: str):
        self._btn_generate.setEnabled(True)
        self._keygen_status_lbl.setText("")
        show_error(self, f"Erro ao gerar chaves: {msg}")

    # ---- Encryption -------------------------------------------------------

    def _on_encrypt(self):
        plaintext = self._enc_plain_input.toPlainText().strip()
        pubkey_txt = self._enc_pubkey_input.toPlainText().strip()

        if not plaintext:
            show_warning(self, translator.get("rsa_err_no_text"))
            return
        if not pubkey_txt:
            show_warning(self, translator.get("rsa_err_no_pubkey"))
            return

        try:
            pub_key = _json_to_key(pubkey_txt)
        except ValueError:
            show_error(self, translator.get("rsa_err_invalid_key"))
            return

        try:
            ciphertext = rsa_encrypt(plaintext.encode("utf-8"), pub_key)
            self._enc_cipher_output.setPlainText(base64.b64encode(ciphertext).decode())
        except ValueError as exc:
            if "longa" in str(exc) or "long" in str(exc).lower():
                show_warning(self, translator.get("rsa_err_msg_too_long"))
            else:
                show_error(self, str(exc))
        except Exception as exc:
            show_error(self, str(exc))

    # ---- Decryption -------------------------------------------------------

    def _on_decrypt(self):
        cipher_b64 = self._dec_cipher_input.toPlainText().strip()
        privkey_txt = self._dec_privkey_input.toPlainText().strip()

        if not cipher_b64:
            show_warning(self, translator.get("rsa_err_no_cipher"))
            return
        if not privkey_txt:
            show_warning(self, translator.get("rsa_err_no_privkey"))
            return

        try:
            priv_key = _json_to_key(privkey_txt)
        except ValueError:
            show_error(self, translator.get("rsa_err_invalid_key"))
            return

        try:
            ciphertext = base64.b64decode(cipher_b64)
        except Exception:
            show_error(self, "Base64 inválido no texto cifrado.")
            return

        try:
            plaintext_bytes = rsa_decrypt(ciphertext, priv_key)
            try:
                self._dec_plain_output.setPlainText(plaintext_bytes.decode("utf-8"))
            except UnicodeDecodeError:
                self._dec_plain_output.setPlainText(plaintext_bytes.hex())
        except Exception:
            show_error(self, translator.get("rsa_err_decrypt_fail"))

    # ---- Sign -------------------------------------------------------------

    def _on_sign(self):
        msg_text = self._sign_msg_input.toPlainText().strip()
        privkey_txt = self._sign_privkey_input.toPlainText().strip()

        if not msg_text:
            show_warning(self, translator.get("rsa_err_no_msg"))
            return
        if not privkey_txt:
            show_warning(self, translator.get("rsa_err_no_privkey_sign"))
            return

        try:
            priv_key = _json_to_key(privkey_txt)
        except ValueError:
            show_error(self, translator.get("rsa_err_invalid_key"))
            return

        try:
            message = msg_text.encode("utf-8")
            digest = hashlib.sha3_256(message).digest()
            signature = _sign_hash(digest, priv_key)

            signed_doc = (
                f"{BEGIN_SIGNED_MSG}\n"
                f"{base64.b64encode(message).decode('ascii')}\n"
                f"{BEGIN_SIGNATURE}\n"
                f"{base64.b64encode(signature).decode('ascii')}\n"
                f"{END_SIGNED_MSG}\n"
            )
            self._sign_doc_output.setPlainText(signed_doc)
        except Exception as exc:
            show_error(self, f"Erro ao assinar: {exc}")

    # ---- Verify -----------------------------------------------------------

    def _on_verify(self):
        signed_doc = self._verify_doc_input.toPlainText().strip()
        pubkey_txt = self._verify_pubkey_input.toPlainText().strip()

        if not signed_doc:
            show_warning(self, translator.get("rsa_err_no_doc"))
            return
        if not pubkey_txt:
            show_warning(self, translator.get("rsa_err_no_pubkey_verify"))
            return

        try:
            pub_key = _json_to_key(pubkey_txt)
        except ValueError:
            show_error(self, translator.get("rsa_err_invalid_key"))
            return

        # Parse signed document
        lines = signed_doc.splitlines()
        try:
            msg_start = lines.index(BEGIN_SIGNED_MSG)
            sig_start = lines.index(BEGIN_SIGNATURE)
            end_idx = lines.index(END_SIGNED_MSG)
        except ValueError:
            show_error(self, "Formato do documento assinado inválido.")
            return

        message_b64 = "".join(lines[msg_start + 1: sig_start]).strip()
        signature_b64 = "".join(lines[sig_start + 1: end_idx]).strip()

        try:
            message = base64.b64decode(message_b64)
            signature = base64.b64decode(signature_b64)
        except Exception:
            show_error(self, "Falha ao decodificar Base64 no documento assinado.")
            return

        try:
            recovered_digest = _verify_signature(signature, pub_key)
            actual_digest = hashlib.sha3_256(message).digest()

            if recovered_digest == actual_digest:
                result_text = (
                    f"✓ {translator.get('rsa_verify_ok')}\n\n"
                    f"Mensagem:\n{message.decode('utf-8', errors='replace')}"
                )
                self._verify_result_output.setStyleSheet(
                    INPUT_STYLE + "QTextEdit { color: #10B981; font-weight: 600; }"
                )
            else:
                result_text = f"✗ {translator.get('rsa_verify_fail')}"
                self._verify_result_output.setStyleSheet(
                    INPUT_STYLE + "QTextEdit { color: #DC2626; font-weight: 600; }"
                )
            self._verify_result_output.setPlainText(result_text)
        except Exception:
            result_text = f"✗ {translator.get('rsa_verify_fail')}"
            self._verify_result_output.setStyleSheet(
                INPUT_STYLE + "QTextEdit { color: #DC2626; font-weight: 600; }"
            )
            self._verify_result_output.setPlainText(result_text)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _copy_to_clipboard(self, text: str):
        if text and text != "—":
            QApplication.clipboard().setText(text)

    # ------------------------------------------------------------------
    # Retranslation
    # ------------------------------------------------------------------

    def retranslate_ui(self, lang_code=None):
        # Home
        self._home_title.setText(translator.get("rsa_home_title"))
        self._home_subtitle.setText(translator.get("rsa_home_subtitle"))
        self._btn_home_keygen.setText(translator.get("rsa_btn_keygen"))
        self._btn_home_encrypt.setText(translator.get("rsa_btn_encrypt"))
        self._btn_home_decrypt.setText(translator.get("rsa_btn_decrypt"))
        self._btn_home_signverify.setText(translator.get("rsa_btn_sign_verify"))

        # Keygen
        for bar in (self._keygen_navbar, self._encrypt_navbar,
                    self._decrypt_navbar, self._sv_navbar):
            bar._btn_back.setText(translator.get("rsa_btn_back"))  # type: ignore[attr-defined]
            bar._lbl_title.setText(translator.get(bar._title_key))  # type: ignore[attr-defined]

        self._keygen_config_card.title_label.setText(translator.get("rsa_keygen_title"))
        self._keygen_info_lbl.setText(translator.get("rsa_keygen_info"))
        self._btn_generate.setText(translator.get("rsa_keygen_btn"))
        self._pubkey_card.title_label.setText(translator.get("rsa_pubkey_label"))
        self._privkey_card.title_label.setText(translator.get("rsa_privkey_label"))
        self._privkey_warning_lbl.setText(translator.get("rsa_privkey_warning"))
        self._btn_copy_pub.setText(translator.get("rsa_btn_copy_pub"))
        self._btn_copy_priv.setText(translator.get("rsa_btn_copy_priv"))

        # Encrypt
        self._enc_plain_card.title_label.setText(translator.get("rsa_plaintext_label"))
        self._enc_plain_limit.setText(translator.get("rsa_msg_limit"))
        self._enc_plain_input.setPlaceholderText(translator.get("rsa_plaintext_placeholder"))
        self._enc_pubkey_card.title_label.setText(translator.get("rsa_pubkey_input_label"))
        self._enc_pubkey_input.setPlaceholderText(translator.get("rsa_pubkey_input_placeholder"))
        self._btn_do_encrypt.setText(translator.get("rsa_btn_do_encrypt"))
        self._enc_cipher_card.title_label.setText(translator.get("rsa_ciphertext_label"))
        self._btn_copy_cipher.setText(translator.get("rsa_btn_copy_cipher"))

        # Decrypt
        self._dec_cipher_card.title_label.setText(translator.get("rsa_ciphertext_input_label"))
        self._dec_cipher_input.setPlaceholderText(translator.get("rsa_ciphertext_input_placeholder"))
        self._dec_privkey_card.title_label.setText(translator.get("rsa_privkey_input_label"))
        self._dec_privkey_input.setPlaceholderText(translator.get("rsa_privkey_input_placeholder"))
        self._btn_do_decrypt.setText(translator.get("rsa_btn_do_decrypt"))
        self._dec_plain_card.title_label.setText(translator.get("rsa_decrypted_label"))
        self._btn_copy_decrypted.setText(translator.get("rsa_btn_copy_decrypted"))

        # Sign/Verify
        self._btn_mode_sign.setText(translator.get("rsa_btn_mode_sign"))
        self._btn_mode_verify.setText(translator.get("rsa_btn_mode_verify"))
        self._sign_msg_card.title_label.setText(translator.get("rsa_sign_msg_label"))
        self._sign_msg_input.setPlaceholderText(translator.get("rsa_sign_msg_placeholder"))
        self._sign_privkey_card.title_label.setText(translator.get("rsa_sign_privkey_label"))
        self._sign_privkey_input.setPlaceholderText(translator.get("rsa_privkey_input_placeholder"))
        self._btn_do_sign.setText(translator.get("rsa_btn_do_sign"))
        self._sign_doc_card.title_label.setText(translator.get("rsa_signed_doc_label"))
        self._btn_copy_signed.setText(translator.get("rsa_btn_copy_signed"))
        self._verify_doc_card.title_label.setText(translator.get("rsa_verify_doc_label"))
        self._verify_doc_input.setPlaceholderText(translator.get("rsa_verify_doc_placeholder"))
        self._verify_pubkey_card.title_label.setText(translator.get("rsa_verify_pubkey_label"))
        self._verify_pubkey_input.setPlaceholderText(translator.get("rsa_pubkey_input_placeholder"))
        self._btn_do_verify.setText(translator.get("rsa_btn_do_verify"))
        self._verify_result_card.title_label.setText(translator.get("rsa_verify_result_label"))
