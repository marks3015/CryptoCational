"""
Utilitários para converter imagens para BMP 24-bit raw e extrair/recombinar header/pixels.

Permite visualizar os efeitos do AES sobre pixels reais preservando o header BMP,
garantindo que o arquivo resultante ainda seja uma imagem válida.
"""

from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray, QBuffer, Qt, QIODevice
import struct


def image_to_bmp_raw(data: bytes, width: int = 512, height: int = 512) -> bytes:
    """
    Converte bytes de imagem (PNG/JPEG/BMP/etc) para BMP 24-bit não comprimido.

    A imagem é redimensionada para (width x height) e convertida para RGB888.
    O resultado é um BMP válido em memória.
    """
    image = QImage()
    if not image.loadFromData(data):
        raise ValueError("Não foi possível carregar a imagem a partir dos dados fornecidos.")

    image = image.scaled(
        width,
        height,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    if image.format() != QImage.Format.Format_RGB888:
        image = image.convertToFormat(QImage.Format.Format_RGB888)

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)

    if not image.save(buffer, "BMP"):
        raise ValueError("Falha ao salvar imagem como BMP em memória.")

    buffer.close()
    return bytes(byte_array)


def extract_bmp_header_and_pixels(bmp_data: bytes) -> tuple[bytes, bytes]:
    """
    Extrai o header BMP e os dados de pixel brutos.

    Valida se é um BMP 24-bit (true color) para garantir preview consistente.
    """
    if len(bmp_data) < 54:
        raise ValueError("Dados BMP muito curtos para serem um BMP válido.")

    if bmp_data[:2] != b"BM":
        raise ValueError("O arquivo não é um BMP válido (assinatura 'BM' não encontrada).")

    # Offset para início dos pixels (offset 0x0A, 4 bytes)
    pixel_offset = struct.unpack("<I", bmp_data[10:14])[0]
    # Bits por pixel (offset 0x1C, 2 bytes)
    bpp = struct.unpack("<H", bmp_data[28:30])[0]

    if bpp != 24:
        raise ValueError(f"BMP deve ser 24-bit, mas detectado {bpp}-bit.")

    header = bmp_data[:pixel_offset]
    pixels = bmp_data[pixel_offset:]
    return header, pixels


def rebuild_bmp(header: bytes, pixel_data: bytes) -> bytes:
    """Reconstrói um arquivo BMP a partir do header e dados de pixel."""
    return header + pixel_data
