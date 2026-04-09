from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QApplication, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBitmap, QPainter, QPen, QColor


class InputDialog(QDialog):
    """Minimalist input popup — clean monospace aesthetic."""
    def __init__(self, title, message, default_text="", parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        QApplication.beep()

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 8)
        layout.setSpacing(12)

        # Title / Label
        message_label = QLabel(message, self)
        message_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            font-family: 'Roboto Mono', monospace;
            color: #1F2937;
            line-height: 1.5;
        """)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Input Field
        self.input_field = QLineEdit(default_text, self)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #1F2937;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Roboto Mono', monospace;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2F80ED;
            }
        """)
        layout.addWidget(self.input_field)

        # Linha divisória
        separator_line = QFrame(self)
        separator_line.setFrameShape(QFrame.Shape.HLine)
        separator_line.setFrameShadow(QFrame.Shadow.Plain)
        separator_line.setLineWidth(1)
        separator_line.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(separator_line)

        # Botoes
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancelar", self)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-family: 'Roboto Mono', monospace;
                font-size: 13px;
                font-weight: 600;
                padding: 8px;
                color: #64748B;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
        """)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setFlat(True)
        
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-family: 'Roboto Mono', monospace;
                font-size: 13px;
                font-weight: 600;
                padding: 8px;
                color: #2F80ED;
            }
            QPushButton:hover {
                background-color: rgba(47, 128, 237, 0.08);
            }
        """)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setFlat(True)

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(ok_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setMinimumSize(400, 180)
        self.setStyleSheet("background-color: #FAFAFA; color: #1F2937;")
        self.setMask(self._get_rounded_mask())

    def _get_rounded_mask(self):
        mask = QBitmap(self.size())
        mask.fill(Qt.GlobalColor.color0)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.GlobalColor.color1)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.end()
        return mask

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#000000"), 1)
        painter.setPen(pen)
        rect = self.rect()
        rect.adjust(0, 0, -1, -1)
        painter.drawRoundedRect(rect, 12, 12)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self._get_rounded_mask())
        
    def get_text(self):
        return self.input_field.text()


def get_input_text(parent, title, message, default_text=""):
    """Utility function to show minimalist input dialog and get string."""
    dialog = InputDialog(title, message, default_text, parent)
    ok = dialog.exec() == QDialog.DialogCode.Accepted
    return dialog.get_text(), ok
