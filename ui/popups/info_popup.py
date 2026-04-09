from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBitmap, QPainter, QPen, QColor


class InfoDialog(QDialog):
    """Minimalist info popup — no icon, clean monospace aesthetic."""
    def __init__(self, message, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        QApplication.beep()

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 8)
        layout.setSpacing(12)

        # Mensagem
        message_label = QLabel(message, self)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            font-size: 14px;
            font-family: 'Roboto Mono', monospace;
            color: #1F2937;
            line-height: 1.5;
        """)
        message_label.setWordWrap(True)

        # Linha divisória
        separator_line = QFrame(self)
        separator_line.setFrameShape(QFrame.Shape.HLine)
        separator_line.setFrameShadow(QFrame.Shadow.Plain)
        separator_line.setLineWidth(1)
        separator_line.setStyleSheet("color: #E2E8F0;")

        # Botão OK
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
                color: #334155;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
        """)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setFlat(True)

        layout.addWidget(message_label)
        layout.addWidget(separator_line)
        layout.addWidget(ok_button)

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


def show_info(parent, message):
    """Utility function to show minimalist info dialog"""
    dialog = InfoDialog(message, parent)
    dialog.exec()
