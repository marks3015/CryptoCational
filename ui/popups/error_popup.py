from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBitmap, QPainter, QPen, QColor


class ErrorDialog(QDialog):
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
        message_label.setStyleSheet("font-size: 16px; font-family: 'Roboto Mono', monospace; color: #333333;")
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

        layout.addStretch()
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addWidget(separator_line)
        layout.addWidget(ok_button)

        self.setLayout(layout)
        self.setFixedSize(400, 180)
        self.setStyleSheet("background-color: #FAFAFA; color: #333333;")
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
        rect.adjust(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 12, 12)


def show_error(parent, message):
    """Utility function to show error dialog"""
    dialog = ErrorDialog(message, parent)
    dialog.exec()
